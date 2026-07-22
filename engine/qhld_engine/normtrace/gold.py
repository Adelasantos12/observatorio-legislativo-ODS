"""Carga y huella del ejemplo dorado (solo lectura).

El CSV dorado es el contrato de calidad: nunca se edita ni se regenera desde el
pipeline. `gold_hash()` fija su huella para el test que reprueba si cambia
(criterio 4 de la adenda). Solo la autora lo cambia, con nota en la Bitácora.
"""

import csv
import hashlib
from pathlib import Path

# engine/qhld_engine/normtrace/gold.py -> repo root son 4 niveles arriba.
_REPO_ROOT = Path(__file__).resolve().parents[3]
GOLD_CSV = _REPO_ROOT / "normtrace/03_tables/legislative_mapping/gold/lga_ods6_mapeo_normtrace.csv"
GOLD_BRIEF = _REPO_ROOT / "normtrace/04_outputs/briefs/lga_ods6_brief_normtrace.md"

# El CSV usa 'disposicion_lga'; el esquema runtime usa 'disposicion'.
_COL_ALIASES = {"disposicion_lga": "disposicion"}


def gold_bytes(path: Path | None = None) -> bytes:
    return (path or GOLD_CSV).read_bytes()


def gold_hash(path: Path | None = None) -> str:
    """SHA-256 del CSV dorado, en hex."""
    return hashlib.sha256(gold_bytes(path)).hexdigest()


def _clean(v):
    v = (v or "").strip()
    return v or None


def load_gold(path: Path | None = None) -> list[dict]:
    """Devuelve los registros dorados normalizados al vocabulario del esquema."""
    path = path or GOLD_CSV
    rows = []
    with path.open(encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = {}
            for k, v in raw.items():
                key = _COL_ALIASES.get(k, k)
                row[key] = v.strip() if isinstance(v, str) else v
            # tipo_brecha/nota pueden venir vacíos -> None.
            row["tipo_brecha"] = _clean(row.get("tipo_brecha"))
            row["nota"] = _clean(row.get("nota"))
            rows.append(row)
    return rows


def gold_run(path: Path | None = None) -> dict:
    """Envuelve el dorado como una corrida `validado_autora` válida contra el esquema."""
    return {
        "nivel_revision": "validado_autora",
        "marco": "ods6",
        "iniciativa_id": None,
        "fecha": "2026-07-17",
        "modelo": None,
        "version_prompt": None,
        "fuente_texto": "LeyesBiblio — Ley General de Aguas, DOF 11-12-2025 (texto vigente completo)",
        "registros": load_gold(path),
    }
