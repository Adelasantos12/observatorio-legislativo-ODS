"""Atribución por grupo parlamentario desde el dictamen (adenda v3 §A3).

El iniclave no trae al presentador de la minuta. Para las minutas que NO son de
origen Ejecutivo, el dato vive en el PDF del dictamen: su primera sección
enumera las iniciativas dictaminadas con el nombre y el grupo de quien las
presentó. Este job descarga el dictamen, busca los patrones
"iniciativa presentada por … del Grupo Parlamentario de …" y llena
`grupos_parlamentarios`. Donde el parseo no alcanza confianza, deja la lista
vacía y la UI muestra "por documentar". NUNCA se inventa la atribución.

El extractor (`extract_grupos`) es determinista y sin red (testeable con texto
de fixture); la descarga vive en `fetch_pdf_text`. El job (`run_atribucion`) es
incremental: solo toca minutas sin atribución documentada y nunca pisa las
`validado_autora`.
"""

import os
import re
from datetime import datetime, timezone

# Grupos parlamentarios de la LXVI Legislatura (Cámara de Diputados).
GRUPOS_LXVI = {
    "MORENA": r"morena",
    "PAN": r"pan|acci[oó]n nacional",
    "PRI": r"pri|revolucionario institucional",
    "PT": r"pt|del trabajo",
    "PVEM": r"pvem|verde ecologista",
    "MC": r"mc|movimiento ciudadano",
    "PRD": r"prd|de la revoluci[oó]n democr[aá]tica",
}

# "del Grupo Parlamentario de[l] <grupo>" / "(GP <grupo>)".
_GP_RE = re.compile(
    r"grupo\s+parlamentario\s+(?:de[l]?\s+)?(?:partido\s+)?"
    r"([A-Za-zÁÉÍÓÚÑáéíóúñ .]+?)(?:[,.;\)]|\s+(?:present|con|y|que)\b|$)",
    re.IGNORECASE,
)


def normaliza_grupo(texto: str):
    """Mapea un fragmento a la sigla canónica del grupo, o None."""
    t = (texto or "").strip().lower()
    for sigla, pat in GRUPOS_LXVI.items():
        if re.search(rf"\b(?:{pat})\b", t):
            return sigla
    return None


def extract_grupos(text: str):
    """Lista de grupos parlamentarios (siglas) presentes en el texto del dictamen.

    Solo cuenta menciones ligadas a "Grupo Parlamentario"; devuelve el conjunto
    ordenado. Vacío si no se reconoce ninguno (→ "por documentar").
    """
    grupos = set()
    for m in _GP_RE.finditer(text or ""):
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
    base = base_url or os.environ.get(
        "INICLAVE_PDF_BASE", "https://gaceta.diputados.gob.mx/PDF/Minutas")
    path = path.lstrip("/")
    return f"{base.rstrip('/')}/{path}"


def fetch_pdf_text(url: str, timeout: int = 60):
    """Descarga un PDF y extrae su texto (None si falla)."""
    import requests
    from pdfminer.high_level import extract_text
    from io import BytesIO

    resp = requests.get(url, timeout=timeout)
    if not resp.ok:
        return None
    try:
        return extract_text(BytesIO(resp.content))
    except Exception:
        return None


def run_atribucion(base_url: str | None = None, limit: int | None = None,
                   fetch=fetch_pdf_text) -> dict:
    """Job incremental: atribuye grupos a minutas sin origen documentado.

    Solo procesa minutas cuyo `origen_tipo` no sea "ejecutivo", con
    `grupos_parlamentarios` vacío y que no estén `validado_autora`. Marca cada
    intento con `updated_at`; deja vacío lo que no se pudo parsear.
    """
    from tipi_data import db

    query = {
        "origen_tipo": {"$ne": "ejecutivo"},
        "nivel_revision": {"$ne": "validado_autora"},
        "$or": [{"grupos_parlamentarios": {"$exists": False}},
                {"grupos_parlamentarios": []}],
    }
    cursor = db.minutas.find(query).sort("numero", 1)
    if limit:
        cursor = cursor.limit(limit)

    procesadas, atribuidas, sin_dictamen = 0, 0, 0
    for minuta in cursor:
        procesadas += 1
        pdf = dictamen_pdf(minuta)
        if not pdf:
            sin_dictamen += 1
            continue
        text = fetch(pdf_url(pdf, base_url))
        grupos = extract_grupos(text) if text else []
        update = {"updated_at": datetime.now(timezone.utc)}
        if grupos:
            update["grupos_parlamentarios"] = grupos
            update["origen_tipo"] = "legislativo"
            atribuidas += 1
        db.minutas.update_one({"_id": minuta["_id"]}, {"$set": update})

    return {
        "procesadas": procesadas,
        "atribuidas": atribuidas,
        "sin_dictamen": sin_dictamen,
        "por_documentar": procesadas - atribuidas,
    }
