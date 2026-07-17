# Plan de trabajo por fases (para Claude Code)

Cada fase termina con sus criterios de aceptación cumplidos y un commit.
No avanzar de fase con criterios pendientes. Si algo del plan choca con la
realidad del código, documentar la decisión en este archivo (sección Bitácora
al final) y seguir.

## F0 — Que el monorepo arranque

1. Regenerar locks: `uv lock` en `api/`, `engine/`, `packages/qhld-tasks/`,
   `packages/qhld-data/`. Resolver conflictos de versión si aparecen.
2. Ajustar los `Dockerfile-dev` de `api/` y `packages/qhld-tasks/` al layout
   monorepo (el contexto de build en `docker-compose.yml` raíz es `.`, los
   paquetes locales deben quedar instalables por ruta).
3. `docker compose up` levanta mongo, redis, api y worker sin crashear.
4. `python knowledgebase/load_kb.py` carga el seed; `GET /topics/?knowledgebase=mx`
   los devuelve.
5. `POST /tagger/` con un párrafo sobre CONAGUA y derecho humano al agua
   devuelve tags del ODS 6 del seed mexicano.

Aceptación: los cinco puntos anteriores, más tests existentes de
`packages/qhld-tasks` y `packages/qhld-data` en verde.

## F1 — Tropicalización visible

Según `docs/TROPICALIZACION.md`:

1. `frontend/`: textos de `src/i18n/messages.js`, `src/config/index.js` y vistas
   a español mexicano y contexto institucional mexicano (Cámara de Diputados,
   DOF, iniciativa, dictamen). Título, metadatos, página "acerca de".
2. Quitar o parametrizar referencias a Congreso de los Diputados, BOE,
   quehacenlosdiputados.es y Google Analytics español.
3. `api/`: mensajes de error y descripciones OpenAPI en español neutro-mexicano.
4. Crear `api/tipi_backend/api/managers/mexico/` con `initiative_type.py` y
   `initiative_status.py` según el proceso legislativo mexicano (iniciativa,
   turno a comisión, dictamen de primera lectura, discusión, minuta, publicación
   en DOF...), tomando `paraguay/` como plantilla estructural.

Aceptación: el escáner corre end-to-end en español mexicano sin rastro visible
del despliegue español; captura de pantalla del resultado en el PR.

## F2 — Diccionario mexicano completo

1. Ampliar `knowledgebase/seeds/ods_mx.seed.json` a los 17 ODS con sus metas
   como subtopics. Estrategia: partir de la estructura de metas ONU en español
   y escribir regexes con vocabulario institucional mexicano (dependencias,
   programas, NOMs, leyes generales). El fixture español
   `api/tests/fixtures/knowledgebase.json` sirve como referencia de estilo de
   regex (uso de `shuffle` para co-ocurrencias), no de vocabulario.
2. Añadir un seed de segundo marco para demostrar multi-marco:
   `rsi_mx.seed.json` generado desde
   `normtrace/03_tables/international_obligations/IHR-2005_obligations_domestic-anchoring.csv`
   (topic = parte del RSI, subtopic = artículo, tag = obligación con regex
   sembrada desde su descripción corta).
3. Script `knowledgebase/validate_seeds.py`: valida JSON, compila cada regex con
   `compile_tag()` real, reporta regexes que no compilan o explotan en
   permutaciones.

Aceptación: 17 topics ODS cargados; escaneo de una iniciativa real de la Gaceta
(hay ejemplos citados en `docs/TROPICALIZACION.md` §Corpus de prueba) produce
etiquetas plausibles; validador en verde.

## F3 — Segmentador jurídico

1. Nuevo paquete `packages/legal-segmenter` (python, sin dependencias pesadas):
   parser determinista de estructura legislativa mexicana según
   `normtrace/02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md`
   (§2 estructura, §3 citas). Entrada: texto plano; salida: lista de unidades
   `{unit_id, unit_type, number, heading, text, parent_id}`.
2. Casos que debe manejar: artículos "bis/ter/quáter", fracciones romanas,
   incisos, transitorios, y texto no estructurado (fallback a párrafos).
3. Tests con fragmentos reales: un artículo de la Ley General de Salud (está en
   `normtrace/01_sources/mexico/` en markdown) y una iniciativa de la Gaceta.
4. Integrar como paso opcional del tagger: si `segment=legal`, los conteos se
   reportan además por unidad.

Aceptación: pytest del paquete en verde; segmentar la LGS produce unidades con
ids estables y sin pérdida de texto (concatenación de unidades ≈ documento).

## F4 — Codificador NormTrace

1. `packages/qhld-tasks/tipi_tasks/normtrace.py`: tarea Celery en cola
   `normtrace`. Por unidad segmentada con tags: construye prompt con extractos
   del cerebro jurídico (cargados de `normtrace/02_country_legal_brains/mexico/`,
   no parafraseados), llama al LLM (proveedor configurable por env:
   `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`), parsea JSON.
2. Esquema de salida: derivar de
   `normtrace/04_outputs/exports/data_package_v0_1/schemas/` un
   `unit_analysis.schema.json` versionado en `normtrace/schemas_runtime/`.
   Validar cada salida; ante fallo, un reintento y luego
   `review_status: needs_human_review`.
3. Campos obligatorios de la salida: los del pipeline descrito en
   `docs/ARCHITECTURE.md` §3, siempre con `confidence_level` y `review_status`.
4. Cache por hash(unidad + versión de prompt) en Mongo para no repagar llamadas.
5. Endpoint: `POST /tagger/` acepta `deep=true` → respuesta incluye
   `normtrace_task_id`; `GET /tagger/result/{id}` devuelve el bloque
   `structural` cuando termina.
6. Presupuesto: variable `NORMTRACE_MAX_UNITS` (default 50) corta documentos
   enormes y lo reporta en la respuesta (`units_analyzed`, `units_skipped`).

Aceptación: escanear en modo deep la iniciativa de salud intercultural de la
Gaceta del 16/jul/2026 (o fragmento equivalente) devuelve unidades codificadas
válidas contra esquema, con actor y tipo de deber identificados razonablemente;
ninguna salida sin `review_status`.

## F5 — Frontend estructural

1. Componente nuevo junto a `scanner-table.vue`: tabla por unidad
   (unidad → actor → deber/facultad → procedimiento → coordinación → brecha),
   badges de `confidence_level` y aviso fijo de "análisis preliminar asistido
   por modelo, no validado por especialista" (texto exacto en
   `docs/TROPICALIZACION.md` §Descargos).
2. Estado de carga del análisis profundo (llega después del rápido).
3. Vista imprimible/exportable del análisis de un documento (la unidad de
   entrega política es el brief en PDF).

Aceptación: flujo completo en navegador: pegar texto → resultado rápido →
resultado estructural → exportar.

## F6 — Ingesta Gaceta (batch, opcional tras F5)

`engine/qhld_engine/extractors/mexico/`: extractor de Gaceta Parlamentaria
(spec de scrapeabilidad en `docs/ARCHITECTURE.md` §4), modelado sobre
`paraguay/`. Etiquetado batch de iniciativas del día + codificación NormTrace
de las que disparen marcos de interés. Esto habilita el observatorio continuo;
no es prerequisito del escáner interactivo.

## Bitácora de decisiones

(vacía; Claude Code documenta aquí desviaciones del plan con fecha y razón)
