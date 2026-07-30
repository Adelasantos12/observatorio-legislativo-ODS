"""Regresión: el escáner debe etiquetar un archivo subido igual que el mismo
texto pegado. El bug: con la firma `file: UploadFile | str | None`, FastAPI
construye el archivo como starlette.UploadFile, que no pasa
`isinstance(file, fastapi.UploadFile)`, así que el endpoint ignoraba TODO
archivo y devolvía "sin coincidencias". Ver tagger.py::extract."""

import io
import pytest
from tests.helpers import build_tags_from_fixture, load_knowledgebase, read_scanner_text

pytestmark = pytest.mark.unit


@pytest.fixture(scope="session")
def kb_tags():
    return build_tags_from_fixture(load_knowledgebase())


@pytest.fixture(autouse=True)
def _inject(monkeypatch, kb_tags):
    monkeypatch.setattr("tipi_backend.api.cache.get", lambda key: kb_tags)


def test_archivo_txt_etiqueta_igual_que_texto(client):
    """Subir un .txt con el mismo contenido debe dar los mismos topics que pegarlo."""
    text = read_scanner_text("w500.txt")

    r_text = client.post("/tagger/", data={"text": text, "knowledgebase": "politicas,ods"})
    topics_text = set(r_text.json()["result"]["topics"])

    r_file = client.post(
        "/tagger/",
        data={"text": "", "knowledgebase": "politicas,ods"},
        files={"file": ("p.txt", io.BytesIO(text.encode()), "text/plain")},
    )
    assert r_file.status_code == 200
    topics_file = set(r_file.json()["result"]["topics"])

    assert topics_file, "el archivo subido no produjo ningún topic (bug del isinstance)"
    assert topics_file == topics_text
