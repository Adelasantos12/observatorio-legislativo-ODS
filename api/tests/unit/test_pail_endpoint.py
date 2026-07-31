"""Endpoint del escáner con el módulo seleccionable PAIL.

Verifica el contrato de activación: pail=false no cambia el flujo; pail=true
añade el bloque `pail`; sin índices la capa CSN degrada sin excepción.
"""

import textwrap

import pytest

from tipi_tasks import config as tcfg, crn_indexer
from tests.helpers import build_tags_from_fixture, load_knowledgebase

pytestmark = pytest.mark.unit


INICIATIVA = textwrap.dedent("""\
    SE REFORMA EL ARTÍCULO 100 DEL CÓDIGO FISCAL DE LA FEDERACIÓN

    EXPOSICIÓN DE MOTIVOS

    La presente iniciativa fortalece el combate a los delitos fiscales.

    Artículo 100. El derecho a formular la querella se extingue en cinco años,
    salvo que la autoridad competente resuelva conforme al reglamento.

    TRANSITORIOS

    Primero. El presente Decreto entrará en vigor al día siguiente de su publicación.
    Segundo. La autoridad deberá emitir las disposiciones reglamentarias.
""")

_LAWS = {
    "cff.md": (
        "---\nnombre: CÓDIGO FISCAL DE LA FEDERACIÓN\npublicacion_dof: 1981-12-31\n"
        "ultima_reforma_dof: 2025-11-14\nestatus: TEXTO VIGENTE\n---\n"
        "# CÓDIGO FISCAL DE LA FEDERACIÓN\n\n## Artículo 100\nSe extingue en cinco años.\n"
    ),
    "cnpp.md": (
        "---\nnombre: CÓDIGO NACIONAL DE PROCEDIMIENTOS PENALES\npublicacion_dof: 2014-03-05\n"
        "ultima_reforma_dof: 2025-06-01\nestatus: TEXTO VIGENTE\n---\n"
        "# CÓDIGO NACIONAL DE PROCEDIMIENTOS PENALES\n\n## Artículo 167\n"
        "Los previstos en el artículo 100 del Código Fiscal de la Federación.\n"
    ),
}


@pytest.fixture(autouse=True)
def _inject_kb(monkeypatch):
    kb = build_tags_from_fixture(load_knowledgebase())
    monkeypatch.setattr("tipi_backend.api.cache.get", lambda key: kb)


@pytest.fixture
def indices(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    for name, body in _LAWS.items():
        (vault / name).write_text(body, encoding="utf-8")
    out = tmp_path / "indices"
    crn_indexer.build(str(vault), str(out))
    monkeypatch.setattr(tcfg, "PAIL_INDICES_PATH", str(out))
    return str(out)


def test_pail_false_no_cambia_el_flujo(client):
    """Criterio 1: con pail=false la respuesta no trae bloque pail y el resultado
    ODS es idéntico a una petición normal."""
    base = client.post("/tagger/", data={"text": INICIATIVA, "knowledgebase": "ods"})
    con_flag = client.post(
        "/tagger/", data={"text": INICIATIVA, "knowledgebase": "ods", "pail": "false"})
    assert base.status_code == con_flag.status_code == 200
    assert "pail" not in base.json()
    assert "pail" not in con_flag.json()
    assert base.json()["result"] == con_flag.json()["result"]


def test_pail_true_con_indices_devuelve_bloque(client, indices):
    """Criterio 2: con pail=true e índices, aparece el bloque pail con dictamen y
    al menos una verificación CSN con metadatos de norma."""
    r = client.post(
        "/tagger/", data={"text": INICIATIVA, "knowledgebase": "ods", "pail": "true"})
    assert r.status_code == 200
    body = r.json()
    # El flujo ODS sigue presente e intacto (el bloque result no desaparece).
    assert body["status"] == "SUCCESS" and "topics" in body["result"]
    p = body["pail"]
    assert p["protocolo"] == "PAIL-MX"
    assert p["dictamen_global"]
    csn06 = next(v for v in p["verificaciones"] if v["id"] == "CSN-06")
    assert csn06["resultado"] == "CUMPLE"
    assert any(n.get("ultima_reforma") == "2025-11-14" for n in csn06["normas_invocadas"])


def test_pail_true_sin_indices_degrada(client, monkeypatch):
    """Criterio 3: sin índices, el bloque pail sale con CSN NO_VERIFICABLE y sin
    excepción no controlada (la petición responde 200)."""
    monkeypatch.setattr(tcfg, "PAIL_INDICES_PATH", "")
    r = client.post(
        "/tagger/", data={"text": INICIATIVA, "knowledgebase": "ods", "pail": "true"})
    assert r.status_code == 200
    p = r.json()["pail"]
    csn = next(v for v in p["verificaciones"] if v["id"] == "CSN-06")
    assert csn["resultado"] == "NO_VERIFICABLE"
