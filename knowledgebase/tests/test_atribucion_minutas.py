"""Verifica el CSV de atribución de grupo parlamentario y su aplicación al sembrar.

La atribución se produjo por OCR de los dictámenes (fuera de línea, porque el sitio
de la Cámara bloquea IPs de datacenter) y vive horneada en
`normtrace/03_tables/legislative_mapping/minutas_atribucion.csv`. Estos tests son
puros (sin Mongo): stubbean pymongo para importar `load_minutas` y prueban la lógica.

Correr:  python knowledgebase/tests/test_atribucion_minutas.py   (o con pytest)
"""

import csv
import importlib.util
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATRIB_CSV = ROOT / "normtrace/03_tables/legislative_mapping/minutas_atribucion.csv"
GRUPOS_VALIDOS = {"MORENA", "PAN", "PRI", "PT", "PVEM", "MC", "PRD"}


def _load_module():
    # pymongo arrastra cryptography; stub para poder importar el módulo sin Mongo.
    if "pymongo" not in sys.modules:
        fake = types.ModuleType("pymongo")
        fake.MongoClient = object
        sys.modules["pymongo"] = fake
    spec = importlib.util.spec_from_file_location(
        "load_minutas", ROOT / "knowledgebase/load_minutas.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_csv_grupos_validos_y_sin_duplicar():
    """Cada sigla del CSV es un grupo real de la LXVI y no se repite en una fila."""
    with ATRIB_CSV.open(encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    claves = [f["clave"].strip() for f in filas]
    assert len(claves) == len(set(claves)), "hay claves duplicadas"
    for f in filas:
        grupos = [g.strip() for g in (f.get("grupos") or "").split(";") if g.strip()]
        assert len(grupos) == len(set(grupos)), f"{f['clave']}: grupo repetido"
        for g in grupos:
            assert g in GRUPOS_VALIDOS, f"{f['clave']}: sigla desconocida {g!r}"


def test_conteo_y_casos_conocidos():
    lm = _load_module()
    atrib = lm.load_atribucion(ATRIB_CSV)
    # 52 con grupo (56 dictámenes menos 4 sin línea de autoría legible).
    assert len(atrib) == 52, len(atrib)
    # Caso de respuesta conocida verificado por la autora.
    assert atrib["CD-LXVI-II-2P-091"] == ["PAN"]
    # Dictamen ómnibus real (delitos con IA): iniciativas de los 6 grupos.
    assert atrib["CD-LXVI-II-2P-132"] == ["MC", "MORENA", "PAN", "PRI", "PT", "PVEM"]


def test_aplica_a_legislativa_y_protege_ejecutiva():
    lm = _load_module()
    atrib = lm.load_atribucion(ATRIB_CSV)

    # Minuta de la Cámara con atribución -> origen_tipo legislativo + grupos.
    raw = {"clave": "CD-LXVI-II-2P-091", "anio": "II", "titulo": "X",
           "estatus": "en_revisora", "pdfs": "66/x/02_dictamen.pdf"}
    doc = lm.build_doc(raw, {}, atrib)
    assert doc["origen_tipo"] == "legislativo"
    assert doc["origen"] == "Cámara de Diputados"
    assert doc["grupos_parlamentarios"] == ["PAN"]

    # Una ejecutiva NUNCA se convierte en legislativo ni recibe grupos, aunque
    # (hipotéticamente) apareciera en el mapa de atribución.
    raw_e = {"clave": "CD-LXVI-I-1P-001", "anio": "I", "titulo": "Y",
             "estatus": "publicada_dof", "pdfs": ""}
    cod_e = {"CD-LXVI-I-1P-001": {"origen_tipo": "ejecutivo", "grupos_parlamentarios": ""}}
    doc_e = lm.build_doc(raw_e, cod_e, {"CD-LXVI-I-1P-001": ["PAN"]})
    assert doc_e["origen_tipo"] == "ejecutivo"
    assert doc_e["origen"] == "Ejecutivo Federal"
    assert doc_e["grupos_parlamentarios"] == []


def test_sin_atribucion_queda_por_documentar():
    lm = _load_module()
    atrib = lm.load_atribucion(ATRIB_CSV)
    raw = {"clave": "CD-LXVI-II-1P-050", "anio": "II", "titulo": "Z",
           "estatus": "en_revisora", "pdfs": ""}
    doc = lm.build_doc(raw, {}, atrib)
    assert doc["grupos_parlamentarios"] == []  # UI: "por documentar", jamás inventado


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
    print("Todos los tests de atribución pasaron.")
