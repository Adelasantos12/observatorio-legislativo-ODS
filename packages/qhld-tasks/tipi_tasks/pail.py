"""Etapa PAIL — análisis ex ante de iniciativas (protocolo PAIL-MX v2).

Módulo SELECCIONABLE del escáner, hermano de la codificación NormTrace. Envuelve
el motor `pail_engine` (que NO se modifica): corre el rulebook determinista/
heurístico + las verificaciones contra el corpus CRN (capa CSN), y opcionalmente
resuelve las verificaciones `PENDIENTE_JUICIO` con un LLM ceñido a la evidencia.
No toca el flujo ODS/tagger.

Contrato (INTEGRACION):
- La capa CSN corre siempre que se pida PAIL; si faltan índices, el motor degrada
  solo a NO_VERIFICABLE (no se envuelve en try/except que oculte errores reales).
- La pasada LLM (opcional) califica CADA `PENDIENTE_JUICIO` usando como sistema la
  `regla_evidencia` del rulebook + la evidencia ya extraída por el motor; tiene
  PROHIBIDO completar con conocimiento propio del derecho mexicano; sin evidencia
  suficiente responde NO_EVALUABLE. Tras la pasada se re-agrega con el propio
  `pail_engine.dictaminar()` (no se reimplementa la agregación).
- La salida valida contra `pail_dictamen.schema.json`, como el codificador con
  `unit_analysis`.
"""

import json
import re
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

from celery import shared_task
from jsonschema import Draft7Validator

from . import config, llm, pail_engine


# --- Rulebook y esquema (fuente de verdad; se leen, no se editan) -------------

@lru_cache(maxsize=1)
def _rulebook() -> dict:
    return json.loads(Path(config.PAIL_PROTOCOL).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _validator() -> Draft7Validator:
    return Draft7Validator(json.loads(Path(config.PAIL_SCHEMA).read_text(encoding="utf-8")))


def validate_dictamen(dictamen: dict) -> list[str]:
    """Errores de validación del dictamen contra el esquema (vacío si es válido)."""
    return [e.message for e in _validator().iter_errors(dictamen)]


def _indices():
    """Índices del corpus CRN, o None si no hay ruta/índices. `cargar_indices` del
    motor ya maneja la ausencia (degradación a NO_VERIFICABLE): no se envuelve."""
    if not config.PAIL_INDICES_PATH:
        return None
    return pail_engine.cargar_indices(config.PAIL_INDICES_PATH)


# --- Pasada de juicio LLM sobre las verificaciones PENDIENTE_JUICIO -----------

def _parse_json(text: str) -> dict | None:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _juicio_system(rulebook: dict) -> str:
    """Instrucción de sistema: la `regla_evidencia` del rulebook + el blindaje.
    El texto de la iniciativa es evidencia válida para juzgar su propia técnica y
    racionalidad; el corpus es la fuente para comparar con derecho vigente. Sin
    evidencia suficiente, NO_EVALUABLE. Se pide explicación (qué y por qué) y una
    recomendación concreta (qué hacer), escritas para quien legisla."""
    validos = "|".join(rulebook["resultados_validos"])
    return (
        rulebook["regla_evidencia"]
        + "\n\nCalificas UNA verificación de técnica legislativa o racionalidad sobre "
        "una iniciativa mexicana, para asesorar a quien la dictamina. Reglas:\n"
        "1. Tu evidencia es el TEXTO DE LA INICIATIVA provisto abajo y las citas del "
        "corpus incluidas. El propio articulado y su exposición de motivos SON fuente "
        "válida para juzgar su técnica, racionalidad y proporcionalidad: léelos y "
        "pronúnciate sobre ellos.\n"
        "2. TIENES PROHIBIDO afirmar como hecho el contenido de normas vigentes que no "
        "estén en la evidencia: para comparar con derecho vigente usa solo las citas del "
        "corpus incluidas; no inventes artículos, cifras ni jurisprudencia.\n"
        "3. Si el texto provisto no contiene lo necesario para calificar con rigor, tu "
        "resultado ES 'NO_EVALUABLE'.\n"
        "4. Escribe para una persona legisladora, sin jerga: la 'explicacion' dice QUÉ se "
        "observó y POR QUÉ importa; la 'recomendacion' dice QUÉ hacer para corregirlo, en "
        "una frase concreta y accionable.\n"
        "5. Responde ÚNICAMENTE un objeto JSON: "
        '{"resultado": <uno de: ' + validos + '>, "explicacion": "<qué y por qué, citando '
        'la evidencia>", "recomendacion": "<qué hacer, concreto>", "evidencia": [{"cita": '
        '"...", "ubicacion": "...", "fuente": "..."}]}.'
    )


def _juicio_user(h: dict, contexto: dict, expediente: str) -> str:
    return (
        f"Verificación {h['id']} — {h['nombre']} (severidad {h['severidad']})\n"
        f"Criterio: {h.get('criterio_para_llm', '')}\n\n"
        f"TEXTO DE LA INICIATIVA (tu evidencia principal; el articulado y su exposición "
        f"son la fuente para juzgar su propia técnica y racionalidad):\n{expediente}\n\n"
        f"Datos extraídos por el motor (tipo de instrumento, normas invocadas): "
        f"{json.dumps(contexto, ensure_ascii=False)[:800]}\n"
        f"Evidencia adicional del motor y del corpus: "
        f"{json.dumps(h.get('evidencia', []), ensure_ascii=False)[:1500]}\n\n"
        "Califica el criterio con esta evidencia. Si el texto no contiene lo necesario, "
        "responde NO_EVALUABLE."
    )


def _resolver_una(h: dict, system: str, contexto: dict, expediente: str,
                  validos: set) -> str | None:
    """Resuelve UNA verificación con el LLM. Muta `h` in situ y devuelve el mensaje
    de error del proveedor si lo hubo (para superficie/diagnóstico), o None."""
    err = None
    try:
        text = llm.complete(system, _juicio_user(h, contexto, expediente))
        data = _parse_json(text) or {}
        res = data.get("resultado")
        if res in validos and res != "PENDIENTE_JUICIO":
            h["resultado"] = res
            h["explicacion"] = (data.get("explicacion") or "")[:1000]
            if data.get("recomendacion"):
                h["recomendacion"] = str(data["recomendacion"])[:600]
            if isinstance(data.get("evidencia"), list) and data["evidencia"]:
                h["evidencia"] = data["evidencia"]
        else:
            h["resultado"] = "NO_EVALUABLE"
            h["explicacion"] = "el modelo no devolvió un resultado válido con la evidencia provista"
    except Exception as e:  # noqa: BLE001 — fallo del proveedor: no bloquea el dictamen
        h["resultado"] = "NO_EVALUABLE"
        h["explicacion"] = f"juicio no resuelto (proveedor LLM: {e})"
        err = str(e)
    h.pop("criterio_para_llm", None)
    return err


def _resolver_juicios(dictamen: dict, texto_norm: str) -> dict:
    """Resuelve las PENDIENTE_JUICIO con el LLM (EN PARALELO, para no exceder el
    tiempo de la petición con decenas de llamadas secuenciales) y re-agrega con el
    motor. A cada juicio se le pasa el TEXTO de la iniciativa (articulado + exposición
    + transitorios) como evidencia: sin él, el blindaje deja todo en NO_EVALUABLE mudo
    y el análisis 'no dice nada'. Si el proveedor falla de forma sistémica
    (clave/modelo/cuota), se expone `llm_error` para diagnóstico."""
    rb = _rulebook()
    validos = set(rb["resultados_validos"])
    system = _juicio_system(rb)
    contexto = dictamen.get("contexto", {})
    expediente = _expediente_para_juicio(texto_norm)
    pendientes = [h for h in dictamen["verificaciones"]
                  if h.get("resultado") == "PENDIENTE_JUICIO"][:config.PAIL_LLM_MAX_JUICIOS]

    errores = []
    if pendientes:
        max_workers = max(1, min(config.PAIL_LLM_CONCURRENCY, len(pendientes)))
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            for err in ex.map(
                    lambda h: _resolver_una(h, system, contexto, expediente, validos),
                    pendientes):
                if err:
                    errores.append(err)

    # Re-agregación con las funciones del propio motor (no se reimplementan): el
    # dictamen y el bloque `resumen` se recalculan sobre los resultados ya resueltos,
    # así sube la cobertura y bajan las verificaciones sin evaluar.
    sin_articulado = dictamen.get("articulos_detectados", 0) == 0
    por_capa, glob, cobertura = pail_engine.dictaminar(
        dictamen["verificaciones"], sin_articulado)
    dictamen["dictamen_por_capa"] = por_capa
    dictamen["dictamen_global"] = glob
    dictamen["cobertura_evaluada"] = cobertura
    dictamen["resumen"] = pail_engine.resumen_ejecutivo(
        dictamen["verificaciones"], cobertura, sin_articulado)
    _enriquecer_resumen(dictamen)
    resueltas = len(pendientes) - len(errores)
    dictamen["nota"] = (
        f"Pasada de juicio LLM: {resueltas}/{len(pendientes)} verificacion(es) resuelta(s) "
        "solo con la evidencia extraída y las citas del corpus."
    )
    if errores:
        # Error sistémico del proveedor: se expone el primer mensaje real (p. ej.
        # 'HTTP 404: model ... not found' o 'API key not valid') para diagnóstico.
        dictamen["llm_error"] = (
            f"{len(errores)}/{len(pendientes)} verificaciones no se pudieron evaluar con el "
            f"LLM. Revisa LLM_PROVIDER/LLM_MODEL/LLM_API_KEY. Primer error: {errores[0][:300]}"
        )
    return dictamen


# --- Normalización del insumo (envoltorio, no toca el motor) ------------------

# La extracción de PDF de la Gaceta ensucia el texto de tres formas que rompen el
# segmentador y el clasificador del motor (que esperan "Artículo" a inicio de línea
# y verbos de reforma en espacio simple). Se normaliza el insumo SIN tocar el motor:
#   (a) pdfminer inserta espacios dobles entre palabras ("se  reforma"), lo que hace
#       fallar TODOS los regex de espacio simple del motor (tipo, enunciado, etc.).
#   (b) el texto reformado va entrecomillado y el encabezado queda pegado a una
#       comilla de apertura («"Artículo 111.»), a media línea, o como "Artículo
#       único:" en minúscula.
#   (c) la cláusula de promulgación ("Decreto por el que se reforma… la Ley X")
#       suele estar tras una exposición larga —fuera de la ventana de 4000 car. que
#       el motor escanea para clasificar— y con saltos de línea internos que impiden
#       casar el nombre de la norma objetivo contra el corpus. Se antepone una copia
#       aplanada para revivir la clasificación (tipo) y la armonización (CSN-04).
# NO se promueven remisiones en minúscula ("el artículo 71 de la Constitución").
_COMILLAS = "“”«»‹›\"'`"
_ENCABEZADO = (r"(?:\d|[ÚU]nico|Primero|Segundo|Tercero|Cuarto|Quinto|Sexto|"
               r"S[eé]ptimo|Octavo|Noveno|D[eé]cimo)")
_WS = re.compile(r"[ \t]{2,}")
_ART_LINEA_COMILLA = re.compile(rf"(?m)^[ \t{re.escape(_COMILLAS)}]+(Art[íi]culo\s)")
_ART_MEDIA_LINEA = re.compile(
    rf"(?<=[\.\:;\)])[ \t{re.escape(_COMILLAS)}]*(Art[íi]culo\s+{_ENCABEZADO})")
_ART_UNICO_MIN = re.compile(r"(Art[íi]culo\s+)[úu]nico\s*[:.]")
# Ancla preferente: la fórmula de promulgación "Decreto por el que se {verbo}…".
# Exige "se" para que el verbo case con el clasificador del motor (se reforma|se
# adiciona|se deroga|se expide). Respaldo: primera cláusula "se {verbo}…" suelta.
_DECRETO = re.compile(
    r"(?i)decreto\s+(?:por\s+el\s+que|que)\s+se\s+"
    r"(?:reforman?|adicionan?|derogan?|expiden?|abrogan?|agregan?)[^.]{0,400}")
_ENACT = re.compile(
    r"(?i)\bse\s+(?:reforman?|adicionan?|derogan?|expiden?)\b[^.]{10,400}")
# Corta la cola no dispositiva (fundamento, autoría, materia) que contamina los
# números de artículo con los del art. 71/72 del fundamento u otros ajenos.
_CORTE_CLAUSULA = re.compile(
    r"(?i),?\s+(?:en\s+materia|a\s+cargo|suscrit|presentad|con\s+fundamento|"
    r"al\s+tenor|del?\s+(?:diputad|senador|grupo)).*$", re.S)


def _clausula_decreto(texto: str) -> str | None:
    """Extrae y aplana la cláusula de promulgación del decreto (o None)."""
    m = _DECRETO.search(texto) or _ENACT.search(texto)
    if not m:
        return None
    return _CORTE_CLAUSULA.sub("", re.sub(r"\s+", " ", m.group(0)).strip())


def _normalizar_insumo(texto: str) -> str:
    """Normaliza el insumo (ver arriba) sin alterar el motor ni crear artículos
    falsos: la cláusula antepuesta va en minúscula/una línea, así que el segmentador
    (que exige "Artículo" capitalizado a inicio de línea) no la toma como encabezado."""
    texto = _WS.sub(" ", texto)
    texto = _ART_LINEA_COMILLA.sub(r"\1", texto)
    texto = _ART_MEDIA_LINEA.sub(lambda m: "\n" + m.group(1), texto)
    texto = _ART_UNICO_MIN.sub(r"\1Único.", texto)
    clausula = _clausula_decreto(texto)
    if clausula:
        texto = "DECRETO: " + clausula + ".\n\n" + texto
    return texto


def _expediente_para_juicio(texto_norm: str, limite: int = 6500) -> str:
    """Arma la evidencia textual que ve el LLM en cada juicio: articulado propuesto
    (donde vive la mayoría de las verificaciones de racionalidad) + régimen
    transitorio + cabeza de la exposición de motivos. Sin este texto el modelo, bajo
    el blindaje, deja todo en NO_EVALUABLE y el análisis 'no dice nada'."""
    P = pail_engine.segmentar(texto_norm)
    arts = "\n\n".join(a["texto"].strip() for a in P.get("articulos", []))[:3500]
    trans = (P.get("transitorios") or "").strip()[:1200]
    resto = max(800, limite - len(arts) - len(trans))
    expo = (P.get("expo") or "").strip()[:resto]
    partes = []
    if expo:
        partes.append("EXPOSICIÓN DE MOTIVOS (extracto):\n" + expo)
    if arts:
        partes.append("ARTICULADO PROPUESTO:\n" + arts)
    if trans:
        partes.append("RÉGIMEN TRANSITORIO:\n" + trans)
    return "\n\n".join(partes) or texto_norm[:limite]


def _enriquecer_resumen(dictamen: dict) -> None:
    """Tras re-agregar con el motor, cuelga en cada fila del resumen la
    `recomendacion` del LLM (qué hacer), buscándola por id en las verificaciones.
    El motor no la conoce; se añade aquí para que el panel muestre acción, no códigos."""
    por_id = {h["id"]: h for h in dictamen.get("verificaciones", [])}
    for bucket in ("red_flags", "areas_oportunidad"):
        for fila in dictamen.get("resumen", {}).get(bucket, []) or []:
            h = por_id.get(fila.get("id"))
            if h and h.get("recomendacion"):
                fila["recomendacion"] = h["recomendacion"]


def _conexiones(dictamen: dict) -> dict:
    """Bloque legible 'con qué leyes se conecta': normas que la iniciativa CITA (con
    vigencia, de CSN-06) y normas del corpus que remiten a lo reformado y por tanto
    son candidatas a armonización conforme (CSN-04). Es el mapa que un legislador
    necesita para saber qué tocar; se deriva de lo que el motor ya calculó."""
    def by_id(vid):
        return next((v for v in dictamen.get("verificaciones", []) if v["id"] == vid), None)

    c04, c06 = by_id("CSN-04"), by_id("CSN-06")
    citadas = []
    if c06:
        for n in (c06.get("normas_invocadas") or []):
            citadas.append({"norma": n.get("norma"), "ultima_reforma": n.get("ultima_reforma"),
                            "estatus": n.get("estatus")})
    armonizar, objetivo, estado_arm = [], None, None
    if c04:
        objetivo = c04.get("norma_objetivo")
        estado_arm = c04.get("resultado")
        vistas = {}
        for a in (c04.get("armonizacion_candidata") or []):
            vistas.setdefault(a["norma"], []).append(a.get("desde_articulo"))
        armonizar = [{"norma": k, "desde": [x for x in v if x][:4]}
                     for k, v in list(vistas.items())]
    return {"norma_objetivo": objetivo, "estado_armonizacion": estado_arm,
            "normas_citadas": citadas[:20], "total_citadas": len(citadas),
            "armonizar": armonizar[:20], "total_armonizar": len(armonizar)}


# --- API de la etapa ----------------------------------------------------------

def analizar_texto(texto: str, mtl: bool = True, llm_juicio: bool = False) -> dict:
    """Corre el motor sobre `texto` y devuelve el dictamen. Con `llm_juicio=True`
    resuelve las PENDIENTE_JUICIO pasándole al modelo el texto de la iniciativa como
    evidencia. Adjunta el bloque `conexiones` (mapa de leyes) y valida contra el
    esquema, marcando los avisos de validación si los hubiera."""
    texto_norm = _normalizar_insumo(texto)
    dictamen = pail_engine.analizar(texto_norm, _rulebook(), _indices(), mtl)
    if llm_juicio:
        dictamen = _resolver_juicios(dictamen, texto_norm)
    dictamen["conexiones"] = _conexiones(dictamen)
    errores = validate_dictamen(dictamen)
    if errores:
        dictamen["_schema_warnings"] = errores[:5]
    return dictamen


@shared_task(name="pail.analyze_initiative")
def analyze_initiative(texto: str, mtl: bool = True, llm_juicio: bool = False) -> dict:
    """Tarea Celery: mismo patrón que `normtrace.analyze_units`. Síncrona por
    defecto desde el endpoint (Config.PAIL_ASYNC=False); encolable con worker."""
    return analizar_texto(texto, mtl=mtl, llm_juicio=llm_juicio)
