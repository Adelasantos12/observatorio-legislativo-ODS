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
    """Instrucción de sistema: la `regla_evidencia` del rulebook + el blindaje
    (solo evidencia provista, prohibido conocimiento propio, NO_EVALUABLE si falta)."""
    validos = "|".join(rulebook["resultados_validos"])
    return (
        rulebook["regla_evidencia"]
        + "\n\nCalificas UNA verificación de una iniciativa legislativa mexicana. "
        "Reglas absolutas e inquebrantables:\n"
        "1. Usa EXCLUSIVAMENTE la evidencia provista abajo y las citas del corpus incluidas.\n"
        "2. TIENES PROHIBIDO completar, suponer o corregir con tu conocimiento del "
        "derecho mexicano: no eres la fuente, el corpus lo es.\n"
        "3. Si la evidencia provista es insuficiente para calificar con rigor, tu "
        "resultado ES 'NO_EVALUABLE'.\n"
        "4. Responde ÚNICAMENTE un objeto JSON: "
        '{"resultado": <uno de: ' + validos + '>, "explicacion": "<breve, citando la '
        'evidencia>", "evidencia": [{"cita": "...", "ubicacion": "...", "fuente": "..."}]}.'
    )


def _juicio_user(h: dict, contexto: dict) -> str:
    return (
        f"Verificación {h['id']} — {h['nombre']} (severidad {h['severidad']})\n"
        f"Criterio: {h.get('criterio_para_llm', '')}\n\n"
        f"Contexto del instrumento (extraído por el motor): "
        f"{json.dumps(contexto, ensure_ascii=False)[:1500]}\n\n"
        f"Evidencia disponible (la única que puedes usar): "
        f"{json.dumps(h.get('evidencia', []), ensure_ascii=False)[:2500]}\n\n"
        "Califica el criterio SOLO con esta evidencia."
    )


def _resolver_una(h: dict, system: str, contexto: dict, validos: set) -> str | None:
    """Resuelve UNA verificación con el LLM. Muta `h` in situ y devuelve el mensaje
    de error del proveedor si lo hubo (para superficie/diagnóstico), o None."""
    err = None
    try:
        text = llm.complete(system, _juicio_user(h, contexto))
        data = _parse_json(text) or {}
        res = data.get("resultado")
        if res in validos and res != "PENDIENTE_JUICIO":
            h["resultado"] = res
            h["explicacion"] = (data.get("explicacion") or "")[:1000]
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


def _resolver_juicios(dictamen: dict) -> dict:
    """Resuelve las PENDIENTE_JUICIO con el LLM (EN PARALELO, para no exceder el
    tiempo de la petición con decenas de llamadas secuenciales) y re-agrega con el
    motor. Si el proveedor falla de forma sistémica (clave/modelo/cuota), se
    expone `llm_error` para diagnóstico en vez de dejar todo en NO_EVALUABLE mudo."""
    rb = _rulebook()
    validos = set(rb["resultados_validos"])
    system = _juicio_system(rb)
    contexto = dictamen.get("contexto", {})
    pendientes = [h for h in dictamen["verificaciones"]
                  if h.get("resultado") == "PENDIENTE_JUICIO"][:config.PAIL_LLM_MAX_JUICIOS]

    errores = []
    if pendientes:
        max_workers = max(1, min(config.PAIL_LLM_CONCURRENCY, len(pendientes)))
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            for err in ex.map(lambda h: _resolver_una(h, system, contexto, validos), pendientes):
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

# La extracción de PDF ensucia los encabezados de artículo del decreto y el
# segmentador del motor exige "Artículo" a inicio de línea. Se normaliza el texto
# de entrada (SIN tocar la lógica del motor) para tres patrones reales de la
# Gaceta: (1) el texto reformado va entrecomillado, así que el encabezado queda
# pegado a una comilla de apertura («"Artículo 111.»); (2) el encabezado quedó a
# media línea tras un signo de cierre; (3) el chapeau "Artículo único:" en
# minúscula y con dos puntos. NO se promueven remisiones en minúscula
# ("el artículo 71 de la Constitución"), que no son encabezados.
_COMILLAS = "“”«»‹›\"'`"
_ENCABEZADO = (r"(?:\d|[ÚU]nico|Primero|Segundo|Tercero|Cuarto|Quinto|Sexto|"
               r"S[eé]ptimo|Octavo|Noveno|D[eé]cimo)")
_ART_LINEA_COMILLA = re.compile(rf"(?m)^[ \t{re.escape(_COMILLAS)}]+(Art[íi]culo\s)")
_ART_MEDIA_LINEA = re.compile(
    rf"(?<=[\.\:;\)])[ \t{re.escape(_COMILLAS)}]*(Art[íi]culo\s+{_ENCABEZADO})")
_ART_UNICO_MIN = re.compile(r"(Art[íi]culo\s+)[úu]nico\s*[:.]")


def _normalizar_insumo(texto: str) -> str:
    """Limpia los encabezados de artículo para que el segmentador del motor los
    reconozca (ver arriba), sin alterar el motor ni crear artículos falsos."""
    texto = _ART_LINEA_COMILLA.sub(r"\1", texto)
    texto = _ART_MEDIA_LINEA.sub(lambda m: "\n" + m.group(1), texto)
    texto = _ART_UNICO_MIN.sub(r"\1Único.", texto)
    return texto


# --- API de la etapa ----------------------------------------------------------

def analizar_texto(texto: str, mtl: bool = True, llm_juicio: bool = False) -> dict:
    """Corre el motor sobre `texto` y devuelve el dictamen. Con `llm_juicio=True`
    resuelve las PENDIENTE_JUICIO. Valida contra el esquema y adjunta los avisos
    de validación si los hubiera (no debería, si el esquema y el motor coinciden)."""
    dictamen = pail_engine.analizar(_normalizar_insumo(texto), _rulebook(), _indices(), mtl)
    if llm_juicio:
        dictamen = _resolver_juicios(dictamen)
    errores = validate_dictamen(dictamen)
    if errores:
        dictamen["_schema_warnings"] = errores[:5]
    return dictamen


@shared_task(name="pail.analyze_initiative")
def analyze_initiative(texto: str, mtl: bool = True, llm_juicio: bool = False) -> dict:
    """Tarea Celery: mismo patrón que `normtrace.analyze_units`. Síncrona por
    defecto desde el endpoint (Config.PAIL_ASYNC=False); encolable con worker."""
    return analizar_texto(texto, mtl=mtl, llm_juicio=llm_juicio)
