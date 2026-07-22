"""Validación de corridas contra `normtrace_mapping.schema.json`."""

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft7Validator

_REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = _REPO_ROOT / "normtrace/schemas_runtime/normtrace_mapping.schema.json"


@lru_cache(maxsize=1)
def _validator() -> Draft7Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return Draft7Validator(schema)


def validate_run(run: dict) -> list[str]:
    """Lista de mensajes de error (vacía si la corrida valida)."""
    return [e.message for e in _validator().iter_errors(run)]


def is_valid(run: dict) -> bool:
    return not validate_run(run)
