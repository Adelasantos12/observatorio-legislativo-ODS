"""Valida los seeds de diccionario (knowledgebase) del Escáner Legislativo MX.

Para cada seed:
  1. Valida la estructura JSON (lista de topics con los campos esperados).
  2. Compila CADA regex con el `compile_tag()` real de tipi_data (el mismo que
     usa el backend), detectando regexes que no compilan.
  3. Reporta tags con `shuffle: true` cuya expansión en permutaciones "explota"
     (factorial del nº de partes separadas por `.*`/`.*?`), que degradan el
     rendimiento del tagger.

Uso:
    python knowledgebase/validate_seeds.py [seed1.json seed2.json ...]

Sin argumentos valida todos los `seeds/*.seed.json`. Sale con código != 0 si
hay errores (regex que no compila, JSON inválido, campo faltante).
"""

import json
import math
import sys
from itertools import permutations
from pathlib import Path

import regex
from tipi_data.repositories.tags import compile_tag

HERE = Path(__file__).parent
SEEDS_DIR = HERE / "seeds"

# Umbral de permutaciones por encima del cual un `shuffle: true` se considera
# explosivo (n! crece muy rápido; >120 = 6 partes ya es señal de alarma).
SHUFFLE_MAX_PERMUTATIONS = 120

REQUIRED_TOPIC_FIELDS = ("name", "knowledgebase")
REQUIRED_TAG_FIELDS = ("regex", "tag", "subtopic")


def _shuffle_parts(regex_str):
    delimiter = ".*?" if ".*?" in regex_str else ".*"
    return regex_str.split(delimiter)


def validate_seed(path):
    """Valida un seed. Devuelve (errores, avisos, n_topics, n_tags)."""
    errors = []
    warnings = []
    try:
        topics = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{path}: JSON inválido: {e}"], [], 0, 0

    if not isinstance(topics, list):
        return [f"{path}: la raíz debe ser una lista de topics"], [], 0, 0

    n_tags = 0
    for i, topic in enumerate(topics):
        loc = f"{Path(path).name}[{i}] '{topic.get('name', '??')}'"
        for field in REQUIRED_TOPIC_FIELDS:
            if not topic.get(field):
                errors.append(f"{loc}: falta el campo obligatorio '{field}'")
        topic.setdefault("public", True)
        topic.setdefault("knowledgebase", "mx")

        for tag in topic.get("tags", []):
            n_tags += 1
            tloc = f"{loc} → tag '{tag.get('tag', '??')}'"
            for field in REQUIRED_TAG_FIELDS:
                if not tag.get(field):
                    errors.append(f"{tloc}: falta el campo obligatorio '{field}'")
            if not tag.get("regex"):
                continue

            # ¿Compila la regex cruda?
            try:
                regex.compile("(?i)" + tag["regex"])
            except regex.error as e:
                errors.append(f"{tloc}: la regex no compila: {e} | {tag['regex']!r}")
                continue

            # ¿La compila el compile_tag real (incluida la expansión de shuffle)?
            compiled = compile_tag(topic, tag)
            if not compiled:
                errors.append(
                    f"{tloc}: compile_tag() no produjo ninguna regex (posible "
                    f"error en permutaciones) | {tag['regex']!r}"
                )
                continue

            # Aviso por explosión de permutaciones en shuffle.
            if tag.get("shuffle"):
                nparts = len(_shuffle_parts(tag["regex"]))
                nperm = math.factorial(nparts)
                if nperm > SHUFFLE_MAX_PERMUTATIONS:
                    warnings.append(
                        f"{tloc}: shuffle con {nparts} partes = {nperm} permutaciones "
                        f"(> {SHUFFLE_MAX_PERMUTATIONS}); considera menos comodines .*"
                    )

    return errors, warnings, len(topics), n_tags


def main(argv):
    if argv:
        paths = [Path(p) for p in argv]
    else:
        paths = sorted(SEEDS_DIR.glob("*.seed.json"))

    if not paths:
        print("No se encontraron seeds que validar.")
        return 1

    total_errors = 0
    total_warnings = 0
    for path in paths:
        errors, warnings, n_topics, n_tags = validate_seed(path)
        status = "OK" if not errors else f"{len(errors)} ERROR(es)"
        print(f"\n== {path} :: {n_topics} topics, {n_tags} tags :: {status} ==")
        for w in warnings:
            print(f"  [aviso] {w}")
        for e in errors:
            print(f"  [ERROR] {e}")
        total_errors += len(errors)
        total_warnings += len(warnings)

    print(
        f"\nResumen: {total_errors} error(es), {total_warnings} aviso(s) "
        f"en {len(paths)} seed(s)."
    )
    return 1 if total_errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
