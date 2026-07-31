"""Tests del módulo PAIL (envoltura del motor pail_engine).

No requieren Mongo, Redis ni broker. El corpus CRN se construye en un vault de
fixture (2-3 leyes) con `crn_indexer`, como sugiere el contrato de integración.
"""

import json
import textwrap

import pytest

from tipi_tasks import config, crn_indexer, pail


# --- Fixtures: mini-vault de 3 leyes + iniciativa de prueba -------------------

_CFF = """\
---
nombre: CÓDIGO FISCAL DE LA FEDERACIÓN
publicacion_dof: 1981-12-31
ultima_reforma_dof: 2025-11-14
estatus: TEXTO VIGENTE
---
# CÓDIGO FISCAL DE LA FEDERACIÓN

## Artículo 100
El derecho a formular la querella se extingue en cinco años.
"""

_CNPP = """\
---
nombre: CÓDIGO NACIONAL DE PROCEDIMIENTOS PENALES
publicacion_dof: 2014-03-05
ultima_reforma_dof: 2025-06-01
estatus: TEXTO VIGENTE
---
# CÓDIGO NACIONAL DE PROCEDIMIENTOS PENALES

## Artículo 167
Se consideran delitos que ameritan prisión preventiva oficiosa los previstos en
el artículo 100 del Código Fiscal de la Federación.
"""

_LFT = """\
---
nombre: LEY FEDERAL DEL TRABAJO
publicacion_dof: 1970-04-01
ultima_reforma_dof: 2024-12-01
estatus: TEXTO VIGENTE
---
# LEY FEDERAL DEL TRABAJO

## Artículo 1
La presente Ley rige las relaciones de trabajo.
"""

INICIATIVA = textwrap.dedent("""\
    SE REFORMA EL ARTÍCULO 100 DEL CÓDIGO FISCAL DE LA FEDERACIÓN

    EXPOSICIÓN DE MOTIVOS

    La presente iniciativa atiende la necesidad de fortalecer el combate a los
    delitos fiscales.

    Artículo 100. El derecho a formular la querella, la declaratoria y la
    declaratoria de perjuicio de la Secretaría de Hacienda y Crédito Público
    precluye y, por lo tanto, se extingue la acción penal, en cinco años, que se
    computarán a partir de la comisión del delito, salvo que la autoridad
    competente resuelva conforme al reglamento.

    TRANSITORIOS

    Primero. El presente Decreto entrará en vigor al día siguiente de su publicación.
    Segundo. La autoridad deberá emitir las disposiciones reglamentarias del
    Registro Nacional de Denuncias Fiscales.
""")


@pytest.fixture
def indices(tmp_path):
    """Construye índices CRN desde un vault de 3 leyes y los deja disponibles."""
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "cff.md").write_text(_CFF, encoding="utf-8")
    (vault / "cnpp.md").write_text(_CNPP, encoding="utf-8")
    (vault / "lft.md").write_text(_LFT, encoding="utf-8")
    out = tmp_path / "indices"
    crn_indexer.build(str(vault), str(out))
    return str(out)


@pytest.fixture
def con_indices(monkeypatch, indices):
    monkeypatch.setattr(config, "PAIL_INDICES_PATH", indices)
    return indices


@pytest.fixture
def sin_indices(monkeypatch):
    monkeypatch.setattr(config, "PAIL_INDICES_PATH", "")


# --- Tests -------------------------------------------------------------------

def test_dictamen_valida_contra_schema(con_indices):
    d = pail.analizar_texto(INICIATIVA, mtl=True)
    assert pail.validate_dictamen(d) == []
    assert d["protocolo"] == "PAIL-MX"
    assert d["modulo_mtl_activo"] is True
    assert d["articulos_detectados"] >= 1


def test_csn_con_metadatos_de_norma(con_indices):
    d = pail.analizar_texto(INICIATIVA, mtl=True)
    # CSN-06: vigencia con la última reforma del corpus (no de memoria).
    csn06 = next(v for v in d["verificaciones"] if v["id"] == "CSN-06")
    assert csn06["resultado"] == "CUMPLE"
    assert any(n["ultima_reforma"] == "2025-11-14" for n in csn06["normas_invocadas"])
    # CSN-04: remisión entrante detectada (CNPP art. 167 cita el CFF).
    csn04 = next(v for v in d["verificaciones"] if v["id"] == "CSN-04")
    assert csn04["armonizacion_candidata"]
    assert any("PROCEDIMIENTOS PENALES" in a["norma"] for a in csn04["armonizacion_candidata"])


def test_sin_indices_degrada_a_no_verificable(sin_indices):
    d = pail.analizar_texto(INICIATIVA, mtl=True)
    for vid in ("CSN-04", "CSN-06"):
        v = next(x for x in d["verificaciones"] if x["id"] == vid)
        assert v["resultado"] == "NO_VERIFICABLE"
    assert pail.validate_dictamen(d) == []  # sigue siendo un dictamen válido


def test_determinista_sin_llm(con_indices):
    a = pail.analizar_texto(INICIATIVA, mtl=True)
    b = pail.analizar_texto(INICIATIVA, mtl=True)
    assert a == b


def test_pasada_llm_resuelve_y_reagrega(monkeypatch, con_indices):
    captured = {}

    def fake_complete(system, user):
        captured["system"] = system
        return json.dumps({
            "resultado": "CUMPLE",
            "explicacion": "evidencia suficiente",
            "evidencia": [{"cita": "x", "ubicacion": "y", "fuente": "iniciativa"}],
        })

    monkeypatch.setattr(config, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    monkeypatch.setattr(pail.llm, "complete", fake_complete)

    d = pail.analizar_texto(INICIATIVA, mtl=True, llm_juicio=True)

    # El blindaje (regla_evidencia + prohibición de conocimiento propio) va en el system.
    assert "PROHIBIDO" in captured["system"]
    assert "corpus" in captured["system"].lower()
    # No quedan verificaciones sin resolver y el dictamen valida.
    assert not [v for v in d["verificaciones"] if v["resultado"] == "PENDIENTE_JUICIO"]
    assert pail.validate_dictamen(d) == []


def test_bloque_resumen_presente(con_indices):
    """Motor v2.1: el dictamen trae el bloque `resumen` (red flags, oportunidades,
    cobertura, sin evaluar)."""
    d = pail.analizar_texto(INICIATIVA, mtl=True)
    r = d["resumen"]
    assert set(r) >= {"red_flags", "areas_oportunidad", "cobertura_evaluada", "sin_evaluar"}
    assert isinstance(r["sin_evaluar"]["total"], int)
    assert 0 <= d["cobertura_evaluada"] <= 1


def test_cobertura_insuficiente_no_es_viable(con_indices):
    """Sin pasada LLM, las 28 de juicio quedan pendientes → cobertura < 0.5 →
    el dictamen NUNCA es VIABLE (es PRELIMINAR_COBERTURA_INSUFICIENTE)."""
    d = pail.analizar_texto(INICIATIVA, mtl=True)
    assert d["cobertura_evaluada"] < 0.5
    assert d["dictamen_global"] == "PRELIMINAR_COBERTURA_INSUFICIENTE"


def test_puerta_de_insumo_sin_articulado(con_indices):
    """Un texto sin articulado segmentable (una nota, no una iniciativa) →
    NO_EVALUABLE_INSUMO con nota_insumo, sin CUMPLE vacuos."""
    nota = "Esta es una opinión sobre política fiscal. No contiene articulado."
    d = pail.analizar_texto(nota, mtl=True)
    assert d["dictamen_global"] == "NO_EVALUABLE_INSUMO"
    assert d["resumen"]["nota_insumo"]
    assert d["articulos_detectados"] == 0
    # No hay CUMPLE de relleno cuando no hay insumo evaluable.
    assert not any(v["resultado"] == "CUMPLE" for v in d["verificaciones"])
    assert pail.validate_dictamen(d) == []


def test_llm_sin_evidencia_suficiente_es_no_evaluable(monkeypatch, con_indices):
    # El modelo responde algo inválido → la envoltura lo marca NO_EVALUABLE.
    monkeypatch.setattr(config, "LLM_PROVIDER", "anthropic")
    monkeypatch.setattr(config, "LLM_API_KEY", "x")
    monkeypatch.setattr(pail.llm, "complete", lambda s, u: "no soy json")

    d = pail.analizar_texto(INICIATIVA, mtl=True, llm_juicio=True)
    juicios = [v for v in d["verificaciones"] if v["tipo"] == "juicio"]
    assert juicios and all(v["resultado"] == "NO_EVALUABLE" for v in juicios)
    assert pail.validate_dictamen(d) == []
