# El método

Dos capas sobre un mismo texto legislativo: una rápida, de vocabulario; otra
profunda, de estructura jurídica. La primera dice de qué trata; la segunda, qué
obliga y qué falta para que sea exigible.

## Capa 1 — Etiquetado por diccionario (base tipi / escáner2030)

Motor de coincidencia por expresiones regulares sobre un diccionario curado.
La taxonomía es de tres niveles: **tema (ODS) → meta → concepto (etiqueta)**.
Cada etiqueta es una regex compilada, sin lematización ni semántica: cuenta la
frecuencia de vocabulario. Cuando la co-ocurrencia distingue el sentido, la
regex se marca para permutar sus partes (aparición en cualquier orden dentro de
la oración). El resultado es la presencia temática del texto: qué ODS y qué
metas menciona, con cuántas coincidencias.

Esta capa **no** evalúa contenido: indica presencia, no cumplimiento.

## Capa 2 — Codificación estructural NormTrace

Sobre las **unidades jurídicas** del texto (artículo, fracción, inciso,
transitorio), una codificación identifica la estructura que crea cada
disposición. Seis dimensiones de ajuste, cada una en escala ordinal
(**fuerte / medio / débil / no aplica**):

| Clave | Dimensión | Pregunta que responde |
|---|---|---|
| **A** | Actor | ¿Hay un responsable nombrado del deber o la facultad? |
| **P** | Procedimiento | ¿Está definido el cómo (plazo, vía, instrumento)? |
| **C** | Coordinación | ¿Se articula entre órdenes de gobierno o instituciones? |
| **E** | Exigibilidad | ¿Es justiciable / tiene consecuencia si no se cumple? |
| **S** | Salvaguarda | ¿Protege derechos y a grupos en situación de vulnerabilidad? |
| **F** | Federalismo | ¿Reparte y ancla competencias entre Federación, entidades y municipios? |

Cada disposición registra además:

- **Rol de correspondencia**: `sustantivo` (crea o define el contenido) o
  `contextual_habilitante` (lo enmarca sin crearlo).
- **Cobertura** de la meta que atiende: `completa`, `parcial`, `contextual`.
- **Tipo de oportunidad de fortalecimiento** (cuando aplica): remisión por
  anclar, procedimiento por precisar, respaldo presupuestal por asegurar,
  alcance por ampliar, garantía por construir, implementación por completar,
  entre otras. Nunca se nombra como "brecha" ni como defecto: son decisiones de
  arquitectura que dejan tarea pendiente en otros instrumentos.
- **Nota** de codificación con la cita verificada contra el texto oficial.

El patrón completo se lee de un vistazo como una **matriz de puntos**: cada
juicio es un glifo (círculo lleno / medio / contorno / punto), y las columnas
débiles —típicamente procedimiento y exigibilidad— saltan como columnas de
círculos vacíos. Eso es el hallazgo, sin colores de calificación: solo tinta.

## Niveles de revisión (regla no negociable)

Toda corrida viaja con su **nivel de revisión** y su descargo:

- `validado_autora` — codificación revisada por la autora contra el texto oficial
  (el ejemplo dorado).
- `automatico_preliminar` — corrida asistida por modelo de lenguaje bajo el
  protocolo; **nunca** se presenta como validada; requiere revisión de
  especialista.

Los campos de **confianza** y **estatus de revisión** acompañan cada registro
hasta la interfaz. El descargo fijo: *registra correspondencia formal entre
texto legal y estándares; no es dictamen jurídico ni evaluación de cumplimiento*.

## Arquitectura de aplicación (resumen)

```
[1] Etiquetado regex  →  [2] Segmentación jurídica  →  [3] Codificación NormTrace
    (temas ODS)            (unidades citables)           (6 dimensiones + oportunidad)
                                                              │
                                                              ▼
                                        [4] Matriz de correspondencia trazable
```

El código de la plataforma que implementa esta arquitectura vive en el
repositorio del observatorio (ver [`REFERENCIAS.md`](REFERENCIAS.md)); este
depósito documenta el método y su ejemplo dorado, no la aplicación web.
