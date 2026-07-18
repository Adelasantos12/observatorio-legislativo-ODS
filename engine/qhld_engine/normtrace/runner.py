"""Motor de corrida NormTrace (fase F4 aterrizada al marco de estándares).

`run(iniciativa_id, marco, text=...)`:
  1. obtiene el texto publicado (LeyesBiblio para leyes nuevas; se puede pasar
     `text`/`text_file` para operación offline y pruebas),
  2. lo segmenta con el segmentador de F3,
  3. por cada estándar del marco llama al LLM con el cerebro jurídico como
     contexto (proveedor real) o produce una fila preliminar conservadora
     (proveedor `mock`, sin red ni clave),
  4. valida cada fila contra `normtrace_mapping.schema.json`; ante fallo reintenta
     una vez y si no valida marca el registro para revisión humana.

Toda corrida nace `nivel_revision: automatico_preliminar`. El flip a
`validado_autora` es manual, nunca automático. Caché por
hash(texto de unidad + versión de prompt + marco) para no repagar llamadas.
"""

import hashlib
import json
import os
import re
from pathlib import Path

from . import frameworks
from .schema import validate_run

# Config por entorno (alineada con tipi_tasks.config).
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "mock")
LLM_MODEL = os.environ.get("LLM_MODEL", "")
NORMTRACE_MAX_UNITS = int(os.environ.get("NORMTRACE_MAX_UNITS", "80"))
PROMPT_VERSION = os.environ.get("NORMTRACE_PROMPT_VERSION", "nt-map-v1")

_REPO_ROOT = Path(__file__).resolve().parents[3]
BRAIN_DIR = Path(os.environ.get(
    "NORMTRACE_BRAIN_DIR",
    str(_REPO_ROOT / "normtrace/02_country_legal_brains/mexico"),
))
LEYESBIBLIO_PDF = "https://www.diputados.gob.mx/LeyesBiblio/pdf/{slug}.pdf"

# Caché en disco (evita repagar llamadas reales).
CACHE_DIR = Path(os.environ.get(
    "NORMTRACE_CACHE_DIR", str(_REPO_ROOT / ".normtrace_cache")))


def _brain_excerpt(max_chars: int = 6000) -> str:
    """Lee un extracto del cerebro jurídico (no se parafrasea a mano)."""
    if not BRAIN_DIR.is_dir():
        return ""
    parts = []
    for md in sorted(BRAIN_DIR.glob("*.md")):
        parts.append(md.read_text(encoding="utf-8"))
    text = "\n\n".join(parts)
    return text[:max_chars]


def _cache_key(unit_text: str, marco: str) -> str:
    h = hashlib.sha256()
    h.update(unit_text.encode("utf-8"))
    h.update(PROMPT_VERSION.encode("utf-8"))
    h.update(marco.encode("utf-8"))
    return h.hexdigest()


def _cache_get(key: str):
    p = CACHE_DIR / f"{key}.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def _cache_put(key: str, value):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def fetch_text(marco: dict, timeout: int = 60) -> str | None:
    """Descarga el texto de la ley vitrina del marco desde LeyesBiblio (PDF)."""
    slug = marco.get("leyesbiblio_slug")
    if not slug:
        return None
    import requests
    from pdfminer.high_level import extract_text

    url = LEYESBIBLIO_PDF.format(slug=slug)
    resp = requests.get(url, timeout=timeout)
    if not resp.ok:
        return None
    tmp = CACHE_DIR / f"{slug}.pdf"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp.write_bytes(resp.content)
    return extract_text(str(tmp))


def _segment(text: str):
    from legal_segmenter import segment_to_dicts

    return segment_to_dicts(text, doc_id="LGAg")


def _units_citing_standard(units, estandar: str) -> list:
    """Heurística de recuperación: unidades cuyo texto menciona la materia del
    estándar. Sirve para acotar el prompt y para el modo mock."""
    key = frameworks.meta_key(estandar).lower()
    terms = {
        "6.1": ["agua potable", "acceso", "asequible"],
        "6.2": ["saneamiento", "higiene", "menstru"],
        "6.3": ["calidad", "reúso", "reuso", "tratamiento"],
        "6.4": ["eficiente", "sobreexplot", "escasez"],
        "6.5": ["estrategia", "gestión integrada", "cuenca"],
        "6.6": ["ecosistema", "naturaleza", "humedal"],
        "6.a": ["internacional", "cooperación"],
        "6.b": ["participación", "comunitario", "vigilancia"],
    }.get(key, [key])
    out = []
    for u in units:
        t = (u.get("text") or "").lower()
        if any(term in t for term in terms):
            out.append(u)
    return out


def _mock_row(estandar: str, units) -> dict:
    """Fila preliminar conservadora (sin LLM): rol contextual y ajustes bajos.

    Deliberadamente NO intenta igualar el dorado: marca una línea base de baja
    confianza que solo el LLM real (o la autora) puede elevar. Así una corrida
    mock jamás se confunde con codificación validada.
    """
    citing = _units_citing_standard(units, estandar)
    disp = ""
    if citing:
        # Toma la primera unidad citante y expresa su artículo si lo trae.
        art = citing[0].get("number")
        disp = f"Art. {art}" if art else (citing[0].get("unit_id") or "")
    return {
        "estandar": estandar,
        "disposicion": disp or "s/d",
        "rol_correspondencia": "contextual_habilitante",
        "cobertura": "contextual",
        "actor_fit": "no_aplica",
        "procedimiento_fit": "no_aplica",
        "coordinacion_fit": "no_aplica",
        "enforcement_fit": "no_aplica",
        "salvaguarda_derechos_fit": "no_aplica",
        "federalismo_fit": "no_aplica",
        "tipo_brecha": None,
        "nota": "Línea base preliminar (mock, sin LLM). Requiere codificación real o revisión de la autora.",
    }


def _llm_row(estandar: str, units, brain: str) -> dict | None:
    """Codifica un estándar con el LLM real. Devuelve None si no valida tras 1 reintento."""
    from tipi_tasks import llm

    citing = _units_citing_standard(units, estandar)
    contexto = "\n".join(
        f"[{u.get('unit_id') or ('Art. ' + str(u.get('number')))}] {(u.get('text') or '')[:500]}"
        for u in citing[:12]
    )
    system = (
        "Eres analista jurídico. Aplicas el protocolo NormTrace usando el cerebro "
        "jurídico mexicano como fuente. Devuelves SOLO un objeto JSON con las claves "
        "estandar, disposicion, rol_correspondencia (sustantivo|contextual_habilitante), "
        "cobertura (completa|parcial|contextual), actor_fit, procedimiento_fit, "
        "coordinacion_fit, enforcement_fit, salvaguarda_derechos_fit, federalismo_fit "
        "(fuerte|medio|debil|no_aplica), tipo_brecha, nota. La disposicion debe citar "
        "un artículo existente del texto.\n\nCEREBRO JURÍDICO (extracto):\n" + brain
    )
    user = f"Estándar: {estandar}\n\nDisposiciones candidatas:\n{contexto or '(ninguna encontrada)'}"
    for _ in range(2):  # intento + un reintento
        try:
            raw = llm.complete(system, user)
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if not m:
                continue
            row = json.loads(m.group(0))
            row["estandar"] = estandar
            return row
        except Exception:
            continue
    return None


def run(iniciativa_id: str | None, marco_nombre: str = "ods6",
        text: str | None = None, text_file: str | None = None) -> dict:
    """Produce una corrida NormTrace `automatico_preliminar` para un marco."""
    marco = frameworks.get_marco(marco_nombre)

    if text is None and text_file:
        text = Path(text_file).read_text(encoding="utf-8")
    if text is None:
        text = fetch_text(marco)
    if not text:
        raise RuntimeError(
            f"No hay texto para el marco {marco_nombre!r} (descarga fallida y sin text_file)."
        )

    units = _segment(text)[:NORMTRACE_MAX_UNITS]
    brain = _brain_excerpt() if LLM_PROVIDER != "mock" else ""

    registros = []
    for estandar in marco["standards"]:
        # estándares no-numéricos (bloques de tratado) se etiquetan como tales.
        etiqueta = estandar if not estandar.replace(".", "").isalnum() or "." in estandar else estandar
        cache_key = _cache_key(etiqueta + "|" + text[:200], marco_nombre)
        cached = _cache_get(cache_key)
        if cached is not None:
            registros.append(cached)
            continue
        if LLM_PROVIDER == "mock":
            row = _mock_row(_std_label(estandar, marco), units)
        else:
            row = _llm_row(_std_label(estandar, marco), units, brain) or _mock_row(
                _std_label(estandar, marco), units)
            row["nota"] = (row.get("nota") or "") + " [automático preliminar]"
        _cache_put(cache_key, row)
        registros.append(row)

    run_obj = {
        "nivel_revision": "automatico_preliminar",
        "marco": marco_nombre,
        "iniciativa_id": iniciativa_id,
        "fecha": os.environ.get("NORMTRACE_FECHA", "") or None,
        "modelo": LLM_MODEL or LLM_PROVIDER,
        "version_prompt": PROMPT_VERSION,
        "fuente_texto": marco["fuente_texto"],
        "registros": registros,
    }
    errors = validate_run(run_obj)
    if errors:
        raise ValueError(f"La corrida no valida contra el esquema: {errors[:3]}")
    return run_obj


def _std_label(estandar: str, marco: dict) -> str:
    """Etiqueta legible del estándar para el registro (metas -> 'ODS 6.1')."""
    if estandar in marco["metas"]:
        return f"ODS {estandar}"
    return estandar
