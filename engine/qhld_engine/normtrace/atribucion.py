"""Atribución por grupo parlamentario desde el dictamen (adenda v3 §A3 + v4.1).

El iniclave no trae al presentador de la minuta. Para las minutas que NO son de
origen Ejecutivo, el dato vive en el PDF del dictamen: su sección de antecedentes
enumera las iniciativas dictaminadas con el nombre y el grupo de quien las
presentó. Este job descarga el dictamen, lo lee y llena `grupos_parlamentarios`.
Donde el parseo no alcanza confianza, deja la lista vacía y la UI muestra
"por documentar". NUNCA se inventa la atribución.

IMPORTANTE (verificado con descargas reales): los dictámenes son **escaneos sin
capa de texto**, así que hay que hacer **OCR** (pytesseract + pdf2image, lang
`spa`, 200 dpi, primeras páginas). Sin OCR, la extracción devuelve cero. La
imagen del engine ya trae `tesseract-ocr`, `tesseract-ocr-spa` y `poppler-utils`.

Base de los PDFs (verificada): `https://www.diputados.gob.mx/LeyesBiblio/iniclave/`
+ `66/{CLAVE}/{archivo}.pdf`. Configurable con `INICLAVE_PDF_BASE`.
"""

import os
import re
from datetime import datetime, timezone

# Base real de los PDFs del iniclave (LeyesBiblio). Ruta = {base}66/{CLAVE}/{archivo}.
DEFAULT_PDF_BASE = "https://www.diputados.gob.mx/LeyesBiblio/iniclave/"

# Grupos parlamentarios de la LXVI: sigla canónica -> patrón (sigla o nombre).
GRUPOS_LXVI = [
    ("MORENA", r"morena"),
    ("PAN", r"pan|acci[oó]n nacional"),
    ("PRI", r"pri|revolucionario institucional"),
    ("PT", r"pt|del trabajo"),
    ("PVEM", r"pvem|verde ecologista(?:\s+de\s+m[eé]xico)?"),
    ("MC", r"mc|movimiento ciudadano"),
    ("PRD", r"prd|de la revoluci[oó]n democr[aá]tica"),
]

# "Grupo Parlamentario (del|de la|de) <grupo>" — la firma de autoría en el dictamen.
_GP_RE = re.compile(
    r"grupo\s+parlamentario\s+(?:de[l]?\s+|de\s+la\s+)?(?:partido\s+)?("
    + "|".join(p for _, p in GRUPOS_LXVI)
    + r")\b",
    re.IGNORECASE,
)


def normaliza_grupo(texto: str):
    """Mapea un fragmento a la sigla canónica del grupo, o None."""
    t = (texto or "").strip().lower()
    for sigla, pat in GRUPOS_LXVI:
        if re.search(rf"\b(?:{pat})\b", t):
            return sigla
    return None


def extract_grupos(text: str):
    """Grupos parlamentarios (siglas) presentes en el dictamen.

    Normaliza el whitespace (el OCR mete saltos de línea), busca las menciones de
    "Grupo Parlamentario del X" y devuelve las siglas únicas ordenadas. Un dictamen
    puede consolidar varias iniciativas: se juntan todos los grupos. Vacío si no se
    reconoce ninguno (→ "por documentar").
    """
    norm = re.sub(r"\s+", " ", text or "")
    grupos = set()
    for m in _GP_RE.finditer(norm):
        sigla = normaliza_grupo(m.group(1))
        if sigla:
            grupos.add(sigla)
    return sorted(grupos)


def dictamen_pdf(minuta: dict):
    """Ruta del PDF de dictamen entre los `pdfs` de la minuta, o None."""
    for p in (minuta.get("pdfs") or []):
        if "dictamen" in p.lower():
            return p
    return None


def pdf_url(path: str, base_url: str | None = None):
    """URL completa del PDF. Base termina en `/iniclave/`; si la ruta ya trae
    `iniclave/` al inicio (los href del año en curso), se quita para no duplicar."""
    base = base_url or os.environ.get("INICLAVE_PDF_BASE", DEFAULT_PDF_BASE)
    p = (path or "").lstrip("/")
    if p.lower().startswith("iniclave/"):
        p = p[len("iniclave/"):]
    return base.rstrip("/") + "/" + p


def ocr_pdf_bytes(content: bytes, pages: int | None = None, dpi: int | None = None):
    """OCR de las primeras páginas de un PDF (escaneo sin capa de texto)."""
    from pdf2image import convert_from_bytes
    import pytesseract

    pages = pages or int(os.environ.get("NORMTRACE_OCR_PAGES", "3"))
    dpi = dpi or int(os.environ.get("NORMTRACE_OCR_DPI", "200"))
    try:
        imgs = convert_from_bytes(content, dpi=dpi, first_page=1, last_page=pages)
    except Exception:
        return None
    out = []
    for img in imgs:
        try:
            out.append(pytesseract.image_to_string(img, lang="spa"))
        except Exception:
            continue
    return "\n".join(out) if out else None


def ocr_pdf_text(url: str, timeout: int | None = None):
    """Descarga un dictamen y devuelve su texto por OCR (None si falla o tarda)."""
    import requests

    timeout = timeout or int(os.environ.get("NORMTRACE_HTTP_TIMEOUT", "45"))
    try:
        resp = requests.get(url, timeout=timeout)
    except Exception:
        return None
    if not resp.ok:
        return None
    return ocr_pdf_bytes(resp.content)


def run_atribucion(base_url: str | None = None, limit: int | None = None,
                   fetch=None) -> dict:
    """Job incremental: atribuye grupos a minutas sin origen documentado.

    Solo procesa minutas cuyo `origen_tipo` no sea "ejecutivo", con
    `grupos_parlamentarios` vacío y que no estén `validado_autora`. Descarga y
    hace OCR del dictamen; deja vacío lo que no se pudo parsear (por documentar).
    """
    from tipi_data import db

    fetch = fetch or ocr_pdf_text
    query = {
        "origen_tipo": {"$ne": "ejecutivo"},
        "nivel_revision": {"$ne": "validado_autora"},
        "$or": [{"grupos_parlamentarios": {"$exists": False}},
                {"grupos_parlamentarios": []}],
    }
    # Materializa la lista para poder mostrar progreso "i/N" (el conjunto es chico).
    minutas = list(db.minutas.find(query).sort("numero", 1))
    if limit:
        minutas = minutas[:limit]
    total = len(minutas)
    print(f"Atribución: {total} minutas por procesar (OCR de dictámenes)…", flush=True)

    procesadas, atribuidas, sin_dictamen = 0, 0, 0
    for minuta in minutas:
        procesadas += 1
        clave = minuta.get("_id")
        pdf = dictamen_pdf(minuta)
        if not pdf:
            sin_dictamen += 1
            print(f"  [{procesadas}/{total}] {clave}: sin dictamen", flush=True)
            continue
        text = fetch(pdf_url(pdf, base_url))
        grupos = extract_grupos(text) if text else []
        update = {"updated_at": datetime.now(timezone.utc)}
        if grupos:
            update["grupos_parlamentarios"] = grupos
            update["origen_tipo"] = "legislativo"
            atribuidas += 1
        db.minutas.update_one({"_id": minuta["_id"]}, {"$set": update})
        print(f"  [{procesadas}/{total}] {clave}: {', '.join(grupos) if grupos else 'por documentar'}",
              flush=True)

    return {
        "procesadas": procesadas,
        "atribuidas": atribuidas,
        "sin_dictamen": sin_dictamen,
        "por_documentar": procesadas - atribuidas,
    }
