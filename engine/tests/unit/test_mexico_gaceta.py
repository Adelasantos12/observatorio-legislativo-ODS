"""Tests del parser e ingesta de la Gaceta Parlamentaria (México, F6).

Sin red ni Mongo: el parser trabaja sobre HTML de fixture; la ingesta se prueba
con el repositorio de iniciativas mockeado.
"""

import pytest

from qhld_engine.extractors.mexico import gaceta
from qhld_engine.extractors.mexico.initiatives import InitiativesExtractor

pytestmark = pytest.mark.unit


GACETA_HTML = """<html><body>
<div class="indice">
  <a class="Indice" href="#Iniciativa1">Que reforma la Ley General de Salud, para garantizar la salud intercultural, a cargo de la diputada Fulana de Tal, del Grupo Parlamentario Morena.</a>
  <a class="Indice" href="#Iniciativa2">Que adiciona la Ley de Aguas Nacionales, a cargo del diputado Zutano P&eacute;rez, del Grupo Parlamentario PAN.</a>
</div>
<a name="Iniciativa1"></a>
<p>La suscrita, diputada federal, somete a consideraci&oacute;n la presente iniciativa.</p>
<p>Articulo Unico. La Secretaria de Salud debera garantizar el acceso a la salud intercultural.</p>
<a name="Iniciativa2"></a>
<p>El que suscribe propone reformar la Ley de Aguas Nacionales para el derecho humano al agua.</p>
</body></html>"""


def test_build_url():
    assert (
        gaceta.build_url("20260716", "66", "I")
        == "https://gaceta.diputados.gob.mx/Gaceta/66/2026/jul/20260716-I.html"
    )
    # Sin anexo.
    assert gaceta.build_url("20260116", "66").endswith("/2026/ene/20260116.html")


@pytest.mark.parametrize(
    "title,author,party",
    [
        (
            "Que reforma la LGS, a cargo de la diputada Fulana de Tal, del Grupo Parlamentario Morena.",
            "Fulana de Tal",
            "Morena",
        ),
        (
            "Que adiciona la Ley X, a cargo del diputado Zutano Pérez, del Grupo Parlamentario PAN.",
            "Zutano Pérez",
            "PAN",
        ),
        (
            "Iniciativa sin autoría explícita en el título.",
            "",
            "",
        ),
    ],
)
def test_parse_title(title, author, party):
    a, p = gaceta.parse_title(title)
    assert a == author
    assert p == party


def test_parse_gaceta_index_and_body():
    inis = gaceta.parse_gaceta(GACETA_HTML)
    assert [i.ref for i in inis] == ["Iniciativa1", "Iniciativa2"]

    first = inis[0]
    assert first.author == "Fulana de Tal"
    assert first.party == "Morena"
    assert "Ley General de Salud" in first.title
    # El cuerpo (inline) se recogió como oraciones, sin invadir la iniciativa 2.
    assert any("salud intercultural" in s for s in first.content)
    assert all("Aguas Nacionales" not in s for s in first.content)

    second = inis[1]
    assert second.author == "Zutano Pérez"
    assert second.party == "PAN"
    assert any("derecho humano al agua" in s for s in second.content)


def test_parse_gaceta_without_index_uses_first_sentence():
    html = (
        '<html><body><a name="Iniciativa1"></a>'
        "<p>Que reforma la Ley General de Salud. Cuerpo de la iniciativa.</p>"
        "</body></html>"
    )
    inis = gaceta.parse_gaceta(html)
    assert len(inis) == 1
    assert inis[0].title.startswith("Que reforma la Ley General de Salud")


def test_ingest_html_persists_initiatives(monkeypatch):
    saved = []

    class _Repo:
        @staticmethod
        def get(ref):
            raise Exception("no existe")

        @staticmethod
        def save(initiative):
            saved.append(initiative)

    monkeypatch.setattr(
        "qhld_engine.extractors.mexico.initiatives.Initiatives", _Repo
    )

    ex = InitiativesExtractor()
    ex.date = "20260716"
    ex.ingest_html(GACETA_HTML, url="https://gaceta.diputados.gob.mx/x.html")

    assert len(saved) == 2
    refs = {i["reference"] for i in saved}
    assert "20260716-Iniciativa1" in refs
    ini = next(i for i in saved if i["reference"] == "20260716-Iniciativa1")
    assert ini["author_deputies"] == ["Fulana de Tal"]
    assert ini["author_parliamentarygroups"] == ["Morena"]
    assert ini["place"] == "Cámara de Diputados"
    assert ini["content"] and any("salud intercultural" in s for s in ini["content"])
