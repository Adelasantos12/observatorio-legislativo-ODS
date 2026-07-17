"""Scraper de minutas de la Cámara de Diputados (iniclave) — Huella 2030, módulo B.

Fuente: sistema "iniclave" de la Cámara de Diputados, que publica por año
legislativo un HTML estático (Latin-1) con la relación de minutas de la Cámara
como cámara de origen. Estructura típica: una tabla con cuatro columnas
[número, denominación/asunto, fecha, estatus/turno].

Diseño (igual que `gaceta.py` y `sil_ejecutivo.py`): el parser (`parse_minutas`)
es determinista y sin red; la descarga vive en `fetch_minutas`. `sync_minutas`
orquesta y hace `upsert_preserving_coding` (nunca pisa la codificación ODS ni la
atribución de origen documentadas por la autora).

Atribución de origen (regla no negociable): el scraper NO inventa la bancada de
origen. Si el iniclave no la trae, `origen` queda en `None` y el frontend lo
muestra como "por documentar". El desglose por origen es descriptivo, jamás un
ranking competitivo entre grupos parlamentarios.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# Los años legislativos publican páginas distintas (p. ej. lxvi_1.htm para el
# año I). Se parametriza por legislatura y año.
BASE = "http://sitl.diputados.gob.mx/LXVI_leg/iniclave"

_DATE_RE = re.compile(r"(\d{1,2}/\d{1,2}/\d{4})")

# Detecta el periodo ordinario/extraordinario en el estatus/turno, si aparece.
_PERIODO_RE = re.compile(r"\b(\d)\s*(?:er|do|o)?\.?\s*periodo", re.IGNORECASE)


@dataclass
class MinutaRow:
    numero: int
    denominacion: str
    fecha: str = ""
    estatus: str = ""
    periodo: str = ""

    def as_dict(self):
        return {
            "numero": self.numero,
            "denominacion": self.denominacion,
            "fecha": self.fecha,
            "estatus": self.estatus,
            "periodo": self.periodo,
        }


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _pick_date(text: str) -> str:
    m = _DATE_RE.search(text or "")
    return m.group(1) if m else ""


def _periodo(estatus: str, default: str = "") -> str:
    m = _PERIODO_RE.search(estatus or "")
    return f"{m.group(1)}P" if m else default


def build_url(anio_slug: str) -> str:
    """URL del iniclave para un año legislativo (p. ej. 'lxvi_1' -> año I)."""
    return f"{BASE}/{anio_slug}.htm"


def fetch_minutas(url: str, timeout: int = 60) -> str | None:
    """Descarga una página del iniclave (Latin-1). None si falla."""
    resp = requests.get(url, timeout=timeout)
    if not resp.ok:
        return None
    resp.encoding = "latin-1"
    return resp.text


def parse_minutas(html: str) -> list:
    """Parsea la tabla del iniclave y devuelve filas de minuta.

    Tolerante: toma filas con >=4 celdas cuya primera celda sea un número.
    Columnas esperadas [num, denominación, fecha, estatus].
    """
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    seen = set()
    for tr in soup.find_all("tr"):
        cells = [_clean(td.get_text(" ", strip=True)) for td in tr.find_all(["td", "th"])]
        if len(cells) < 4:
            continue
        num_raw = cells[0].strip().rstrip(".")
        if not num_raw.isdigit():
            continue
        numero = int(num_raw)
        denominacion = cells[1]
        if not denominacion:
            continue
        fecha = _pick_date(cells[2])
        estatus = cells[3]
        if numero in seen:
            continue
        seen.add(numero)
        rows.append(
            MinutaRow(
                numero=numero,
                denominacion=denominacion,
                fecha=fecha,
                estatus=estatus,
                periodo=_periodo(estatus),
            )
        )
    rows.sort(key=lambda r: r.numero)
    return rows


def make_clave(legislatura: str, anio: str, periodo: str, numero: int) -> str:
    """Clave estable de la minuta, p. ej. 'CD-LXVI-II-2P-139'."""
    periodo = periodo or "SP"  # sin periodo identificado
    return f"CD-{legislatura}-{anio}-{periodo}-{numero}"


def to_minuta(row: MinutaRow, legislatura: str, anio: str):
    """Convierte una fila del iniclave en un Minuta sin codificar ni atribuir.

    `origen` se deja en `None` (por documentar): el iniclave no publica la
    bancada de origen y no se infiere.
    """
    from tipi_data.models.minuta import Minuta

    clave = make_clave(legislatura, anio, row.periodo, row.numero)
    return Minuta(
        _id=clave,
        clave=clave,
        legislatura=legislatura,
        anio=anio,
        periodo=row.periodo or None,
        numero=row.numero,
        denominacion=row.denominacion,
        fecha_presentacion=row.fecha or None,
        estatus=row.estatus or None,
        origen=None,
        ods_principal=None,
        ods_secundarios=[],
        tema=None,
        confianza="pendiente",
        metas=[],
        updated_at=datetime.now(timezone.utc),
    )


def _normaliza(texto: str) -> str:
    """Normaliza denominación para comparar (minúsculas, sin puntuación/espacios)."""
    texto = (texto or "").lower()
    texto = re.sub(r"[^a-záéíóúñ0-9 ]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


ORIGEN_EJECUTIVO = "Ejecutivo Federal"


def atribuir_origen(minuta, executive_index):
    """Resuelve el origen de una minuta SIN inventarlo.

    `executive_index`: dict {denominación_normalizada: executive_initiative_dict}.
    Si la denominación de la minuta coincide con una iniciativa del Ejecutivo, el
    origen es "Ejecutivo Federal" y se enlaza el expediente. En cualquier otro
    caso el origen queda como está (típicamente `None` → "por documentar"): la
    bancada solo se asienta cuando hay evidencia documental (dictamen), nunca por
    inferencia. Devuelve (origen, expediente_ref) o (origen_previo, None).
    """
    clave = _normaliza(minuta.get("denominacion") if isinstance(minuta, dict) else minuta.denominacion)
    match = executive_index.get(clave)
    if match:
        return ORIGEN_EJECUTIVO, match.get("id")
    return (minuta.get("origen") if isinstance(minuta, dict) else minuta.origen), None


def build_executive_index(executive_initiatives):
    """Índice denominación_normalizada -> dict de iniciativa del Ejecutivo."""
    index = {}
    for ei in executive_initiatives:
        d = ei if isinstance(ei, dict) else {
            "id": ei.id, "denominacion": ei.denominacion,
            "ods_principal": ei.ods_principal, "ods_secundarios": ei.ods_secundarios,
            "metas": ei.metas, "tema": ei.tema, "confianza": ei.confianza,
        }
        index[_normaliza(d.get("denominacion"))] = d
    return index


def sync_minutas(legislatura: str = "LXVI", anios=None, html_por_anio=None) -> dict:
    """Sincroniza el iniclave con la colección `minutas`.

    `anios`: lista de (anio, anio_slug), p. ej. [("I","lxvi_1"), ("II","lxvi_2")].
    `html_por_anio`: dict {anio: html} para operación offline/pruebas.
    Preserva codificación y atribución de origen ya documentadas.
    """
    from tipi_data.repositories.executive_initiatives import ExecutiveInitiatives
    from tipi_data.repositories.minutas import Minutas

    anios = anios or [("I", "lxvi_1"), ("II", "lxvi_2")]
    html_por_anio = html_por_anio or {}

    # Índice para atribuir origen "Ejecutivo Federal" por coincidencia de
    # denominación (nunca se infiere la bancada de un diputado).
    index = build_executive_index(ExecutiveInitiatives.get_all())

    total = 0
    atribuidas_ejecutivo = 0
    por_anio = {}
    for anio, slug in anios:
        html = html_por_anio.get(anio)
        if html is None:
            html = fetch_minutas(build_url(slug))
        if html is None:
            por_anio[anio] = 0
            continue
        rows = parse_minutas(html)
        for row in rows:
            minuta = to_minuta(row, legislatura, anio)
            origen, expediente_ref = atribuir_origen(minuta, index)
            minuta.origen = origen
            minuta.expediente_ref = expediente_ref
            Minutas.upsert_preserving_coding(minuta)
            if origen == ORIGEN_EJECUTIVO:
                atribuidas_ejecutivo += 1
        por_anio[anio] = len(rows)
        total += len(rows)

    corte = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    Minutas.set_corte(corte)
    return {
        "total": total,
        "por_anio": por_anio,
        "atribuidas_ejecutivo": atribuidas_ejecutivo,
        "corte": corte,
    }
