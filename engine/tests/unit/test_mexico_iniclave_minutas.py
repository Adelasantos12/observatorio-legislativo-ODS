"""Tests de minutas de la LXVI (adenda v3): scraper, codificación y atribución.

Sin red ni Mongo: parsers deterministas sobre la semilla cruda y textos fixture.
"""

import pytest

from qhld_engine.extractors.mexico import iniclave_minutas as im
from qhld_engine.normtrace import atribucion, minutas_coding as mc

pytestmark = pytest.mark.unit


# --- Scraper / semilla cruda -------------------------------------------------

def test_parse_clave():
    assert im.parse_clave("CD-LXVI-I-1P-001") == ("LXVI", "I", "1P", 1)
    assert im.parse_clave("CD-LXVI-II-1E-139") == ("LXVI", "II", "1E", 139)


def test_sequence_report_sin_huecos():
    claves = [f"CD-LXVI-I-1P-{n:03d}" for n in range(1, 6)]
    rep = im.sequence_report(claves)
    assert rep == {"min": 1, "max": 5, "total": 5, "gaps": []}


def test_sequence_report_detecta_huecos():
    claves = ["CD-LXVI-I-1P-001", "CD-LXVI-I-1P-002", "CD-LXVI-I-1P-005"]
    rep = im.sequence_report(claves)
    assert rep["gaps"] == [3, 4]


def test_semilla_cruda_139_continua():
    rows = im.load_raw_csv()
    assert len(rows) == 139
    rep = im.sequence_report([r["clave"] for r in rows])
    assert rep["gaps"] == []
    assert (rep["min"], rep["max"]) == (1, 139)


def test_raw_to_minuta_solo_fuente():
    rows = im.load_raw_csv()
    m = im.raw_to_minuta(rows[0])
    assert m.clave == "CD-LXVI-I-1P-001"
    assert m.numero == 1
    assert m.estatus in ("publicada_dof", "en_revisora", "devuelta")
    assert m.pdfs  # la primera trae PDFs
    assert m.confianza == "pendiente"
    assert m.nivel_revision is None  # el scraper no codifica ni atribuye


# --- Codificación (§A2) ------------------------------------------------------

def test_herencia_confianza_por_score():
    execs = [{"num": "9", "seccion": "Aprobadas y/o publicadas en DOF",
              "denominacion": "x", "ods_principal": "3", "ods_secundarios": "",
              "metas": "3.8", "tema": "Salud", "confianza": "alta"}]
    matches = {"CD-X-1": [0, 0.93], "CD-X-2": [0, 0.66]}
    raw1 = {"clave": "CD-X-1", "titulo": "t", "estatus": "en_revisora", "anio": "I"}
    raw2 = {"clave": "CD-X-2", "titulo": "t", "estatus": "en_revisora", "anio": "I"}
    c1, manual1 = mc.inherit(raw1, matches, execs)
    c2, manual2 = mc.inherit(raw2, matches, execs)
    assert c1["confianza"] == "alta" and manual1 is False        # score>=0.75 → origen
    assert c2["confianza"] == "media" and manual2 is True         # 0.62–0.75 → media + manual
    assert c1["origen_tipo"] == "ejecutivo"
    assert c1["metas"] == ["3.8"]
    assert c1["nivel_revision"] == "automatico_preliminar"


def test_mock_no_inventa():
    c = mc._mock_llm_coding({"titulo": "PROYECTO de Decreto por el que se declara el Día Nacional del Tejate"})
    assert c["ods_principal"] is None
    assert c["metas"] == []
    assert c["confianza"] == "baja"
    assert c["nivel_revision"] == "automatico_preliminar"


def test_code_all_semilla():
    filas, resumen = mc.code_all()
    assert resumen["total"] == 139
    assert resumen["heredadas"] == 81
    assert resumen["por_llm"] == 58
    # Las heredadas llevan origen_tipo ejecutivo y expediente_ref.
    her = [f for f in filas if f["origen_tipo"] == "ejecutivo"]
    assert len(her) == 81
    assert all(f["expediente_ref"] for f in her)


# --- Atribución (§A3) --------------------------------------------------------

# Texto OCR real de las primeras páginas del dictamen CD-LXVI-II-2P-091
# (patrones verificados por la autora; respuesta conocida: PAN).
OCR_091 = """ANTECEDENTES

1. En sesión celebrada por la Cámara de Diputados, la Dip. Annia Sarahí Gómez
Cárdenas y Diputados integrantes del Grupo Parlamentario del PAN presentaron
la Iniciativa con proyecto de decreto por el que se reforman diversas
disposiciones.

SUSCRITA POR LA DIP. ANNIA SARAHÍ GÓMEZ CÁRDENAS Y DIP. INTEGRANTES DEL
GRUPO PARLAMENTARIO DEL PAN"""


def test_atribuye_091_a_pan():
    """Caso de respuesta conocida: el dictamen 091 se atribuye a PAN (v4.1 §4)."""
    assert atribucion.extract_grupos(OCR_091) == ["PAN"]


def test_extract_grupos_normaliza_saltos_de_linea():
    # El OCR parte "GRUPO PARLAMENTARIO" en dos líneas; el whitespace se normaliza.
    texto = "integrantes del Grupo\nParlamentario del\nMORENA presentaron"
    assert atribucion.extract_grupos(texto) == ["MORENA"]


def test_extract_grupos_consolida_varios():
    # Dictamen ómnibus: cada iniciativa trae su propia línea de autoría con verbo.
    texto = (
        "La diputada X, del Grupo Parlamentario del PAN, presentó la iniciativa. "
        "El diputado Y, del Grupo Parlamentario de MORENA, presentó otra. "
        "La diputada Z, del Grupo Parlamentario de Movimiento Ciudadano, suscribió la suya."
    )
    assert atribucion.extract_grupos(texto) == ["MC", "MORENA", "PAN"]


def test_extract_grupos_ignora_lista_de_comision():
    # La lista de integrantes de la comisión nombra a todos los grupos SIN autoría:
    # no debe atribuirse ninguno (antes producía "los 6 partidos" falsos).
    roster = (
        "Integrantes de la Comisión: Grupo Parlamentario de MORENA; "
        "Grupo Parlamentario del PAN; Grupo Parlamentario del PRI; "
        "Grupo Parlamentario del PT; Grupo Parlamentario del PVEM; "
        "Grupo Parlamentario de Movimiento Ciudadano."
    )
    assert atribucion.extract_grupos(roster) == []


def test_extract_grupos_vacio_si_no_hay():
    assert atribucion.extract_grupos("Texto sin grupos parlamentarios.") == []


def test_pdf_url_base_real_y_sin_duplicar_iniclave():
    base = "https://www.diputados.gob.mx/LeyesBiblio/iniclave/"
    assert atribucion.pdf_url("66/CD-LXVI-II-2P-091/02_dictamen_091_17feb26.pdf", base) == (
        base + "66/CD-LXVI-II-2P-091/02_dictamen_091_17feb26.pdf"
    )
    # href del año en curso: ruta con 'iniclave/' al inicio no debe duplicar.
    assert atribucion.pdf_url("iniclave/66/CD-X/02_dictamen.pdf", base) == (
        base + "66/CD-X/02_dictamen.pdf"
    )


def test_dictamen_pdf_elige_el_correcto():
    minuta = {"pdfs": ["66/x/01_minuta.pdf", "66/x/02_dictamen_001.pdf", "66/x/03_dof.pdf"]}
    assert atribucion.dictamen_pdf(minuta) == "66/x/02_dictamen_001.pdf"
    assert atribucion.dictamen_pdf({"pdfs": []}) is None
