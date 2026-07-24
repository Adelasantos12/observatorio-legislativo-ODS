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
    brecha: /brecha/i.test(t), agenda: t.includes('Agenda'), oportunidad: t.includes('Oportunidad de fortalecimiento') };`);
  assert('la ficha muestra el análisis NormTrace', f.nt);
  // D · la palabra "brecha" no aparece en ninguna vista; la columna es "Agenda"
  assert('D · cero apariciones de "brecha" en la ficha', f.brecha === false);
  assert('D · la columna se presenta como "Agenda" / "Oportunidad de fortalecimiento"', f.agenda && f.oportunidad);

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
} catch (e) {
  fail('runner sin excepción', String(e && e.stack || e));
} finally {
  chrome.kill(); server.close();
}

const passed = results.filter(r => r[0]).length;
const failed = results.length - passed;
console.log(`\nInvariantes: ${passed}/${results.length} en verde` + (failed ? `, ${failed} en rojo` : ''));
process.exit(failed ? 1 : 0);
