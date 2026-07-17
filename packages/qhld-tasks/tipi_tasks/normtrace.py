"""Etapa 3 — Codificación estructural NormTrace por unidad jurídica.

Por cada unidad segmentada que disparó tags en la etapa 1, produce una
codificación `{actor, deber/facultad, procedimiento, coordinación, sanción,
salvaguarda, nivel de fuente, tipo de brecha}` validada contra
`normtrace/schemas_runtime/unit_analysis.schema.json`.

Proveedor por defecto: `mock` — un codificador heurístico local determinista que
usa los marcadores lingüísticos del cerebro jurídico (§5) para extraer los
campos, sin llamar a ningún LLM ni requerir clave. Con `LLM_PROVIDER=anthropic|openai`
se construye un prompt con extractos del cerebro jurídico y se llama al modelo real.

Reglas (CLAUDE.md): toda salida lleva `confidence_level` y `review_status`; ante
fallo de validación se reintenta una vez y luego se marca `needs_human_review`;
nunca se presenta como dictamen de cumplimiento. Caché por hash(unidad + versión
de prompt) en Mongo para no repagar llamadas.
"""

import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

from celery import shared_task
from jsonschema import Draft7Validator

from . import config, llm


# --- Esquema -----------------------------------------------------------------

@lru_cache(maxsize=1)
def _validator() -> Draft7Validator:
    schema = json.loads(Path(config.NORMTRACE_SCHEMA).read_text(encoding="utf-8"))
    return Draft7Validator(schema)


def validate_analysis(data: dict) -> list[str]:
    """Devuelve la lista de errores de validación (vacía si es válida)."""
    return [e.message for e in _validator().iter_errors(data)]


# --- Marcadores lingüísticos (cerebro §5) ------------------------------------

_ACTORS = [
    "el Consejo de Salubridad General", "Consejo de Salubridad General",
    "la Secretaría de Salud", "Secretaría de Salud", "las autoridades sanitarias",
    "el Ejecutivo Federal", "la Federación", "las entidades federativas",
    "los municipios", "COFEPRIS", "IMSS-Bienestar", "IMSS", "ISSSTE", "CONAGUA",
    "SEMARNAT", "CONAFOR", "PROFEPA", "INMUJERES", "INPI", "CONAPRED", "INEGI",
    "la Secretaría",
]
_DUTY = ["deberá", "deberán", "tienen la obligación de", "tendrá la obligación",
         "se sujetará a", "es obligatorio", "de observancia obligatoria",
         "garantizar", "garantiza", "garantizará", "asegurar", "promoverá"]
_POWER = ["podrá", "podrán", "estará facultado", "corresponde a", "corresponderá a",
          "son atribuciones de", "tendrá las siguientes atribuciones",
          "le corresponde el despacho", "estarán facultadas"]
_PROCEDURE = ["procedimiento", "plazo", "en un término de", "notificar",
              "notificación", "recurso de", "conforme al procedimiento",
              "previa consulta", "solicitud"]
_COORD = ["en coordinación con", "se coordinará", "coordinarse", "celebrarán convenios",
          "convenios", "la Federación y los gobiernos de las entidades",
          "por sí o en coordinación"]
_SANCTION = ["sanción", "sanciones", "multa", "infracción", "clausura",
             "queda prohibido", "se prohíbe", "está prohibid", "delito",
             "revocación"]
_RIGHTS = ["derecho", "garantía", "consentimiento", "debido proceso",
           "protección de datos", "dignidad", "no discriminación",
           "acceso a la salud", "pueblos indígenas"]


def _first_marker(text_low: str, markers: list[str]) -> str | None:
    for m in markers:
        if m.lower() in text_low:
            return m
    return None


def _heuristic_code(unit: dict) -> dict:
    """Codificador determinista (proveedor `mock`) basado en los marcadores §5.

    No es un juicio de modelo: emite `confidence_level='low'` y
    `review_status='needs_human_review'` siempre.
    """
    text = unit.get("text", "") or ""
    low = text.lower()

    actor = _first_marker(low, [a.lower() for a in _ACTORS])
    # Recupera la forma original del actor detectado.
    actor_surface = ""
    if actor:
        for a in _ACTORS:
            if a.lower() == actor:
                actor_surface = a
                break

    duty_m = _first_marker(low, _DUTY)
    power_m = _first_marker(low, _POWER)
    proc_m = _first_marker(low, _PROCEDURE)
    coord_m = _first_marker(low, _COORD)
    sanc_m = _first_marker(low, _SANCTION)
    rights_m = _first_marker(low, _RIGHTS)

    duty = f"Deber (marcador: «{duty_m}»)" if duty_m else ""
    power = f"Facultad/atribución (marcador: «{power_m}»)" if power_m else ""
    procedure = f"Procedimiento (marcador: «{proc_m}»)" if proc_m else ""
    coordination = f"Coordinación (marcador: «{coord_m}»)" if coord_m else ""
    sanction = f"Sanción/medida (marcador: «{sanc_m}»)" if sanc_m else ""
    rights = f"Salvaguarda de derechos (marcador: «{rights_m}»)" if rights_m else ""

    # Nivel de fuente (anclaje) heurístico.
    if "nom-" in low or "norma oficial" in low or "reglamento" in low:
        source_level = "regulatory"
    elif "ley" in low or duty or power:
        source_level = "statutory"
    else:
        source_level = "unknown"

    # Tipología de brechas (heurística conservadora, máx. 2).
    gaps = []
    mentions_levels = "entidades federativas" in low or "municipios" in low
    if duty and not coordination and mentions_levels:
        gaps.append("coordination_gap")
    if duty and not procedure:
        gaps.append("procedural_gap")
    if rights and not sanction and not procedure and "rights_safeguard_gap" not in gaps:
        # Derecho mencionado sin procedimiento/garantía operativa aparente.
        if len(gaps) < 2:
            gaps.append("rights_safeguard_gap")
    gaps = gaps[:2]

    return {
        "unit_id": unit.get("unit_id", ""),
        "unit_type": unit.get("unit_type", ""),
        "actor_mentioned": actor_surface,
        "power_granted": power,
        "duty_created": duty,
        "procedure_created": procedure,
        "coordination_mechanism": coordination,
        "enforcement_or_sanction": sanction,
        "rights_safeguard": rights,
        "source_level": source_level,
        "anchoring_score": None,
        "gap_type": gaps,
        "confidence_level": "low",
        "review_status": "needs_human_review",
    }


# --- Prompt para proveedores reales ------------------------------------------

@lru_cache(maxsize=1)
def _brain_extracts() -> str:
    """Lee extractos del cerebro jurídico (no se parafrasean): reglas de
    razonamiento (anclaje, brechas) y marcadores lingüísticos (§5)."""
    brain = Path(config.NORMTRACE_BRAIN_DIR)
    parts = []
    rules = brain / "mexico_legal_reasoning_rules.md"
    struct = brain / "mexico_legal_document_structure_patterns.md"
    if rules.exists():
        parts.append("# Reglas de razonamiento (extracto)\n" + rules.read_text(encoding="utf-8")[:6000])
    if struct.exists():
        txt = struct.read_text(encoding="utf-8")
        idx = txt.find("## 5. Legal Drafting Markers")
        if idx != -1:
            parts.append("# Marcadores de redacción legal (extracto)\n" + txt[idx:idx + 5000])
    return "\n\n".join(parts)


def _build_prompt(unit: dict) -> tuple[str, str]:
    tags = ", ".join(sorted({t.get("tag", "") for t in unit.get("tags", [])}))
    system = (
        "Eres un asistente que codifica la estructura jurídica de unidades de "
        "textos legislativos mexicanos bajo el protocolo NormTrace. Usa el "
        "contexto jurídico siguiente para clasificar; no emitas dictamen de "
        "cumplimiento. Responde ÚNICAMENTE con un objeto JSON que valide contra "
        "el esquema unit_analysis (campos: unit_id, actor_mentioned, power_granted, "
        "duty_created, procedure_created, coordination_mechanism, "
        "enforcement_or_sanction, rights_safeguard, source_level "
        "[statutory|regulatory|administrative|operational|none|unknown], "
        "gap_type [lista de: legal_silence, competence_ambiguity, "
        "administrative_only_anchoring, procedural_gap, coordination_gap, "
        "federal_implementation_gap, rights_safeguard_gap, oversight_gap, "
        "budget_capacity_gap, update_review_needed], confidence_level "
        "[low|medium|high], review_status "
        "[needs_human_review|reviewed|auto_accepted]).\n\n"
        + _brain_extracts()
    )
    user = (
        f"unit_id: {unit.get('unit_id', '')}\n"
        f"tipo: {unit.get('unit_type', '')}\n"
        f"temas detectados: {tags}\n\n"
        f"Texto de la unidad:\n{unit.get('text', '')}\n\n"
        "Devuelve el JSON de codificación."
    )
    return system, user


def _parse_json(text: str) -> dict | None:
    text = text.strip()
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _coerce_required(data: dict, unit: dict) -> dict:
    """Rellena/normaliza campos para maximizar la validez del JSON del modelo."""
    data.setdefault("unit_id", unit.get("unit_id", ""))
    for f in ("actor_mentioned", "power_granted", "duty_created", "procedure_created",
              "coordination_mechanism", "enforcement_or_sanction", "rights_safeguard"):
        data.setdefault(f, "")
        if data[f] is None:
            data[f] = ""
    data.setdefault("source_level", "unknown")
    data.setdefault("gap_type", [])
    if isinstance(data.get("gap_type"), str):
        data["gap_type"] = [data["gap_type"]]
    data.setdefault("confidence_level", "low")
    data.setdefault("review_status", "needs_human_review")
    return data


def _needs_review_fallback(unit: dict, reason: str) -> dict:
    base = _heuristic_code(unit)
    base["confidence_level"] = "low"
    base["review_status"] = "needs_human_review"
    base["_note"] = reason
    # `_note` no está en el esquema; se elimina antes de validar/almacenar.
    return base


# --- Codificación de una unidad ----------------------------------------------

def code_unit(unit: dict) -> dict:
    """Codifica una unidad y devuelve un análisis válido contra el esquema.

    Estrategia: caché → proveedor (mock heurístico o LLM real con un reintento)
    → validación → si nada valida, heurístico marcado como needs_human_review.
    """
    cached = _cache_get(unit)
    if cached is not None:
        return cached

    if config.LLM_PROVIDER == "mock":
        analysis = _heuristic_code(unit)
    else:
        analysis = _code_with_llm(unit)

    analysis.pop("_note", None)
    errors = validate_analysis(analysis)
    if errors:
        # Último recurso: heurístico válido marcado para revisión.
        analysis = _heuristic_code(unit)
        analysis["review_status"] = "needs_human_review"

    _cache_set(unit, analysis)
    return analysis


def _code_with_llm(unit: dict) -> dict:
    system, user = _build_prompt(unit)
    for attempt in range(2):  # una llamada + un reintento
        try:
            text = llm.complete(system, user)
        except Exception as e:  # noqa: BLE001 — cualquier fallo del proveedor
            return _needs_review_fallback(unit, f"error del proveedor LLM: {e}")
        data = _parse_json(text)
        if data is None:
            continue
        data = _coerce_required(data, unit)
        data.pop("_note", None)
        if not validate_analysis(data):
            return data
    return _needs_review_fallback(unit, "el modelo no devolvió JSON válido tras un reintento")


# --- Caché (Mongo) -----------------------------------------------------------

def _cache_key(unit: dict) -> str:
    raw = f"{config.NORMTRACE_PROMPT_VERSION}|{config.LLM_PROVIDER}|{config.LLM_MODEL}|{unit.get('text', '')}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


# Colección de caché con un cliente dedicado de timeout corto: si Mongo no está
# disponible, se desactiva tras el primer intento (evita bloqueos de 30 s por la
# selección de servidor del cliente global de tipi_data).
_cache_state = {"checked": False, "collection": None}


def _cache_collection():
    if _cache_state["checked"]:
        return _cache_state["collection"]
    _cache_state["checked"] = True
    try:
        from pymongo import MongoClient
        from tipi_data import config as dcfg
        client = MongoClient(
            host=dcfg.MONGO_HOST, port=dcfg.MONGO_PORT,
            username=dcfg.MONGO_USER, password=dcfg.MONGO_PASSWORD,
            serverSelectionTimeoutMS=800,
        )
        client.admin.command("ping")
        _cache_state["collection"] = client[dcfg.MONGO_DB]["normtrace_cache"]
    except Exception:  # noqa: BLE001 — sin Mongo, la caché queda desactivada
        _cache_state["collection"] = None
    return _cache_state["collection"]


def _cache_get(unit: dict):
    col = _cache_collection()
    if col is None:
        return None
    try:
        doc = col.find_one({"_id": _cache_key(unit)})
        return doc["analysis"] if doc else None
    except Exception:  # noqa: BLE001
        return None


def _cache_set(unit: dict, analysis: dict):
    col = _cache_collection()
    if col is None:
        return
    try:
        key = _cache_key(unit)
        col.replace_one({"_id": key}, {"_id": key, "analysis": analysis}, upsert=True)
    except Exception:  # noqa: BLE001
        pass


# --- Tarea Celery ------------------------------------------------------------

@shared_task(name="normtrace.analyze_units")
def analyze_units(units: list[dict], max_units: int | None = None) -> dict:
    """Codifica hasta `max_units` unidades (con tags) y devuelve el bloque
    `structural`. Reporta `units_analyzed` y `units_skipped` (presupuesto)."""
    if max_units is None:
        max_units = config.NORMTRACE_MAX_UNITS

    to_code = units[:max_units]
    skipped = len(units) - len(to_code)
    coded = []
    for unit in to_code:
        analysis = code_unit(unit)
        coded.append(
            {
                "unit_id": unit.get("unit_id"),
                "unit_type": unit.get("unit_type"),
                "number": unit.get("number"),
                "heading": (unit.get("heading") or "")[:200],
                "parent_id": unit.get("parent_id"),
                "topics": unit.get("topics", []),
                "analysis": analysis,
            }
        )

    return {
        "status": "SUCCESS",
        "provider": config.LLM_PROVIDER,
        "prompt_version": config.NORMTRACE_PROMPT_VERSION,
        "units_analyzed": len(coded),
        "units_skipped": max(0, skipped),
        "units": coded,
    }


def check_status_task(task_id):
    """Estado/resultado de una tarea de codificación (para el endpoint deep)."""
    from tipi_tasks import app
    task = app.AsyncResult(task_id)
    st = task.status
    structural = task.get() if st == "SUCCESS" else None
    return {"status": st, "structural": structural}
