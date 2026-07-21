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

def test_extract_grupos_reconoce_bancadas():
    texto = (
        "Iniciativa presentada por la diputada Fulana, del Grupo Parlamentario de "
        "MORENA. Otra, del Grupo Parlamentario del Partido Acción Nacional."
    )
    assert atribucion.extract_grupos(texto) == ["MORENA", "PAN"]


def test_extract_grupos_vacio_si_no_hay():
    assert atribucion.extract_grupos("Texto sin grupos parlamentarios.") == []


def test_dictamen_pdf_elige_el_correcto():
    minuta = {"pdfs": ["66/x/01_minuta.pdf", "66/x/02_dictamen_001.pdf", "66/x/03_dof.pdf"]}
    assert atribucion.dictamen_pdf(minuta) == "66/x/02_dictamen_001.pdf"
    assert atribucion.dictamen_pdf({"pdfs": []}) is None
