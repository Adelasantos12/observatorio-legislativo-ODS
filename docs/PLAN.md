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

### 2026-07-17 — F2

- **Validador** `knowledgebase/validate_seeds.py`: valida el JSON, compila cada
  regex con el `compile_tag()` real y avisa de `shuffle` con explosión de
  permutaciones. Sale con código != 0 ante errores.
- **Diccionario 17 ODS** (`seeds/ods_mx.seed.json`): ampliado de 3 a 17 topics
  (74 tags) con vocabulario institucional mexicano (CONEVAL, SEGALMEX, SEP,
  INMUJERES, CFE/SENER, STPS/LFT, CONAHCYT, CONAPRED/INPI/INM, SEDATU/CONAVI,
  PROFECO/LGPGIR, LGCC/INECC, CONAPESCA, CONAFOR/CONANP/SEMARNAT, FGR/SNA/CNDH/INAI,
  AMEXCID/INEGI/SHCP). Nombres de topic alineados con las claves de `config/index.js`
  del frontend para que hereden color e icono ODS.
- **Segundo marco (RSI)** `seeds/rsi_mx.seed.json`, generado de forma reproducible
  por `knowledgebase/gen_rsi_seed.py` desde
  `normtrace/03_tables/international_obligations/IHR-2005_obligations_domestic-anchoring.csv`
  (se lee, no se muta): 8 topics = Títulos del RSI, 45 subtopics = artículos,
  45 tags = obligaciones con regex **en español** (el CSV está en inglés) para
  detectar menciones en textos mexicanos (Centro Nacional de Enlace, vigilancia
  epidemiológica/SINAVE, notificación a la OMS, capacidades básicas, etc.).
- **Aceptación verificada:** validador en verde (0 errores/avisos en ambos seeds);
  escaneo de un párrafo tipo iniciativa de la Gaceta produce etiquetas plausibles
  en 5 ODS (3, 5, 10, 13, 15) y demuestra multi-marco al detectar además 2 Títulos
  del RSI. `load_kb` carga cada seed por su knowledgebase (`mx` y `rsi_mx`).

### 2026-07-17 — F3

- **Paquete `packages/legal-segmenter`** (Python puro, sin dependencias): parser
  determinista de estructura legislativa mexicana. Entrada texto plano o markdown;
  salida unidades `{unit_id, unit_type, number, heading, text, parent_id}`. Maneja
  Libro/Título/Capítulo/Sección/Artículo (incl. numeración "3o.", "Bis/Ter/Quáter",
  "166 Bis 17"), Fracción (romanos, "IV Bis 1"), Inciso, Apartado, artículos
  nominales ("Artículo Único"), Transitorios, y fallback a párrafos para texto no
  estructurado. Ids estables y jerárquicos (p. ej. `MX-LGS-art3-fracII`).
  **Invariante:** cada línea se asigna a una unidad, la concatenación reproduce el
  documento (sin pérdida de texto).
- **Tests** (`tests/unit/test_segmenter.py`, 13 casos): fragmento sintético,
  **fragmento real de la LGS** e iniciativa tipo Gaceta; jerarquía, bis/ter,
  transitorios, ids estables, preservación y fallback. Verificado además sobre la
  **LGS completa**: 2334 unidades (653 artículos, 1094 fracciones), texto preservado
  al 100 % e ids únicos.
- **Integración `segment=legal`** en `POST /tagger/` (etapa 2): añade el bloque
  `segmentation` con `units_total`, `units_with_tags` y los conteos de tags por
  unidad citable. `legal-segmenter` añadido como path-dep editable del api.
  Cubierto por dos tests de endpoint nuevos. Tests unit del api en verde (11).

### 2026-07-17 — F4

- **Esquema** `normtrace/schemas_runtime/unit_analysis.schema.json` (draft-07),
  derivado de `mexico_legal_provisions.schema.json` y las reglas de razonamiento:
  campos del pipeline (actor, deber/facultad, procedimiento, coordinación,
  sanción, salvaguarda) + `source_level` (anclaje A–D), `gap_type` (10 tipos),
  `anchoring_score` (0–5) y, obligatorios, `confidence_level` y `review_status`.
- **Abstracción LLM** `tipi_tasks/llm.py`: proveedores reales anthropic/openai por
  HTTP con la librería estándar (sin SDKs de pago). Proveedor por defecto `mock`.
- **Codificador** `tipi_tasks/normtrace.py`: tarea Celery `normtrace.analyze_units`
  en cola `normtrace`. Modo `mock` = codificador heurístico determinista basado en
  los marcadores lingüísticos del cerebro (§5): extrae actor/deber/facultad/
  coordinación/sanción/salvaguarda sin llamar a ningún LLM ni requerir clave
  (queda `confidence_level=low`, `review_status=needs_human_review`). Modo real:
  prompt con extractos del cerebro jurídico (leídos de los .md, no parafraseados),
  parseo de JSON, **validación contra esquema con un reintento** y, si nada valida,
  `needs_human_review`. **Caché** por hash(unidad+versión de prompt) en Mongo con
  cliente de timeout corto (se autodesactiva sin Mongo). **Presupuesto**
  `NORMTRACE_MAX_UNITS` (default 50) → reporta `units_analyzed`/`units_skipped`.
- **Endpoint**: `POST /tagger/` acepta `deep=true` → añade `segmentation` y encola
  la codificación devolviendo `normtrace_task_id`; `GET /tagger/deep/{id}` devuelve
  el bloque `structural`. El worker consume `-Q celery,normtrace`; el cerebro y el
  esquema se hornean en la imagen (`COPY normtrace`).
- **Decisión / desviación:** el resultado deep se recupera en `GET /tagger/deep/{id}`
  (endpoint propio) en lugar de reutilizar `/tagger/result/{id}` del tagger, para no
  mezclar dos formas de resultado; el contrato de polling es equivalente.
- **Aceptación verificada:** escaneo deep de una iniciativa de salud intercultural
  → unidad codificada **válida contra esquema**, con actor ("la Secretaría de Salud")
  y deber ("deberá") identificados, coordinación y salvaguarda detectadas; **ninguna
  salida sin `review_status`**. Tests: qhld-tasks 24 unit (7 de normtrace), api 12
  unit (deep). Con `LLM_PROVIDER=mock` todo corre sin clave ni tokens.

### 2026-07-17 — F5

- **Componente `frontend/src/components/structural-panel.vue`** (junto a
  `scanner-table.vue`): tabla por unidad jurídica (unidad → actor → deber/facultad
  → procedimiento → coordinación → tipo de brecha), badge de `confidence_level`
  (baja/media/alta con color) y `review_status` visible en cada fila. Aviso fijo con
  el **descargo exacto** de `docs/TROPICALIZACION.md` §Descargos (análisis
  estructural). Estado de carga (`tipi-loader`) mientras llega el análisis profundo,
  y botón **Imprimir / Exportar PDF** (impresión del navegador con hoja de estilos de
  impresión) para el brief.
- **Wiring** en `Scanner.vue` + `api/index.js`: toggle "Análisis estructural
  (NormTrace)"; con deep activo, `annotate` envía `segment=legal` + `deep=true`, y
  tras el resultado rápido sondea `GET /tagger/deep/{id}` (hasta ~3 min) para pintar
  el bloque `structural`. i18n es/en.
- **Mock mejorado:** la lista de actores del codificador heurístico se amplió con
  nombres institucionales completos (Comisión Nacional del Agua, INMUJERES, INPI…)
  para una extracción más útil.
- **Limitación del sandbox:** el build de la SPA no corre aquí (la dependencia
  `xlsx` se baja de `cdn.sheetjs.com`, bloqueado por egress). Verificado: sintaxis
  ESM de los archivos, estructura i18n y descargo exacto, y **contrato de datos** del
  panel calzando con la salida real de `/tagger/deep`. La captura de aceptación
  (`docs/img/f5_structural.png`) es un **render estático fiel del componente con
  datos reales** de la codificación; el flujo en navegador se valida en Railway o en
  un entorno con acceso a npm/cdn.

### 2026-07-17 — F6

- **Parser de la Gaceta** `engine/qhld_engine/extractors/mexico/gaceta.py`
  (determinista, sin red): `build_url` (rutas `/Gaceta/{leg}/{año}/{mes3}/{YYYYMMDD}[-anexo].html`),
  `parse_gaceta` (índice `a.Indice` → `#IniciativaN`, texto inline por ancla) y
  `parse_title` (regex autor/partido). `fetch_gaceta` aísla la descarga (Latin-1).
- **Módulo extractor `mexico/`** modelado sobre `paraguay/`: `InitiativesExtractor`
  recorre la página del día y anexos, parsea y crea/actualiza `Initiative`;
  `members`/`groups` no-op (la Gaceta no expone esos feeds; la autoría sale del
  título); `initiatives_status` alineado con el manager de la API. Se activa con
  `MODULE_EXTRACTOR=mexico` + `GACETA_DATE`/`GACETA_LEGISLATURA`.
- **Hook NormTrace batch** en `tagger/tag_initiatives.py`: tras etiquetar, si
  `NORMTRACE_DEEP=true` y la iniciativa tiene tags, segmenta su cuerpo, codifica las
  unidades con tags y guarda el bloque `structural` en `extra['analysis']`.
  **Desactivado por defecto** (el etiquetado no requiere LLM salvo que se active).
- **Mejora del mock:** el emparejamiento de marcadores des-acentúa ambos lados
  ("Secretaría" vs "Secretaria"), robusto para el texto Latin-1/OCR de la Gaceta.
- **Tests** `tests/unit/test_mexico_gaceta.py` (7): `build_url`, `parse_title`,
  parseo de índice+cuerpo con autor/partido, fallback sin índice, e ingesta con el
  repositorio mockeado. Suite unit del engine en verde (111).
- **Limitación del sandbox:** el scraping en vivo de gaceta.diputados.gob.mx no se
  ejecuta aquí (egress/Mongo); el parser y la ingesta se verifican con fixtures. F6
  es opcional y no es prerequisito del escáner interactivo.

### 2026-07-17 — Fase H v2 (Huella 2030) — Módulo A backend

- **Assets** colocados: CSV semilla → `normtrace/03_tables/legislative_mapping/`,
  referencia de diseño → `docs/referencia/`.
- **Catálogos** `normtrace/03_tables/catalogos/`: `ods.json` (17 ODS con nombre es +
  color oficial, de la referencia) y `metas.json` (169 metas: código+ods, nombre
  corto de las 45 usadas; `nombre_oficial_es: null` — no se inventan redacciones ONU).
- **Datos** `executive_initiatives`: modelo + repositorio en qhld-data
  (`upsert_preserving_coding` no pisa `ods_*`/`metas`/`tema`/`confianza`);
  importador `knowledgebase/load_executive.py` (id `EJE-2024-2030-{num}-{seccion_slug}`).
- **API** `GET /huella/ejecutivo`, `/ejecutivo/iniciativas`, `/ejecutivo/iniciativas/{id}`
  (agregación pura y testeable, caché 1 h). `COPY normtrace` añadido a la imagen del api.
- **Verificado contra la semilla:** 82 iniciativas, 76 aprobadas, 95% con
  correspondencia ODS, 17 leyes nuevas, ODS 16 dominante, 45 metas distintas con
  16.6 (23) y 16.3 (14) a la cabeza; end-to-end con mongomock. api 12 tests unit verdes.
- **Nota:** el criterio 2 dice "ODS 16 con 40 menciones"; el dato real de la semilla
  (y de la referencia) es **44** (35 principal + 9 secundario). La agregación reproduce
  la referencia con fidelidad; el "40" del brief es aproximado.
- **Pendiente de la fase:** scraper SIL (H.5), Módulo B Minutas (H.6), identidad +
  vistas Vue (H.7), tests con fixtures + capturas (H.8).

### 2026-07-18 — Fase H v2 — Módulo A frontend, Módulo B (Minutas) e identidad

- **Identidad "Huella 2030" (guinda)** `frontend/src/styles/identity.css`: tokens
  guinda (`--accent:#9f2241`), modo claro/oscuro (prefers-color-scheme + `data-theme`),
  barras en guinda y color oficial ODS **solo** en chips pequeños. Aplicada a las
  tres superficies nuevas del portal; el escáner de texto queda intacto (regla
  "no tocar el motor").
- **Módulo A — vistas Vue:** `HuellaView.vue` (KPIs, correspondencia por ODS,
  metas frecuentes, presentación por trimestre, tabla filtrable) y
  `ExpedienteView.vue` (ficha con ODS principal/secundarios, metas con
  "denominación abreviada" cuando no hay redacción oficial, confianza, descargo).
  Endpoint `GET /huella/catalogos` sirve `ods.json`+`metas.json`. Rutas `/huella`
  y `/expedientes/:id`; menú "Huella 2030".
- **Módulo B — Minutas (H.6):** modelo `Minuta` + repo `Minutas` (colección
  `minutas`, `upsert_preserving_coding` conserva codificación **y** origen).
  Scraper `engine/.../iniclave_minutas.py` (parser sin red, clave estable
  `CD-LXVI-II-2P-139`, CLI `qhld minutas`). **Atribución de origen SOLO por
  coincidencia** con iniciativas del Ejecutivo; lo no documentado queda
  "por documentar" — **nunca se inventa la bancada**. Agregado
  `aggregate_minutas`: *aportación por origen* descriptiva, **orden alfabético
  (no ranking)**, bucket "por documentar" al final. Endpoints `/minutas`,
  `/minutas/lista`, `/minutas/{id}`; vista `MinutasView.vue` + ruta/menú.
- **Semilla `minutas_ods.csv`** (editable): 76 minutas de origen **Ejecutivo
  Federal** (subconjunto real de iniciativas aprobadas, origen de autoría
  inequívoco). Las minutas de grupos parlamentarios se documentan luego vía el
  iniclave; hasta entonces el panorama es parcial y así se declara en la UI.
- **Scraper SIL (H.5):** `engine/.../sil_ejecutivo.py` clasifica cada iniciativa
  en sección (Aprobadas/Pendientes/Desechadas/Retiradas) derivándola del estatus,
  extrae fecha DOF y hace `upsert_preserving_coding`. CLI `qhld sil-ejecutivo`
  (`--html-file` para operación offline). Reproduce el desglose del piloto
  (76/4/1/1).
- **Tests (H.8):** engine unit `test_mexico_sil_ejecutivo.py` (6) y
  `test_mexico_iniclave_minutas.py` (6); api unit `test_huella_aggregate.py` (3,
  contra la semilla: 82/76/ODS 16) y `test_minutas_aggregate.py` (4: orden
  alfabético no-ranking, bucket por-documentar, 76 Ejecutivo Federal). Suites en
  verde: engine 122 unit, api 19 unit. End-to-end con mongomock: sync SIL y sync
  minutas preservan codificación/origen y atribuyen correctamente.
- **Capturas** `docs/img/h_huella.png` y `docs/img/h_minutas.png` (render estático
  con la identidad guinda alimentado por la semilla real).
- **Limitación del sandbox:** el scraping en vivo (SIL, iniclave) no se ejecuta
  aquí (egress); parsers e ingesta se verifican con fixtures y mongomock.
- **Nota de despliegue:** el servicio *worker* de Railway falla en deploy por
  configuración de entorno (falta wirear `BROKER`/`RESULT_BACKEND` a la referencia
  de Redis; el default `redis://redis:6379` no resuelve en Railway), no por el
  código de esta fase (los modelos nuevos importan limpio y `uv lock --check` pasa).

### 2026-07-18 — Adenda nivel 2 — protocolo NormTrace y ejemplo dorado

- **Assets dorados:** `lga_ods6_mapeo_normtrace.csv` en
  `normtrace/03_tables/legislative_mapping/gold/` (solo lectura, 34 registros) y
  brief `lga_ods6_brief_normtrace.md` **restaurado** en `normtrace/04_outputs/briefs/`
  (se había borrado por error en un commit previo; recuperado del árbol git). Un
  CSV duplicado que quedó traspapelado en `briefs/` (byte-idéntico al dorado) se
  eliminó: el canónico vive en `gold/`.
- **Esquema versionado** `normtrace/schemas_runtime/normtrace_mapping.schema.json`
  derivado de las columnas del dorado: `estandar, disposicion, rol_correspondencia,
  cobertura, 6×*_fit, tipo_brecha, nota` + metadatos de corrida (`nivel_revision`
  validado_autora|automatico_preliminar, fecha, modelo, version_prompt, fuente_texto).
- **Motor** `qhld_engine/normtrace/`: `gold` (carga + hash), `frameworks` (marco
  ods6 = 8 metas + bloques OG15/PIDESC/cadena federal), `citations` (resolución
  programática, expande rangos y plurales), `schema` (validación), `runner`
  (descarga LeyesBiblio → segmenta F3 → codifica por estándar; `mock` = línea base
  preliminar sin clave, proveedor real vía la abstracción F4), `evaluator`
  (5 umbrales). CLI `qhld normtrace-run` y `qhld normtrace-eval`.
- **Candado de calidad:** `normtrace-eval` sin `--run` hace autochequeo del dorado
  (resolución de citas 100% y cobertura 100%) — así CI verifica el contrato sin
  clave LLM; con `--run` aplica los 5 umbrales y sale con error si reprueba. Test
  `test_normtrace_gold.py` reprueba si cambia el hash del CSV dorado (solo la
  autora lo cambia, con nota aquí). Workflow `.github/workflows/normtrace-eval.yml`.
- **Verificado:** autochequeo del dorado APRUEBA los 5 umbrales; una corrida `mock`
  (offline) es schema-válida, nace `automatico_preliminar` y REPRUEBA el gate
  (línea base conservadora ≠ dorado) — honesto: solo LLM real o validación de la
  autora pasa. engine unit 129 verdes.
- **Portal (§4):** API `/normtrace/expediente/{id}` (dorado validado para la LGA
  —iniciativa 54—, preliminar de Mongo para el resto), `/normtrace/brief/{nombre}`
  (con guarda anti-traversal), KPI `iniciativas_con_normtrace` (1 de 82). Ficha de
  expediente con sección "Análisis NormTrace": tabla por estándar (fits como puntos
  llenos/medios/vacíos), badge grande validado/preliminar, brief renderizado y
  descargo fijo. Callout de vitrina en el dashboard. Captura
  `docs/img/h_expediente_normtrace.png`. api unit 24 verdes.

### 2026-07-21 — Adenda v3 — 139 minutas de la LXVI + rediseño narrativo

**Parte A — minutas completas.**
- Semilla cruda `minutas_lxvi_raw.csv` (139 minutas: 62 DOF, 75 en revisora, 2
  devueltas; año I 39, II 100; secuencia 1–139 sin huecos) + `matches_minutas_
  ejecutivo.json` (81 cruces con score). Modelo `Minuta` ampliado (titulo,
  observaciones, estatus, pdfs, origen_tipo, grupos_parlamentarios, nivel_revision).
- Scraper `iniclave_minutas` reescrito al esquema real; CLI `iniclave-minutas` con
  verificación de secuencia (reporta huecos, no los silencia).
- Codificación §A2 (`normtrace/minutas_coding`): herencia de las 81 (confianza =
  origen si score ≥ 0.75, media si 0.62–0.75; 28 a verificación manual) + LLM para
  las 58 (mock = línea base sin inventar). Export a `minutas_ods.csv`; el importador
  preserva filas `validado_autora`. CLI `minutas-coding`.
- Atribución §A3 (`normtrace/atribucion`): job incremental `normtrace-atribucion`
  que lee el grupo parlamentario del dictamen; lo no parseable queda "por
  documentar", nunca inventado.
- API `/minutas`: agregado por origen (no ranking) + ODS/meta/estatus/año, KPI
  "atribución documentada: X de 139", filtros nuevos.

**Parte B — /huella data essay (scrollytelling).**
- `/huella` reescrita como historia en 6 escenas: gráfico sticky +
  IntersectionObserver (sin dependencias). Unit chart de 221 cuadritos (139
  minutas guinda + 82 iniciativas doradas) que se reagrupan por transición CSS:
  retícula → estatus → barras por ODS (16 dominante) → singulares (agua, sin
  correspondencia) → caso del agua (mini ficha NormTrace + enlace) → explorador.
  Toda cifra del dato vivo; fallback sin animación (escenas apiladas),
  prefers-reduced-motion y layout móvil. Colores ODS solo en chips, prosa 18–20px.
- Verificado: herencia determinista de las 81 (offline), pipeline de las 58 y
  atribución quedan listos para clave/red; render estático de las 6 escenas
  (`docs/img/h_story.png`). Suites: engine 135, api 26, qhld-data 11 unit.
- **Sandbox:** el LLM real (58 minutas) y la descarga de dictámenes (atribución)
  necesitan `LLM_API_KEY`/egress; corren en despliegue con los CLIs anteriores.
  **Jobs diarios sugeridos:** `qhld iniclave-minutas`, `qhld minutas-coding`,
  `qhld normtrace-atribucion` (worker/cron).
