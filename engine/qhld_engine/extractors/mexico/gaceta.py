"""Parser de la Gaceta Parlamentaria de la Cámara de Diputados (México).

Spec (docs/ARCHITECTURE.md §4): HTML estático en gaceta.diputados.gob.mx, con
URLs predecibles `/Gaceta/{legislatura}/{año}/{mes}/{YYYYMMDD}[-anexo].html`,
un índice con anclas `a.Indice` que apuntan a `#IniciativaN`, y el texto completo
de cada iniciativa inline. Codificación Latin-1. Autor/partido/materia vienen en
el string del título y se parsean con regex.

Este módulo es determinista y sin red: `parse_gaceta(html)` recibe el HTML ya
descargado. La descarga vive en `fetch_gaceta()` (aislada para poder testear el
parser con fixtures).
"""

import re
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

# Abreviaturas de mes usadas en las rutas de la Gaceta (p. ej. .../2026/jul/...).
MONTHS_ES = [
    "ene", "feb", "mar", "abr", "may", "jun",
    "jul", "ago", "sep", "oct", "nov", "dic",
]

BASE = "https://gaceta.diputados.gob.mx/Gaceta"

# Ancla de iniciativa: "Iniciativa1", "Iniciativa12"...
_ANCHOR_RE = re.compile(r"^Iniciativa\d+$", re.IGNORECASE)

# "... a cargo de la diputada Fulana de Tal, del Grupo Parlamentario Morena"
_AUTHOR_RE = re.compile(
    r"a cargo de(?:l| la)?\s+(?:la|el)?\s*"
    r"(?:diputad[oa]s?|senador[ao]s?)?\s*(.+?)"
    r"(?:,?\s+del?\s+Grupo Parlamentario\s+(.+?))?"
    r"(?:\.|;|$)",
    re.IGNORECASE,
)


@dataclass
class GacetaInitiative:
    ref: str                       # ancla, p. ej. "Iniciativa3"
    title: str                     # título completo (del índice)
    author: str = ""
    party: str = ""
    content: list = field(default_factory=list)  # oraciones del texto inline

    def as_dict(self):
        return {
            "ref": self.ref,
            "title": self.title,
            "author": self.author,
            "party": self.party,
            "content": self.content,
        }


def build_url(date_yyyymmdd: str, legislatura: str, anexo: str | None = None) -> str:
    """Construye la URL de la Gaceta para una fecha (YYYYMMDD) y legislatura.

    Ej.: build_url("20260716", "66", "I")
      -> https://gaceta.diputados.gob.mx/Gaceta/66/2026/jul/20260716-I.html
    """
    year = date_yyyymmdd[0:4]
    month = MONTHS_ES[int(date_yyyymmdd[4:6]) - 1]
    name = f"{date_yyyymmdd}-{anexo}.html" if anexo else f"{date_yyyymmdd}.html"
    return f"{BASE}/{legislatura}/{year}/{month}/{name}"


def parse_title(title: str) -> tuple[str, str]:
    """Extrae (autor, partido) del string del título de una iniciativa."""
    m = _AUTHOR_RE.search(title or "")
    if not m:
        return "", ""
    author = (m.group(1) or "").strip(" .,")
    party = (m.group(2) or "").strip(" .,")
    return author, party


def _split_sentences(text: str) -> list:
    text = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in re.split(r"\.(?!\d)", text) if s.strip()]


def parse_gaceta(html: str) -> list:
    """Parsea el HTML de una Gaceta y devuelve la lista de iniciativas.

    Estrategia: el índice (`a.Indice`) aporta el título completo (con autor y
    partido) y el ancla destino `#IniciativaN`; el cuerpo se recoge desde cada
    ancla `<a name="IniciativaN">` hasta la siguiente.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Título por ancla, tomado del índice.
    titles = {}
    order = []
    for a in soup.select("a.Indice"):
        href = a.get("href", "")
        if href.startswith("#") and _ANCHOR_RE.match(href[1:]):
            ref = href[1:]
            titles[ref] = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
            if ref not in order:
                order.append(ref)

    # Anclas de cuerpo, en orden de aparición en el documento.
    body_anchors = [
        a for a in soup.find_all("a")
        if (a.get("name") and _ANCHOR_RE.match(a.get("name")))
        or (a.get("id") and _ANCHOR_RE.match(a.get("id")))
    ]
    anchor_names = [a.get("name") or a.get("id") for a in body_anchors]

    initiatives = []
    for i, anchor in enumerate(body_anchors):
        ref = anchor_names[i]
        stop = set(anchor_names[i + 1:])
        # Recoge el texto desde esta ancla hasta la siguiente ancla de iniciativa.
        chunks = []
        for el in anchor.next_elements:
            name = getattr(el, "get", lambda *_: None)("name") if hasattr(el, "get") else None
            an_id = getattr(el, "get", lambda *_: None)("id") if hasattr(el, "get") else None
            if (name in stop) or (an_id in stop):
                break
            if isinstance(el, str):
                chunks.append(el)
        body_text = " ".join(chunks)
        title = titles.get(ref, "")
        # Si no hubo índice, usa la primera oración del cuerpo como título.
        sentences = _split_sentences(body_text)
        if not title and sentences:
            title = sentences[0]
        author, party = parse_title(title)
        initiatives.append(
            GacetaInitiative(
                ref=ref, title=title, author=author, party=party, content=sentences
            )
        )

    # Preserva el orden del índice cuando exista.
    if order:
        by_ref = {ini.ref: ini for ini in initiatives}
        ordered = [by_ref[r] for r in order if r in by_ref]
        extras = [ini for ini in initiatives if ini.ref not in set(order)]
        return ordered + extras
    return initiatives


def fetch_gaceta(url: str, timeout: int = 30) -> str | None:
    """Descarga una Gaceta (Latin-1). Devuelve None si no existe (404) o falla."""
    resp = requests.get(url, timeout=timeout)
    if not resp.ok:
        return None
    resp.encoding = "latin-1"
    return resp.text
