# Arquitectura: cómo funciona el stack y dónde se inserta NormTrace

## 1. El stack tipi tal como llega de Political Watch

Cinco componentes, cada uno con un papel claro:

**`frontend/` (escaner2030.es).** SPA Vue 3 + Vite + Pinia. No contiene lógica de
análisis. `src/api/index.js` define toda la superficie que consume:
`GET /topics/`, `POST /tagger/` (multipart: `text`, `file`, `knowledgebase`),
`GET /tagger/result/{taskID}` (polling cada 3 s si el backend respondió
`status: PROCESSING`), `POST /scanned/` (guardar escaneo con caducidad). El
knowledgebase que pide viene de `VITE_KNOWLEDGEBASE` (`.env`). Los nombres,
colores e iconos de los 17 ODS están fijos en `src/config/index.js` y los
SVG en `public/img/topics/`. La misma base de código sirve dos despliegues
(escaner2030.es y scanner2030.com) cambiando solo `.env`: el multi-país ya es
un patrón soportado.

**`api/` (qhld-backend, FastAPI).** El endpoint del escáner es
`tipi_backend/api/endpoints/tagger.py`. Flujo de `extract()`: extraer texto del
upload (pdfminer, python-docx, antiword, python-pptx) → cargar todos los tags de
Mongo con `get_tags()` (cache ~5 min) → si el texto supera `TAGGER_MAX_WORDS`,
despachar como tarea Celery y devolver `task_id`; si no, correr síncrono →
`filter_tags()` deja solo los del knowledgebase pedido. También sirve el resto
del universo parlamentario (diputados, iniciativas, votaciones, huella) con
managers por país en `tipi_backend/api/managers/{spain,paraguay,andorra}/`.

**`packages/qhld-tasks/`.** El motor de matching vive aquí:
`tipi_tasks/tagger.py::extract_tags_from_text(text, tags)`. Une líneas, corta el
texto por `"."` en oraciones, y por cada oración corre `regex.findall` con cada
tag compilado; acumula conteos por (topic, subtopic, tag). Es todo: frecuencia
de vocabulario curado. Sin lematización, sin semántica, sin negaciones.

**`packages/qhld-data/`.** Modelos Mongo (mongoengine/pydantic) y repositorios.
El diccionario es la colección `topics`: documentos
`{name, shortname, description, knowledgebase, public, tags: [{tag, subtopic, regex, shuffle}]}`.
`repositories/tags.py::compile_tag()` compila cada regex case-insensitive y, si
`shuffle: true`, parte la regex por `.*`/`.*?` y genera todas las permutaciones
de las partes (co-ocurrencia en cualquier orden dentro de la oración). La
taxonomía es de tres niveles: topic (ODS) → subtopic (meta) → tag (concepto).

**`engine/` (qhld-engine).** Pipeline batch para poblar el sistema: extractores
por país (`qhld_engine/extractors/{spain,paraguay,andorra}/`), etiquetado masivo
(`tagger/tag_initiatives.py`: etiqueta título + cuerpo de cada iniciativa,
descarta ocurrencias únicas, calcula `topic_alignment`, guarda y dispara
alertas), huella por diputado/grupo (`footprint/`), estadísticas (`stats/`).

Dependencias internas: `api` y `engine` dependen de `qhld-data` y `qhld-tasks`;
`qhld-tasks` depende de `qhld-data`. En este monorepo ya están recableadas por
ruta local editable en `[tool.uv.sources]`.

## 2. La capa NormTrace: qué añade y por qué

El motor tipi responde "¿de qué habla este texto?". NormTrace responde "¿qué
estructura jurídica crea?": qué actor queda obligado o facultado, con qué
procedimiento, con qué coordinación entre órdenes de gobierno, con qué sanción o
salvaguarda, en qué nivel de fuente formal, y qué tipo de brecha presenta
(tipología de 10 tipos en `normtrace/00_project/methodology_note.md`).

Activos reutilizables del directorio `normtrace/`:

- `02_country_legal_brains/mexico/mexico_legal_system_profile.md`: arquitectura
  constitucional, jerarquía normativa, distribución de competencias, gobernanza
  sanitaria. Contexto de sistema para el LLM.
- `02_country_legal_brains/mexico/mexico_legal_reasoning_rules.md`: reglas de
  decisión (categorías de anclaje A–D, escala 0–5, reserva de ley, cautelas).
  Rúbrica de codificación.
- `02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md`:
  estructura de documentos legislativos mexicanos (Título/Capítulo/Artículo/
  Fracción/Inciso/Transitorios, numeración "bis/Quater"), convenciones de cita,
  patrones de extracción de actores/competencias/obligaciones (§4) y marcadores
  lingüísticos de efecto jurídico (§5: "corresponde a", "son atribuciones de",
  "deberá", "se coordinará"). §2 y §4–5 son convertibles a reglas deterministas.
- `03_tables/`: datos codificados del piloto RSI (corpus mexicano indexado,
  110 disposiciones codificadas, 80 mapeos obligación↔disposición, registro de
  18 actores de gobernanza sanitaria con base legal). El registro de actores
  sirve como gazetteer de vinculación de entidades.
- `04_outputs/exports/data_package_v0_1/schemas/*.schema.json`: contrato de
  salida validable para cada tabla.

## 3. El pipeline fusionado

```
POST /tagger/ {text|file, knowledgebase: "mx", deep: true|false}
  │
  ├─ Etapa 1 — regex (existente, sin cambios)
  │    extract_tags_from_text → topics + tags + conteos
  │    función: filtro de recuperación barato y ruteo temático
  │
  ├─ Etapa 2 — segmentación jurídica (nueva, determinista)
  │    packages/legal-segmenter: parser por estructura mexicana
  │    entrada: texto plano; salida: unidades {unit_id, tipo, número, texto}
  │    unit_id estable estilo MX-<ley>-art<N>-frac<M> (mismo esquema de ids
  │    que usa normtrace/03_tables/country_legal_mapping)
  │    Si el documento no es texto legal estructurado (discurso, plan),
  │    degrada a párrafos con ids posicionales.
  │
  ├─ Etapa 3 — codificación NormTrace (nueva, LLM, asíncrona)
  │    solo si deep=true; tarea Celery aparte (cola "normtrace")
  │    por cada unidad que disparó tags en la etapa 1:
  │      prompt = extractos del cerebro jurídico + reglas + unidad + tags
  │      salida JSON validada contra esquema derivado de
  │      mexico_legal_provisions.schema.json:
  │      {unit_id, actor_mentioned, power_granted, duty_created,
  │       procedure_created, coordination_mechanism, enforcement_or_sanction,
  │       rights_safeguard, source_level, gap_type, confidence_level,
  │       review_status}
  │    coste controlado: N unidades × 1 llamada; cachear por hash de unidad
  │
  └─ Etapa 4 — respuesta
       resultado etapa 1 (compatible con frontend actual)
       + bloque `structural` opcional con las unidades codificadas
```

Puntos de inserción concretos en el código:

1. `api/tipi_backend/api/endpoints/tagger.py::extract()` — aceptar parámetro
   `deep`; tras el tagging regex, encolar la tarea NormTrace y devolver
   `normtrace_task_id` junto al resultado rápido.
2. `packages/qhld-tasks/tipi_tasks/` — nuevo módulo `normtrace.py` con la tarea
   Celery (cola separada para no bloquear el tagger).
3. `engine/qhld_engine/tagger/tag_initiatives.py::tag_initiative()` — tras
   `add_tag(...)`, para iniciativas con etiquetas de interés, encolar la misma
   codificación y guardar el subdocumento `analysis` en la iniciativa. La huella
   de `footprint/compute_footprint.py` muestra el patrón para agregar después
   un "perfil estructural" por legislador o comisión.
4. Frontend — `src/components/` nuevo panel junto a `scanner-table.vue` que
   pinta el bloque `structural` (tabla unidad → actor → deber → brecha, con
   badge de confianza y estatus de revisión).

## 4. Ingesta México (fase posterior al escáner)

Plantilla: `engine/qhld_engine/extractors/paraguay/` (basado en API, más limpio
que el scraper de España). Fuentes, por orden de facilidad:

- **Gaceta Parlamentaria** (`gaceta.diputados.gob.mx`): HTML estático, URLs
  predecibles `/Gaceta/{legislatura}/{año}/{mes}/{YYYYMMDD}[-anexo].html`,
  índice con anclas `a.Indice` → `#IniciativaN`, texto completo de cada
  iniciativa inline. Codificación Latin-1. Autor/partido/materia vienen en el
  string del título: parsear con regex.
- **LeyesBiblio** (`diputados.gob.mx/LeyesBiblio/`): ~330 leyes vigentes, PDF y
  DOC por ley, fecha de última reforma DOF por fila; ideal para detectar
  reformas por diff de fechas.
- **SIL** (`sil.gobernacion.gob.mx`): estatus de iniciativas; el reporte de
  iniciativas del Ejecutivo tiene export XLS. Ojo: servir por http, el https
  redirige al http.
- Managers nuevos: `api/tipi_backend/api/managers/mexico/` (tipos y estados de
  iniciativa mexicanos), siguiendo el patrón de `paraguay/`.
