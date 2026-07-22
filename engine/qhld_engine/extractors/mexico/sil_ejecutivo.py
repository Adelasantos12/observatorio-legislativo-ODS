"""Scraper del SIL para iniciativas del Ejecutivo Federal (Huella 2030, fase H).

Fuente: Sistema de Información Legislativa (SIL) de la Secretaría de Gobernación.
El SIL publica el estado procesal de cada iniciativa presentada por el Ejecutivo
Federal en la legislatura vigente. Este módulo alimenta la colección
`executive_initiatives` (Módulo A de la Huella 2030), **sin** tocar el motor de
etiquetado ni la colección de iniciativas del escáner de texto.

Diseño (igual que `gaceta.py`): el parser (`parse_sil`) es determinista y sin red
—recibe el HTML ya descargado— para poder probarse con fixtures; la descarga vive
en `fetch_sil` (aislada). `sync_sil_ejecutivo` orquesta: descarga → parsea →
`upsert_preserving_coding` (nunca pisa la codificación ODS de la autora).

La **sección** de cada iniciativa se deriva de su estatus procesal, de modo que
el corte reproduce el desglose del piloto (Aprobadas/Pendientes/Desechadas/
Retiradas). La codificación (`ods_*`, `metas`, `tema`, `confianza`) NO viene del
SIL: la aporta la autora y se preserva entre sincronizaciones.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# Página de resultados del SIL filtrada por "origen = Ejecutivo Federal" en la
# legislatura vigente. Se parametriza por legislatura para no fijar la actual.
BASE = "http://sil.gobernacion.gob.mx/Busquedas/Avanzada/ResultadosBusquedaAvanzada.php"

# Las cuatro secciones del tablero de la Huella, derivadas del estatus del SIL.
SECCION_APROBADAS = "Aprobadas y/o publicadas en DOF"
SECCION_PENDIENTES = "Pendientes en Comisiones"
SECCION_DESECHADAS = "Desechadas"
SECCION_RETIRADAS = "Retiradas"

# Orden estable para el reporte (reproduce el desglose del piloto: 76/4/1/1).
SECCIONES = (
    SECCION_APROBADAS,
    SECCION_PENDIENTES,
    SECCION_DESECHADAS,
    SECCION_RETIRADAS,
)

# Fecha en formato dd/mm/aaaa dentro del texto de estatus.
_DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")


@dataclass
class SilInitiative:
    """Registro de fuente del SIL (sin codificación ODS)."""

    num: int
    denominacion: str
    fecha_presentacion: str = ""
    estatus: str = ""
    seccion: str = ""
    fecha_dof: str = ""

    def as_dict(self):
        return {
            "num": self.num,
            "denominacion": self.denominacion,
            "fecha_presentacion": self.fecha_presentacion,
            "estatus": self.estatus,
            "seccion": self.seccion,
            "fecha_dof": self.fecha_dof,
        }


def clasificar_seccion(estatus: str) -> str:
    """Deriva la sección del tablero a partir del estatus procesal del SIL.

    El estatus del SIL usa frases estables como "Publicado en DOF el ...",
    "Pendiente en comisión(es) ...", "Desechado en pleno ...", "Retirada el ...".
    """
    e = (estatus or "").lower()
    if "dof" in e or "publicad" in e:
        return SECCION_APROBADAS
    if "pendiente" in e or "comisi" in e:
        return SECCION_PENDIENTES
    if "desechad" in e:
        return SECCION_DESECHADAS
    if "retirad" in e:
        return SECCION_RETIRADAS
    # Por defecto, cae en pendientes: nunca se descarta un registro silenciosamente.
    return SECCION_PENDIENTES


def _fecha_dof(estatus: str) -> str:
    """Extrae la fecha DOF del estatus cuando la iniciativa fue publicada."""
    e = (estatus or "").lower()
    if "dof" not in e and "publicad" not in e:
        return ""
    m = _DATE_RE.search(estatus or "")
    return m.group(1) if m else ""


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def parse_sil(html: str) -> list:
    """Parsea la tabla de resultados del SIL y devuelve la lista de iniciativas.

    Estrategia tolerante: busca filas con al menos cuatro celdas donde la primera
    sea un número consecutivo (num). Columnas esperadas:
    [num, denominación, fecha de presentación, estatus]. Filas de encabezado o
    sin número se ignoran.
    """
    soup = BeautifulSoup(html, "html.parser")
    initiatives = []
    seen = set()
    for tr in soup.find_all("tr"):
        cells = [_clean(td.get_text(" ", strip=True)) for td in tr.find_all(["td", "th"])]
        if len(cells) < 4:
            continue
        num_raw = cells[0].strip().rstrip(".")
        if not num_raw.isdigit():
            continue
        num = int(num_raw)
        denominacion = cells[1]
        if not denominacion:
            continue
        fecha_pres = _pick_date(cells[2])
        estatus = cells[3]
        # Algunas plantillas del SIL ponen la fecha de presentación y el estatus
        # invertidos; si la col 2 no es fecha pero la 3 sí, se intercambian.
        if not fecha_pres and _DATE_RE.search(cells[3] or ""):
            fecha_pres, estatus = _pick_date(cells[3]), cells[2]
        seccion = clasificar_seccion(estatus)
        key = (num, denominacion)
        if key in seen:
            continue
        seen.add(key)
        initiatives.append(
            SilInitiative(
                num=num,
                denominacion=denominacion,
                fecha_presentacion=fecha_pres,
                estatus=estatus,
                seccion=seccion,
                fecha_dof=_fecha_dof(estatus),
            )
        )
    initiatives.sort(key=lambda i: i.num)
    return initiatives


def _pick_date(text: str) -> str:
    m = _DATE_RE.search(text or "")
    return m.group(1) if m else ""


def build_url(legislatura: str) -> str:
    """URL de resultados del SIL para el origen Ejecutivo Federal y legislatura."""
    # Origen 1 = Ejecutivo Federal en el catálogo del SIL.
    return f"{BASE}?SID=&Origen=1&Legislatura={legislatura}"


def fetch_sil(url: str, timeout: int = 60) -> str | None:
    """Descarga una página de resultados del SIL. Devuelve None si falla."""
    resp = requests.get(url, timeout=timeout)
    if not resp.ok:
        return None
    # El SIL sirve en ISO-8859-1; forzamos para no romper acentos.
    resp.encoding = resp.encoding or "latin-1"
    return resp.text


def to_executive_initiative(sil: SilInitiative):
    """Convierte un registro del SIL en un ExecutiveInitiative sin codificar.

    La codificación se deja en `None`/vacío y `confianza="pendiente"`: el
    `upsert_preserving_coding` conservará la codificación previa si existe.
    """
    from tipi_data.models.executive_initiative import ExecutiveInitiative
    from tipi_data.utils import generate_slug

    _id = f"EJE-2024-2030-{sil.num}-{generate_slug(sil.seccion)}"
    return ExecutiveInitiative(
        _id=_id,
        seccion=sil.seccion,
        num=sil.num,
        denominacion=sil.denominacion,
        fecha_presentacion=sil.fecha_presentacion or None,
        fecha_dof=sil.fecha_dof or None,
        estatus=sil.estatus or None,
        ods_principal=None,
        ods_secundarios=[],
        tema=None,
        confianza="pendiente",
        metas=[],
        updated_at=datetime.now(timezone.utc),
    )


def sync_sil_ejecutivo(legislatura: str = "66", html: str | None = None) -> dict:
    """Sincroniza el SIL con la colección `executive_initiatives`.

    Descarga (o recibe `html` para pruebas), parsea, hace upsert preservando la
    codificación y actualiza la fecha de corte. Devuelve el desglose por sección.
    """
    from tipi_data.repositories.executive_initiatives import ExecutiveInitiatives

    if html is None:
        url = build_url(legislatura)
        html = fetch_sil(url)
        if html is None:
            raise RuntimeError(f"No se pudo descargar el SIL: {url}")

    inits = parse_sil(html)
    conteo = {s: 0 for s in SECCIONES}
    for sil in inits:
        ExecutiveInitiatives.upsert_preserving_coding(to_executive_initiative(sil))
        conteo[sil.seccion] = conteo.get(sil.seccion, 0) + 1

    corte = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ExecutiveInitiatives.set_corte(corte)
    return {"total": len(inits), "por_seccion": conteo, "corte": corte}
