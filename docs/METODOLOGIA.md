---
título: "Huella 2030: trazado normativo por capas para el análisis legislativo asistido por IA"
subtítulo: "Del protocolo NormTrace al escáner de la Agenda 2030 en México"
autora: "Adela B. Santos Domínguez"
orcid: "0000-0002-8691-0544"
versión: "0.1 — borrador metodológico para revisión de la autora"
estado: "Preliminar. No citar como autoridad jurídica."
licencia: "Contenido NormTrace CC BY 4.0; plataforma sobre tecnología tipi/escáner2030 (AGPL-3.0)."
---

# Huella 2030: trazado normativo por capas para el análisis legislativo asistido por IA

## Resumen

El etiquetado temático responde a la pregunta "¿de qué habla un texto?"; no responde "¿qué estructura jurídica crea?". Este trabajo documenta la metodología de **Huella 2030**, un instrumento de análisis de iniciativas y leyes mexicanas frente a la Agenda 2030 que separa esas dos preguntas y las resuelve en capas sucesivas. La metodología aplica el protocolo **NormTrace** —un método hermenéutico-estructural de trazado del anclaje normativo, no de coincidencia de palabras— sobre un canal de procesamiento de cuatro capas: (1) etiquetado léxico-temático por diccionario curado; (2) segmentación jurídica determinista en unidades citables; (3) codificación estructural por unidad (actor, deber o facultad, procedimiento, coordinación, sanción, salvaguarda, nivel de fuente, tipo de brecha); y (4) revisión ex ante de técnica legislativa y sistematización normativa (protocolo PAIL) contra un corpus de derecho vigente. La inteligencia artificial interviene como apoyo estructural acotado, no como autoridad: las capas deterministas corren como código, la capa de juicio se ciñe a la evidencia extraída y a las citas del corpus, y toda salida viaja con su nivel de confianza y su estatus de revisión. Ninguna salida constituye dictamen de cumplimiento. El documento describe la fundamentación doctrinal del trazado, la arquitectura por capas, el papel de la IA en cada una, los mecanismos de trazabilidad y validación, y las limitaciones.

**Palabras clave:** trazado normativo; técnica legislativa; sistematización normativa; Agenda 2030; análisis legislativo asistido por IA; anclaje normativo; México.

---

## 1. Problema y objetivo

Las herramientas de escaneo legislativo por vocabulario detectan presencia temática: cuentan coincidencias de términos curados y sitúan un texto respecto de un catálogo (aquí, los 17 Objetivos de Desarrollo Sostenible y sus metas). Esa señal es útil para recuperar y rutear, pero no dice nada sobre la estructura que el texto crea. Una iniciativa puede mencionar "salud" muchas veces y no obligar a ningún actor, no fijar procedimiento, no prever coordinación entre órdenes de gobierno y no proteger derecho alguno. El conteo de vocabulario no distingue entre una disposición operativa y una declaración de intención.

El objetivo de Huella 2030 es reconstruir, disposición por disposición, la arquitectura jurídica de un texto legislativo mexicano y hacerlo de forma **trazable, conservadora y auditable**: cada resultado remite a su cita fuente, la incertidumbre se declara en vez de ocultarse, y ninguna clasificación automática se presenta como veredicto. El instrumento no sustituye el juicio del especialista; produce una codificación preliminar que un ser humano valida.

Este objetivo hereda directamente el protocolo NormTrace, desarrollado y probado por primera vez en el dominio del derecho internacional de la salud (piloto NormTrace-IHR sobre el Reglamento Sanitario Internacional en México). La presente metodología traslada ese protocolo del mapeo obligación↔disposición al análisis de iniciativas legislativas frente a la Agenda 2030, y añade una capa de revisión ex ante de técnica legislativa.

---

## 2. Fundamentación doctrinal del trazado (NormTrace)

NormTrace es un método de **trazabilidad legal-institucional**: mapea cada obligación o materia a las disposiciones de derecho interno, los actores, las competencias y los procedimientos que constituyen su anclaje doméstico. Su carácter es hermenéutico y estructural, no de palabras clave: lee el texto por su sentido, su delegación, su estructura, sus omisiones y sus silencios (`normtrace/00_project/methodology_note.md`).

### 2.1 Categorías de anclaje

El método clasifica primero el **tipo** de instrumento normativo que sostiene una materia dentro del orden jurídico mexicano, en una jerarquía consistente con la arquitectura constitucional (`normtrace/02_country_legal_brains/mexico/mexico_legal_reasoning_rules.md`, §2):

- **A. Anclaje estatutario** — ley en sentido formal, con fuerza suficiente para crear competencias, obligaciones, restricciones, procedimientos, derechos, sanciones o mecanismos de coordinación.
- **B. Anclaje reglamentario** — reglamento, reglamento interior, disposición administrativa general o norma técnica (NOM/NMX), siempre que exista habilitación legal en una ley; desarrolla y especifica, no crea competencias nuevas.
- **C. Anclaje administrativo** — acuerdo, lineamiento, protocolo o manual dentro de autorizaciones ya existentes; no puede generar obligaciones vinculantes para terceros ni medidas coercitivas.
- **D. Implementación operativa** — contenido técnico u organizativo ejecutable dentro de competencias ya atribuidas, sin nuevo instrumento normativo.

### 2.2 Escala de anclaje (0–5)

Sobre esa tipología, cada disposición recibe una puntuación de anclaje que refleja la calidad y especificidad de su base jurídica interna (`methodology_note.md`, §2):

| Nivel | Etiqueta | Descripción sintética |
|:---:|---|---|
| 0 | Sin anclaje identificable | Ninguna disposición del orden jurídico aborda la materia, ni siquiera de forma contextual. |
| 1 | Anclaje contextual indirecto | Existe una disposición general o tangencial; su relevancia es interpretativamente forzada. |
| 2 | Anclaje administrativo u operativo | Se aborda por instrumentos administrativos, sin desarrollo estatutario o reglamentario. |
| 3 | Anclaje estatutario parcial | Una disposición aborda la materia de forma incompleta: cubre parte, deja elementos sin definir o carece de reglamento. |
| 4 | Anclaje estatutario-administrativo fuerte | Base estatutaria más instrumento de desarrollo que cubren los elementos principales; las brechas restantes son secundarias. |
| 5 | Anclaje de implementación integrada | Marco coherente ley-reglamento-institución: mandato claro, actor designado, procedimiento, coordinación y control. |

**El puntaje es conservador.** Ante la duda entre dos niveles, se asigna el menor y se marca para revisión de especialista (`methodology_note.md`, §2). La escala mide el anclaje textual documentado en el corpus disponible; no mide desempeño operativo, aplicación efectiva ni cumplimiento.

### 2.3 Tipología de brechas

Cuando el anclaje es incompleto o ausente, la naturaleza del déficit se clasifica con una tipología de diez tipos, no excluyentes entre sí (`methodology_note.md`, §3; `mexico_legal_reasoning_rules.md`, §6): silencio legal, ambigüedad de competencia, anclaje solo administrativo, brecha procedimental, brecha de coordinación, brecha de implementación federal, brecha de salvaguarda de derechos, brecha de control, brecha presupuestaria o de capacidad, y necesidad de actualización.

### 2.4 Reglas de cautela para el sistema mexicano

La rúbrica incorpora guardarraíles derivados de la arquitectura constitucional, no elecciones interpretativas (`mexico_legal_reasoning_rules.md`, §7). Entre ellas: no inferir suficiencia legal de la mera existencia de una facultad general; no suponer que una NOM crea competencias que exigen forma estatutaria; no equiparar un acuerdo administrativo a un mandato legislativo; no tratar la práctica administrativa como anclaje normativo fuerte; no confundir competencia federal con capacidad de implementación estatal; y marcar para revisión humana obligatoria cuando la materia afecta derechos, datos personales sensibles, medidas restrictivas, o poblaciones en movilidad. La presencia de un solo indicador de necesidad de anclaje estatutario prevalece sobre cualquier apariencia de simplicidad operativa.

### 2.5 Trazabilidad y estatus de revisión

Toda fila de las tablas de mapeo debe ser trazable a una disposición concreta (instrumento, artículo, párrafo) o a una nota de incertidumbre que explique qué se buscó y por qué no se identificó anclaje. Las filas sin trazabilidad no se consideran completas, y el campo `review_status` permanece en `preliminary` hasta que se confirme la trazabilidad de la fuente (`methodology_note.md`, §4). Este principio —la cita fuente viaja con cada registro y la incertidumbre se declara— es el eje del método y se conserva íntegro en el instrumento de software.

### 2.6 El "cerebro jurídico"

El mapeo correcto exige reconstruir antes la lógica constitucional y administrativa por la que se organiza y delega la autoridad legal. Para México, NormTrace codifica un **perfil de sistema jurídico** con nueve componentes (arquitectura constitucional y derechos; efecto de incorporación de tratados, arts. 133 y 1° CPEUM; jerarquía normativa; federalismo y distribución de competencias en salud; estructura de gobernanza; administración pública y delegación; tipos de instrumento reglamentario; patrones de técnica legislativa; y mecanismos de control). Este perfil gobierna las decisiones de mapeo y previene falsos positivos por coincidencia terminológica entre el lenguaje internacional y el texto estatutario doméstico (`normtrace_ihr_methodology_full.md`, Etapa 3).

El cerebro jurídico se materializa en tres documentos, que son contenido académico de la autora y fuente de verdad del método:

- `mexico_legal_system_profile.md` — perfil del sistema jurídico (contexto de sistema).
- `mexico_legal_reasoning_rules.md` — reglas de decisión: categorías de anclaje, escala, brechas, reglas de cautela (rúbrica de codificación).
- `mexico_legal_document_structure_patterns.md` — estructura de los documentos legislativos mexicanos y marcadores lingüísticos de efecto jurídico (base de la segmentación y la extracción deterministas).

Regla operativa: cuando una capa del instrumento necesita un extracto del cerebro jurídico, lo construye leyéndolo en tiempo de ejecución o de compilación; no se copian fragmentos parafraseados a mano.

---

## 3. El instrumento: arquitectura por capas

Huella 2030 se construye sobre el stack tipi (escáner2030 de Political Watch, AGPL-3.0) e inserta el protocolo NormTrace como etapas nuevas, sin reescribir el motor de etiquetado existente. El canal completo procesa un texto (pegado, o extraído de PDF, imagen, TXT, DOCX, DOC o PPTX) en cuatro capas sucesivas, cada una con un papel epistémico distinto y un grado de intervención de IA creciente y acotado.

```
texto / iniciativa
   │
   ▼
[Capa 1] Etiquetado léxico-temático (regex, diccionario ODS curado)
   │   "¿de qué habla?" — presencia temática, recuperación y ruteo
   ▼
[Capa 2] Segmentación jurídica determinista (estructura mexicana)
   │   corte por Artículo/Fracción/Inciso/Transitorios → unidades citables
   ▼
[Capa 3] Codificación estructural NormTrace (por unidad)
   │   actor, deber/facultad, procedimiento, coordinación, sanción,
   │   salvaguarda, nivel de fuente, tipo de brecha → valida contra esquema
   ▼
[Capa 4] Revisión ex ante PAIL (técnica legislativa y sistematización)
   │   43 verificaciones en 4 subcapas, contra corpus de derecho vigente
   ▼
resultado: presencia temática + panel estructural + dictamen preliminar
```

El principio de diseño es la **separación de responsabilidades**: cada capa responde una pregunta acotada y ninguna se presenta como más de lo que es. La capa 1 recupera, no evalúa; la capa 2 estructura, no interpreta; la capa 3 codifica de forma preliminar; la capa 4 revisa técnica y sistematización, no dictamina cumplimiento.

---

## 4. Las capas en detalle

### 4.1 Capa 1 — Etiquetado léxico-temático

Un motor de coincidencia por expresiones regulares recorre el texto contra un diccionario curado de vocabulario institucional mexicano, organizado en tres niveles: tema (ODS) → meta (subtema) → etiqueta (concepto). Cada etiqueta es una expresión regular compilada; cuando se marca para ello, la regex se descompone por comodines y se generan todas las permutaciones de sus partes, de modo que la co-ocurrencia de conceptos se detecta en cualquier orden dentro de una oración.

Esta capa cuenta frecuencia de vocabulario curado. No hay lematización, semántica ni tratamiento de negaciones. Su salida —temas, etiquetas y conteos— es un filtro de recuperación barato y un mecanismo de ruteo temático. Indica **presencia temática, no evaluación de contenido**, y así se declara al usuario en toda la interfaz. La IA no interviene en esta capa: es determinismo puro sobre un diccionario que un equipo humano cura.

### 4.2 Capa 2 — Segmentación jurídica determinista

Un segmentador corta el texto según la estructura de los documentos legislativos mexicanos (Título/Capítulo/Sección/Artículo/Fracción/Inciso/Transitorios, con numeración "bis/ter/quáter"), a partir de los patrones documentados en `mexico_legal_document_structure_patterns.md`. Produce unidades citables con un identificador estable (por ejemplo, `MX-<ley>-art<N>-frac<M>`), bajo el mismo esquema de identificadores que emplean las tablas codificadas de NormTrace. Cuando el documento no es texto legal estructurado (un discurso, un plan), degrada a párrafos con identificadores posicionales.

La segmentación es enteramente determinista y corre como código. Su corrección importa porque toda capa posterior cita por unidad: un identificador estable es la condición de la trazabilidad. La extracción de PDF de la Gaceta introduce ruido característico (espacios dobles entre palabras por ausencia de kerning en la capa de texto; encabezados de artículo pegados a comillas de apertura cuando el texto reformado va entrecomillado; cláusulas de decreto sepultadas tras una exposición de motivos larga) que se normaliza como preprocesamiento del insumo, sin alterar la lógica del segmentador ni crear artículos falsos. Los PDF cuyo texto incrustado carece de tabla ToUnicode devuelven glifos sin mapear; el instrumento los detecta y recurre a reconocimiento óptico de caracteres (OCR) para recuperar el texto legible.

### 4.3 Capa 3 — Codificación estructural NormTrace por unidad

Por cada unidad relevante, el codificador reconstruye su estructura jurídica y devuelve un registro con los campos: actor mencionado, facultad otorgada, deber creado, procedimiento creado, mecanismo de coordinación, sanción o medio de exigibilidad, salvaguarda de derechos, nivel de fuente formal, tipo de brecha, nivel de confianza y estatus de revisión. La salida se valida contra un esquema JSON versionado (derivado del esquema de disposiciones de NormTrace); si el modelo devuelve algo que no valida, se reintenta o se marca el registro como `needs_human_review`.

La capa admite dos modos, ambos deterministas en su salida:

- **Modo por reglas (por defecto).** Un codificador heurístico local aplica marcadores lingüísticos de efecto jurídico —"corresponde a", "son atribuciones de", "deberá", "se coordinará", entre otros, documentados en `mexico_legal_document_structure_patterns.md`, §4–5— para extraer actor, deber o facultad y procedimiento sin llamar a ningún modelo de lenguaje. Es reproducible por construcción: el mismo texto produce el mismo resultado. Detecta señales de estructura jurídica; no interpreta.
- **Modo asistido por LLM.** Cuando se activa, un modelo de lenguaje codifica cada unidad recibiendo como contexto extractos del cerebro jurídico, la rúbrica de razonamiento, la unidad y sus etiquetas. La salida se valida contra el mismo esquema. La temperatura se fija en cero para estabilidad.

En ambos modos, cada registro conserva su cita fuente y viaja con `confidence_level` y `review_status`. La codificación es preliminar y asistida; requiere revisión de especialista, y así se declara.

### 4.4 Capa 4 — Revisión ex ante PAIL: técnica legislativa y sistematización

La capa PAIL (Protocolo de Análisis de Iniciativas Legislativas) revisa una iniciativa antes de su discusión: forma, redacción e inserción en el ordenamiento. Aplica un catálogo de 43 verificaciones organizado en cuatro subcapas:

- **Núcleo de triaje** — tipo de instrumento, partes presentes (exposición de motivos, articulado, régimen transitorio) y titularidad de la iniciativa.
- **Técnica legislativa** — denominación, exposición de motivos funcional, correspondencia motivos-articulado, numeración, unidad temática del artículo, formato de fracciones, técnica de reforma parcial, régimen transitorio completo, mandatos transitorios con plazo, claridad sintáctica, taxatividad sancionadora, consistencia terminológica, definiciones y remisiones inteligibles.
- **Sistematización normativa (CSN)** — duplicidades, antinomias, armonización (remisiones entrantes), precisión de remisiones salientes y vigencia de lo citado, verificadas **contra un corpus indexado de derecho vigente** (índices de las normas federales, sus artículos y sus remisiones cruzadas).
- **Racionalidad** — competencia, reserva de ley, habilitaciones reglamentarias, lagunas estructurales, retroactividad, destinatarios identificables, capacidad institucional, suficiencia presupuestaria, legislación simbólica, fines verificables, diagnóstico con evidencia, nexo medios-fines, y el examen de proporcionalidad (intensidad de escrutinio, intervención en derechos, fin legítimo, idoneidad, necesidad, proporcionalidad estricta, carril penal e igualdad).

Cada verificación es de uno de tres tipos: **determinista** (corre como código sobre la estructura del texto), **heurística** (corre como código con un patrón que aproxima el criterio) o **de juicio** (requiere valoración). Las verificaciones deterministas y heurísticas se resuelven sin IA. Las de juicio se emiten con su criterio embebido y, opcionalmente, se resuelven con un modelo de lenguaje ceñido a la evidencia (§5.2).

La agregación es conservadora y no compensatoria: un incumplimiento con severidad bloqueante degrada el dictamen a "no viable en sus términos"; las capas no se promedian entre sí. Además, el dictamen global está **condicionado por cobertura**: si la proporción de verificaciones efectivamente evaluadas no alcanza un umbral, el resultado es "preliminar por cobertura insuficiente" y nunca "viable", con lo que la ausencia de evaluación no se confunde con conformidad. Cuando el insumo no contiene articulado segmentable, el motor lo marca como no evaluable en vez de emitir cumplimientos vacuos.

La capa produce, además, un mapa legible de "conexión con el ordenamiento": la norma que la iniciativa modifica, las leyes que cita (con su última reforma, verificada contra el corpus) y las normas candidatas a armonización conforme (aquellas del corpus que remiten a lo reformado). Este mapa responde, para quien legisla, la pregunta operativa de con qué leyes hay que conectar y armonizar.

---

## 5. El uso de la inteligencia artificial

### 5.1 Postura epistémica

La IA se emplea como **apoyo estructural y analítico**, no como sustituto del juicio jurídico experto (`normtrace/00_project/ai_use_disclosure.md`). Sistematiza grandes volúmenes de texto legal según esquemas, reglas de decisión y lógica jurídica definidos por la investigadora. No emite interpretaciones jurídicas con autoridad, no determina puntajes o clasificaciones finales sin revisión humana, y sus salidas no constituyen asesoría legal. Toda clasificación asistida se marca `review_status: preliminary` hasta la validación de un especialista, y ninguna salida debe citarse, publicarse ni usarse para fines de política o jurídicos sin esa validación.

Cuatro decisiones de diseño traducen esta postura a mecanismos verificables.

### 5.2 Determinismo primero; el LLM como último recurso acotado

El instrumento resuelve determinísticamente todo lo que puede. La capa 1 es regex; la capa 2 es un parser; la capa 3 tiene un modo por reglas como opción por defecto; en la capa 4, las verificaciones deterministas y heurísticas corren como código. El modelo de lenguaje interviene solo donde el criterio exige valoración que no se reduce a una regla, y siempre bajo un **blindaje** de evidencia.

El blindaje, para la pasada de juicio de PAIL, impone al modelo reglas absolutas: usar exclusivamente la evidencia provista —el texto de la propia iniciativa y las citas del corpus incluidas— para juzgar la técnica y la racionalidad del texto; tener prohibido afirmar como hecho el contenido de normas vigentes que no estén en la evidencia, sin inventar artículos ni cifras; y, si la evidencia es insuficiente para calificar con rigor, responder `NO_EVALUABLE`. Tras la pasada, el dictamen se re-agrega con las mismas funciones deterministas del motor; el modelo no reimplementa la agregación. La regla de evidencia proviene del propio protocolo, no del modelo.

### 5.3 Reproducibilidad

El proveedor por defecto de la capa de codificación es un modo local por reglas (sin clave ni tokens): el sistema corre y se prueba sin llamar a ningún modelo, y las llamadas reales quedan activables por variable de entorno. Cuando se usa un modelo, la temperatura se fija en cero. El objetivo es que el mismo insumo produzca el mismo resultado, de modo que un análisis sea auditable y no una salida distinta en cada ejecución.

### 5.4 Confianza, estatus de revisión y validación de esquema

Cada salida asistida viaja con dos campos que llegan hasta la interfaz: `confidence_level` y `review_status`. Ninguna codificación se presenta como veredicto de cumplimiento; el protocolo produce correspondencias trazables con estatus preliminar. Toda salida de la etapa de codificación profunda valida contra su esquema JSON; si no valida, se reintenta o se marca para revisión humana. La separación de fuentes es estricta: el cerebro jurídico es fuente de verdad y se lee, no se parafrasea a mano en los prompts.

### 5.5 Transparencia

Esta divulgación del uso de IA se publica como parte del método para asegurar transparencia. Se invita a quien use las salidas de Huella 2030 a leer esta sección y la nota metodológica antes de emplear cualquier dato o tabla.

---

## 6. Trazabilidad, validación y control de calidad

La trazabilidad es la propiedad central del método y se sostiene en varios mecanismos concretos:

- **Identificadores estables por unidad** (capa 2), que permiten citar y reproducir cada resultado.
- **Cita fuente por registro** en las capas 3 y 4: cada hallazgo remite a la porción literal del texto y su ubicación.
- **Validación contra esquema** de toda salida estructural, con reintento o marca de revisión humana ante fallo.
- **Verificación contra corpus** en la subcapa CSN: la vigencia y las remisiones se resuelven contra índices del derecho vigente, no de memoria; si faltan los índices, la verificación degrada a "no verificable" en vez de inventar un resultado.
- **Pruebas automatizadas** por componente y una puerta de integración continua que corre las suites de unidad antes de fusionar cambios en el backend.

Ninguno de estos mecanismos convierte una salida preliminar en definitiva: su función es garantizar que lo preliminar sea rastreable, reproducible y honesto sobre su incertidumbre.

---

## 7. Limitaciones

- El análisis cubre el **texto** de la norma, no su interpretación judicial ni su práctica administrativa; puede haber brechas no visibles desde el texto estatutario.
- Todas las salidas asistidas son **preliminares** y requieren validación de un especialista antes de cualquier aplicación de política o jurídica.
- La subcapa de sistematización depende de la **cobertura y actualidad del corpus** indexado; una remisión a una norma ausente del corpus se reporta como no verificable, no como inexistente.
- La escala de anclaje mide anclaje **textual** documentado; un puntaje alto para una disposición formalmente válida pero prácticamente inaplicada sobreestimaría la capacidad legal-institucional.
- La extracción de documentos escaneados depende del OCR; un OCR pobre degrada todas las capas por igual.
- La pasada de juicio recibe texto de origen no confiable (el documento analizado) y es, en principio, susceptible de intentos de manipulación del prompt; el encuadre preliminar, la validación de esquema y la naturaleza no vinculante de la salida acotan el riesgo, que se declara de forma explícita.
- La metodología se desarrolla y prueba sobre un sistema jurídico (el mexicano); su validez y sensibilidad a la variación entre familias jurídicas requieren prueba en más jurisdicciones.

---

## 8. Antecedente doctrinal validado

El protocolo NormTrace se probó primero en el dominio del Reglamento Sanitario Internacional (RSI). El piloto NormTrace-IHR mapeó las 45 obligaciones del RSI 2005 contra disposiciones del derecho interno mexicano, con la escala de anclaje 0–5 y la tipología de brechas descritas arriba, y documentó hallazgos granulares no recuperables de los puntajes de capacidad agregados (`normtrace/00_project/normtrace_ihr_methodology_full.md`). Ese trabajo estableció la doctrina del trazado —método hermenéutico-estructural, puntaje conservador, trazabilidad obligatoria, IA como apoyo acotado, revisión experta como condición— que Huella 2030 traslada al análisis de iniciativas frente a la Agenda 2030 y extiende con la capa de revisión ex ante de técnica legislativa.

---

## 9. Ética, licencias y disponibilidad

**Ética y transparencia.** El instrumento no procesa datos personales sensibles ni confidenciales. La divulgación del uso de IA (§5) se publica con el método. Ninguna salida debe citarse ni usarse para fines jurídicos o de política sin validación de especialista.

**Licencias.** El contenido y el método NormTrace se publican bajo Creative Commons Atribución 4.0 (CC BY 4.0). La plataforma se construye sobre la tecnología tipi / escáner2030 (AGPL-3.0).

**Autoría y cita.** Protocolo NormTrace © Adela B. Santos Domínguez (ORCID 0000-0002-8691-0544), DOI 10.5281/zenodo.21631277. Módulos publicados del protocolo: CRPD (DOI 10.5281/zenodo.19676921), RSI/IHR (DOI 10.5281/zenodo.20085169) y derechos políticos (DOI 10.5281/zenodo.21296393).

**Disponibilidad.** El código de las capas, los esquemas de salida, la documentación del método y las pruebas están en el repositorio del proyecto. Todas las salidas se designan preliminares y requieren revisión experta antes de cualquier aplicación.

---

## Fuentes internas citadas

- `normtrace/00_project/methodology_note.md` — nota metodológica (escala 0–5, tipología de brechas, trazabilidad, limitaciones).
- `normtrace/00_project/ai_use_disclosure.md` — divulgación del uso de IA.
- `normtrace/00_project/project_scope.md` — alcance y unidad de análisis.
- `normtrace/00_project/normtrace_ihr_methodology_full.md` — metodología completa del piloto RSI.
- `normtrace/02_country_legal_brains/mexico/mexico_legal_reasoning_rules.md` — categorías de anclaje, escala, brechas, reglas de cautela.
- `normtrace/02_country_legal_brains/mexico/mexico_legal_system_profile.md` — perfil del sistema jurídico mexicano.
- `normtrace/02_country_legal_brains/mexico/mexico_legal_document_structure_patterns.md` — estructura documental y marcadores de efecto jurídico.
- `docs/ARCHITECTURE.md` — arquitectura del stack y puntos de inserción de NormTrace.
- `normtrace/schemas_runtime/` — esquemas de validación de las salidas estructurales (codificación por unidad y dictamen PAIL).

---

*Borrador v0.1. Documento metodológico preliminar. No citar como autoridad jurídica; para uso metodológico y analítico.*
