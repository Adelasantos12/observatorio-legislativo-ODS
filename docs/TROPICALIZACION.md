# Tropicalización: mapa de términos y contexto España → México

Guía para la fase F1. La regla general: nada visible al usuario debe delatar el
origen español del stack. La regla fina: el español mexicano institucional tiene
su propio léxico legislativo; usarlo con precisión es parte de la credibilidad
del producto ante equipos parlamentarios.

## Instituciones y fuentes

| España (en el código/UI) | México (usar) |
|---|---|
| Congreso de los Diputados | Cámara de Diputados |
| Cortes Generales | Congreso de la Unión |
| Senado (España) | Senado de la República |
| BOE (Boletín Oficial del Estado) | DOF (Diario Oficial de la Federación) |
| Boletín Oficial de las Cortes | Gaceta Parlamentaria |
| Diario de Sesiones | Diario de los Debates |
| Grupo parlamentario (uso igual) | Grupo parlamentario |
| Diputado/a (uso igual) | Diputado/a (federal) |
| Comisión (uso igual) | Comisión (ordinaria/especial) |
| Mesa del Congreso | Mesa Directiva |
| Junta de Portavoces | Junta de Coordinación Política (JUCOPO) |
| Letrados | Secretaría de Servicios Parlamentarios / CEDIP |

## Tipos de documento e iniciativa

| España | México |
|---|---|
| Proposición de ley | Iniciativa (de diputados/senadores) |
| Proyecto de ley | Iniciativa del Ejecutivo Federal |
| Proposición no de ley (PNL) | Proposición con punto de acuerdo |
| Enmienda | Reserva / modificación en lo particular |
| Interpelación / pregunta parlamentaria | Pregunta parlamentaria / comparecencia |
| Real Decreto | Decreto / Reglamento |
| Ley Orgánica | (no existe como categoría; usar Ley General o Federal según el caso) |
| Texto refundido | (no aplica; el equivalente funcional es texto vigente con reformas DOF) |

Estados del trámite mexicano para `api/tipi_backend/api/managers/mexico/`:
presentada → turnada a comisión → dictaminada (primera lectura) → discusión y
votación en pleno → minuta a cámara revisora → aprobada → publicada en DOF.
Ramas adicionales: desechada, retirada, precluida, en comisiones unidas,
con prórroga. Fuente de verdad de estados reales: el SIL usa su propio
catálogo; alinearse con él facilita la ingesta futura.

## Léxico jurídico fino

- "Normativa" (España) → "normatividad" o "marco normativo" (México).
- "Recurrir" una norma → "impugnar"; el medio es amparo, controversia
  constitucional o acción de inconstitucionalidad.
- Jerarquía mexicana para textos de UI (simplificada): Constitución → tratados →
  leyes generales/federales → reglamentos → NOMs → acuerdos. La versión precisa
  y sus matices están en
  `normtrace/02_country_legal_brains/mexico/mexico_legal_system_profile.md`;
  ante duda, ese archivo manda.
- Marcadores de efecto jurídico para regexes y prompts (del cerebro, §5):
  "corresponde a", "son atribuciones de", "compete a", "deberá", "podrá",
  "queda prohibido", "se coordinará con", "en el ámbito de sus competencias".

## Vocabulario para diccionarios (ejemplos por ODS)

Instituciones que las regexes españolas jamás capturarían y las mexicanas deben
capturar: IMSS, ISSSTE, IMSS-Bienestar, COFEPRIS, CONEVAL, CONAGUA, CONAFOR,
PROFEPA, SEMARNAT, CONAVI, INMUJERES, INPI, CNDH, INEGI, CURP, NOM-XXX-SSA,
programas de Bienestar (pensión de adultos mayores, Sembrando Vida, Jóvenes
Construyendo el Futuro), salario mínimo / UMA, Ley General de..., materia
concurrente. Al escribir regexes: acentos opcionales donde el corpus real
fluctúa, `\b` en siglas, y `shuffle: true` solo cuando la co-ocurrencia
distingue el sentido (patrón del fixture español).

## Corpus de prueba (documentos reales para validar)

- Gaceta Parlamentaria del 16/jul/2026, Anexo I:
  https://gaceta.diputados.gob.mx/Gaceta/66/2026/jul/20260716-I.html
  (16 iniciativas; incluye salud intercultural, consulta indígena, bonos de
  carbono, violencia contra las mujeres: buen surtido multi-ODS).
- Ley General de Salud (markdown ya convertido en `normtrace/01_sources/mexico/`).
- Ley General de Aguas (promulgada 11/dic/2025): caso demo político prioritario
  contra ODS 6.

## Descargos (texto exacto para el frontend)

Análisis rápido: "Resultados generados por coincidencia de vocabulario
curado. Indican presencia temática, no evaluación de contenido."

Análisis estructural: "Codificación preliminar asistida por modelo de lenguaje
bajo el protocolo NormTrace. No constituye dictamen jurídico ni evaluación de
cumplimiento; requiere revisión de especialista. Cada registro conserva su
cita fuente para verificación."

## Lo que NO se tropicaliza

- Nombres de paquetes y módulos python (`qhld_*`, `tipi_*`): son internos,
  renombrarlos rompe imports y aleja el repo del upstream sin ganancia.
- El cerebro jurídico y las tablas NormTrace: ya son mexicanos.
- Los extractores de otros países en `engine/`: se quedan como plantillas.
