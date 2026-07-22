# Estructura — portal Huella 2030 (adenda v4)

Mapa de información y orden de escenas. Corrige el amontonamiento y saca la nota
metodológica de junto a las gráficas. Ninguna cifra se escribe a mano: todas
salen del API en tiempo de render.

## Páginas

| Ruta | Qué es | Qué NO vive aquí |
|---|---|---|
| `/huella` | La historia: 6 escenas + "por qué importa" + explorador al final | La nota metodológica larga; los disclaimers |
| `/minutas` | Explorador de las 139 minutas con filtros vivos | Texto que anuncie encuadre |
| `/expedientes/:id` | Ficha por iniciativa; ficha dorada NormTrace de la LGA | — |
| `/metodologia` | **Nueva.** Método, fuentes, límites, y el contador "origen documentado: X de 139" como transparencia | Nada que compita con la historia |

## Orden de escenas en `/huella`

Una idea por pantalla. El explorador va al final, nunca al principio.

1. **Apertura — lo que ya se hizo.** Se ve primero: una frase en pasado con dos
   números (minutas aprobadas; iniciativas logradas). El scroll deja caer los
   221 cuadritos a una retícula. Dato: `kpis.minutas_totales`, `kpis.aprobadas`,
   `kpis.iniciativas_presentadas`.

2. **¿Cuántas ya son ley?** Los cuadritos se separan por estatus. La serie se
   dibuja a medio llenar, con la casilla vacía visible (las que faltan por
   completar el tramo al DOF). Dato: `por_estatus` (62/75/2).

3. **El hallazgo.** Los cuadritos se reagrupan en barras por ODS; nace la barra
   dominante (ODS 16) y detrás los otros picos. Dato: `por_ods`.

4. **Lo que casi nadie ve.** Sobre la misma vista por ODS se iluminan las piezas
   singulares (la del agua; las sin correspondencia). Dato: nodos con
   `ods_principal` nulo y el nodo de la LGA.

5. **El caso del agua.** Zoom al cuadrito del agua: extracto de la ficha dorada
   (metas 6.1–6.b) y el **contador de armonización estatal** (serie abierta).
   Enlaza a `/expedientes/{vitrina}` como "el análisis completo, artículo por
   artículo". Dato: `/normtrace/expediente/{vitrina}`.

6. **Por qué importa.** Capa de sentido entre la historia y el explorador. Cuatro
   piezas, cada una un hecho con destino real (foros donde se lee evidencia;
   decisión soberana primero y resonancia después; parlamento abierto como
   credencial; memoria hacia 2027 y 2030). Texto en `es.json → porque_importa`.

7. **Explora.** El explorador completo (búsqueda, filtros por ODS/meta, tabla,
   fichas) y CTA a `/minutas` y a los expedientes.

8. **Pie de método.** Una línea con enlace a `/metodologia`.

## Vista `/minutas`

- Tabla de las 139 con filtros vivos por **tema, ODS, meta, estatus y año**.
- La **vista por origen se ordena cronológica o alfabéticamente por defecto**,
  nunca por conteo. Sin podios. Las co-presentaciones se listan como hecho.
- El contador de atribución ("origen documentado: X de 139") aparece como una
  categoría más y se explica en `/metodologia`, no junto a la gráfica.

## Reglas transversales

- El explorador siempre al final; la historia primero.
- El caso del agua es trofeo y serie abierta a la vez, jamás anomalía.
- La metodología completa vive en `/metodologia`; en la historia solo el enlace.
