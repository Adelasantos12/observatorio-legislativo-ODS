"""Extracción de texto robusta del escáner — que "funcione siempre" con
cualquier PDF (con texto, escaneado o foto) y con imágenes sueltas.

Dos capas de prueba:

* **Sin OCR** (siempre corren): detección de tipo por firma binaria
  (`_sniff_kind`), umbral de "texto pobre" (`_looks_thin`), decodificación de
  .txt tolerante (`_decode_text`).
* **Con OCR real** (corren donde hay `tesseract`+`poppler`; si no, se saltan):
  una foto (PNG) y un PDF escaneado (imagen sin capa de texto) se generan al
  vuelo y deben devolver su texto. Prueba de verdad el camino foto/escáner.

Los binarios de OCR van en la imagen Docker del api; en un entorno sin ellos
estas pruebas se saltan en vez de fallar.
"""

import io
import shutil

import pytest

from fastapi import HTTPException

from tipi_backend.api.endpoints import tagger

pytestmark = pytest.mark.unit

HAS_OCR = shutil.which("tesseract") is not None and shutil.which("pdftoppm") is not None
PIL = pytest.importorskip("PIL") if False else None  # import perezoso abajo


class _FakeUpload:
    """UploadFile mínimo para `_extract_text_from_file` (sin FastAPI)."""

    def __init__(self, content: bytes, content_type: str, filename: str):
        self.file = io.BytesIO(content)
        self.content_type = content_type
        self.filename = filename


# --- Fixtures generadas al vuelo (una imagen/PDF con texto legible) ---------

_TEXTO = "La presente ley regula el cambio climatico y la salud publica en Mexico"


def _text_image_png() -> bytes:
    """Una "foto" nítida con texto negro sobre blanco (PNG)."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (1400, 220), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 46)
    except OSError:
        font = ImageFont.load_default()
    draw.text((30, 80), _TEXTO, font=font, fill="black")
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _scanned_pdf() -> bytes:
    """Un PDF "escaneado": una sola imagen, sin capa de texto seleccionable."""
    from PIL import Image

    img = Image.open(io.BytesIO(_text_image_png())).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=150.0)
    return buf.getvalue()


# ============================ Sin OCR (siempre) =============================

def test_sniff_pdf_por_firma_aunque_el_content_type_mienta():
    # Un PDF subido como 'application/octet-stream' y sin extensión: la firma
    # %PDF manda. Antes esto caía en "Formato no soportado".
    assert tagger._sniff_kind(b"%PDF-1.7\n%...", "documento", "application/octet-stream") == "pdf"
    assert tagger._sniff_kind(b"%PDF-1.4", "x.pdf", "") == "pdf"


def test_sniff_imagenes_por_firma():
    assert tagger._sniff_kind(b"\xff\xd8\xff\xe0", "foto", "application/octet-stream") == "image"   # jpeg
    assert tagger._sniff_kind(b"\x89PNG\r\n\x1a\n", "captura", "") == "image"                       # png
    assert tagger._sniff_kind(b"II*\x00", "escaneo.tif", "") == "image"                             # tiff


def test_sniff_office_y_texto():
    assert tagger._sniff_kind(b"PK\x03\x04", "informe.docx", "") == "docx"
    assert tagger._sniff_kind(b"PK\x03\x04", "diapos.pptx", "") == "pptx"
    assert tagger._sniff_kind(b"texto plano", "notas.txt", "text/plain") == "txt"


def test_sniff_desconocido():
    assert tagger._sniff_kind(b"\x00\x01\x02\x03", "raro.bin", "application/octet-stream") == "unknown"


def test_looks_thin_distingue_ruido_de_texto():
    assert tagger._looks_thin("") is True
    assert tagger._looks_thin("1 2 3 \x0c 4") is True          # números/artefactos, sin palabras
    assert tagger._looks_thin("Ley del cambio climatico y salud publica nacional") is False


def test_decode_text_tolera_codificaciones():
    assert tagger._decode_text("energía y salud".encode("utf-8")) == "energía y salud"
    assert tagger._decode_text("energía y salud".encode("cp1252")) == "energía y salud"


def test_formato_no_soportado_da_400():
    up = _FakeUpload(b"\x00\x01\x02\x03 binario random", "application/octet-stream", "cosa.bin")
    with pytest.raises(HTTPException) as exc:
        tagger._extract_text_from_file(up)
    assert exc.value.status_code == 400


def test_txt_se_lee_directo():
    up = _FakeUpload("cambio climático y salud".encode("utf-8"), "text/plain", "n.txt")
    assert "cambio" in tagger._extract_text_from_file(up)


# ============================ Con OCR real =================================

@pytest.mark.skipif(not HAS_OCR, reason="requiere tesseract + poppler")
def test_foto_png_se_lee_por_ocr():
    pytest.importorskip("PIL")
    up = _FakeUpload(_text_image_png(), "image/png", "foto.png")
    text = tagger._extract_text_from_file(up)
    assert "cambio" in text.lower() and "salud" in text.lower()


@pytest.mark.skipif(not HAS_OCR, reason="requiere tesseract + poppler")
def test_foto_sin_extension_ni_content_type_se_detecta_y_lee():
    # Caso móvil: blob de cámara sin nombre ni tipo. La firma PNG basta.
    pytest.importorskip("PIL")
    up = _FakeUpload(_text_image_png(), "", "")
    text = tagger._extract_text_from_file(up)
    assert "salud" in text.lower()


@pytest.mark.skipif(not HAS_OCR, reason="requiere tesseract + poppler")
def test_pdf_escaneado_cae_a_ocr_de_verdad():
    pytest.importorskip("PIL")
    up = _FakeUpload(_scanned_pdf(), "application/pdf", "escaneo.pdf")
    text = tagger._extract_text_from_file(up)
    assert "cambio" in text.lower() and "salud" in text.lower()


@pytest.mark.skipif(not HAS_OCR, reason="requiere tesseract + poppler")
def test_pdf_escaneado_como_octet_stream_se_detecta_por_firma():
    # PDF válido pero subido como 'octet-stream' y sin extensión: %PDF manda,
    # y al ser escaneado, OCR lo lee. Antes: "Formato no soportado".
    pytest.importorskip("PIL")
    up = _FakeUpload(_scanned_pdf(), "application/octet-stream", "documento")
    text = tagger._extract_text_from_file(up)
    assert "salud" in text.lower()
