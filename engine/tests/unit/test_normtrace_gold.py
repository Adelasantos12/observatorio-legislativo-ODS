"""Tests del candado de calidad NormTrace (adenda nivel 2).

Sin red ni LLM. Verifican: (4) el CSV dorado es intocable por el pipeline —el test
reprueba si cambia su hash—; el autochequeo del dorado aprueba los umbrales
estructurales; el esquema valida el dorado; y la resolución de citas es 100%.
"""

import pytest

from qhld_engine.normtrace import citations, gold, schema
from qhld_engine.normtrace.evaluator import evaluate
from qhld_engine.normtrace.frameworks import cobertura_estandares

pytestmark = pytest.mark.unit


# Huella del ejemplo dorado (34 registros, codificación de autora verificada).
# Si este hash cambia, el dorado fue editado: DEBE ser decisión humana explícita
# con nota en la Bitácora, nunca un efecto colateral del pipeline.
GOLD_SHA256 = "1ec830348d0b01516a6424b9315003442f316b80914920656ab8d690b87310a7"


def test_gold_hash_es_estable():
    """El pipeline no puede mutar el dorado. Actualizar GOLD_SHA256 solo a mano."""
    actual = gold.gold_hash()
    assert actual == GOLD_SHA256, (
        "El hash del CSV dorado cambió. Si fue una edición deliberada de la autora, "
        f"actualiza GOLD_SHA256 a {actual} y anótalo en la Bitácora. Si no, revierte "
        "el cambio: el dorado es solo lectura."
    )


def test_dorado_valida_contra_esquema():
    run = gold.gold_run()
    errores = schema.validate_run(run)
    assert errores == [], errores


def test_dorado_tiene_34_registros():
    assert len(gold.load_gold()) == 34


def test_resolucion_de_citas_100pct():
    run = gold.gold_run()
    rep = citations.citation_resolution(run["registros"])
    assert rep["tasa"] == 1.0, rep["no_resueltas"]


def test_cobertura_estandares_completa():
    _, faltantes = cobertura_estandares(gold.load_gold(), "ods6")
    assert faltantes == set(), f"estándares sin cubrir: {faltantes}"


def test_autochequeo_dorado_aprueba():
    """El dorado, evaluado como corrida validada contra sí mismo, aprueba los 5 umbrales."""
    report = evaluate(gold.gold_run())
    assert report["aprueba"], [u for u in report["umbrales"] if u.get("pasa") is False]


def test_falso_sustantivo_grave_reprueba():
    """Un registro sustantivo+completa donde el dorado marca contextual debe reprobar."""
    gold_rows = gold.load_gold()
    # Encuentra un registro dorado contextual y falséalo a sustantivo+completa.
    ctx = next(r for r in gold_rows if r["rol_correspondencia"] == "contextual_habilitante")
    falso = dict(ctx, rol_correspondencia="sustantivo", cobertura="completa")
    run = {
        "nivel_revision": "automatico_preliminar", "marco": "ods6",
        "fuente_texto": "test", "registros": [falso],
    }
    report = evaluate(run)
    t5 = next(u for u in report["umbrales"] if u["nombre"].startswith("Sin falsos"))
    assert t5["pasa"] is False
