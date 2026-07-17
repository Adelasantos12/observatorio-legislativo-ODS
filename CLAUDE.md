# CLAUDE.md — Escáner Legislativo MX (escaner2030 + NormTrace)

## Qué es este proyecto

Fusión de dos sistemas:

1. **Stack tipi de Political Watch** (escáner ODS del Congreso español): frontend Vue
   (`frontend/`), API FastAPI (`api/`), motor de etiquetado por regex
   (`packages/qhld-tasks/tipi_tasks/tagger.py`), modelos y diccionarios en Mongo
   (`packages/qhld-data/`), pipeline batch de ingesta y etiquetado (`engine/`).
2. **NormTrace** (`normtrace/`): protocolo de trazabilidad jurídica para México.
   Contiene el "cerebro jurídico" (`normtrace/02_country_legal_brains/mexico/`),
   tablas analíticas codificadas (`normtrace/03_tables/`), esquemas JSON de salida
   (`normtrace/04_outputs/exports/data_package_v0_1/schemas/`) y método documentado
   (`normtrace/00_project/`).

Objetivo: un escáner de iniciativas y leyes mexicanas que combine
(a) etiquetado rápido por diccionario (regex, estilo tipi) y
(b) análisis estructural profundo por unidad jurídica (actor, procedimiento,
coordinación, anclaje, tipo de brecha) aplicando el protocolo NormTrace con LLM.

Lee `docs/ARCHITECTURE.md` (cómo funciona el stack y dónde se inserta NormTrace),
`docs/PLAN.md` (fases con criterios de aceptación) y `docs/TROPICALIZACION.md`
(mapa de términos España → México) antes de tocar código.

## Estado actual del repo

- Código copiado como snapshot (sin historial) de los repos originales; ver `NOTICE.md`.
- `pyproject.toml` de `api/`, `engine/` y `packages/qhld-tasks/` ya apuntan a los
  paquetes locales del monorepo por ruta (editable). Los `uv.lock` se borraron:
  **regenerar con `uv lock` dentro de cada componente** como primer paso.
- `docker-compose.yml` raíz existe pero los `Dockerfile-dev` originales asumen
  repos sueltos: hay que ajustar contextos y rutas COPY (fase F0).
- `knowledgebase/seeds/ods_mx.seed.json` es un seed de arranque con 3 ODS de
  ejemplo y vocabulario mexicano; `knowledgebase/load_kb.py` lo carga en Mongo.
- Nada se ha probado end-to-end todavía en esta fusión.

## Reglas de trabajo

- **No reescribir el motor tipi.** El tagger regex (`tipi_tasks/tagger.py`) y el
  compilador de diccionarios (`tipi_data/repositories/tags.py`, función
  `compile_tag`, con su lógica de `shuffle`/permutaciones) funcionan y tienen
  tests. La capa NormTrace se añade como etapa nueva, no como reemplazo.
- **El cerebro jurídico es fuente de verdad, no se edita a la ligera.** Los tres
  archivos de `normtrace/02_country_legal_brains/mexico/` son contenido académico
  de la autora. Si un prompt necesita un extracto, se construye leyendo de ahí en
  tiempo de ejecución o build; no se copian fragmentos parafraseados a mano.
- **Salidas NormTrace validan contra esquema.** Toda salida de la etapa de
  codificación profunda debe validar contra los JSON Schemas de
  `normtrace/04_outputs/exports/data_package_v0_1/schemas/` (o extensiones de
  ellos versionadas en `normtrace/`). Si el modelo devuelve algo que no valida,
  se reintenta o se marca el registro como `review_status: needs_human_review`.
- **Nunca presentar la codificación LLM como veredicto de cumplimiento.** El
  protocolo produce correspondencias trazables con estatus preliminar. Los campos
  `confidence_level` y `review_status` viajan siempre hasta el frontend.
- **Español mexicano en todo lo visible al usuario.** Ver `docs/TROPICALIZACION.md`.
- **Tests:** api y packages usan pytest (`runtests.sh` en api). Correr los tests
  del componente tocado antes de dar por cerrada una tarea. Los tests de
  integración usan testcontainers (necesitan Docker).
- **Commits pequeños por fase**, mensajes en español, prefijo del componente:
  `api:`, `frontend:`, `engine:`, `kb:`, `normtrace:`, `docs:`.

## Arquitectura en una pantalla

```
texto/iniciativa
   │
   ▼
[1] Tagger regex (qhld-tasks)  ← diccionario "mx" en Mongo (topics/tags)
   │   detecta temas ODS/marcos, cuenta coincidencias
   ▼
[2] Segmentador jurídico (NUEVO: packages/legal-segmenter)
   │   corta por Artículo/Fracción/Inciso según
   │   normtrace/02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md
   │   → unidades citables con id estable (p.ej. MX-LGS-art134-fracII)
   ▼
[3] Codificador NormTrace (NUEVO: api/tipi_backend/normtrace/ como tarea Celery)
   │   LLM + cerebro jurídico → actor, deber/facultad, procedimiento,
   │   coordinación, sanción, salvaguarda, nivel de fuente, tipo de brecha
   │   valida contra JSON Schema; marca confianza y estatus de revisión
   ▼
[4] Frontend: resultados del escáner + panel estructural por unidad
```

El punto de inserción exacto en la API es
`api/tipi_backend/api/endpoints/tagger.py::extract()`: hoy hace
extraer texto → `extract_tags_from_text` → `filter_tags` → responder.
La etapa [3] se cuelga después, como tarea asíncrona opcional
(parámetro `deep=true` en el POST a `/tagger/`).

## Comandos útiles

```bash
# entorno python por componente (uv)
cd api && uv sync && uv run uvicorn tipi_backend.main:app --reload --port 8080
cd packages/qhld-tasks && uv sync && uv run celery -A tipi_tasks worker
# frontend
cd frontend && npm install && cp .env.mx .env && npm run dev
# diccionario
python knowledgebase/load_kb.py            # carga seed mx en Mongo local
# stack completo
docker compose up --build
```

## Qué NO hacer

- No subir claves de API de LLM al repo (usar variables de entorno,
  `LLM_API_KEY`, y documentar en README).
- No eliminar los extractores de España/Paraguay/Andorra en `engine/`:
  el de Paraguay es la plantilla para el de México (está basado en API,
  más limpio que el scraper de España).
- No convertir los datos del piloto RSI (`normtrace/03_tables/`) en fixtures de
  tests que luego se editen: son datos de investigación, se leen, no se mutan.
- No introducir dependencias de servicios de pago sin dejarlas desactivables.
