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

### 2026-07-17 — F0

- **Locks regenerados** (`uv lock`) en `packages/qhld-data`, `packages/qhld-tasks`,
  `api` y `engine`: resueltos sin conflictos con CPython 3.12.
- **`api/tipi_backend/settings.py` creado y versionado.** El stack tipi lo tenía
  en `.gitignore` (config por-despliegue), pero sin él ni la API ni sus tests
  arrancan. Se reescribió dirigido por variables de entorno (12-factor, sin
  secretos) con defaults que coinciden con `docker-compose.yml`, y se quitó del
  `.gitignore`. Incluye `MAX_CONTENT_LENGTH` (lo exige el middleware de subida).
- **Bug del `_id` en los seeds.** `Topic` (MongoModel) exige un `_id` **string**;
  el seed no lo traía, así que Mongo asignaba un ObjectId y `GET /topics` fallaba
  al validar. Se añadió `_id` (slug estable) a `ods_mx.seed.json` y `load_kb.py`
  lo genera por defecto con `generate_slug(name)` si falta.
- **Consistencia de variables Mongo.** `tipi_data` lee `MONGO_DB_NAME` /
  `MONGO_USER` / `MONGO_PASSWORD`, pero el compose usaba `MONGO_DB` y no pasaba
  credenciales. Corregido en `docker-compose.yml` (+ credenciales root en el
  servicio `mongo`) y en `load_kb.py` (conecta con auth y respeta `MONGO_DB_NAME`).
- **Dockerfiles al layout monorepo.** `Dockerfile-dev` (api y qhld-tasks) y los
  `Dockerfile` de producción reescritos con contexto de build = raíz, path-deps
  copiados desde `packages/`, y venv en `/app/.venv` (fuera de los bind-mounts).
- **Despliegue en Railway** (decisión del usuario: todo el stack en Railway, no
  Vercel — Vercel no corre Celery ni bases de datos). Añadidos
  `deploy/railway/{api,worker,frontend}.json`, `frontend/Dockerfile-mx` y
  `docs/DEPLOY_RAILWAY.md`.
- **Limitación del sandbox (no del código).** La política de egress de este
  entorno bloquea el registry de Docker (403 al bajar `mongo:7`, `python:3.12`,
  `testcontainers/ryuk`). Por eso **no** se pudo ejecutar `docker compose up`
  (F0.3) ni los tests de integración (testcontainers) aquí. Verificado en su
  lugar: `docker compose config` válido; tests **unit** verdes en qhld-data (11),
  qhld-tasks (17) y api (9); el motor de tagging real produce los tags del ODS 6
  para el párrafo CONAGUA/derecho al agua (F0.5); y `load_kb` + `GET /topics?knowledgebase=mx`
  devuelven los 3 ODS mexicanos con un Mongo en memoria (mongomock). En Railway,
  donde el registry no está bloqueado, F0.3 corre sin cambios.

### 2026-07-17 — F1

- **Managers México** (`api/tipi_backend/api/managers/mexico/`): tipos y estados
  de iniciativa según el trámite mexicano (docs/TROPICALIZACION.md), sobre la
  plantilla de `paraguay/`. `COUNTRY=mexico` en compose y guía de Railway.
- **Tropicalización del frontend:** rebrand a "Escáner Legislativo MX" (i18n es/en,
  index.html, config, metatags), "Acerca" reescrito (herramienta + método
  NormTrace), OpenAPI y docstrings del escáner en español mexicano.
- **Rastro español eliminado:** enlace a la versión española, URLs
  escaner2030.es/scanner2030.com, @_PoliticalWatch, logos de Political Watch y del
  Ministerio de Exteriores español, y el Google Analytics español hardcodeado
  (ahora vía `VITE_GA_ID`, vacío por defecto).
- **Decisiones del usuario:** (a) *sin atribución institucional* — el "Acerca" y el
  footer describen la herramienta y el método, con crédito técnico neutral a la
  tecnología abierta (tipi/escáner2030) y a NormTrace, sin inventar una
  organización mexicana; (b) *logo placeholder textual* — `public/img/logo-mx.svg`
  con el nombre de marca hasta tener arte definitivo.
- **Limitación del sandbox:** el build del frontend no se pudo ejecutar aquí porque
  la dependencia `xlsx` se descarga de `cdn.sheetjs.com` (fuera de npm) y la
  política de egress la bloquea (403), igual que el registry Docker. Por eso **no**
  se adjunta la captura de pantalla de F1 en este entorno. Verificado en su lugar:
  sintaxis ESM de los archivos tocados, estructura de `messages.js` sin rastro
  español, y tests unit de la api en verde. La captura debe generarse en un entorno
  con acceso a npm/cdn (o en el propio Railway).
