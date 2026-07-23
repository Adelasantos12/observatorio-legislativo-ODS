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
// Red de seguridad: nunca colgar más de 100s.
setTimeout(() => { console.error('Timeout global del runner'); process.exit(1); }, 100000).unref();
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
    const steps = [...document.querySelectorAll('[data-step]')].map(e=>e.getAttribute('data-step'));
    const units = document.querySelectorAll('.unit-stage .unit');
    const unit = units[0];
    const td = unit ? getComputedStyle(unit).transitionDuration : '0s';
    const agua = document.querySelector('.nt-badge--validado');
    const enlace = document.querySelector('a[href*="/expedientes/"]');
    return {
      titulos: {
        agenda: txt.includes('La agenda, en cuadritos'),
        estatus: txt.includes('¿Cuántas ya son ley?'),
        hallazgo: txt.includes('Casi la mitad mira al mismo lugar'),
        singulares: txt.includes('Lo que se ve al acercarse'),
        agua: txt.includes('Una ley llegó el año'),
        porque: txt.includes('Por qué nombrar esto vale la pena'),
        quien_mas: txt.includes('Otros parlamentos ya llevan su cuenta'),
        explorador: txt.includes('Explora')||txt.includes('explora')||!!document.querySelector('.explorador'),
      },
      steps, unitCount: units.length, td,
      aguaBadge: agua ? agua.textContent.trim() : null,
      enlaceHref: enlace ? enlace.getAttribute('href') : null,
    };
  `);
  const T = h.titulos;
  assert('escena apertura (agenda) presente', T.agenda);
  assert('escena estatus presente', T.estatus);
  assert('escena hallazgo presente', T.hallazgo);
  assert('escena singulares presente', T.singulares);
  assert('escena del agua presente', T.agua);
  assert('sección "por qué importa" presente', T.porque);
  assert('sección "quién más lo hace" presente', T.quien_mas);
  assert('explorador presente', T.explorador);
  assert('pasos del scrollytelling en orden 0..4', JSON.stringify(h.steps) === JSON.stringify(['0','1','2','3','4']), JSON.stringify(h.steps));
  assert('unit chart existe con cuadritos (>20)', h.unitCount > 20, `count=${h.unitCount}`);
  assert('unit chart transiciona (transition-duration ≠ 0s)', h.td && h.td !== '0s', `td=${h.td}`);
  assert('ficha del agua con badge "Validado por la autora"', (h.aguaBadge||'').includes('Validado por la autora'), h.aguaBadge);
  assert('la tarjeta del agua enlaza a un expediente', !!h.enlaceHref && h.enlaceHref.includes('/expedientes/'), h.enlaceHref);

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
} catch (e) {
  fail('runner sin excepción', String(e && e.stack || e));
} finally {
  chrome.kill(); server.close();
}

const passed = results.filter(r => r[0]).length;
const failed = results.length - passed;
console.log(`\nInvariantes: ${passed}/${results.length} en verde` + (failed ? `, ${failed} en rojo` : ''));
process.exit(failed ? 1 : 0);
