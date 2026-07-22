"""Tests del scraper del SIL para iniciativas del Ejecutivo Federal (Huella, H.5).

Sin red ni Mongo: el parser trabaja sobre HTML de fixture; la conversión a
`ExecutiveInitiative` y la clasificación por sección se prueban en aislamiento.
"""

import pytest

from qhld_engine.extractors.mexico import sil_ejecutivo as sil

pytestmark = pytest.mark.unit


# Cuatro filas que ejercen las cuatro secciones (Aprobadas/Pendientes/
# Desechadas/Retiradas), más una fila de encabezado y una fila corta que deben
# ignorarse.
SIL_HTML = """<html><body>
<table>
  <tr><th>#</th><th>Denominaci&oacute;n</th><th>Presentaci&oacute;n</th><th>Estatus</th></tr>
  <tr>
    <td>1</td>
    <td>Que reforma la Ley General de Instituciones, en materia judicial.</td>
    <td>08/10/2024</td>
    <td>Publicado en DOF el 14/10/2024</td>
  </tr>
  <tr>
    <td>2</td>
    <td>Que expide la Ley de Aguas Nacionales.</td>
    <td>01/06/2026</td>
    <td>Pendiente en comisi&oacute;n(es) de origen el 01/06/2026</td>
  </tr>
  <tr>
    <td>3</td>
    <td>Que adiciona disposiciones diversas.</td>
    <td>10/03/2026</td>
    <td>Desechado en pleno origen el 11/03/2026</td>
  </tr>
  <tr>
    <td>4</td>
    <td>Que reforma el C&oacute;digo Nacional.</td>
    <td>15/03/2025</td>
    <td>Retirada el 19/03/2025</td>
  </tr>
  <tr><td>fila</td><td>corta</td></tr>
</table>
</body></html>"""


def test_clasificar_seccion():
    assert sil.clasificar_seccion("Publicado en DOF el 14/10/2024") == sil.SECCION_APROBADAS
    assert sil.clasificar_seccion("Pendiente en comisión(es) de origen el 01/06/2026") == sil.SECCION_PENDIENTES
    assert sil.clasificar_seccion("Desechado en pleno origen el 11/03/2026") == sil.SECCION_DESECHADAS
    assert sil.clasificar_seccion("Retirada el 19/03/2025") == sil.SECCION_RETIRADAS
    # Estatus desconocido nunca se pierde: cae en pendientes.
    assert sil.clasificar_seccion("En estudio") == sil.SECCION_PENDIENTES


def test_build_url_incluye_legislatura():
    url = sil.build_url("66")
    assert "Origen=1" in url
    assert "Legislatura=66" in url


def test_parse_sil_cuatro_secciones():
    inits = sil.parse_sil(SIL_HTML)
    assert [i.num for i in inits] == [1, 2, 3, 4]
    secciones = {i.num: i.seccion for i in inits}
    assert secciones[1] == sil.SECCION_APROBADAS
    assert secciones[2] == sil.SECCION_PENDIENTES
    assert secciones[3] == sil.SECCION_DESECHADAS
    assert secciones[4] == sil.SECCION_RETIRADAS


def test_parse_sil_extrae_fecha_dof_solo_en_aprobadas():
    inits = {i.num: i for i in sil.parse_sil(SIL_HTML)}
    assert inits[1].fecha_dof == "14/10/2024"
    assert inits[1].fecha_presentacion == "08/10/2024"
    # Pendiente/desechada/retirada no tienen fecha DOF.
    assert inits[2].fecha_dof == ""
    assert inits[3].fecha_dof == ""
    assert inits[4].fecha_dof == ""


def test_parse_sil_ignora_encabezado_y_filas_cortas():
    inits = sil.parse_sil(SIL_HTML)
    # Solo 4 iniciativas: se ignoran la fila th y la fila de 2 celdas.
    assert len(inits) == 4


def test_to_executive_initiative_id_estable_y_sin_codificar():
    inits = sil.parse_sil(SIL_HTML)
    ei = sil.to_executive_initiative(inits[0])
    assert ei.id == "EJE-2024-2030-1-aprobadas-y-o-publicadas-en-dof"
    assert ei.num == 1
    assert ei.fecha_dof == "14/10/2024"
    # El scraper no aporta codificación: entra como pendiente y vacío.
    assert ei.ods_principal is None
    assert ei.ods_secundarios == []
    assert ei.metas == []
    assert ei.confianza == "pendiente"
