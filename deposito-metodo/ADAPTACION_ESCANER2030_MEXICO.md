# Adaptación: de escáner2030 (España) a México, y la capa NormTrace

Este método reutiliza la base técnica de **escáner2030** (el stack *tipi* de
Political Watch, AGPL-3.0) y la adapta al contexto mexicano, añadiendo encima la
capa de codificación estructural **NormTrace**. Aquí se documenta qué se tomó y
qué se cambió, para dejar clara la trazabilidad y la atribución.

## Qué aportó escáner2030 / tipi (base reutilizada)

- **Motor de etiquetado por regex** sobre un diccionario curado (`tagger`), con
  taxonomía tema → meta → concepto y compilación de regex con permutaciones por
  co-ocurrencia.
- **Modelo de diccionario** en base de datos (colección de temas con etiquetas).
- **Stack de aplicación**: API en FastAPI, SPA en Vue, pipeline batch de ingesta
  y etiquetado.
- **Patrón multi-país**: la misma base sirve varios despliegues cambiando la
  configuración; el multi-país ya era un patrón soportado (España, Paraguay,
  Andorra).

## Qué se cambió para México

### 1. Tropicalización del léxico legislativo (España → México)

Nada visible al usuario delata el origen español del stack. El español mexicano
institucional tiene su propio léxico; usarlo con precisión es parte de la
credibilidad ante equipos parlamentarios. Ejemplos:

| España | México |
|---|---|
| Congreso de los Diputados | Cámara de Diputados |
| BOE (Boletín Oficial del Estado) | DOF (Diario Oficial de la Federación) |
| Proposición de ley | Iniciativa (de diputados/senadores) |
| Proyecto de ley | Iniciativa del Ejecutivo Federal |
| Real Decreto | Decreto / Reglamento |
| "Normativa" | "Normatividad" / "marco normativo" |

Estados del trámite mexicano: presentada → turnada a comisión → dictaminada →
discusión y votación en pleno → minuta a cámara revisora → aprobada → publicada
en DOF (con ramas: desechada, retirada, precluida, comisiones unidas, prórroga).

### 2. Diccionario mexicano

Instituciones y programas que las regexes españolas jamás capturarían y las
mexicanas deben capturar: IMSS, ISSSTE, IMSS-Bienestar, COFEPRIS, CONEVAL,
CONAGUA, CONAFOR, PROFEPA, SEMARNAT, CONAVI, INMUJERES, INPI, CNDH, INEGI, CURP,
NOM-XXX-SSA, programas de Bienestar, salario mínimo / UMA, "Ley General de…",
"materia concurrente". Regex con acentos opcionales donde el corpus real
fluctúa, `\b` en siglas y permutación solo cuando la co-ocurrencia distingue el
sentido.

### 3. Estructura jurídica mexicana

Segmentación por **Artículo / Fracción / Inciso / Transitorio** para producir
unidades citables con id estable (p. ej. `MX-LGS-art134-fracII`). Jerarquía de
fuentes para la interfaz: Constitución → tratados → leyes generales/federales →
reglamentos → NOMs → acuerdos. Marcadores de efecto jurídico para regex y
prompts: "corresponde a", "son atribuciones de", "compete a", "deberá", "podrá",
"queda prohibido", "se coordinará con", "en el ámbito de sus competencias".

### 4. Extractor por API (plantilla de Paraguay)

Para la ingesta de datos parlamentarios se toma como plantilla el extractor
basado en API (más limpio que el scraper de España), del patrón multi-país del
stack.

## Qué se añadió: la capa NormTrace

Sobre el etiquetado temático se añade la **codificación estructural NormTrace**
(contribución propia de la autora): las seis dimensiones de ajuste (actor,
procedimiento, coordinación, exigibilidad, salvaguarda, federalismo), el rol de
correspondencia, la cobertura, el tipo de oportunidad de fortalecimiento y la
nota con cita verificada. Ver [`METODO.md`](METODO.md). Esta capa es lo que
distingue el método: de *"¿de qué habla el texto?"* a *"¿qué estructura jurídica
crea y qué falta para que sea exigible?"*.

## Frontera de licencias

La base *tipi* / escáner2030 es **AGPL-3.0**: su atribución se conserva y, al
ofrecerse en red, obliga a publicar el código de la versión desplegada. La capa
NormTrace, su documentación y sus datos (incluido el ejemplo dorado) son
contribución de la autora bajo **CC BY 4.0**. Ambas conviven sin conflicto: son
obras separadas, cada una con su licencia declarada.
