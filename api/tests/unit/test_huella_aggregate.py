"""Tests del agregado de la Huella del Ejecutivo (fase H, módulo A, H.8).

Sin infraestructura: la agregación es pura. Se verifica su consistencia contra la
semilla `iniciativas_ejecutivo_ods.csv` (82 iniciativas, 76 aprobadas, ODS 16
dominante).
"""

import csv
import re
from pathlib import Path

import pytest

from tipi_backend.api.huella import aggregate_executive

pytestmark = pytest.mark.unit

CSV_PATH = (
    Path(__file__).resolve().parents[3]
    / "normtrace/03_tables/legislative_mapping/iniciativas_ejecutivo_ods.csv"
)


def _split(v):
    return [p.strip() for p in re.split(r"[;,]", v or "") if p.strip()]


def _load_seed():
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    return [
        {
            "seccion": r["seccion"],
            "denominacion": r["denominacion"],
            "fecha_presentacion": r["fecha_presentacion"],
            "ods_principal": (r.get("ods_principal") or "").strip() or None,
            "ods_secundarios": _split(r.get("ods_secundarios")),
            "metas": _split(r.get("metas")),
        }
        for r in rows
    ]


def test_kpis_semilla():
    agg = aggregate_executive(_load_seed(), corte="2026-07-17")
    k = agg["kpis"]
    assert k["iniciativas_presentadas"] == 82
    assert k["aprobadas"] == 76
    assert k["ods_dominante"] == "16"
    assert 0 <= k["pct_con_correspondencia_ods"] <= 100
    assert agg["corte"] == "2026-07-17"


def test_por_ods_incluye_principal_y_secundario():
    agg = aggregate_executive(_load_seed())
    ods16 = next(r for r in agg["por_ods"] if r["ods"] == "16")
    # ODS 16 domina: principal + secundario es el mayor del conjunto.
    total16 = ods16["principal"] + ods16["secundario"]
    assert total16 == max(r["principal"] + r["secundario"] for r in agg["por_ods"])
    # Orden numérico por ODS.
    ods = [int(r["ods"]) for r in agg["por_ods"]]
    assert ods == sorted(ods)


def test_por_meta_ordenado_por_frecuencia():
    agg = aggregate_executive(_load_seed())
    ns = [r["n"] for r in agg["por_meta"]]
    assert ns == sorted(ns, reverse=True)
