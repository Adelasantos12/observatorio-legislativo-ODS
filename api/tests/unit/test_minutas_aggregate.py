"""Tests del agregado de minutas (fase H, módulo B, H.8).

Sin infraestructura: la agregación es pura sobre dicts. Se verifica la regla no
negociable (aportación por origen, NO ranking; bucket "por documentar"; orden
alfabético) y la consistencia contra la semilla `minutas_ods.csv`.
"""

import csv
import re
from pathlib import Path

import pytest

from tipi_backend.api.minutas import POR_DOCUMENTAR, aggregate_minutas

pytestmark = pytest.mark.unit

CSV_PATH = (
    Path(__file__).resolve().parents[3]
    / "normtrace/03_tables/legislative_mapping/minutas_ods.csv"
)


def _split(v):
    return [p.strip() for p in re.split(r"[;,]", v or "") if p.strip()]


def _load_seed():
    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8")))
    return [
        {
            "origen": (r.get("origen") or "").strip() or None,
            "ods_principal": (r.get("ods_principal") or "").strip() or None,
            "ods_secundarios": _split(r.get("ods_secundarios")),
            "metas": _split(r.get("metas")),
        }
        for r in rows
    ]


def test_por_origen_orden_alfabetico_no_ranking():
    minutas = [
        {"origen": "Zeta", "ods_principal": "3"},
        {"origen": "Alfa", "ods_principal": "5"},
        {"origen": "Alfa", "ods_principal": "5"},
    ]
    agg = aggregate_minutas(minutas)
    origenes = [o["origen"] for o in agg["por_origen"]]
    # Alfabético (Alfa antes que Zeta) aunque Alfa tenga más: no es un ranking.
    assert origenes == ["Alfa", "Zeta"]


def test_por_documentar_va_al_final_y_marcado():
    minutas = [
        {"origen": "Alfa", "ods_principal": "5"},
        {"origen": None, "ods_principal": None},
        {"origen": "", "ods_principal": None},
    ]
    agg = aggregate_minutas(minutas)
    ultimo = agg["por_origen"][-1]
    assert ultimo["origen"] == POR_DOCUMENTAR
    assert ultimo["por_documentar"] is True
    assert ultimo["n"] == 2
    assert agg["kpis"]["sin_origen_documentado"] == 2
    # El bucket "por documentar" no cuenta como origen documentado.
    assert agg["kpis"]["origenes_documentados"] == 1


def test_semilla_atribuye_todo_al_ejecutivo_federal():
    minutas = _load_seed()
    assert len(minutas) == 76
    agg = aggregate_minutas(minutas, corte="2026-07-17")
    # Toda la semilla tiene origen documentado (Ejecutivo Federal): sin bucket.
    origenes = {o["origen"]: o["n"] for o in agg["por_origen"]}
    assert origenes == {"Ejecutivo Federal": 76}
    assert agg["kpis"]["minutas_totales"] == 76
    assert agg["kpis"]["sin_origen_documentado"] == 0
    assert agg["kpis"]["pct_con_correspondencia_ods"] > 0
    assert agg["corte"] == "2026-07-17"


def test_por_ods_ordenado_numericamente():
    minutas = _load_seed()
    agg = aggregate_minutas(minutas)
    ods = [int(r["ods"]) for r in agg["por_ods"]]
    assert ods == sorted(ods)
