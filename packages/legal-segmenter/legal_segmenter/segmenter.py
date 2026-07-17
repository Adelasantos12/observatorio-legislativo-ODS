"""Segmentador determinista de estructura legislativa mexicana.

Convierte un texto legislativo (markdown extraído o texto plano) en una lista de
unidades citables `{unit_id, unit_type, number, heading, text, parent_id}`, según
`normtrace/02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md`
(§2 estructura, §3 citas).

Maneja: Libro, Título, Capítulo, Sección, Artículo (incl. "Bis/Ter/Quáter" y
numeración ordinal "3o."), Fracción (romanos, incl. "IV Bis 1"), Inciso
(minúsculas), Apartado (A./B.), Artículos Transitorios, y texto no estructurado
(fallback a párrafos).

Invariante de preservación: cada línea del documento se asigna a exactamente una
unidad, de modo que la concatenación de los textos de las unidades reproduce el
documento original íntegro.

Sin dependencias externas: solo la librería estándar.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict

__all__ = ["Unit", "segment", "segment_to_dicts"]


@dataclass
class Unit:
    unit_id: str
    unit_type: str
    number: str | None
    heading: str
    text: str
    parent_id: str | None

    def as_dict(self) -> dict:
        return asdict(self)


# --- Romanos -----------------------------------------------------------------

_ROMAN_PAIRS = [
    (1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"),
    (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
    (5, "V"), (4, "IV"), (1, "I"),
]


def _int_to_roman(n: int) -> str:
    out = []
    for value, sym in _ROMAN_PAIRS:
        while n >= value:
            out.append(sym)
            n -= value
    return "".join(out)


def _roman_to_int(s: str) -> int | None:
    s = s.upper()
    if not s or any(c not in "IVXLCDM" for c in s):
        return None
    values = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    total, prev = 0, 0
    for c in reversed(s):
        v = values[c]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def _is_canonical_roman(s: str) -> bool:
    """True si `s` es un romano válido y canónico (p. ej. 'IV' sí, 'IIII' no)."""
    n = _roman_to_int(s)
    return n is not None and n > 0 and _int_to_roman(n) == s.upper()


# --- Ordinales en español ----------------------------------------------------

_ORDINALS = {
    "primero": 1, "primera": 1, "segundo": 2, "segunda": 2, "tercero": 3,
    "tercera": 3, "cuarto": 4, "cuarta": 4, "quinto": 5, "quinta": 5,
    "sexto": 6, "sexta": 6, "septimo": 7, "séptimo": 7, "septima": 7,
    "octavo": 8, "octava": 8, "noveno": 9, "novena": 9, "decimo": 10,
    "décimo": 10, "decima": 10, "undecimo": 11, "undécimo": 11,
    "duodecimo": 12, "duodécimo": 12, "decimotercero": 13, "decimocuarto": 14,
    "decimoquinto": 15, "decimosexto": 16, "decimoseptimo": 17,
    "decimoctavo": 18, "decimonoveno": 19, "vigesimo": 20, "vigésimo": 20,
}


_ACCENTS = str.maketrans("áéíóúüñÁÉÍÓÚÜÑ", "aeiouunAEIOUUN")


def _unaccent(s: str) -> str:
    return s.translate(_ACCENTS)


def _norm_container_number(raw: str) -> str:
    """Normaliza el número de un contenedor (título/capítulo/…) a un token id."""
    tok = _unaccent(raw.strip().lower())
    if tok in ("unico", "único"):
        return "unico"
    if tok in _ORDINALS:
        return str(_ORDINALS[tok])
    if _is_canonical_roman(tok.upper()):
        return str(_roman_to_int(tok.upper()))
    m = re.match(r"^(\d+)", tok)
    if m:
        return m.group(1)
    return re.sub(r"[^a-z0-9]+", "-", tok).strip("-") or "s-n"


def _norm_article_number(raw: str) -> str:
    """'166 Bis 17.' -> '166bis17'; '3o.' -> '3'; '51 Bis 1' -> '51bis1'."""
    tok = _unaccent(raw.strip().rstrip(".-–").lower())
    tok = re.sub(r"(\d+)[oa]\b", r"\1", tok)  # 3o -> 3
    tok = re.sub(r"\s+", "", tok)
    return re.sub(r"[^a-z0-9]", "", tok)


def _norm_fraccion_number(raw: str) -> str:
    """'IV Bis 1' -> 'IVbis1'; 'XII Quater' -> 'XIIquater'."""
    tok = raw.strip().rstrip(".-–)")
    parts = tok.split()
    if not parts:
        return "s-n"
    out = parts[0].upper()
    for p in parts[1:]:
        out += p.lower()
    return re.sub(r"[^A-Za-z0-9]", "", out)


# --- Patrones de línea -------------------------------------------------------

_MD_HEADING = re.compile(r"^\s*(#{1,6})\s*(.*)$")

_NUM_AFTER = r"(?:PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]PTIMO|OCTAVO|NOVENO|D[EÉ]CIMO\w*|UND[EÉ]CIMO|DUOD[EÉ]CIMO|VIG[EÉ]SIMO\w*|[UÚ]NICO|[IVXLCDM]+|\d+)"

_RE_LIBRO = re.compile(rf"^LIBRO\s+({_NUM_AFTER})\b", re.IGNORECASE)
_RE_TITULO = re.compile(rf"^T[IÍ]TULO\s+({_NUM_AFTER})\b", re.IGNORECASE)
_RE_CAPITULO = re.compile(rf"^CAP[IÍ]TULO\s+({_NUM_AFTER})\b", re.IGNORECASE)
_RE_SECCION = re.compile(rf"^SECCI[OÓ]N\s+({_NUM_AFTER})\b", re.IGNORECASE)

# Encabezado de bloque de transitorios.
_RE_TRANSITORIOS = re.compile(
    r"^(ART[IÍ]CULOS?\s+)?TRANSITORIO(S)?(\s+DE\s+.*)?$", re.IGNORECASE
)

# Artículo: número + posibles sufijos Bis/Ter/Quáter/Quinquies (con índice).
_RE_ARTICULO = re.compile(
    r"^Art[ií]culo\s+"
    r"(\d+(?:[oOaA])?"
    r"(?:\s+(?:Bis|Ter|Qu[aá]ter|Quinquies)(?:\s+\d+)?)*"
    r")\s*[.\-–]",
)

# Artículo nombrado por ordinal o "Único" ("Artículo Único.-", común en decretos
# de reforma e iniciativas de la Gaceta), fuera de un bloque de transitorios.
_RE_ARTICULO_NAMED = re.compile(
    r"^Art[ií]culo\s+(PRIMERO|SEGUNDO|TERCERO|CUARTO|QUINTO|SEXTO|S[EÉ]PTIMO|"
    r"OCTAVO|NOVENO|D[EÉ]CIMO\w*|[UÚ]NICO)\b",
    re.IGNORECASE,
)

# Artículo transitorio nombrado por ordinal ("PRIMERO.-", "Artículo Segundo.-").
_RE_TRANS_ART = re.compile(
    rf"^(?:Art[ií]culo\s+)?({_NUM_AFTER})\s*[.\-–]", re.IGNORECASE
)

# Fracción: romano (+ Bis/Ter/Quáter con índice) seguido de separador.
_RE_FRACCION = re.compile(
    r"^([IVXLCDM]+(?:\s+(?:Bis|Ter|Qu[aá]ter)(?:\s+\d+)?)?)\s*[.\-–)]"
)

_RE_INCISO = re.compile(r"^([a-zñ])\s*[.\-–)]\s")
_RE_APARTADO_KW = re.compile(r"^Apartado\s+([A-Z])\b")
_RE_APARTADO_BARE = re.compile(r"^([A-Z])\s*[.\-–)]\s")


def _strip_md(line: str):
    m = _MD_HEADING.match(line)
    if m:
        return m.group(2).strip(), True
    return line.strip(), False


class _Builder:
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.units: list[Unit] = []
        self._by_id: dict[str, Unit] = {}
        self._lines: dict[str, list[str]] = {}
        # Punteros jerárquicos.
        self.libro = self.titulo = self.capitulo = self.seccion = None
        self.articulo = self.apartado = self.fraccion = self.inciso = None
        self.transitorios = None
        self.in_transitorios = False
        self.current = None  # unidad más profunda para adjuntar texto

    def _add(self, unit_id, unit_type, number, heading, parent, raw_line):
        # Evita colisiones de id con un sufijo incremental.
        base, n = unit_id, 2
        while unit_id in self._by_id:
            unit_id = f"{base}--{n}"
            n += 1
        u = Unit(unit_id, unit_type, number, heading, raw_line, parent)
        self.units.append(u)
        self._by_id[unit_id] = u
        self._lines[unit_id] = [raw_line]
        self.current = u
        return u

    def append_text(self, raw_line):
        if self.current is None:
            # Preámbulo: texto antes de la primera unidad estructural.
            self._add(f"{self.doc_id}-preambulo", "preambulo", None,
                      "", None, raw_line)
            return
        self._lines[self.current.unit_id].append(raw_line)

    def _container_parent(self, level):
        order = ["libro", "titulo", "capitulo", "seccion"]
        idx = order.index(level)
        for lv in reversed(order[:idx]):
            u = getattr(self, lv)
            if u is not None:
                return u.unit_id
        return None

    def add_libro(self, number, raw):
        uid = f"{self.doc_id}-lib{_norm_container_number(number)}"
        u = self._add(uid, "libro", number, raw, None, raw)
        self.libro = u
        self.titulo = self.capitulo = self.seccion = None
        self.articulo = self.apartado = self.fraccion = self.inciso = None

    def add_titulo(self, number, raw):
        uid = f"{self.doc_id}-tit{_norm_container_number(number)}"
        u = self._add(uid, "titulo", number, raw, self._container_parent("titulo"), raw)
        self.titulo = u
        self.capitulo = self.seccion = None
        self.articulo = self.apartado = self.fraccion = self.inciso = None

    def add_capitulo(self, number, raw):
        parent = self._container_parent("capitulo")
        base = parent or self.doc_id
        uid = f"{base}-cap{_norm_container_number(number)}"
        u = self._add(uid, "capitulo", number, raw, parent, raw)
        self.capitulo = u
        self.seccion = None
        self.articulo = self.apartado = self.fraccion = self.inciso = None

    def add_seccion(self, number, raw):
        parent = self._container_parent("seccion")
        base = parent or self.doc_id
        uid = f"{base}-sec{_norm_container_number(number)}"
        u = self._add(uid, "seccion", number, raw, parent, raw)
        self.seccion = u
        self.articulo = self.apartado = self.fraccion = self.inciso = None

    def add_articulo(self, number, raw):
        parent = self.seccion or self.capitulo or self.titulo or self.libro
        pid = parent.unit_id if parent else None
        uid = f"{self.doc_id}-art{_norm_article_number(number)}"
        u = self._add(uid, "articulo", number.strip().rstrip(".-–"), raw, pid, raw)
        self.articulo = u
        self.apartado = self.fraccion = self.inciso = None

    def add_transitorios(self, raw):
        uid = f"{self.doc_id}-transitorios"
        u = self._add(uid, "transitorios", None, raw, None, raw)
        self.transitorios = u
        self.in_transitorios = True
        self.articulo = self.apartado = self.fraccion = self.inciso = None

    def add_transitorio(self, number, raw):
        parent = self.transitorios.unit_id if self.transitorios else None
        base = self.transitorios.unit_id if self.transitorios else self.doc_id
        uid = f"{base}-{_norm_container_number(number)}"
        u = self._add(uid, "transitorio", number.strip().rstrip(".-–"), raw, parent, raw)
        self.articulo = u  # las fracciones cuelgan del transitorio como de un artículo
        self.apartado = self.fraccion = self.inciso = None

    def add_apartado(self, letter, raw):
        parent = self.articulo
        pid = parent.unit_id if parent else None
        base = pid or self.doc_id
        uid = f"{base}-ap{letter.upper()}"
        u = self._add(uid, "apartado", letter.upper(), raw, pid, raw)
        self.apartado = u
        self.fraccion = self.inciso = None

    def add_fraccion(self, number, raw):
        parent = self.apartado or self.articulo
        pid = parent.unit_id if parent else None
        base = pid or self.doc_id
        uid = f"{base}-frac{_norm_fraccion_number(number)}"
        u = self._add(uid, "fraccion", number.strip().rstrip(".-–)"), raw, pid, raw)
        self.fraccion = u
        self.inciso = None

    def add_inciso(self, letter, raw):
        parent = self.fraccion or self.apartado or self.articulo
        pid = parent.unit_id if parent else None
        base = pid or self.doc_id
        uid = f"{base}-inc{letter.lower()}"
        self._add(uid, "inciso", letter.lower(), raw, pid, raw)

    def finalize(self) -> list[Unit]:
        for u in self.units:
            u.text = "\n".join(self._lines[u.unit_id])
        return self.units


def _has_structure(text: str) -> bool:
    for raw in text.splitlines():
        content, _ = _strip_md(raw)
        if not content:
            continue
        if (_RE_ARTICULO.match(content) or _RE_ARTICULO_NAMED.match(content)
                or _RE_TITULO.match(content) or _RE_CAPITULO.match(content)
                or _RE_LIBRO.match(content) or _RE_SECCION.match(content)
                or _RE_TRANSITORIOS.match(content)):
            return True
    return False


def _fallback_paragraphs(text: str, doc_id: str) -> list[Unit]:
    """Texto no estructurado: divide en párrafos por líneas en blanco."""
    units: list[Unit] = []
    buf: list[str] = []
    idx = 1

    def flush():
        nonlocal idx, buf
        if not buf:
            return
        joined = "\n".join(buf)
        if joined.strip():
            heading = next((ln.strip() for ln in buf if ln.strip()), "")
            units.append(Unit(f"{doc_id}-p{idx}", "parrafo", str(idx),
                              heading[:120], joined, None))
            idx += 1
        buf = []

    for raw in text.splitlines():
        if raw.strip() == "":
            buf.append(raw)
            flush()
        else:
            buf.append(raw)
    flush()
    return units


def segment(text: str, doc_id: str = "DOC") -> list[Unit]:
    """Segmenta un texto legislativo mexicano en unidades citables.

    Args:
        text: texto plano o markdown extraído.
        doc_id: prefijo estable para los `unit_id` (p. ej. 'MX-LGS').

    Returns:
        Lista de `Unit` en orden de aparición. La concatenación de sus `.text`
        reproduce el documento original.
    """
    if not _has_structure(text):
        return _fallback_paragraphs(text, doc_id)

    b = _Builder(doc_id)

    for raw in text.splitlines():
        content, _is_md = _strip_md(raw)

        if content == "":
            b.append_text(raw)
            continue

        m = _RE_LIBRO.match(content)
        if m:
            b.add_libro(m.group(1), raw); continue
        m = _RE_TITULO.match(content)
        if m:
            b.in_transitorios = False
            b.add_titulo(m.group(1), raw); continue
        m = _RE_CAPITULO.match(content)
        if m:
            b.in_transitorios = False
            b.add_capitulo(m.group(1), raw); continue
        m = _RE_SECCION.match(content)
        if m:
            b.add_seccion(m.group(1), raw); continue
        if _RE_TRANSITORIOS.match(content):
            b.add_transitorios(raw); continue

        m = _RE_ARTICULO.match(content)
        if m:
            b.add_articulo(m.group(1), raw); continue

        # Artículo nombrado ("Artículo Único/Primero…") fuera de transitorios.
        if not b.in_transitorios:
            m = _RE_ARTICULO_NAMED.match(content)
            if m:
                b.add_articulo(m.group(1), raw); continue

        # Dentro de un bloque de transitorios, los ordinales encabezan artículos.
        if b.in_transitorios:
            m = _RE_TRANS_ART.match(content)
            if m and content.split()[0].lower().rstrip(".-–") in _ORDINALS or (
                m and _is_canonical_roman(m.group(1).upper())
            ):
                b.add_transitorio(m.group(1), raw); continue

        m = _RE_FRACCION.match(content)
        if m and _is_canonical_roman(m.group(1).split()[0]):
            b.add_fraccion(m.group(1), raw); continue

        m = _RE_APARTADO_KW.match(content)
        if m:
            b.add_apartado(m.group(1), raw); continue

        m = _RE_INCISO.match(content)
        if m:
            b.add_inciso(m.group(1), raw); continue

        # Apartado "A./B." sin palabra clave: solo letras NO romanas para no
        # confundir con fracciones (I., V., X., L., C., D., M.).
        m = _RE_APARTADO_BARE.match(content)
        if m and m.group(1) not in "IVXLCDM":
            b.add_apartado(m.group(1), raw); continue

        b.append_text(raw)

    return b.finalize()


def segment_to_dicts(text: str, doc_id: str = "DOC") -> list[dict]:
    return [u.as_dict() for u in segment(text, doc_id)]
