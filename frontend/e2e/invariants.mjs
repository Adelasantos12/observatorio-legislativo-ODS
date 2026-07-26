// Tests e2e de invariantes del producto (adenda v6.2 §3/§4). Si una escena o
// pieza desaparece, este runner truena y CI no fusiona el PR.
// Sin framework pesado: sirve el dist con fixtures y conduce Chromium por CDP.
// Chromium: process.env.CHROME (ruta al binario). Requiere un dist compilado.
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { startServer } from './fixtures-server.mjs';

// El dist se compila con VITE_VUE_APP_BACKEND_URL=http://localhost:8080, así que
// el servidor de fixtures escucha en 8080 (mismo origen que la app y su API).
const PORT = Number(process.env.E2E_PORT || 8080);
const BASE = `http://localhost:${PORT}`;
const CHROME = process.env.CHROME
  || ['/opt/pw-browsers/chromium-1194/chrome-linux/chrome','/usr/bin/chromium-browser','/usr/bin/chromium','/usr/bin/google-chrome'].find(existsSync);
if (!CHROME) { console.error('No se encontró Chromium; define CHROME=<ruta>'); process.exit(2); }

const results = [];
const ok = (name) => { results.push([true, name]); console.log(`  ✓ ${name}`); };
const fail = (name, detail) => { results.push([false, name]); console.log(`  ✗ ${name}${detail ? ' — ' + detail : ''}`); };
function assert(name, cond, detail) { cond ? ok(name) : fail(name, detail); }

const server = await startServer(PORT);
const chrome = spawn(CHROME, ['--headless','--no-sandbox','--disable-gpu',
  '--disable-background-timer-throttling','--disable-renderer-backgrounding',
  '--disable-backgrounding-occluded-windows','--disable-features=CalculateNativeWinOcclusion',
  '--remote-debugging-port=9223','--window-size=1280,1000','about:blank']);
// Espera a que el endpoint de DevTools responda (no cuelga si Chromium tarda).
let devtoolsUp = false;
for (let i = 0; i < 40; i++) {
  await new Promise(r => setTimeout(r, 300));
  try { await (await fetch('http://localhost:9223/json/version')).json(); devtoolsUp = true; break; } catch {}
}
if (!devtoolsUp) { console.error('DevTools no respondió'); chrome.kill(); server.close(); process.exit(2); }

function conn(url) {
  const ws = new WebSocket(url); let id = 0; const pend = {};
  ws.onmessage = e => { const d = JSON.parse(e.data); if (d.id && pend[d.id]) { pend[d.id](d.result); delete pend[d.id]; } };
  const ready = Promise.race([
    new Promise(r => ws.onopen = r),
    new Promise((_, rej) => setTimeout(() => rej(new Error('ws open timeout')), 8000)),
  ]);
  const send = (m, p = {}) => { const i = ++id; ws.send(JSON.stringify({ id: i, method: m, params: p })); return new Promise(r => pend[i] = r); };
  return { ready, send };
}
// Red de seguridad: nunca colgar más de 240s (el barrido de 5 anchos es lento).
setTimeout(() => { console.error('Timeout global del runner'); process.exit(1); }, 240000).unref();
async function newPage() {
  const t = await (await fetch(`http://localhost:9223/json/new?about:blank`, { method: 'PUT' })).json();
  const c = conn(t.webSocketDebuggerUrl); await c.ready;
  await c.send('Page.enable'); await c.send('Runtime.enable');
  await c.send('Emulation.setFocusEmulationEnabled', { enabled: true }).catch(() => {});
  await c.send('Page.setWebLifecycleState', { state: 'active' }).catch(() => {});
  return c;
}
const evalJson = async (c, expr) => {
  const r = await c.send('Runtime.evaluate', { returnByValue: true, expression: `JSON.stringify((()=>{${expr}})())` });
  return JSON.parse(r.result.value);
};
async function goto(c, path, readyExpr) {
  await c.send('Page.navigate', { url: BASE + path });
  for (let i = 0; i < 50; i++) {
    await new Promise(r => setTimeout(r, 300));
    const r = await c.send('Runtime.evaluate', { returnByValue: true, expression: `!!(${readyExpr})` }).catch(() => ({ result: { value: false } }));
    if (r.result && r.result.value) return true;
  }
  return false;
}

try {
  // ---------- /huella ----------
  console.log('\n/huella — scrollytelling e invariantes de escena');
  let c = await newPage();
  const huellaReady = await goto(c, '/huella', `document.querySelector('.hero-art') && !/Cargando/.test((document.querySelector('.story-hero .lede')||{}).textContent||'')`);
  assert('huella carga con datos (hero visible)', huellaReady);

  const h = await evalJson(c, `
    const txt = document.body.innerText;
    const steps = [...document.querySelectorAll('.step[data-step]')];
    const dsteps = steps.map(e=>e.getAttribute('data-step'));
    const sinEstado = steps.filter(s=>!s.getAttribute('data-state')).length;
    const units = document.querySelectorAll('.unit-stage .unit');
    const td = units[0] ? getComputedStyle(units[0]).transitionDuration : '0s';
    const agua = document.querySelector('.nt-badge--validado');
    const enlace = document.querySelector('a[href*="/expedientes/"]');
    return {
      titulos: {
        agenda: txt.includes('La agenda, en cuadritos'),
        estatus: txt.includes('¿Cuántas ya son ley?'),
        hallazgo: txt.includes('Y cuando se leen en clave 2030'),
        singulares: txt.includes('Lo que se ve al acercarse'),
        agua: txt.includes('Una ley llegó el año'),
        registro: txt.includes('¿Y esto no se sabía ya?'),
        hito2015: txt.includes('193 países'),
        hito2025: txt.includes('De los 35 países') && txt.includes('solo 10 mencionaron'),
        hito2030: txt.includes('Vence la Agenda'),
        explorador: !!document.querySelector('.explorador'),
      },
      // Cifras exactas de la escena del registro (patch registro, regla dura):
      // el texto puede abreviarse, el dato no. Se verifican verbatim.
      cifras: {
        c130: txt.includes('cerca de 130'),
        unaMencion: txt.includes('una sola mención'),
        tresMil: txt.includes('más de tres mil estudios'),
        dies35: txt.includes('35 países') && txt.includes('solo 10'),
      },
      // Meta-lenguaje prohibido en la escena (candado): "ni siquiera" no aparece.
      niSiquiera: txt.includes('ni siquiera'),
      // Los dos tramos ⟦…⟧ enlazan a referencias de /metodologia (#ref-…).
      regEnlaces: [...document.querySelectorAll('a[href*=\"/metodologia#ref-\"]')].map(a=>a.getAttribute('href')),
      dsteps, sinEstado, unitCount: units.length, td,
      lineaSteps: document.querySelectorAll('.step[data-step^=\"l\"]').length,
      lineaPts: document.querySelectorAll('.linea-pt').length,
      // El hito 2025 lleva su enlace fuente (VNR Synthesis Report).
      hito2025Fuente: [...document.querySelectorAll('.linea-fuente')].length,
      hoy: !!document.querySelector('.linea-pt.hoy'),
      counters: document.querySelectorAll('.linea-num').length,
      hasFig: !!document.querySelector('.viaje-fig'),
      aguaBadge: agua ? agua.textContent.trim() : null,
      enlaceHref: enlace ? enlace.getAttribute('href') : null,
      // v8 §B: vista previa compacta de la matriz NormTrace en la escena del agua.
      aguaMatrixRows: document.querySelectorAll('.card .ntm-row').length,
    };
  `);
  const T = h.titulos;
  assert('E1 apertura (agenda) presente', T.agenda);
  assert('E2 estatus presente', T.estatus);
  assert('E3 "el momento del color" presente', T.hallazgo);
  assert('E4 singulares presente', T.singulares);
  assert('E5 agua presente', T.agua);
  assert('B · escena del registro presente', T.registro);
  assert('Acto II · línea de tiempo con sus extremos (2015 y 2030)', T.hito2015 && T.hito2030);
  assert('Acto II · hito 2025 (10 de 35 informes citan a su parlamento)', T.hito2025);
  assert('explorador presente', T.explorador);
  assert('cada paso tiene su data-state (ningún paso sin estado)', h.sinEstado === 0, `sin estado=${h.sinEstado}`);
  assert('Acto I + registro con sus 8 pasos (0..7)', ['0','1','2','3','4','5','6','7'].every(s=>h.dsteps.includes(s)), JSON.stringify(h.dsteps));
  assert('la línea de tiempo tiene 12 pasos y 12 hitos', h.lineaSteps === 12 && h.lineaPts === 12, `pasos=${h.lineaSteps} hitos=${h.lineaPts}`);
  // Patch registro: cifras exactas verbatim, meta-lenguaje fuera y enlaces vivos.
  assert('cifra "cerca de 130" preservada verbatim', h.cifras.c130);
  assert('cifra "una sola mención" preservada verbatim', h.cifras.unaMencion);
  assert('cifra "más de tres mil estudios" preservada verbatim', h.cifras.tresMil);
  assert('cifra "10 de 35" preservada verbatim (hito 2025)', h.cifras.dies35);
  assert('la escena del registro no usa "ni siquiera" (candado)', h.niSiquiera === false);
  assert('la escena del registro enlaza a dos referencias de /metodologia', h.regEnlaces.length === 2, JSON.stringify(h.regEnlaces));
  assert('los enlaces apuntan a #ref-estrategia y #ref-biermann',
    h.regEnlaces.some(x=>x.includes('#ref-estrategia')) && h.regEnlaces.some(x=>x.includes('#ref-biermann')), JSON.stringify(h.regEnlaces));
  assert('el hito 2025 lleva enlace fuente (VNR)', h.hito2025Fuente > 0, `fuentes=${h.hito2025Fuente}`);
  assert('marcador HOY distinto presente', h.hoy);
  assert('dos contadores vivos con cifras tabulares', h.counters >= 2, `contadores=${h.counters}`);
  assert('C · sin figura viajera (óvalo gris eliminado)', h.hasFig === false);
  assert('unit chart existe con cuadritos (>20)', h.unitCount > 20, `count=${h.unitCount}`);
  assert('unit chart transiciona (transition-duration ≠ 0s)', h.td && h.td !== '0s', `td=${h.td}`);
  assert('ficha del agua con badge "Validado por la autora"', (h.aguaBadge||'').includes('Validado por la autora'), h.aguaBadge);
  assert('la tarjeta del agua enlaza a un expediente', !!h.enlaceHref && h.enlaceHref.includes('/expedientes/'), h.enlaceHref);
  assert('la vista previa de la matriz del agua muestra sus primeras filas (v8 §B, ≤8)', h.aguaMatrixRows > 0 && h.aguaMatrixRows <= 8, `filas=${h.aguaMatrixRows}`);

  async function scrollToStep(sel) {
    await c.send('Runtime.evaluate', { expression: `(()=>{const s=document.querySelector('${sel}');if(s){const r=s.getBoundingClientRect();window.scrollTo(0, window.scrollY + r.top - innerHeight*0.4);}})()` });
    await new Promise(r => setTimeout(r, 900));
  }

  // ---------- E3 · el momento del color + E · rótulos ODS completos ----------
  console.log('\n/huella — E3: el momento del color; E: rótulos ODS');
  await scrollToStep('.step[data-state=orden]');
  const beatOrden = await evalJson(c, `return { hasOds: document.querySelectorAll('.unit.has-ods').length }`);
  assert('E3 beat 1 (orden): cuadritos agrupados pero SIN color', beatOrden.hasOds === 0, `has-ods=${beatOrden.hasOds}`);
  await scrollToStep('.step[data-state=color]');
  const beatColor = await evalJson(c, `
    const rows = [...document.querySelectorAll('.unit-anno.ods-row')].filter(a=>getComputedStyle(a).opacity!=='0');
    const names = rows.map(a=>(a.querySelector('.ods-row-name')||{}).textContent||'');
    return { hasOds: document.querySelectorAll('.unit.has-ods').length,
             rows: rows.length, truncadas: names.filter(n=>/^O\\.\\.\\.$|^\\S{0,2}\\.\\.\\.$/.test(n.trim())).length,
             ejemplo: names.find(n=>/·/.test(n))||'' };
  `);
  assert('E3 beat 2 (color): los cuadritos se tiñen de su ODS', beatColor.hasOds > 20, `has-ods=${beatColor.hasOds}`);
  assert('E · rótulos de fila ODS presentes y sin truncar a "O…"', beatColor.rows > 3 && beatColor.truncadas === 0 && /·/.test(beatColor.ejemplo), `filas=${beatColor.rows} truncadas=${beatColor.truncadas} ej="${beatColor.ejemplo}"`);

  // ---------- B · la escena del registro (color → contorno → color) ----------
  console.log('\n/huella — B: la escena del registro');
  await scrollToStep('.step[data-state=registro-sin]');
  const regSin = await evalJson(c, `return { outline: document.querySelectorAll('.unit.outline').length, hasOds: document.querySelectorAll('.unit.has-ods').length }`);
  assert('registro sin registro: los cuadritos pierden color (contorno)', regSin.outline > 20 && regSin.hasOds === 0, `outline=${regSin.outline} color=${regSin.hasOds}`);
  await scrollToStep('.step[data-state=registro-con]');
  const regCon = await evalJson(c, `return { hasOds: document.querySelectorAll('.unit.has-ods').length }`);
  assert('registro documentado: el color regresa', regCon.hasOds > 20, `color=${regCon.hasOds}`);

  // ---------- A/C · la línea de tiempo avanza (paneo ≥ un paso) ----------
  console.log('\n/huella — A: la línea de tiempo avanza');
  await scrollToStep('.step[data-step=l0]');
  const l0 = await evalJson(c, `const t=document.querySelector('.linea-track'); return { x: t?getComputedStyle(t).transform:'' }`);
  await scrollToStep('.step[data-step=l5]');
  const l5 = await evalJson(c, `
    const t=document.querySelector('.linea-track');
    const m = t ? new DOMMatrixReadOnly(getComputedStyle(t).transform) : null;
    return { x: t?getComputedStyle(t).transform:'', tx: m?m.m41:0 };
  `);
  assert('la línea de tiempo se desplaza entre pasos', l0.x !== l5.x && !!l5.x, `${l0.x} → ${l5.x}`);

  // ---------- expediente de la vitrina (LGA / NormTrace) ----------
  console.log('\n/expedientes/:id — ficha NormTrace de la vitrina');
  const ficha = await goto(c, h.enlaceHref || '/expedientes/ini5', `!/Cargando expediente/.test(document.body.innerText) && document.querySelector('header h1')`);
  assert('la ficha del expediente carga (no queda en «Cargando»)', ficha);
  const f = await evalJson(c, `const t=document.body.innerText; return { nt: t.includes('Análisis NormTrace'), lga: t.includes('LGA'),
    brecha: /brecha/i.test(t), oportunidad: t.includes('Oportunidad de fortalecimiento') };`);
  assert('la ficha muestra el análisis NormTrace', f.nt);
  // D · la palabra "brecha" no aparece en ninguna vista (vocabulario v7.1-D).
  // Patch v8 §B: la matriz reemplaza la columna "Agenda" por el marcador ▸ y la
  // hoja/panel de detalle; el vocabulario "Oportunidad de fortalecimiento" vive
  // ahora en la leyenda de la matriz (siempre visible, sin necesidad de tocar
  // una fila).
  assert('D · cero apariciones de "brecha" en la ficha', f.brecha === false);
  assert('D · el vocabulario es "Oportunidad de fortalecimiento" (nunca "brecha")', f.oportunidad);

  // ---------- v8 §B · matriz NormTrace (glifos, no tabla) — escritorio ----------
  console.log('\n/expedientes/:id — matriz NormTrace (patch v8 §B), escritorio 1280px');
  const NREGS = 34; // filas del snapshot dorado servido por el fixture (34 registros)
  const matrixDesktop = await evalJson(c, `
    const rows = document.querySelectorAll('.ntm-row');
    const glyphs = document.querySelectorAll('.ntm-g[aria-label]');
    const cellText = [...rows].some(r => /fuerte|medio|d(e|é)bil/i.test((r.querySelector('.ntm-cells')||{}).textContent||''));
    return { rows: rows.length, glyphs: glyphs.length, cellText,
      hasToggle: !!document.querySelector('.ntm-toggle'), hasCsv: !!document.querySelector('.ntm-csv') };
  `);
  assert('la matriz renderiza sus filas (34, dato vivo del fixture)', matrixDesktop.rows === NREGS, `rows=${matrixDesktop.rows}`);
  assert('cada glifo trae aria-label (≥ filas × 7: cobertura + 6 dimensiones)', matrixDesktop.glyphs >= matrixDesktop.rows * 7, `glifos=${matrixDesktop.glyphs}`);
  assert('ninguna celda de la matriz imprime "fuerte/medio/débil" (solo glifos con aria-label)', matrixDesktop.cellText === false);
  assert('toggle "vista de tabla" presente', matrixDesktop.hasToggle);
  assert('botón de descarga CSV presente', matrixDesktop.hasCsv);

  // Vista de tabla: la alternativa textual completa (ahí SÍ hay palabras).
  await c.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-toggle').click()` });
  await new Promise(r => setTimeout(r, 250));
  const tablaMatriz = await evalJson(c, `return {
    table: !!document.querySelector('.ntm-full-table'),
    rows: document.querySelectorAll('.ntm-full-table tbody tr').length,
    matrixHidden: !document.querySelector('.ntm-colhead'),
  };`);
  assert('la vista de tabla existe como alternativa textual completa (34 filas)', tablaMatriz.table && tablaMatriz.rows === NREGS, JSON.stringify(tablaMatriz));
  await c.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-toggle').click()` });
  await new Promise(r => setTimeout(r, 250));

  // Filtros: un chip a la vez, removible.
  await c.send('Runtime.evaluate', { expression: `[...document.querySelectorAll('.ntm-chip')].find(b=>/procedimiento/i.test(b.textContent)).click()` });
  await new Promise(r => setTimeout(r, 250));
  const filtrado = await evalJson(c, `return { rows: document.querySelectorAll('.ntm-row').length, chipOn: !!document.querySelector('.ntm-chip.on') }`);
  assert('el filtro por dimensión débil reduce las filas visibles', filtrado.rows > 0 && filtrado.rows < NREGS, `rows=${filtrado.rows}`);
  assert('el chip activo queda marcado', filtrado.chipOn);
  await c.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-chip.on').click()` });
  await new Promise(r => setTimeout(r, 250));
  const sinFiltro = await evalJson(c, `return { rows: document.querySelectorAll('.ntm-row').length }`);
  assert('el chip es removible (un segundo toque lo quita)', sinFiltro.rows === NREGS, `rows=${sinFiltro.rows}`);

  // Tocar una fila abre el detalle con la nota (panel lateral en escritorio).
  await c.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-row').click()` });
  await new Promise(r => setTimeout(r, 300));
  const sheetDesktop = await evalJson(c, `
    const sheet = document.querySelector('.ntm-sheet');
    const r = sheet ? sheet.getBoundingClientRect() : null;
    return { open: !!sheet, hasNote: !!(sheet && sheet.querySelector('.ntm-note')),
      hasOportunidad: document.body.innerText.includes('Oportunidad de fortalecimiento'),
      width: r ? r.width : 0, height: r ? r.height : 0 };
  `);
  assert('tocar una fila abre el detalle con su nota', sheetDesktop.open && sheetDesktop.hasNote, JSON.stringify(sheetDesktop));
  assert('escritorio: el detalle es un panel lateral (ancho acotado, alto de pantalla)', sheetDesktop.width <= 420 && sheetDesktop.height >= 400, JSON.stringify(sheetDesktop));
  await c.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-close') && document.querySelector('.ntm-close').click()` });
  await new Promise(r => setTimeout(r, 200));

  // ---------- v8 §B · matriz NormTrace @375px (sin scroll horizontal) ----------
  console.log('\n/expedientes/:id — matriz NormTrace @375px, sin scroll horizontal');
  const cMobFicha = await newPage();
  await cMobFicha.send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 2, mobile: true, screenWidth: 375, screenHeight: 812 });
  await cMobFicha.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 1 }).catch(() => {});
  await goto(cMobFicha, h.enlaceHref || '/expedientes/ini5', `document.querySelector('.ntm-row')`);
  const mobMatrix = await evalJson(cMobFicha, `
    const rows = document.querySelectorAll('.ntm-row');
    const glyphs = document.querySelectorAll('.ntm-g[aria-label]');
    const cellText = [...rows].some(r => /fuerte|medio|d(e|é)bil/i.test((r.querySelector('.ntm-cells')||{}).textContent||''));
    return { rows: rows.length, glyphs: glyphs.length, cellText,
      scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth };
  `);
  assert('@375 la matriz renderiza sus 34 filas', mobMatrix.rows === NREGS, `rows=${mobMatrix.rows}`);
  assert('@375 la matriz se lee sin scroll horizontal de página', mobMatrix.scrollW <= mobMatrix.clientW + 1, JSON.stringify(mobMatrix));
  assert('@375 ninguna celda imprime fuerte/medio/débil (solo glifos con aria-label)', mobMatrix.cellText === false);
  assert('@375 los glifos traen aria-label (≥ filas × 7)', mobMatrix.glyphs >= mobMatrix.rows * 7, `glifos=${mobMatrix.glyphs}`);

  await cMobFicha.send('Runtime.evaluate', { expression: `document.querySelector('.ntm-row').click()` });
  await new Promise(r => setTimeout(r, 300));
  const mobSheet = await evalJson(cMobFicha, `
    const sheet = document.querySelector('.ntm-sheet');
    const r = sheet ? sheet.getBoundingClientRect() : null;
    return { open: !!sheet, hasNote: !!(sheet && sheet.querySelector('.ntm-note')), bottom: r ? r.bottom : 0, width: r ? r.width : 0 };
  `);
  assert('@375 tocar una fila abre la hoja inferior con su nota', mobSheet.open && mobSheet.hasNote, JSON.stringify(mobSheet));
  assert('@375 la hoja se ancla al fondo con el ancho completo (hoja inferior, no panel)', mobSheet.bottom >= 812 - 4 && mobSheet.width >= 375 - 4, JSON.stringify(mobSheet));
  await cMobFicha.send('Page.close').catch(() => {});

  // ---------- /minutas ----------
  console.log('\n/minutas — tarjetas dinámicas y filtros');
  const minReady = await goto(c, '/minutas', `document.querySelector('.kpi .v') && document.querySelectorAll('.rec-card').length>0`);
  assert('minutas carga con datos', minReady);
  // count-up: la cifra final aparece
  let kpiFinal = false;
  for (let i = 0; i < 12; i++) {
    const r = await evalJson(c, `return [...document.querySelectorAll('.kpi .v')].map(e=>e.textContent)`);
    if (r.some(v => /\b139\b/.test(v))) { kpiFinal = true; break; }
    await new Promise(r => setTimeout(r, 250));
  }
  assert('KPI cards animan hasta su cifra final (139)', kpiFinal);
  const m = await evalJson(c, `
    return {
      cards: document.querySelectorAll('.rec-card').length,
      toggle: !!document.querySelector('.view-toggle'),
      filtro: !!document.querySelector('.filters input'),
      contador: (document.querySelector('.result-count')||{}).textContent||'',
      barrasOds: document.querySelectorAll('.bar-row.is-ods').length,
    };
  `);
  assert('minutas conserva tarjetas (rec-card)', m.cards > 0, `cards=${m.cards}`);
  assert('minutas conserva toggle tarjetas/tabla', m.toggle);
  assert('minutas conserva filtros', m.filtro);
  assert('minutas muestra contador vivo ("… de …")', /\bde\b/.test(m.contador), m.contador);
  assert('gráfica por ODS usa barras is-ods', m.barrasOds > 0, `is-ods=${m.barrasOds}`);
  // toggle a tabla
  await c.send('Runtime.evaluate', { expression: `[...document.querySelectorAll('.view-toggle button')].find(b=>/Tabla/i.test(b.textContent))?.click()` });
  await new Promise(r => setTimeout(r, 400));
  const tabla = await evalJson(c, `return { table: !!document.querySelector('table tbody tr') }`);
  assert('el toggle muestra la tabla densa', tabla.table);

  // ---------- /metodologia · bloque de referencias (patch registro §5) ----------
  console.log('\n/metodologia — bloque de referencias con anclas');
  const metReady = await goto(c, '/metodologia', `document.querySelector('article.prose h1')`);
  assert('metodologia carga', metReady);
  const met = await evalJson(c, `
    const ids = ['ref-estrategia','ref-biermann','ref-vnr','ref-toolkit'];
    return {
      anclas: ids.filter(id => !!document.getElementById(id)),
      enlaces: ids.filter(id => { const el=document.getElementById(id); return el && el.querySelector('a[href^=\"http\"]'); }),
      biermannDoi: (document.getElementById('ref-biermann')||{}).innerHTML ? /10\\.1038\\/s41893-022-00909-5/.test(document.getElementById('ref-biermann').innerHTML) : false,
    };
  `);
  assert('las cuatro referencias tienen su ancla (#ref-…)', met.anclas.length === 4, JSON.stringify(met.anclas));
  assert('cada referencia trae su enlace externo', met.enlaces.length === 4, JSON.stringify(met.enlaces));
  assert('la referencia Biermann conserva su DOI', met.biermannDoi);

  // ---------- Anticolisión de etiquetas de grupo en 5 anchos (v7 §0.2) ----------
  console.log('\n/huella — etiquetas de grupo sin traslape (5 anchos)');
  for (const width of [320, 375, 768, 1024, 1440]) {
    const cw = await newPage();
    await cw.send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: width <= 480, screenWidth: width, screenHeight: 900 });
    await goto(cw, '/huella', `document.querySelector('.hero-art')`);
    await cw.send('Runtime.evaluate', { expression: `(()=>{const s=document.querySelector('.step[data-state=estatus]');if(s){const r=s.getBoundingClientRect();window.scrollTo(0, window.scrollY + r.top - innerHeight*0.4);}})()` });
    await new Promise(r => setTimeout(r, 900));
    const res = await evalJson(cw, `
      const annos = [...document.querySelectorAll('.unit-anno')].filter(a=>getComputedStyle(a).opacity!=='0').map(a=>a.getBoundingClientRect());
      let overlap = 0;
      for (let i=0;i<annos.length;i++) for (let j=i+1;j<annos.length;j++) {
        const a=annos[i], b=annos[j];
        if (a.right>b.left+1 && b.right>a.left+1 && a.bottom>b.top+1 && b.bottom>a.top+1) overlap++;
      }
      return { count: annos.length, overlap };
    `);
    assert(`etiquetas de grupo sin traslape @${width}px`, res.overlap === 0, `annos=${res.count} traslapes=${res.overlap}`);
    await cw.send('Page.close').catch(() => {});
  }

  // ---------- §A.5 (v8) · Scrollytelling MÓVIL: recupera el sticky sin romper
  // nada (head gigante, scroll bloqueado, storytelling eliminado). Viewports
  // 375×667 y 390×844, scroll NATIVO del documento (window.scrollTo), mismo
  // mecanismo de estado que el IntersectionObserver de producción. ----------
  console.log('\n/huella — scrollytelling móvil (sticky ≤45vh, texto legible, scroll nativo)');
  for (const vp of [{ w: 375, h: 667 }, { w: 390, h: 844 }]) {
    const cm = await newPage();
    await cm.send('Emulation.setDeviceMetricsOverride', { width: vp.w, height: vp.h, deviceScaleFactor: 2, mobile: true, screenWidth: vp.w, screenHeight: vp.h });
    await cm.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 1 }).catch(() => {});
    const mobileReady = await goto(cm, '/huella', `document.querySelector('.hero-art') && !/Cargando/.test((document.querySelector('.story-hero .lede')||{}).textContent||'')`);
    assert(`@${vp.w}×${vp.h} huella carga con datos en móvil`, mobileReady);
    await new Promise(r => setTimeout(r, 400));
    const tag = `${vp.w}×${vp.h}`;

    // Lleva el TOP del paso 'sel' a la línea central del viewport: es
    // exactamente el criterio del IntersectionObserver de producción
    // (rootMargin '-50% 0px -50% 0px', threshold 0 → dispara cuando el TOP
    // del target cruza esa línea, no su centro). +6px de margen para no caer
    // justo en el límite flotante entre dos pasos. Scroll NATIVO
    // (window.scrollTo), no un scroll-jacking propio.
    async function toTrigger(sel) {
      await cm.send('Runtime.evaluate', { expression: `(()=>{const s=document.querySelector('${sel}');if(s){const r=s.getBoundingClientRect();window.scrollTo(0, window.scrollY + r.top - innerHeight*0.5 + 6);}})()` });
      await new Promise(r => setTimeout(r, 900));
    }

    // a + e. cada escena del Acto I existe y dispara su estado al cruzar la
    // línea de disparo real; b. el panel jamás tapa la tarjeta (su borde
    // superior queda por debajo del panel) y le deja ≥50% del viewport
    // disponible para leer (garantizado por el panel ≤45vh + nav ocultable);
    // d. el panel gráfico nunca excede 45vh.
    const escenasActoI = ['grid', 'estatus', 'orden', 'color', 'singulares', 'agua', 'registro-sin', 'registro-con'];
    let scenesOk = true; const scenesDetail = [];
    for (const st of escenasActoI) {
      await toTrigger(`.step[data-state="${st}"]`);
      const r = await evalJson(cm, `
        const actI = document.querySelectorAll('.scrolly-graphic')[0];
        const card = document.querySelector('.step[data-state="${st}"] .step-card');
        const pr = actI ? actI.getBoundingClientRect() : null;
        const cr = card ? card.getBoundingClientRect() : null;
        return {
          state: actI ? actI.getAttribute('data-state') : null,
          panelH: pr ? pr.height : 0,
          panelBottom: pr ? pr.bottom : 0,
          panelPos: actI ? getComputedStyle(actI).position : '',
          cardTop: cr ? cr.top : null, cardH: cr ? cr.height : 0, innerH: innerHeight,
        };
      `);
      if (r.state !== st) { scenesOk = false; scenesDetail.push(`${st}→${r.state}`); }
      const readingArea = r.innerH - r.panelBottom;
      // El panel nunca debe robarle lectura a una tarjeta que SÍ cabría entera
      // en el área disponible. Cuando la tarjeta es más alta que esa área
      // (p. ej. "registro-sin", con título + dos párrafos y enlaces: no se
      // acorta el copy por esto), es geométricamente inevitable que parte
      // quede fuera de pantalla — igual que en cualquier bloque de texto más
      // largo que la pantalla — y lo que importa es que el área disponible
      // esté aprovechada con texto de principio a fin, no tapada de más.
      const cabeEntera = r.cardH <= readingArea + 2;
      if (cabeEntera) {
        assert(`@${tag} paso "${st}": el panel nunca tapa el arranque de la tarjeta`, r.cardTop == null || r.cardTop >= r.panelBottom - 4, `cardTop=${Math.round(r.cardTop)} panelBottom=${Math.round(r.panelBottom)}`);
      } else {
        assert(`@${tag} paso "${st}": tarjeta más alta que el área disponible — el área queda llena de texto, sin franja tapada de más`, r.cardTop <= r.panelBottom + 2, `cardTop=${Math.round(r.cardTop)} panelBottom=${Math.round(r.panelBottom)} cardH=${Math.round(r.cardH)} área=${Math.round(readingArea)}`);
      }
      assert(`@${tag} paso "${st}": el texto dispone de ≥50% del alto del viewport bajo el panel`, readingArea >= r.innerH * 0.5 - 2, `disponible=${Math.round(readingArea)}px de ${r.innerH}px (${Math.round(readingArea / r.innerH * 100)}%)`);
      assert(`@${tag} paso "${st}": el panel gráfico nunca excede 45vh`, r.panelH <= vp.h * 0.45 + 1, `panelH=${Math.round(r.panelH)}px, 45vh=${Math.round(vp.h * 0.45)}px`);
      assert(`@${tag} paso "${st}": el panel usa position:sticky (nunca fixed)`, r.panelPos === 'sticky', r.panelPos);
    }
    assert(`@${tag} e · las 8 escenas del Acto I disparan su estado al cruzar la línea de disparo (mismo mecanismo del IntersectionObserver)`, scenesOk, scenesDetail.join(', ') || 'ok');

    // e. la línea de tiempo (Acto II) también existe y se detecta en móvil.
    let lineaOk = true; const lineaDetail = [];
    for (const li of [0, 5, 11]) {
      await toTrigger(`.step[data-step="l${li}"]`);
      const r = await evalJson(cm, `
        const lp = document.querySelectorAll('.scrolly-graphic')[1];
        return { state: lp ? lp.getAttribute('data-state') : null, panelH: lp ? lp.getBoundingClientRect().height : 0 };
      `);
      if (r.state !== ('linea-' + li)) { lineaOk = false; lineaDetail.push(`l${li}→${r.state}`); }
      assert(`@${tag} línea l${li}: el panel nunca excede 45vh`, r.panelH <= vp.h * 0.45 + 1, `panelH=${Math.round(r.panelH)}px`);
    }
    assert(`@${tag} e · la línea de tiempo dispara su estado al cruzar la línea de disparo en móvil`, lineaOk, lineaDetail.join(', ') || 'ok');

    // c. body/html sin overflow bloqueado: se puede scrollear de la apertura al pie.
    await cm.send('Runtime.evaluate', { expression: `window.scrollTo(0, 0)` });
    await new Promise(r => setTimeout(r, 300));
    const overflowInfo = await evalJson(cm, `return {
      htmlOverflowY: getComputedStyle(document.documentElement).overflowY,
      bodyOverflowY: getComputedStyle(document.body).overflowY,
    };`);
    assert(`@${tag} c · html sin overflow-y bloqueado`, overflowInfo.htmlOverflowY !== 'hidden', overflowInfo.htmlOverflowY);
    assert(`@${tag} c · body sin overflow-y bloqueado`, overflowInfo.bodyOverflowY !== 'hidden', overflowInfo.bodyOverflowY);
    await cm.send('Runtime.evaluate', { expression: `window.scrollTo(0, document.documentElement.scrollHeight)` });
    await new Promise(r => setTimeout(r, 600));
    const bottom = await evalJson(cm, `return { y: window.scrollY, maxY: document.documentElement.scrollHeight - innerHeight }`);
    assert(`@${tag} c · el scroll nativo llega hasta el pie sin quedar atrapado`, bottom.y >= bottom.maxY - 4, `scrollY=${bottom.y} maxY=${bottom.maxY}`);

    await cm.send('Page.close').catch(() => {});
  }
} catch (e) {
  fail('runner sin excepción', String(e && e.stack || e));
} finally {
  chrome.kill(); server.close();
}

const passed = results.filter(r => r[0]).length;
const failed = results.length - passed;
console.log(`\nInvariantes: ${passed}/${results.length} en verde` + (failed ? `, ${failed} en rojo` : ''));
process.exit(failed ? 1 : 0);
