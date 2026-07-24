# Guion v7 — La huella, contada de verdad

Guion completo de `/huella`: coreografía + copy, escena por escena. El copy de
este documento es **borrador de autora**: va a `es.json` bajo las claves
indicadas y se revisa antes de merge, como siempre. Sustituye la sección "por
qué importa" en tres columnas por el **Acto II (el viaje)**. Las reglas vigentes
no cambian: nada de meta-lenguaje, nada de déficit, candados de la v4/v6.2.

## 0. Arreglos mecánicos previos (bloqueantes, sin esto no hay historia)

1. **Regla de oro del scrollytelling: ningún paso sin estado gráfico.** El panel
   gráfico es UNO, fijo (sticky, 55% izquierdo en desktop), y cada paso de texto
   (40% derecho) dispara una transformación de ese mismo panel. Hoy hay tarjetas
   flotando junto a un panel vacío: eso queda prohibido con test e2e (cada
   `data-step` tiene su `data-state` del gráfico y el estado cambia al cruzar el
   50% del viewport, transición 600ms ease-in-out).
2. **Anticolisión de etiquetas de grupo.** "62 Publicada en el DO75" es dos
   etiquetas encimadas. Las etiquetas de grupo del unit chart se colocan con
   medición: ancho del texto + 24px de separación mínima entre grupos; si no
   caben, el grupo se baja de fila o la etiqueta se abrevia ("En el Senado" →
   "Senado") con título completo en tooltip. Verificado en 5 anchos.
3. **Sincronía.** El estado del gráfico se deriva EXCLUSIVAMENTE del índice de
   paso activo (máquina de estados), nunca del progreso continuo del scroll. Un
   paso, un estado, sin estados intermedios que lleguen tarde.
4. **En móvil:** gráfico fijo en el tercio superior, pasos deslizando debajo.

## ACTO I — Lo que ya pasó en San Lázaro

### E1 · Apertura (claves `escenas.agenda.*`)
Coreografía: pantalla casi vacía; caen los 221 cuadritos y se ordenan en
retícula. Minutas en tinta, iniciativas del Ejecutivo en gris. SIN color ODS
todavía: el color llega después y esa espera es deliberada. Copy (ya existe en
es_revisado; se conserva).

### E2 · ¿Cuántas ya son ley? (`escenas.estatus.*`)
Coreografía: los mismos cuadritos se reagrupan en tres bloques por estatus, con
sus etiquetas medidas (62 en el DOF, 75 Senado, 2 devueltas) y la serie del DOF
con casillas vacías punteadas hasta 139 (Zeigarnik). El bloque del Ejecutivo se
atenúa al 30% en esta escena: la pregunta es de las minutas. Copy: el existente.

### E3 · El momento del color (`escenas.hallazgo.*`, REESCRITA)
Coreografía: beat en dos tiempos. Primero los cuadritos, aún neutros, se
reagrupan en columnas por objetivo. Pausa de medio paso. Después, al entrar el
segundo párrafo, TODOS se tiñen a la vez del color oficial de su ODS: es el
único momento de la página en que el color llega de golpe, y es el clímax
visual. La barra del 16 sobresale con su etiqueta.
Copy propuesto:
- `titulo`: "Y cuando se leen en clave 2030, aparece esto"
- `p1`: "Los mismos cuadritos, ordenados ahora por objetivo. Todavía sin color: primero el orden."
- `p2`: "Ahora sí. Cada asunto toma el color de su objetivo, y una columna crece por encima del resto: paz, justicia e instituciones. Detrás, igualdad, trabajo, infraestructura y hacienda."

### E4 · Lo que se ve al acercarse (`escenas.singulares.*`)
Coreografía: la retícula coloreada se atenúa; se iluminan y crecen los cuadritos
singulares: el celeste del agua y los grises sin casilla. Copy: el existente
(revisado).

### E5 · El agua (`escenas.agua.*`)
Coreografía: zoom al cuadrito celeste, que se expande en la tarjeta de la ficha
NormTrace (badge "Validado por la autora", metas, contador "en documentación",
enlace al análisis completo). Invariante v6.2: no puede faltar. Copy: el
existente.

## ACTO II — El viaje (SUSTITUYE a las tres columnas)

Formato: misma mecánica de scrollytelling. El panel gráfico se convierte en un
camino horizontal punteado con cuatro paradas; una figura mancha (neutra,
`--neutral-2`, sin cara) avanza de parada en parada conforme se scrollea. Cada
parada es un punto con el nombre de la ciudad en chip de texto; México es la
parada final, más grande, con el anillo ODS. Sin banderas, sin mapa detallado:
el camino y los nombres bastan.

### V1 · Madrid (claves `viaje.madrid.*`)
Coreografía: la figura llega a la primera parada; junto al punto aparece una
mini-retícula de cuadritos etiquetados.
Copy propuesto:
- `titulo`: "En Madrid ya lo hacen, desde afuera"
- `p`: "Desde 2019, una organización civil etiqueta todo lo que pasa por el Congreso de los Diputados en clave 2030. El parlamento español es observado; la evidencia la construye la sociedad civil."

### V2 · Asunción (`viaje.asuncion.*`)
Coreografía: la figura avanza; segunda parada, mini-retícula con marco
institucional.
Copy propuesto:
- `titulo`: "En Asunción lo hacen desde adentro"
- `p`: "El Congreso paraguayo publica sus propios expedientes etiquetados por objetivo. Ahí el parlamento no espera a que lo observen: se observa a sí mismo. Eso tiene nombre en la literatura: parlamento abierto."

### V3 · Ginebra y Nueva York (`viaje.foros.*`)
Coreografía: tercera parada; junto al punto, tres siglas en chips (UIP, PNUD,
HLPF).
Copy propuesto:
- `titulo`: "Y en los foros ya hay mesa puesta"
- `p`: "La Unión Interparlamentaria y el PNUD publican desde 2016 una herramienta para que cada parlamento documente su parte de la Agenda 2030. Cada julio, el foro de alto nivel de la ONU revisa avances país por país. Los que llegan con registro, hablan; los que no, escuchan."

### V4 · México, al centro (`viaje.mexico.*`)
Coreografía: la figura llega a la última parada, que crece; el anillo ODS
aparece completo; alrededor, dos chips de texto (Parlatino, ParlAmericas) y uno
hacia agenda2030.mx.
Copy propuesto (dos pasos):
- `titulo`: "México no llega tarde. Llega con registro propio"
- `p1`: "El Ejecutivo ya tiene su tablero: agenda2030.mx sigue los indicadores del país desde hace años. Lo que no existía era la mitad legislativa. Este observatorio la pone sobre la mesa, y con eso México se vuelve el primer caso de la región donde las dos mitades del Estado pueden contarse juntas."
- `p2`: "La política exterior mexicana tiene principios escritos en la Constitución: cooperación internacional para el desarrollo, respeto a los derechos humanos, igualdad jurídica de los Estados. Nombrar el trabajo legislativo en el lenguaje que el mundo comparte no es adoptar una agenda ajena: es ejercer una identidad que ya está en el artículo 89. La influencia también se construye así, contando con método lo que ya se decidió en casa. En el Parlatino y en ParlAmericas, ese registro convierte a México en referencia, no en audiencia."

### V5 · Cierre del viaje (`viaje.cierre.*`)
Coreografía: el camino completo queda a la vista, la figura junto al anillo;
transición suave al explorador.
Copy propuesto:
- `titulo`: "Quien guarda el registro cuenta la historia"
- `p`: "La legislatura que cierra en 2027 deja constancia con fecha y fuente. La década que termina en 2030 se va a contar con datos. Ya están aquí."

## ACTO III — Explorador
Sin cambios de contenido; hereda las tarjetas y filtros de la v6.

## Notas para Code

1. Los hechos del Acto II están verificados y NO se amplían sin fuente:
   España/Parlamento2030 (desde 2019, sociedad civil), Paraguay/Congreso 2030
   (institucional), UIP-PNUD herramienta de autoevaluación (2016), HLPF cada
   julio, agenda2030.mx (tablero de indicadores del Estado mexicano), principios
   del art. 89 fracc. X constitucional (los tres citados son textuales de la
   fracción). Nada de cifras de "70 parlamentos" ni afirmaciones no verificadas.
2. Todo el copy nuevo entra a `es.json` bajo las claves indicadas, marcado
   DRAFT, pasa el candado anti-IA y el de meta-lenguaje, y se somete a revisión
   de la autora antes de merge.
3. La figura del viaje se construye con la receta de manchas (v5.1 §4): neutra,
   sin cara; su avance se anima con transform sobre el path, respetando
   reduced-motion (fallback: aparece en cada parada sin desplazamiento).
4. Tests e2e nuevos: cada paso tiene estado gráfico; el beat del color en E3
   ocurre (los cuadritos cambian de neutro a color entre p1 y p2); el viaje
   tiene 5 paradas y la figura se mueve; las etiquetas de grupo no se traslapan
   en los 5 anchos.
5. Aceptación: video del scroll completo desktop y móvil; captura del momento
   del color; captura de cada parada del viaje.
