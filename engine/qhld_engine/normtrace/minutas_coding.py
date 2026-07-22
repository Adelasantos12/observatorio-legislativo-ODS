"""Codificación ODS/metas de las minutas de la LXVI (adenda v3 §A2).

Regla de tres pasos, en orden:
  1. HERENCIA (cero costo): las minutas cruzadas con una iniciativa del Ejecutivo
     (`matches_minutas_ejecutivo.json`) heredan su codificación. `confianza` = la
     de origen si score ≥ 0.75; "media" si 0.62 ≤ score < 0.75. `origen_tipo`
     = "ejecutivo". Los pares con score < 0.75 van a una lista de verificación
     manual (el match difuso puede fallar).
  2. LLM ASISTIDO: el resto (y toda minuta nueva) se codifica con el LLM (config
     `LLM_*`); las conmemorativas se codifican por su materia o como sin
     correspondencia; ante duda, `confianza: baja`; nunca se inventan metas. Con
     `LLM_PROVIDER=mock` (sin clave) se emite una línea base honesta: sin
     correspondencia, `confianza: baja`, para que una revisión real la eleve.
  3. EXPORTA a `minutas_ods.csv`: fuente de verdad editable a mano. El importador
     NUNCA pisa filas `nivel_revision = validado_autora`.

Toda salida automática nace `nivel_revision: automatico_preliminar`.
"""

import csv
import json
import os
import re
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
MAP_DIR = _REPO_ROOT / "normtrace/03_tables/legislative_mapping"
RAW_CSV = MAP_DIR / "minutas_lxvi_raw.csv"
MATCHES_JSON = MAP_DIR / "matches_minutas_ejecutivo.json"
EXEC_CSV = MAP_DIR / "iniciativas_ejecutivo_ods.csv"
ODS_CODING_CSV = MAP_DIR / "minutas_ods.csv"
CATALOGOS_DIR = _REPO_ROOT / "normtrace/03_tables/catalogos"

SCORE_ALTA = 0.75
SCORE_MIN = 0.62

# Columnas del CSV de codificación (fuente de verdad revisable por la autora).
CODING_COLS = [
    "clave", "denominacion", "estatus", "anio",
    "ods_principal", "ods_secundarios", "metas", "tema", "confianza",
    "origen_tipo", "grupos_parlamentarios", "expediente_ref",
    "nivel_revision", "fuente_codificacion",
]

# Marcadores de decreto conmemorativo ("Día Nacional/Internacional de …").
_CONMEMORATIVO = re.compile(r"\bd[ií]a\s+(nacional|internacional|mundial)\b", re.IGNORECASE)


def _split(v):
    return [p.strip() for p in re.split(r"[;,]", v or "") if p.strip()]


def _join(xs):
    return ";".join(xs or [])


def load_matches(path=None):
    return json.loads(Path(path or MATCHES_JSON).read_text(encoding="utf-8"))


def load_executive(path=None):
    with Path(path or EXEC_CSV).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_raw(path=None):
    with Path(path or RAW_CSV).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _exec_id(exec_row):
    from tipi_data.utils import generate_slug
    num = int(exec_row["num"])
    return f"EJE-2024-2030-{num}-{generate_slug(exec_row['seccion'])}"


def inherit(minuta_raw, matches, execs):
    """Devuelve (coding|None, needs_manual: bool). Herencia del Ejecutivo."""
    clave = minuta_raw["clave"].strip()
    match = matches.get(clave)
    if not match:
        return None, False
    idx, score = match[0], float(match[1])
    ei = execs[idx]
    confianza = (ei.get("confianza") or "media").strip() if score >= SCORE_ALTA else "media"
    coding = {
        "ods_principal": (ei.get("ods_principal") or "").strip() or None,
        "ods_secundarios": _split(ei.get("ods_secundarios")),
        "metas": _split(ei.get("metas")),
        "tema": (ei.get("tema") or "").strip() or None,
        "confianza": confianza,
        "origen_tipo": "ejecutivo",
        "grupos_parlamentarios": [],
        "expediente_ref": _exec_id(ei),
        "nivel_revision": "automatico_preliminar",
        "fuente_codificacion": f"herencia(score={score:.2f})",
    }
    return coding, (score < SCORE_ALTA)


def _mock_llm_coding(minuta_raw):
    """Línea base honesta sin LLM: no inventa metas ni ODS."""
    return {
        "ods_principal": None,
        "ods_secundarios": [],
        "metas": [],
        "tema": None,
        "confianza": "baja",
        "origen_tipo": None,
        "grupos_parlamentarios": [],
        "expediente_ref": None,
        "nivel_revision": "automatico_preliminar",
        "fuente_codificacion": "mock(sin_llm)",
    }


def _ods_catalog_text():
    try:
        ods = json.loads((CATALOGOS_DIR / "ods.json").read_text(encoding="utf-8"))
        metas = json.loads((CATALOGOS_DIR / "metas.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ""
    lineas = [f"ODS {k}: {v['nombre_es']}" for k, v in ods.items()]
    metas_l = [f"{m['codigo']} ({m.get('nombre_corto_es') or '—'})" for m in metas]
    return "OBJETIVOS:\n" + "\n".join(lineas) + "\n\nMETAS:\n" + ", ".join(metas_l)


def llm_coding(minuta_raw):
    """Codifica una minuta con el LLM real; cae a mock si no hay proveedor/clave."""
    provider = os.environ.get("LLM_PROVIDER", "mock")
    if provider == "mock":
        return _mock_llm_coding(minuta_raw)
    from tipi_tasks import llm

    titulo = (minuta_raw.get("titulo") or "").strip()
    system = (
        "Eres analista legislativo. Clasifica el proyecto de decreto contra la "
        "Agenda 2030. Devuelve SOLO JSON: {ods_principal (str|null), "
        "ods_secundarios (list[str]), metas (list[str]), tema (str|null), "
        "confianza ('alta'|'media'|'baja')}. Reglas: los decretos conmemorativos "
        "('Día Nacional/Internacional de X') se codifican por su materia si la "
        "tienen, o sin correspondencia (ods_principal=null) si son puramente "
        "conmemorativos. Ante duda, confianza='baja'. NUNCA inventes metas.\n\n"
        + _ods_catalog_text()
    )
    for _ in range(2):
        try:
            raw = llm.complete(system, f"Proyecto: {titulo}")
            m = re.search(r"\{.*\}", raw, re.DOTALL)
            if not m:
                continue
            data = json.loads(m.group(0))
            return {
                "ods_principal": (data.get("ods_principal") or None),
                "ods_secundarios": data.get("ods_secundarios") or [],
                "metas": data.get("metas") or [],
                "tema": data.get("tema") or None,
                "confianza": data.get("confianza") or "baja",
                "origen_tipo": None,
                "grupos_parlamentarios": [],
                "expediente_ref": None,
                "nivel_revision": "automatico_preliminar",
                "fuente_codificacion": f"llm({os.environ.get('LLM_MODEL', provider)})",
            }
        except Exception:
            continue
    return _mock_llm_coding(minuta_raw)


def code_all(raw=None, matches=None, execs=None, existing_validated=None):
    """Codifica las 139 (herencia + LLM/mock). Devuelve (filas, resumen).

    `existing_validated`: dict {clave: fila_dict} de codificación ya validada por
    la autora (para no pisarla). `filas` = lista de dicts con CODING_COLS.
    """
    raw = raw if raw is not None else load_raw()
    matches = matches if matches is not None else load_matches()
    execs = execs if execs is not None else load_executive()
    existing_validated = existing_validated or {}

    filas, manual, n_her, n_llm, n_val = [], [], 0, 0, 0
    for r in raw:
        clave = r["clave"].strip()
        base = {
            "clave": clave,
            "denominacion": (r.get("titulo") or "").strip(),
            "estatus": (r.get("estatus") or "").strip(),
            "anio": (r.get("anio") or "").strip(),
        }
        if clave in existing_validated:
            filas.append(existing_validated[clave])
            n_val += 1
            continue
        coding, needs_manual = inherit(r, matches, execs)
        if coding is None:
            coding = llm_coding(r)
            n_llm += 1
        else:
            n_her += 1
            if needs_manual:
                manual.append(clave)
        fila = dict(base)
        fila.update({
            "ods_principal": coding["ods_principal"] or "",
            "ods_secundarios": _join(coding["ods_secundarios"]),
            "metas": _join(coding["metas"]),
            "tema": coding["tema"] or "",
            "confianza": coding["confianza"],
            "origen_tipo": coding["origen_tipo"] or "",
            "grupos_parlamentarios": _join(coding["grupos_parlamentarios"]),
            "expediente_ref": coding["expediente_ref"] or "",
            "nivel_revision": coding["nivel_revision"],
            "fuente_codificacion": coding["fuente_codificacion"],
        })
        filas.append(fila)

    resumen = {
        "total": len(filas),
        "heredadas": n_her,
        "por_llm": n_llm,
        "validadas_preservadas": n_val,
        "verificacion_manual": manual,
    }
    return filas, resumen


def _read_validated(path):
    """Filas ya validadas por la autora en el CSV existente (para no pisarlas)."""
    path = Path(path)
    if not path.is_file():
        return {}
    out = {}
    with path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if (row.get("nivel_revision") or "").strip() == "validado_autora":
                out[row["clave"].strip()] = row
    return out


def export_coding(out_path=None):
    """Genera `minutas_ods.csv` preservando las filas validadas por la autora."""
    out_path = Path(out_path or ODS_CODING_CSV)
    validated = _read_validated(out_path)
    filas, resumen = code_all(existing_validated=validated)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CODING_COLS)
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in CODING_COLS})
    return resumen
