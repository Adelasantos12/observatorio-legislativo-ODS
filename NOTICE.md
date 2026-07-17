# Atribución y licencias

Este monorepo combina dos linajes de código y contenido:

## Stack tipi (Political Watch) — AGPL-3.0

Los directorios `frontend/`, `api/`, `engine/`, `packages/qhld-data/` y
`packages/qhld-tasks/` derivan de los siguientes repositorios de
[Political Watch](https://github.com/politicalwatch), todos bajo licencia
GNU Affero General Public License v3.0:

| Directorio aquí | Repo original |
|---|---|
| `frontend/` | politicalwatch/escaner2030.es |
| `api/` | politicalwatch/tipi-backend |
| `engine/` | politicalwatch/tipi-engine |
| `packages/qhld-data/` | politicalwatch/tipi-data (paquete `qhld-data`) |
| `packages/qhld-tasks/` | politicalwatch/tipi-tasks (paquete `qhld-tasks`) |

La copia se hizo sin historial git (snapshot, julio 2026). Por ser AGPL-3.0,
este repositorio completo se distribuye bajo AGPL-3.0 (ver `LICENSE`).
Si el servicio se ofrece en red, la AGPL obliga a publicar el código fuente
de la versión desplegada, incluidas las modificaciones.

## Capa NormTrace — CC BY 4.0

El directorio `normtrace/` deriva de
[Adelasantos12/normtrace-ihr-mexico-pilot](https://github.com/Adelasantos12/normtrace-ihr-mexico-pilot),
de Adela Santos, bajo Creative Commons Attribution 4.0
(ver `normtrace/LICENSE-CC-BY-4.0` y `normtrace/CITATION.cff`).
Se excluyeron los PDF de fuentes primarias (disponibles en el repo original),
la webapp del piloto y el archivo histórico; se conservan el cerebro jurídico,
las tablas analíticas, los esquemas JSON y la documentación de método.

## Convivencia de licencias

El contenido CC BY 4.0 (datos, documentación, método) convive con el código
AGPL sin conflicto: son obras separadas dentro del mismo repositorio, cada una
con su licencia declarada. El código nuevo que se escriba aquí queda bajo
AGPL-3.0; los datos y documentos nuevos de la capa NormTrace pueden mantenerse
CC BY 4.0 si se desea, declarándolo en el directorio correspondiente.
