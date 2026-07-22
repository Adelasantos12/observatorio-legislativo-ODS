# Adenda v3 — Minutas completas de la LXVI + rediseño narrativo (estilo data essay)

Complemento de INSTRUCCIONES_CODE_huella2030_v2.md y de la adenda de nivel 2.
Dos entregas: (A) cargar TODAS las minutas con clave única de la Cámara de
Diputados de la LXVI Legislatura, no solo las de origen Ejecutivo; (B) rediseñar
la página /huella como una historia con datos, no como un tablero amontonado.

## 0. Assets que acompañan esta adenda

| Archivo | Destino | Qué es |
|---|---|---|
| `minutas_scraper.py` | `engine/qhld_engine/extractors/mexico/iniclave_minutas.py` | Scraper YA PROBADO contra las dos páginas de iniclave; conserva la limpieza de whitespace en la clave y la verificación de secuencia sin huecos |
| `minutas_lxvi.csv` | `normtrace/03_tables/legislative_mapping/minutas_lxvi_raw.csv` | Las 139 minutas reales al corte 21/jul/2026 (año I: 001-039; año II: 040-139): 62 publicadas en DOF, 75 en revisora, 2 devueltas. Semilla cruda, SIN codificación |
| `matches_minutas_ejecutivo.json` | junto al CSV | 81 minutas ya cruzadas contra el dataset del Ejecutivo (difflib ratio ≥ 0.62), con el índice de la iniciativa y el score |

## A. Minutas completas

### A1. Carga y actualización
1. Integra el scraper como comando `iniclave-minutas` (mismo patrón que
   `sil-ejecutivo`). Corre diario. Verificación de completitud: la numeración
   de claves es continua en la legislatura; si aparece un hueco en la
   secuencia, repórtalo en el log, no lo silencies.
2. Colección `minutas` con los campos del CSV crudo + los de codificación
   (`ods_principal, ods_secundarios, metas, tema, confianza`) + atribución
   (`origen_tipo, grupos_parlamentarios`) + `nivel_revision`.

### A2. Codificación ODS/metas de las 139 (y las que vengan)
Regla de tres pasos, en este orden:
1. **Herencia (81 minutas, cero costo):** si la minuta está en
   `matches_minutas_ejecutivo.json`, hereda `ods_*`, `metas`, `tema` de la
   iniciativa del Ejecutivo correspondiente, con `confianza` = la de origen si
   el score ≥ 0.75, o "media" si el score está entre 0.62 y 0.75, y
   `origen_tipo: "ejecutivo"`. Los pares con score < 0.75 van a una lista de
   verificación manual (el match difuso puede fallar).
2. **Codificación asistida (las 58 restantes y toda minuta nueva):** llama al
   LLM (misma config `LLM_*` de la fase F4) con el título completo y el
   catálogo ODS/metas, pidiendo `{ods_principal, ods_secundarios, metas, tema,
   confianza}` en JSON validado. Reglas del prompt: las declaratorias de "Día
   Nacional de X" y similares se codifican por su materia si la tienen (Día de
   las Mujeres Afromexicanas → ODS 5/10) o como sin correspondencia si son
   puramente conmemorativas; ante duda, `confianza: "baja"`, nunca inventar
   metas. Todo resultado nace `nivel_revision: automatico_preliminar`.
3. **CSV de revisión de la autora:** exporta la codificación completa a
   `normtrace/03_tables/legislative_mapping/minutas_ods.csv`. Ese archivo,
   editado a mano, es fuente de verdad: el importador NUNCA pisa filas cuyo
   `nivel_revision` sea `validado_autora`.

### A3. Atribución por grupo parlamentario
Sigue vigente lo dicho en la v2 §4.3: iniclave no trae presentador. Para las
81 de origen Ejecutivo ya está resuelto. Para las 58 restantes, el dato vive
en el PDF del dictamen (columna Aprobación/Dictamen; URLs en el campo `pdfs`):
la primera sección del dictamen enumera las iniciativas dictaminadas con
nombre y grupo de quien las presentó. Implementa la extracción como job
incremental (`normtrace-atribucion`): descarga el dictamen, busca los patrones
"iniciativa presentada por" / "del Grupo Parlamentario de", llena
`grupos_parlamentarios` como lista, y donde el parseo no alcance confianza
deja `null` y la UI muestra "por documentar". Nunca inventes atribución.

### A4. La vista /minutas con datos completos
Con las 139 cargadas, los filtros que hoy están vacíos cobran sentido: por
tema, por ODS/meta, por estatus (62 DOF / 75 en Senado / 2 devueltas), por año
legislativo, y por origen conforme la atribución avance. KPI honesto de
avance: "atribución documentada: X de 139".

## B. Rediseño narrativo de /huella (estilo The Pudding)

### B1. El principio
El problema actual: todo compite por atención al mismo tiempo. La solución no
es más diseño sino jerarquía narrativa: una sola idea por pantalla, el dato
aparece cuando la historia lo pide, y la exploración libre va al final, no al
principio. Referencia de tono: los ensayos visuales de pudding.cool. El rigor
no se pierde: cada escena muestra su número con su método y confianza.

### B2. Arquitectura técnica (Vue)
Patrón scrollytelling clásico: una columna de gráfico fijo (position sticky)
y pasos de prosa que se deslizan sobre ella; cada paso que entra al viewport
(IntersectionObserver o la librería scrollama) dispara una transición del
gráfico. Un solo sistema visual continuo: el "unit chart" donde CADA MINUTA E
INICIATIVA ES UN CUADRITO que se reagrupa entre escenas (transiciones CSS/FLIP
o D3; 220 nodos se animan sin problema). Los tokens de identidad de la v2 §1
no cambian; tipografía más grande en la prosa (18-20px), una idea por párrafo.

### B3. Storyboard (con los números reales del semilla; recalcula del dato vivo)
1. **Apertura.** Pantalla casi vacía, una frase: "Desde octubre de 2024, la
   Cámara de Diputados ha aprobado 139 minutas; el Ejecutivo ha logrado 76 de
   sus 82 iniciativas." Los 139+82 cuadritos caen y se ordenan en una retícula.
2. **¿Cuántas se vuelven ley?** Los cuadritos se separan por estatus: 62
   publicadas en DOF, 75 esperando al Senado, 2 devueltas. Anotación directa
   sobre los grupos, sin leyenda aparte.
3. **El hallazgo.** Los cuadritos se reagrupan por ODS y el lector ve nacer la
   barra dominante: "Casi la mitad de la agenda es un solo objetivo: paz,
   justicia e instituciones (ODS 16)". Luego, en la misma escena, los otros
   picos: género, trabajo, infraestructura, hacienda.
4. **Lo que casi nadie ve.** Se iluminan los cuadritos singulares: la única
   del ODS 6 (Ley General de Aguas), las 4 sin correspondencia (monedas), la
   meta de menstruación digna. Aquí el tono Pudding rinde más: el detalle
   inesperado como recompensa del scroll.
5. **El caso del agua.** Zoom al cuadrito del agua: mini-versión de la ficha
   NormTrace dorada (metas 6.1-6.b con sus juicios) y enlace a la ficha
   completa. Es la demostración del nivel 3 dentro de la historia.
6. **Explora tú.** Cierre: el unit chart se convierte en el explorador
   completo (los filtros y la tabla actuales, que se mudan aquí). CTA a
   /minutas y /expedientes.
7. Pie fijo de método y descargos (los textos vigentes de la v2).

### B4. Reglas de visualización (no negociables)
Las de la referencia y el brief v2: colores ODS solo como chips de identidad,
marcas en guinda/tintas, anotaciones directas en vez de leyendas cuando el
grupo ≤ 4, badges de estatus siempre icono+texto, modo oscuro, y cada cifra
derivada del dato vivo del API, jamás hardcodeada (los números del storyboard
son del corte 21/jul/2026 y van a cambiar).

### B5. Criterios de aceptación
1. `/huella` cuenta la historia en 6 escenas con scroll fluido en desktop y
   móvil (en móvil el gráfico sticky pasa a media pantalla superior).
2. Las 139 minutas + 82 iniciativas están en el unit chart desde la escena 1
   y ningún número visible está hardcodeado.
3. La escena 5 enlaza a la ficha dorada de la LGA.
4. El explorador conserva TODAS las capacidades actuales (búsqueda, filtros,
   fichas) al final de la página.
5. Lighthouse accesibilidad ≥ 90; la historia es legible sin JS de animación
   (fallback: escenas apiladas estáticas).
6. Capturas de las 6 escenas en el PR.
