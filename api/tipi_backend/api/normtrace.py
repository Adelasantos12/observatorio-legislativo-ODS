"""Análisis NormTrace (nivel 3) servido al portal.

Sirve la corrida validada del ejemplo dorado (Ley General de Aguas × ODS 6) para
la ficha vitrina, y las corridas automáticas preliminares que existan en Mongo.
Regla no negociable: toda corrida viaja con `nivel_revision`; las automáticas
nunca se presentan como validadas. El descargo fijo acompaña siempre el análisis.

La API lee el mismo CSV dorado que el motor (la imagen incluye `normtrace/`); no
lo edita. Si el archivo no está disponible, el análisis simplemente no aparece.
"""

import csv
import os
import re
from pathlib import Path

# Expediente vitrina: iniciativa 54 del Ejecutivo = Ley General de Aguas.
LGA_EXPEDIENTE_ID = "EJE-2024-2030-54-aprobadas-y-o-publicadas-en-dof"

DESCARGO = (
    "Registra correspondencia formal entre texto legal y estándares; no es "
    "dictamen jurídico ni evaluación de cumplimiento."
)

_COL_ALIASES = {"disposicion_lga": "disposicion"}


def _gold_dir():
    candidates = [
        os.environ.get("NORMTRACE_GOLD_DIR"),
        "/app/normtrace/03_tables/legislative_mapping/gold",
        str(Path(__file__).resolve().parents[3]
            / "normtrace/03_tables/legislative_mapping/gold"),
    ]
    for c in candidates:
        if c and Path(c).is_dir():
            return Path(c)
    return None


def _briefs_dir():
    candidates = [
        os.environ.get("NORMTRACE_BRIEFS_DIR"),
        "/app/normtrace/04_outputs/briefs",
        str(Path(__file__).resolve().parents[3] / "normtrace/04_outputs/briefs"),
    ]
    for c in candidates:
        if c and Path(c).is_dir():
            return Path(c)
    return None


def _clean(v):
    v = (v or "").strip()
    return v or None


def load_gold_run():
    """Corrida validada del dorado LGA×ODS6, o None si el CSV no está disponible."""
    d = _gold_dir()
    if d is None:
        return None
    path = d / "lga_ods6_mapeo_normtrace.csv"
    if not path.is_file():
        return None
    registros = []
    with path.open(encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            row = {_COL_ALIASES.get(k, k): (v.strip() if isinstance(v, str) else v)
                   for k, v in raw.items()}
            row["tipo_brecha"] = _clean(row.get("tipo_brecha"))
            row["nota"] = _clean(row.get("nota"))
            registros.append(row)
    return {
        "nivel_revision": "validado_autora",
        "marco": "ods6",
        "iniciativa_id": LGA_EXPEDIENTE_ID,
        "fecha": "2026-07-17",
        "fuente_texto": "LeyesBiblio — Ley General de Aguas, DOF 11-12-2025 (texto vigente completo)",
        "brief": "lga_ods6_brief_normtrace.md",
        "descargo": DESCARGO,
        "registros": registros,
    }


def load_brief(nombre="lga_ods6_brief_normtrace.md"):
    """Devuelve el markdown del brief dorado, o None."""
    # Evita traversal: solo nombres de archivo simples dentro de briefs/.
    if "/" in nombre or ".." in nombre:
        return None
    d = _briefs_dir()
    if d is None:
        return None
    path = d / nombre
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def count_con_analisis(count_runs=None):
    """Nº de expedientes con análisis NormTrace: dorado (si disponible) + automáticos."""
    gold = 1 if load_gold_run() is not None else 0
    autos = count_runs() if count_runs else 0
    return gold + autos


def run_for_expediente(expediente_id, mongo_lookup=None):
    """Corrida NormTrace para un expediente.

    Vitrina (LGA) -> dorado validado. Otros -> corrida automática preliminar de
    Mongo si `mongo_lookup` la provee. None si no hay análisis.
    """
    if expediente_id == LGA_EXPEDIENTE_ID:
        return load_gold_run()
    if mongo_lookup is not None:
        run = mongo_lookup(expediente_id)
        if run:
            run.setdefault("descargo", DESCARGO)
            return run
    return None
