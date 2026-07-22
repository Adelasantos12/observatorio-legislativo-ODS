#!/usr/bin/env python3
"""Candado de texto visible (adenda v4 §2/§7/§8.1).

Recorre `frontend/src/content/es.json` y reprueba si aparece una frase que
anuncia el propio encuadre (§2) o un tic de escritura de IA (§7). Corre en CI:
todo el copy visible vive en ese archivo, así que este check lo cubre entero.

Sin dependencias; sale con código ≠ 0 si encuentra violaciones.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ES_JSON = ROOT / "frontend/src/content/es.json"

# §2 — frases que niegan una lectura temida (el encuadre se ejecuta, no se anuncia).
FRASES_PROHIBIDAS = [
    "no es un ranking",
    "no es una competencia",
    "no se trata de",
    "esto no pretende",
    "sin ánimo de comparar",
    "más allá de colores partidistas",
    "no es un concurso",
    "no busca comparar",
]

# §7 — tics de IA en texto visible.
TICS_IA = [
    "es importante destacar",
    "es importante señalar",
    "cabe destacar",
    "cabe señalar",
    "en este sentido",
    "en el marco de",
    "a la luz de",
    "en conclusión",
    "en definitiva",
    "holístico",
    "holistico",
    "robusto",
    "sinergia",
    "potenciar",
    "impulsar",
]


def _norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return s.lower()


def _walk(obj, path="root"):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k.startswith("_"):  # claves de nota (p. ej. _nota_autora) no son visibles
                continue
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def check(text_items):
    problemas = []
    for path, s in text_items:
        low = _norm(s)
        for frase in FRASES_PROHIBIDAS:
            if _norm(frase) in low:
                problemas.append((path, f"frase de encuadre prohibida: «{frase}»"))
        for tic in TICS_IA:
            if re.search(rf"\b{re.escape(_norm(tic))}\b", low):
                problemas.append((path, f"tic de IA: «{tic}»"))
        # Guion largo como puntuación (em/en dash).
        if "—" in s or "–" in s:
            problemas.append((path, "guion largo (—/–) como puntuación"))
        # Construcción "no es X, es Y" / "no es X sino Y".
        if re.search(r"\bno es\b[^.]{0,60}\b(sino|,\s*es)\b", low):
            problemas.append((path, "construcción «no es X, es Y»"))
    return problemas


def main():
    if not ES_JSON.is_file():
        print(f"No existe {ES_JSON}", file=sys.stderr)
        return 1
    data = json.loads(ES_JSON.read_text(encoding="utf-8"))
    problemas = check(list(_walk(data)))
    if problemas:
        print("Texto visible: violaciones de la adenda v4 §2/§7:")
        for path, msg in problemas:
            print(f"  [{path}] {msg}")
        return 1
    n = sum(1 for _ in _walk(data))
    print(f"Texto visible OK: {n} cadenas revisadas, sin frases de encuadre ni tics de IA.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
