# Escáner Legislativo MX

Escáner de legislación e iniciativas mexicanas frente a marcos internacionales
(ODS, RSI, tratados de derechos humanos), en dos capas:

1. **Escaneo rápido** por diccionario curado (motor tipi de Political Watch):
   detecta presencia temática en segundos.
2. **Análisis estructural** por unidad jurídica (protocolo NormTrace): qué actor
   queda obligado o facultado, con qué procedimiento, qué coordinación, en qué
   nivel de fuente formal y con qué brechas, mediante codificación asistida por
   LLM con el cerebro jurídico mexicano y validación contra esquema.

Este repo es la fusión de [escaner2030.es y el stack tipi de Political Watch](https://github.com/politicalwatch)
(AGPL-3.0) con [NormTrace-IHR Mexico pilot](https://github.com/Adelasantos12/normtrace-ihr-mexico-pilot)
(CC BY 4.0). Atribución completa en `NOTICE.md`.

## Estructura

```
frontend/     SPA Vue del escáner (de escaner2030.es)
api/          API FastAPI (de tipi-backend)
engine/       pipeline batch de ingesta y etiquetado (de tipi-engine)
packages/
  qhld-data/  modelos Mongo y compilador de diccionarios (de tipi-data)
  qhld-tasks/ motor de matching regex + tareas Celery (de tipi-tasks)
normtrace/    protocolo, cerebro jurídico mexicano, tablas y esquemas
knowledgebase/ diccionarios mexicanos (seeds) y cargador
docs/         ARCHITECTURE.md · PLAN.md · TROPICALIZACION.md
CLAUDE.md     instrucciones de trabajo para Claude Code
```

## Arranque

Ver `CLAUDE.md` (comandos) y `docs/PLAN.md` (fases F0–F6 con criterios de
aceptación). Estado actual: esqueleto fusionado, sin probar end-to-end; la
fase F0 es hacerlo arrancar.

## Método y descargos

La capa de análisis estructural produce codificación preliminar trazable, no
dictámenes jurídicos ni evaluaciones de cumplimiento. Método completo en
`normtrace/00_project/` y en el paper del protocolo. Cada registro conserva su
cita fuente.

## Licencias

Código: AGPL-3.0 (ver `LICENSE`). Contenido NormTrace: CC BY 4.0
(ver `normtrace/LICENSE-CC-BY-4.0`). Detalle en `NOTICE.md`.
