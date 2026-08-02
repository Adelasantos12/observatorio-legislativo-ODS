# Estabilización de la rama y contrato de trabajo

Este documento fija el punto estable del proyecto y las reglas de trabajo a partir
de aquí. Rige toda contribución posterior (mejoras, refactors, revisión de
seguridad). No sustituye a `CLAUDE.md`; lo complementa con disciplina de proceso.

## Punto estable (baseline)

- **Rama de trabajo:** `claude/adenda-v5-1-ods-identity-2mrqvp`.
- **`main` estable:** commit `0646f26` (incluye #37, #38 y #39: segmentación de
  encabezados, normalización de PDF + armonización viva + panel legible, y OCR
  ante glifos sin mapear).
- **Estado de pruebas en el baseline:**
  - `packages/qhld-tasks` (unidad): verde.
  - `api` (unidad): verde.
  - `frontend`: build verde, candado de contenido verde, invariantes e2e 156/156.
  - Los tests de integración de `api` usan Docker (testcontainers) y solo corren
    donde hay Docker; no forman parte del baseline de unidad.

La rama se alineó con `main` mediante **merge** (nunca reset ni force-push), de
modo que `main` es ancestro de la rama y los PRs siguientes muestran diffs limpios.

## Las 10 reglas de estabilización

1. Está prohibido usar force-push.
2. Está prohibido hacer reset de commits ya publicados.
3. Está prohibido eliminar, silenciar o relajar tests fallidos.
4. Todo bug corregido debe tener una prueba de regresión permanente.
5. Railway sólo puede desplegar commits que hayan pasado CI.
6. Antes de afirmar que un cambio está desplegado, debe reportarse el hash exacto.
7. Ningún cambio puede considerarse terminado sin probar la URL real en staging.
8. No mezclar correcciones funcionales con refactors o rendimiento.
9. No modificar migraciones ya aplicadas.
10. Si un error conocido reaparece, detener cambios y ejecutar una investigación de
    regresión.

## Cómo se traduce cada regla al flujo de trabajo

- **(1, 2) Sin force-push ni reset.** Cada cambio se hace en commits nuevos sobre
  la rama. Para traer lo ya mergeado en `main` se usa `git merge origin/main`
  (produce un merge commit y un push fast-forward), nunca `checkout -B` + reset.
- **(3) No tocar tests fallidos.** Un test rojo se arregla arreglando el código, o
  se documenta como fallo conocido y se abre investigación (regla 10). No se borra,
  no se marca `skip`, no se afloja el assert.
- **(4) Regresión permanente.** Ver el mapa de abajo. Todo bug futuro añade su
  prueba en el mismo PR que lo corrige.
- **(5) CI antes de desplegar.** `main` debe tener protección de rama que exija los
  checks (`invariants`, `content-check`, `identidad-ods`, `normtrace-eval`,
  `hex-retirados`) en verde antes de fusionar; Railway despliega `main` solo tras
  la fusión (es decir, tras CI). Ver "Puertas de CI".
- **(6) Hash exacto.** Al reportar un despliegue se cita el commit (p. ej. "`main`
  en `0646f26`"), no "ya quedó".
- **(7) Staging real.** "Terminado" exige verificar la URL desplegada, no solo los
  tests locales ni el contenedor. Mientras no se pruebe la URL, el cambio está
  "mergeado, pendiente de verificación en staging".
- **(8) Un PR, un propósito.** Corrección funcional, refactor y rendimiento van en
  PRs separados. Este documento es solo-docs por esa razón.
- **(9) Migraciones inmutables.** Una migración ya aplicada no se edita; los cambios
  de esquema van en migraciones nuevas.
- **(10) Regresión = alto.** Si reaparece un bug con prueba de regresión, se detiene
  el trabajo en curso y se investiga por qué la prueba no lo atrapó antes de seguir.

## Mapa de bug → prueba de regresión permanente

| Bug corregido | Componente | Prueba de regresión |
| --- | --- | --- |
| Encabezado de artículo entrecomillado / a media línea / "único:" | `qhld-tasks` | `tests/unit/test_pail.py::test_normaliza_encabezado_entrecomillado`, `::test_normaliza_encabezado_a_media_linea` |
| Espacios dobles de PDF + cláusula de decreto enterrada (tipo indeterminado, armonización muerta) | `qhld-tasks` | `tests/unit/test_pail.py::test_normaliza_espacios_dobles_y_decreto_enterrado`, `::test_multi_ley_se_clasifica_como_reforma` |
| Mapa de leyes (con qué conectar/armonizar) ausente | `qhld-tasks` | `tests/unit/test_pail.py::test_conexiones_mapea_leyes_citadas_y_armonizacion` |
| Juicio LLM sin evidencia (todo NO_EVALUABLE) | `qhld-tasks` | `tests/unit/test_pail.py::test_juicio_recibe_el_texto_de_la_iniciativa`, `::test_recomendacion_del_llm_llega_al_resumen` |
| Insumo sin articulado (no es iniciativa) | `qhld-tasks` | `tests/unit/test_pail.py::test_puerta_de_insumo_sin_articulado` |
| PDF con glifos sin mapear `(cid:N)`: no disparaba OCR (0 ODS, 0 articulado) | `api` | `tests/unit/test_tagger.py::test_pdf_basura_cid_cae_a_ocr` |

## Puertas de CI → despliegue (acción de configuración pendiente)

Estas requieren permisos de administrador del repo y del panel de Railway; se
listan para completar la regla 5:

1. **Protección de rama en `main`:** exigir que los checks de CI pasen antes de
   fusionar, y prohibir push directo (solo vía PR).
2. **Railway:** desplegar desde `main` solo tras la fusión, o activar la espera de
   checks, para que ningún commit sin CI llegue a producción.

## Pendiente de verificación en staging (regla 7)

- **#39 (OCR ante glifos `cid`):** mergeado en `main` `0646f26`. Falta redeploy del
  servicio `api` y **verificar en la URL real** subiendo el PDF afectado
  (`asun_4895947`): debe extraer texto por OCR (~60 s, 23 páginas) y devolver ODS,
  NormTrace y PAIL con articulado (24 unidades en la prueba de laboratorio).
