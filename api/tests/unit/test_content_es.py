"""Candado del texto visible es.json (adenda v4 §8.1).

Reprueba si el copy anuncia su encuadre (§2) o tiene tics de IA (§7). El checker
vive en scripts/check_content.py (sin dependencias) y también corre en CI.
"""

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

_ROOT = Path(__file__).resolve().parents[3]
_CHECKER = _ROOT / "scripts/check_content.py"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_content", _CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_es_json_sin_frases_prohibidas_ni_tics():
    cc = _load_checker()
    data = __import__("json").loads(cc.ES_JSON.read_text(encoding="utf-8"))
    problemas = cc.check(list(cc._walk(data)))
    assert problemas == [], problemas


def test_checker_detecta_violaciones():
    cc = _load_checker()
    muestra = [
        ("x", "Esto no es un ranking entre bancadas."),
        ("y", "Es importante destacar el avance."),
        ("z", "Un texto con guion largo — como este."),
    ]
    problemas = cc.check(muestra)
    assert len(problemas) >= 3


def test_estado_vacio_tiene_copy():
    """La historia con datos vacíos usa este copy, no ceros (v4.1 §5)."""
    cc = _load_checker()
    data = __import__("json").loads(cc.ES_JSON.read_text(encoding="utf-8"))
    ev = data.get("estadoVacio", {})
    assert ev.get("titulo") and ev.get("cuerpo")


def test_agua_tiene_contador_sin_dato():
    """El contador de armonización usa 'en documentación', nunca '0 de 32' (v4.1 §2)."""
    cc = _load_checker()
    data = __import__("json").loads(cc.ES_JSON.read_text(encoding="utf-8"))
    assert data["escenas"]["agua"].get("contadorSinDato")
