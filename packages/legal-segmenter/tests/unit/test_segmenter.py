"""Tests del segmentador jurídico mexicano.

Cubre: jerarquía título/capítulo/artículo/fracción/inciso, numeración
"bis/ter/quáter", artículos transitorios, ids estables, preservación de texto y
fallback a párrafos para texto no estructurado. Usa un fragmento real de la Ley
General de Salud y una iniciativa tipo Gaceta.
"""

import pytest

from legal_segmenter import Unit, segment, segment_to_dicts

pytestmark = pytest.mark.unit


SAMPLE_LGS = """## TITULO PRIMERO

Disposiciones Generales

## CAPITULO UNICO

Articulo 1o.- La presente Ley reglamenta el derecho a la protección de la salud.

Articulo 3o.- En los términos de esta Ley, es materia de salubridad general:

I.- La organización y control de la prestación de servicios de salud;

II.- La atención médica, preferentemente en beneficio de grupos vulnerables;

III Bis.- El programa de prevención y atención de adicciones;

Articulo 17 Bis.- La Secretaría de Salud ejercerá las atribuciones siguientes:

a) Efectuar la evaluación de riesgos a la salud;

b) Proponer políticas en materia de salubridad general;

## TRANSITORIOS

PRIMERO.- La presente Ley entrará en vigor al día siguiente de su publicación.

SEGUNDO.- Se abroga el Código Sanitario anterior.
"""


# Fragmento REAL de la Ley General de Salud (Art. 6o. y primeras fracciones),
# tal como aparece en normtrace/01_sources/mexico/md/ (incluye anotaciones de
# reforma y la fracción romana en su propia línea).
REAL_LGS = """### Artículo 6o.- El Sistema Nacional de Salud tiene los siguientes objetivos:

Párrafo reformado DOF 19-09-2006, 13-01-2014

I.-
Proporcionar servicios de salud a toda la población y mejorar la calidad de los mismos,
atendiendo a los problemas sanitarios prioritarios;
Fracción reformada DOF 13-01-2014

II.
Contribuir al desarrollo demográfico armónico del país;

III.
Colaborar al bienestar social de la población mediante servicios de asistencia social;
"""


GACETA_INICIATIVA = """Iniciativa con proyecto de decreto que reforma la Ley General de Salud, a cargo
de la diputada Fulana de Tal, del Grupo Parlamentario correspondiente.

La suscrita, diputada federal, somete a consideración de esta soberanía la
presente iniciativa, al tenor de la siguiente exposición de motivos.

Por lo anteriormente expuesto, se somete el siguiente proyecto de decreto:

Articulo Unico.- Se reforma el artículo 77 bis de la Ley General de Salud para
garantizar el acceso a la salud intercultural de los pueblos indígenas.
"""


def _by_type(units, t):
    return [u for u in units if u.unit_type == t]


def _ids(units):
    return [u.unit_id for u in units]


# --- Estructura y jerarquía ---------------------------------------------------

def test_detects_container_hierarchy():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    tit = _by_type(units, "titulo")
    cap = _by_type(units, "capitulo")
    assert len(tit) == 1 and tit[0].unit_id == "MX-LGS-tit1"
    assert len(cap) == 1 and cap[0].unit_id == "MX-LGS-tit1-capunico"
    assert cap[0].parent_id == "MX-LGS-tit1"


def test_articles_hang_from_container():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    arts = _by_type(units, "articulo")
    assert [a.unit_id for a in arts] == [
        "MX-LGS-art1", "MX-LGS-art3", "MX-LGS-art17bis",
    ]
    assert all(a.parent_id == "MX-LGS-tit1-capunico" for a in arts)


def test_bis_article_number_normalized():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    bis = [u for u in units if u.unit_id == "MX-LGS-art17bis"]
    assert bis and bis[0].unit_type == "articulo"
    assert bis[0].number == "17 Bis"


def test_roman_fractions_with_bis():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    fracs = _by_type(units, "fraccion")
    ids = _ids(fracs)
    assert "MX-LGS-art3-fracI" in ids
    assert "MX-LGS-art3-fracII" in ids
    assert "MX-LGS-art3-fracIIIbis" in ids
    # Todas cuelgan del artículo 3o.
    assert all(f.parent_id == "MX-LGS-art3" for f in fracs)


def test_incisos_hang_from_article():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    inc = _by_type(units, "inciso")
    assert {u.unit_id for u in inc} == {"MX-LGS-art17bis-inca", "MX-LGS-art17bis-incb"}
    assert all(u.parent_id == "MX-LGS-art17bis" for u in inc)


def test_transitorios():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    cont = _by_type(units, "transitorios")
    trans = _by_type(units, "transitorio")
    assert len(cont) == 1
    assert [t.number for t in trans] == ["PRIMERO", "SEGUNDO"]
    assert all(t.parent_id == cont[0].unit_id for t in trans)


# --- Invariantes --------------------------------------------------------------

def test_text_preservation_sample():
    units = segment(SAMPLE_LGS, doc_id="MX-LGS")
    recon = "\n".join(u.text for u in units)
    assert recon.strip() == SAMPLE_LGS.strip()


def test_text_preservation_real_lgs():
    units = segment(REAL_LGS, doc_id="MX-LGS")
    recon = "\n".join(u.text for u in units)
    assert recon.strip() == REAL_LGS.strip()


def test_stable_ids_deterministic():
    a = _ids(segment(SAMPLE_LGS, doc_id="MX-LGS"))
    b = _ids(segment(SAMPLE_LGS, doc_id="MX-LGS"))
    assert a == b
    # ids únicos
    assert len(a) == len(set(a))


# --- Fragmento real LGS -------------------------------------------------------

def test_real_lgs_article_and_fractions():
    units = segment(REAL_LGS, doc_id="MX-LGS")
    arts = _by_type(units, "articulo")
    fracs = _by_type(units, "fraccion")
    assert len(arts) == 1 and arts[0].unit_id == "MX-LGS-art6"
    assert {f.number for f in fracs} == {"I", "II", "III"}
    assert all(f.parent_id == "MX-LGS-art6" for f in fracs)
    # La anotación de reforma va DENTRO del texto de su unidad (sin pérdida).
    assert "Fracción reformada DOF 13-01-2014" in fracs[0].text


# --- Fallback a párrafos ------------------------------------------------------

def test_gaceta_initiative_detects_article():
    units = segment(GACETA_INICIATIVA, doc_id="GACETA-2026-07-16")
    arts = _by_type(units, "articulo")
    assert len(arts) == 1
    assert arts[0].unit_id == "GACETA-2026-07-16-artunico"
    # El preámbulo (exposición de motivos) queda como unidad sin perder texto.
    recon = "\n".join(u.text for u in units)
    assert recon.strip() == GACETA_INICIATIVA.strip()


def test_unstructured_text_falls_back_to_paragraphs():
    prosa = (
        "Este es un discurso sin estructura legislativa.\n\n"
        "Habla de salud y de agua pero no tiene artículos ni fracciones.\n\n"
        "Solo párrafos separados por líneas en blanco."
    )
    units = segment(prosa, doc_id="DISCURSO")
    assert all(u.unit_type == "parrafo" for u in units)
    assert len(units) == 3
    assert units[0].unit_id == "DISCURSO-p1"
    recon = "\n".join(u.text for u in units)
    assert recon.strip() == prosa.strip()


def test_segment_to_dicts_shape():
    dicts = segment_to_dicts(SAMPLE_LGS, doc_id="MX-LGS")
    assert isinstance(dicts, list) and isinstance(dicts[0], dict)
    assert set(dicts[0]) == {
        "unit_id", "unit_type", "number", "heading", "text", "parent_id",
    }
