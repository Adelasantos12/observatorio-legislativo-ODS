"""Tests del scraper de minutas del iniclave (Huella 2030, módulo B, H.6).

Sin red ni Mongo: el parser trabaja sobre HTML de fixture; la clave, la
conversión a `Minuta` y la atribución de origen se prueban en aislamiento.
"""

import pytest

from qhld_engine.extractors.mexico import iniclave_minutas as im

pytestmark = pytest.mark.unit


MINUTAS_HTML = """<html><body>
<table>
  <tr><th>#</th><th>Denominaci&oacute;n</th><th>Fecha</th><th>Estatus</th></tr>
  <tr>
    <td>1</td>
    <td>Que reforma la Ley General de Salud.</td>
    <td>05/02/2025</td>
    <td>Aprobada en el 2do. periodo; turnada al Senado</td>
  </tr>
  <tr>
    <td>2</td>
    <td>Que expide la Ley de Ciencia y Tecnolog&iacute;a.</td>
    <td>10/03/2025</td>
    <td>Aprobada; turnada al Senado</td>
  </tr>
  <tr><td>encabezado</td><td>ignorar</td></tr>
</table>
</body></html>"""


def test_parse_minutas_filas_validas():
    rows = im.parse_minutas(MINUTAS_HTML)
    assert [r.numero for r in rows] == [1, 2]
    assert rows[0].denominacion.startswith("Que reforma la Ley General de Salud")
    assert rows[0].fecha == "05/02/2025"


def test_parse_minutas_detecta_periodo():
    rows = {r.numero: r for r in im.parse_minutas(MINUTAS_HTML)}
    assert rows[1].periodo == "2P"   # "2do. periodo"
    assert rows[2].periodo == ""      # sin periodo explícito


def test_make_clave_formato():
    assert im.make_clave("LXVI", "II", "2P", 139) == "CD-LXVI-II-2P-139"
    # Sin periodo identificado usa 'SP' y no rompe.
    assert im.make_clave("LXVI", "I", "", 7) == "CD-LXVI-I-SP-7"


def test_to_minuta_sin_codificar_ni_origen():
    row = im.parse_minutas(MINUTAS_HTML)[0]
    m = im.to_minuta(row, "LXVI", "II")
    assert m.id == "CD-LXVI-II-2P-1"
    assert m.numero == 1
    assert m.origen is None            # por documentar; jamás inventado
    assert m.confianza == "pendiente"
    assert m.ods_principal is None
    assert m.metas == []


def test_atribuir_origen_solo_por_coincidencia():
    execs = [{
        "id": "EJE-2024-2030-9-aprobadas",
        "denominacion": "Que reforma la Ley General de Salud.",
        "ods_principal": "3", "ods_secundarios": [], "metas": ["3.8"],
        "tema": "Salud", "confianza": "alta",
    }]
    index = im.build_executive_index(execs)
    rows = im.parse_minutas(MINUTAS_HTML)
    # La minuta 1 coincide con la iniciativa del Ejecutivo -> origen Ejecutivo.
    origen, ref = im.atribuir_origen(im.to_minuta(rows[0], "LXVI", "II"), index)
    assert origen == im.ORIGEN_EJECUTIVO
    assert ref == "EJE-2024-2030-9-aprobadas"
    # La minuta 2 no coincide con nada -> queda por documentar (None).
    origen2, ref2 = im.atribuir_origen(im.to_minuta(rows[1], "LXVI", "II"), index)
    assert origen2 is None
    assert ref2 is None
