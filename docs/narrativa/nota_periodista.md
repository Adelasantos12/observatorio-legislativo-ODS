# Nota del periodista — pasada anti-IA sobre es.json (adenda v4 §7)

Todo el texto visible del portal se escribió en `frontend/src/content/es.json` y
pasó el checklist anti-IA de §7. El candado automático `scripts/check_content.py`
(y su test en CI) verifica lo mismo en cada cambio. Ejemplos de lo que se corrigió:

- **Guion largo como puntuación.** El primer argumento de "por qué importa" abría
  su lista de foros con guiones largos (`—la revisión del T-MEC…—`). Se cambió a
  paréntesis: `(la revisión del T-MEC, el foro de alto nivel de la ONU, …)`.
- **Verbo inflado.** "cuántos asuntos impulsó cada origen" → "cuántos asuntos
  vienen de cada origen". `impulsar` está en la lista de §7.
- **Frases de encuadre (§2).** Se eliminó por completo el bloque de /minutas que
  decía "Esto no es un ranking ni una competencia entre bancadas…". La neutralidad
  ahora la da el orden (por año y nombre) y la ausencia de podios, no un aviso.
- **Titulares descriptivos → brecha de curiosidad.** "Aportación por origen a la
  Agenda 2030" (título de página) → "Lo que la Cámara mandó al Senado". La escena
  por ODS pasó de un rótulo técnico a "Casi la mitad mira al mismo lugar".
- **Marco de déficit → serie abierta.** El caso del agua ya no dice "solo una
  iniciativa tocó el ODS 6"; cuenta la ley como logro y abre la serie de
  armonización estatal con su contador (0 de 32, casillas vacías visibles).
- **Cierres rituales / signposting / moralejas:** ninguno; las escenas terminan en
  el dato o en la siguiente acción, no en una conclusión.

Regla aplicada en todo: verbos concretos, datos con fecha, oraciones de longitud
variable, y prosa que se lee en voz alta sin sonar a comunicado.
