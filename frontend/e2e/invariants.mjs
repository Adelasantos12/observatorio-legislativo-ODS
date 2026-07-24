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
        madrid: txt.includes('En Madrid ya lo hacen'),
        asuncion: txt.includes('En Asunción lo hacen desde adentro'),
        foros: txt.includes('Y en los foros ya hay mesa puesta'),
        mexico: txt.includes('México no llega tarde'),
        cierre: txt.includes('Quien guarda el registro cuenta la historia'),
        explorador: !!document.querySelector('.explorador'),
      },
      dsteps, sinEstado, unitCount: units.length, td,
      viajeStops: document.querySelectorAll('.viaje-stop').length,
      viajeSteps: document.querySelectorAll('.step[data-step^=\"v\"]').length,
      hasFig: !!document.querySelector('.viaje-fig'),
      aguaBadge: agua ? agua.textContent.trim() : null,
      enlaceHref: enlace ? enlace.getAttribute('href') : null,
    };
  `);
  const T = h.titulos;
  assert('E1 apertura (agenda) presente', T.agenda);
  assert('E2 estatus presente', T.estatus);
  assert('E3 "el momento del color" presente (título reescrito)', T.hallazgo);
  assert('E4 singulares presente', T.singulares);
  assert('E5 agua presente', T.agua);
  assert('Acto II · V1 Madrid presente', T.madrid);
  assert('Acto II · V2 Asunción presente', T.asuncion);
  assert('Acto II · V3 foros presente', T.foros);
  assert('Acto II · V4 México presente', T.mexico);
  assert('Acto II · V5 cierre presente', T.cierre);
  assert('explorador presente', T.explorador);
  // v7 §0.1: ningún paso sin estado gráfico
  assert('cada paso tiene su data-state (ningún paso sin estado)', h.sinEstado === 0, `sin estado=${h.sinEstado}`);
  assert('Acto I con sus 6 pasos (0..5)', ['0','1','2','3','4','5'].every(s=>h.dsteps.includes(s)), JSON.stringify(h.dsteps));
  assert('el viaje tiene sus 5 pasos y 4 paradas', h.viajeSteps === 5 && h.viajeStops === 4, `pasos=${h.viajeSteps} paradas=${h.viajeStops}`);
  assert('la figura del viaje existe', h.hasFig);
  assert('unit chart existe con cuadritos (>20)', h.unitCount > 20, `count=${h.unitCount}`);
  assert('unit chart transiciona (transition-duration ≠ 0s)', h.td && h.td !== '0s', `td=${h.td}`);
  assert('ficha del agua con badge "Validado por la autora"', (h.aguaBadge||'').includes('Validado por la autora'), h.aguaBadge);
  assert('la tarjeta del agua enlaza a un expediente', !!h.enlaceHref && h.enlaceHref.includes('/expedientes/'), h.enlaceHref);

  // ---------- E3 · el momento del color (beat neutro → color) ----------
  console.log('\n/huella — E3: el momento del color');
  async function scrollToStep(sel) {
    await c.send('Runtime.evaluate', { expression: `(()=>{const s=document.querySelector('${sel}');if(s){const r=s.getBoundingClientRect();window.scrollTo(0, window.scrollY + r.top - innerHeight*0.4);}})()` });
    await new Promise(r => setTimeout(r, 900));
  }
  await scrollToStep('.step[data-state=orden]');
  const beatOrden = await evalJson(c, `return { hasOds: document.querySelectorAll('.unit.has-ods').length, state: (document.querySelector('.scrolly .scrolly-graphic')||{}).getAttribute?.('data-state') }`);
  assert('E3 beat 1 (orden): cuadritos agrupados pero SIN color', beatOrden.hasOds === 0, `has-ods=${beatOrden.hasOds}`);
  await scrollToStep('.step[data-state=color]');
  const beatColor = await evalJson(c, `return { hasOds: document.querySelectorAll('.unit.has-ods').length }`);
  assert('E3 beat 2 (color): los cuadritos se tiñen de su ODS', beatColor.hasOds > 20, `has-ods=${beatColor.hasOds}`);

  // ---------- Acto II · la figura del viaje se mueve ----------
  console.log('\n/huella — Acto II: la figura recorre el camino');
  await scrollToStep('.step[data-step=v0]');
  const p0 = await evalJson(c, `return { left: (document.querySelector('.viaje-fig')||{}).style?.left||'' }`);
  await scrollToStep('.step[data-step=v3]');
  const p3 = await evalJson(c, `return { left: (document.querySelector('.viaje-fig')||{}).style?.left||'', ring: getComputedStyle(document.querySelector('.viaje-stop.is-final .ring')||document.body).opacity }`);
  assert('la figura del viaje se mueve entre paradas', p0.left !== p3.left && !!p3.left, `${p0.left} → ${p3.left}`);

  // ---------- expediente de la vitrina (LGA / NormTrace) ----------
  console.log('\n/expedientes/:id — ficha NormTrace de la vitrina');
  const ficha = await goto(c, h.enlaceHref || '/expedientes/ini5', `!/Cargando expediente/.test(document.body.innerText) && document.querySelector('header h1')`);
  assert('la ficha del expediente carga (no queda en «Cargando»)', ficha);
  const f = await evalJson(c, `const t=document.body.innerText; return { nt: t.includes('Análisis NormTrace'), lga: t.includes('LGA') };`);
  assert('la ficha muestra el análisis NormTrace', f.nt);

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
