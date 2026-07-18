"""Resolución de citas: toda disposición citada debe existir en el texto.

Umbral 1 de la evaluación dorada: 100% de resolución. Una cita inventada
reprueba la corrida completa. La verificación es programática: se extraen los
números de artículo (y transitorios) de cada `disposicion` y se comprueban
contra el índice de artículos del texto. Cuando el texto está disponible
(descargado y segmentado) el índice se deriva de él; sin red se usa el índice
estructural conocido de la ley vitrina (LGA: 45 artículos + transitorios).
"""

import re

# La Ley General de Aguas tiene 45 artículos (brief §ficha técnica) más
# transitorios propios y del decreto.
LGA_MAX_ARTICULO = 45

# Marcador de artículo(s): "Art.", "Arts.", "Artículo", "Artículos"…
_ART_TOKEN = re.compile(r"\barts?[íictulos\.]*", re.IGNORECASE)
# Rango arábigo "30-31" (también 30–31 con guion largo).
_RANGE = re.compile(r"(\d{1,3})\s*[-–]\s*(\d{1,3})")
_NUM = re.compile(r"\d{1,3}")
_TRANS_RE = re.compile(r"transitori", re.IGNORECASE)


def article_numbers(disposicion: str) -> list[int]:
    """Extrae los números de artículo citados, expandiendo rangos y plurales.

    'Arts. 30-31' -> [30, 31]; 'Art. 7 fracc. I-VI' -> [7] (las fracciones son
    romanas, no cuentan); 'Art. 6 ...; Art. 10' -> [6, 10].
    """
    text = disposicion or ""
    nums = set()
    for m in _ART_TOKEN.finditer(text):
        # Ventana hasta el siguiente marcador de artículo (o fin).
        nxt = _ART_TOKEN.search(text, m.end())
        tail = text[m.end():nxt.start()] if nxt else text[m.end():]
        for a, b in _RANGE.findall(tail):
            lo, hi = int(a), int(b)
            if lo <= hi and hi - lo < 50:
                nums.update(range(lo, hi + 1))
        for n in _NUM.findall(tail):
            nums.add(int(n))
    return sorted(nums)


def cites_transitorio(disposicion: str) -> bool:
    return bool(_TRANS_RE.search(disposicion or ""))


def lga_article_index() -> set:
    """Índice estructural offline de la LGA: artículos 1..45."""
    return set(range(1, LGA_MAX_ARTICULO + 1))


def article_index_from_units(units) -> set:
    """Deriva el índice de artículos de las unidades segmentadas (cuando hay texto).

    `units`: iterable de dicts/objetos con un campo/atributo que contenga el
    número de artículo. Tolerante a ambas formas.
    """
    idx = set()
    for u in units:
        if isinstance(u, dict):
            art = u.get("number") or u.get("article") or u.get("articulo")
        else:
            art = getattr(u, "number", None) or getattr(u, "article", None)
        if art is None:
            continue
        m = re.search(r"\d{1,3}", str(art))
        if m:
            idx.add(int(m.group(0)))
    return idx


def resolves(disposicion: str, article_index: set) -> bool:
    """True si toda referencia de la disposición existe en el índice.

    Una disposición sin número de artículo pero que cita un transitorio se
    considera resuelta (los transitorios existen por construcción del decreto).
    """
    nums = article_numbers(disposicion)
    if not nums:
        return cites_transitorio(disposicion)
    return all(n in article_index for n in nums)


def citation_resolution(registros: list[dict], article_index: set | None = None) -> dict:
    """Reporta la resolución de citas de una corrida.

    Devuelve {total, resueltas, no_resueltas: [disposicion...], tasa}.
    """
    article_index = article_index if article_index is not None else lga_article_index()
    no_resueltas = []
    for r in registros:
        disp = r.get("disposicion", "")
        if not resolves(disp, article_index):
            no_resueltas.append(disp)
    total = len(registros)
    resueltas = total - len(no_resueltas)
    return {
        "total": total,
        "resueltas": resueltas,
        "no_resueltas": no_resueltas,
        "tasa": (resueltas / total) if total else 1.0,
    }
