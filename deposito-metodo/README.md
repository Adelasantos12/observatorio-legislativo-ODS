# Huella 2030 — NormTrace aplicado a la correspondencia legislativa con la Agenda 2030 (México)

**Autora:** Adela B. Santos Domínguez · ORCID: `TODO-0000-0000-0000-0000`
**Licencia:** Creative Commons Attribution 4.0 (CC BY 4.0) — ver [`LICENSE`](LICENSE)
**Versión:** 0.1.0 · **Estado:** versión preliminar en desarrollo

> Este directorio es un **depósito de método**: documenta el protocolo y su
> aplicación a la legislación mexicana frente a los Objetivos de Desarrollo
> Sostenible (ODS) de la Agenda 2030. **No incluye la aplicación web**; para el
> código de la plataforma, ver el repositorio del observatorio (referencias abajo).

## Qué es

Un método para leer iniciativas y leyes mexicanas en dos capas:

1. **Etiquetado por diccionario** (heredado del stack *tipi* de Political Watch,
   base de escáner2030): detecta de qué ODS y metas habla un texto, por
   coincidencia de vocabulario curado (regex). Responde *"¿de qué trata?"*.
2. **Codificación estructural NormTrace** (contribución propia de la autora):
   sobre cada unidad jurídica (artículo, fracción, inciso) codifica **qué
   estructura jurídica crea** — actor obligado o facultado, procedimiento,
   coordinación entre órdenes de gobierno, exigibilidad, salvaguarda de derechos
   y reparto federal — y el tipo de oportunidad de fortalecimiento que presenta.
   Responde *"¿qué obliga, a quién, cómo, y qué falta para que sea exigible?"*.

El resultado es una **correspondencia trazable**, con cita a la fuente y estatus
de revisión, entre el texto legal y los estándares de la Agenda 2030 y del
derecho internacional. **No es un dictamen jurídico ni una evaluación de
cumplimiento**: es una lectura preliminar y verificable que siempre viaja con su
nivel de revisión.

## Qué usó de escáner2030 y qué se adaptó a México

La base técnica (motor de etiquetado por regex, modelo de diccionario, patrón
multi-país, stack FastAPI/Vue) proviene del **stack *tipi* de Political Watch**
(escáner2030), bajo licencia **AGPL-3.0**. Sobre esa base se hizo la
**adaptación a México** y se añadió la **capa NormTrace**. El detalle está en
[`ADAPTACION_ESCANER2030_MEXICO.md`](ADAPTACION_ESCANER2030_MEXICO.md); en
resumen:

- **Tropicalización** del léxico legislativo España → México (instituciones,
  tipos de iniciativa, estados del trámite, jerarquía normativa).
- **Diccionario mexicano** con instituciones y programas que las regexes
  españolas nunca capturarían (IMSS, CONAGUA, COFEPRIS, CONEVAL, UMA, leyes
  generales, materia concurrente, etc.).
- **Patrones de estructura jurídica mexicana** (Artículo / Fracción / Inciso /
  Transitorio) para segmentar en unidades citables con id estable.
- **Capa NormTrace** de codificación estructural profunda, con su taxonomía de
  dimensiones y de oportunidades de fortalecimiento.

## El método en una pantalla

```
texto / iniciativa / ley
   │
   ▼
[1] Etiquetado por diccionario (regex, estilo tipi)  →  temas ODS / marcos
   │
   ▼
[2] Segmentación jurídica  →  unidades citables (Artículo/Fracción/Inciso)
   │
   ▼
[3] Codificación NormTrace por unidad  →  actor · procedimiento · coordinación ·
   │   exigibilidad · salvaguarda · federalismo · tipo de oportunidad
   │   (con nivel de confianza y estatus de revisión)
   ▼
[4] Matriz de correspondencia trazable  (leída de un vistazo)
```

El detalle metodológico está en [`METODO.md`](METODO.md).

## Ejemplo dorado (prueba de concepto)

[`ejemplo-dorado/`](ejemplo-dorado/) contiene la codificación **validada por la
autora** de la **Ley General de Aguas (LGA) frente al ODS 6** y al derecho
humano al agua:

- `lga_ods6_mapeo_normtrace.csv` — 34 registros (disposición × 6 dimensiones).
- `lga_ods6_brief_normtrace.md` — el análisis narrado que fija el estándar de
  exigencia.

Es el patrón de referencia contra el cual se validan las corridas automáticas
del portal.

## Cómo citar

Ver [`CITATION.cff`](CITATION.cff). Una vez depositado en Zenodo, cítese con el
DOI que Zenodo asigne.

## Referencias a los repositorios

Ver [`REFERENCIAS.md`](REFERENCIAS.md): el stack *tipi* / escáner2030 (Political
Watch, AGPL-3.0), las instancias previas del marco NormTrace de la autora
(CRPD, IHR, derechos políticos), y el repositorio del observatorio.

## Nota de licencias

Este depósito de **método y documentación** se publica bajo **CC BY 4.0**. La
**plataforma de software** (fuera de este depósito) deriva del stack *tipi*
(AGPL-3.0) y se distribuye bajo esa licencia; la capa NormTrace y sus datos se
mantienen CC BY 4.0. Ver [`REFERENCIAS.md`](REFERENCIAS.md).
