"""Tests del análisis NormTrace servido por la API (adenda nivel 2, §4)."""

import pytest

from tipi_backend.api.normtrace import (
    DESCARGO,
    LGA_EXPEDIENTE_ID,
    count_con_analisis,
    load_brief,
    load_gold_run,
    run_for_expediente,
)

pytestmark = pytest.mark.unit


def test_dorado_se_sirve_validado_con_34_registros():
    run = load_gold_run()
    assert run is not None
    assert run["nivel_revision"] == "validado_autora"
    assert len(run["registros"]) == 34
    assert run["descargo"] == DESCARGO
    # Columna renombrada al vocabulario del esquema.
    assert "disposicion" in run["registros"][0]
    assert "disposicion_lga" not in run["registros"][0]


def test_vitrina_es_la_lga_y_otros_no_tienen_analisis():
    assert run_for_expediente(LGA_EXPEDIENTE_ID)["nivel_revision"] == "validado_autora"
    assert run_for_expediente("EJE-2024-2030-1-otra") is None


def test_corrida_automatica_lleva_descargo_y_no_se_marca_validada():
    preliminar = {
        "_id": "EJE-2024-2030-9-x", "nivel_revision": "automatico_preliminar",
        "marco": "ods6", "registros": [],
    }
    run = run_for_expediente("EJE-2024-2030-9-x", mongo_lookup=lambda i: dict(preliminar))
    assert run["nivel_revision"] == "automatico_preliminar"
    assert run["descargo"] == DESCARGO


def test_kpi_cuenta_el_dorado():
    assert count_con_analisis(lambda: 0) == 1
    assert count_con_analisis(lambda: 3) == 4


def test_brief_se_sirve_y_bloquea_traversal():
    assert (load_brief() or "").startswith("# La Ley General de Aguas")
    assert load_brief("../../../etc/passwd") is None
