"""Tests del agregado de minutas (Huella módulo B; adenda v3).

Sin infraestructura: la agregación es pura. Se verifica la regla no negociable
(aportación por origen, NO ranking; bucket "por documentar"; orden alfabético) y
la consistencia contra la semilla v3 `minutas_ods.csv` (139 minutas).
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
            "origen": "Ejecutivo Federal" if (r.get("origen_tipo") or "").strip() == "ejecutivo" else None,
            "origen_tipo": (r.get("origen_tipo") or "").strip() or None,
            "grupos_parlamentarios": _split(r.get("grupos_parlamentarios")),
            "ods_principal": (r.get("ods_principal") or "").strip() or None,
            "ods_secundarios": _split(r.get("ods_secundarios")),
            "metas": _split(r.get("metas")),
            "estatus": (r.get("estatus") or "").strip() or None,
            "anio": (r.get("anio") or "").strip() or None,
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
    assert agg["kpis"]["atribucion_documentada"] == 1


def test_grupos_parlamentarios_cuentan_como_origen():
    minutas = [
        {"grupos_parlamentarios": ["MORENA"], "ods_principal": "1"},
        {"grupos_parlamentarios": ["PAN", "PRI"], "ods_principal": "8"},
    ]
    agg = aggregate_minutas(minutas)
    origenes = {o["origen"]: o["n"] for o in agg["por_origen"]}
    # Una minuta con coautoría cuenta en cada grupo, pero como atribución única.
    assert origenes == {"MORENA": 1, "PAN": 1, "PRI": 1}
    assert agg["kpis"]["atribucion_documentada"] == 2
    assert agg["kpis"]["sin_origen_documentado"] == 0


def test_semilla_139_ejecutivo_y_por_documentar():
    minutas = _load_seed()
    assert len(minutas) == 139
    agg = aggregate_minutas(minutas, corte="2026-07-21")
    origenes = {o["origen"]: o["n"] for o in agg["por_origen"]}
    assert origenes.get("Ejecutivo Federal") == 81
    assert origenes.get(POR_DOCUMENTAR) == 58
    assert agg["kpis"]["minutas_totales"] == 139
    assert agg["kpis"]["atribucion_documentada"] == 81
    assert agg["corte"] == "2026-07-21"


def test_por_estatus_y_por_anio():
    agg = aggregate_minutas(_load_seed())
    est = {e["estatus"]: e["n"] for e in agg["por_estatus"]}
    assert est == {"publicada_dof": 62, "en_revisora": 75, "devuelta": 2}
    anios = {a["anio"]: a["n"] for a in agg["por_anio"]}
    assert anios == {"I": 39, "II": 100}


def test_por_ods_ordenado_numericamente():
    agg = aggregate_minutas(_load_seed())
    ods = [int(r["ods"]) for r in agg["por_ods"]]
    assert ods == sorted(ods)
