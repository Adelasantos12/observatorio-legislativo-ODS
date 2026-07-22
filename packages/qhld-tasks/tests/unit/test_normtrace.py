"""Tests de la codificación estructural NormTrace (etapa 3).

Sin infraestructura: el proveedor por defecto es el codificador heurístico
`mock` y la caché Mongo se autodesactiva al no haber servidor. Cubre validez
contra esquema, presupuesto, presencia de confidence/review, y el camino del
proveedor real (JSON válido vs. inválido → needs_human_review) con un LLM falso.
"""

import json

import pytest

from tipi_tasks import config, normtrace

pytestmark = pytest.mark.unit


UNIT_SALUD = {
    "unit_id": "GACETA-artunico",
    "unit_type": "articulo",
    "number": "Único",
    "heading": "Articulo Unico.- ...",
    "text": (
        "Articulo Unico.- La Secretaría de Salud deberá garantizar el acceso a la "
        "salud intercultural de los pueblos indígenas, previa consulta indígena, en "
        "coordinación con las entidades federativas."
    ),
    "topics": ["ODS 3 Salud y bienestar"],
    "tags": [{"tag": "Salud intercultural"}],
}


def test_heuristic_output_is_schema_valid():
    analysis = normtrace.code_unit(UNIT_SALUD)
    assert normtrace.validate_analysis(analysis) == []
    # Actor y deber identificados razonablemente.
    assert "Secretaría de Salud" in analysis["actor_mentioned"]
    assert analysis["duty_created"]  # marcador «deberá»


def test_every_output_carries_confidence_and_review():
    analysis = normtrace.code_unit(UNIT_SALUD)
    assert analysis["confidence_level"] in ("low", "medium", "high")
    assert analysis["review_status"] in (
        "needs_human_review", "reviewed", "auto_accepted",
    )


def test_gap_types_within_enum():
    analysis = normtrace.code_unit(UNIT_SALUD)
    allowed = {
        "legal_silence", "competence_ambiguity", "administrative_only_anchoring",
        "procedural_gap", "coordination_gap", "federal_implementation_gap",
        "rights_safeguard_gap", "oversight_gap", "budget_capacity_gap",
        "update_review_needed",
    }
    assert set(analysis["gap_type"]) <= allowed


def test_analyze_units_budget():
    units = [dict(UNIT_SALUD, unit_id=f"U{i}") for i in range(3)]
    res = normtrace.analyze_units(units, max_units=2)
    assert res["status"] == "SUCCESS"
    assert res["units_analyzed"] == 2
    assert res["units_skipped"] == 1
    assert all("analysis" in u for u in res["units"])
    # Ninguna salida sin review_status.
    assert all(u["analysis"]["review_status"] for u in res["units"])


def test_deterministic_mock():
    a = normtrace.code_unit(UNIT_SALUD)
    b = normtrace.code_unit(UNIT_SALUD)
    assert a == b


# --- Camino del proveedor real (LLM falso) -----------------------------------

def test_llm_invalid_json_falls_back_to_needs_review(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    monkeypatch.setattr(normtrace.llm, "complete", lambda system, user: "no soy json")
    analysis = normtrace.code_unit(UNIT_SALUD)
    assert normtrace.validate_analysis(analysis) == []
    assert analysis["review_status"] == "needs_human_review"


def test_llm_valid_json_is_used(monkeypatch):
    model_out = {
        "unit_id": "GACETA-artunico",
        "actor_mentioned": "la Secretaría de Salud",
        "power_granted": "",
        "duty_created": "garantizar el acceso a la salud intercultural",
        "procedure_created": "consulta indígena previa",
        "coordination_mechanism": "con las entidades federativas",
        "enforcement_or_sanction": "",
        "rights_safeguard": "derecho a la salud de los pueblos indígenas",
        "source_level": "statutory",
        "gap_type": ["coordination_gap"],
        "confidence_level": "medium",
        "review_status": "needs_human_review",
    }
    monkeypatch.setattr(config, "LLM_PROVIDER", "openai")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    monkeypatch.setattr(
        normtrace.llm, "complete",
        lambda system, user: "Aquí tienes:\n" + json.dumps(model_out),
    )
    analysis = normtrace.code_unit(UNIT_SALUD)
    assert normtrace.validate_analysis(analysis) == []
    assert analysis["confidence_level"] == "medium"
    assert analysis["gap_type"] == ["coordination_gap"]
