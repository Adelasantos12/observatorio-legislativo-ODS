<template>
  <div class="huella-page" :class="{ 'no-anim': !animate }">
    <!-- Sin datos: la historia nunca se dibuja con ceros del API (v4.1 §5) -->
    <div v-if="!ready" class="story-hero">
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ C.hero.cargando }}</h1>
    </div>
    <div v-else-if="!hasData" class="story-hero">
      <img class="section-art" :src="art.neutra" alt="" aria-hidden="true" />
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ C.estadoVacio.titulo }}</h1>
      <p class="sub">{{ C.estadoVacio.cuerpo }}</p>
    </div>

    <template v-else>
    <!-- Apertura (escena 1): hero de manchas ODS ascendiendo al anillo -->
    <header class="story-hero">
      <img class="hero-art" :src="art.hero" alt="Figuras en colores de los ODS ascendiendo hacia el anillo de los 17 Objetivos" />
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ fill(C.hero.lede, { minutas: nMinutas, aprobadas: nLogradas, iniciativas: nIniciativas }) }}</h1>
      <p class="sub">{{ C.hero.sub }}</p>
    </header>

    <div class="story">
      <div class="scrolly">
        <!-- Gráfico fijo (un solo panel; su estado se deriva del índice de paso, v7 §0.3) -->
        <div class="scrolly-graphic" :data-state="graphicState">
          <div style="width:100%">
            <div v-show="scene <= 4">
              <div ref="stageEl" class="unit-stage">
                <div v-for="n in nodes" :key="n.id" class="unit"
                  :class="[n.type === 'min' ? 'is-min' : 'is-ini', { faint: scene === 1 && n.type === 'ini', 'has-ods': colored && n.ods, dim: pos[n.id] && pos[n.id].dim, glow: pos[n.id] && pos[n.id].glow }]"
                  :style="unitStyle(n)" :title="n.label"></div>
                <div v-for="a in annotations" :key="a.key" class="unit-anno"
                     :style="{ left: a.x + 'px', top: a.y + 'px', maxWidth: (a.w ? a.w + 'px' : undefined), opacity: a.show ? 1 : 0 }" :title="a.full || a.text">
                  <b>{{ a.n }}</b> {{ a.text }}
                </div>
              </div>
              <div class="unit-legend">
                <span class="k"><span class="sw" style="background:var(--ink-2);opacity:.8"></span> {{ C.leyenda.minuta }} ({{ nMinutas }})</span>
                <span class="k"><span class="sw" style="background:var(--ink-3)"></span> {{ C.leyenda.iniciativa }} ({{ nIniciativas }})</span>
                <span class="k" v-show="colored"><span class="sw" style="background:linear-gradient(90deg,#e5243b,#26bde2,#4c9f38)"></span> agrupadas por ODS</span>
              </div>
            </div>

            <!-- E5: el caso del agua (invariante v6.2, no puede faltar) -->
            <div v-show="scene === 5" class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
                <h3 style="margin:0">{{ C.escenas.agua.fichaTitulo }}</h3>
                <span class="nt-badge nt-badge--validado">● {{ C.escenas.agua.fichaBadge }}</span>
              </div>
              <p class="muted">{{ C.escenas.agua.fichaResumen }}</p>
              <table class="nt-table" v-if="agua.length">
                <thead><tr><th>Estándar</th><th>Disposición</th><th>Rol</th><th>Cobertura</th></tr></thead>
                <tbody>
                  <tr v-for="(r,i) in agua.slice(0,6)" :key="i">
                    <td>{{ r.estandar }}</td><td>{{ r.disposicion }}</td>
                    <td><span :class="{muted: r.rol_correspondencia!=='sustantivo'}">{{ r.rol_correspondencia==='sustantivo'?'sustantivo':'contextual' }}</span></td>
                    <td>{{ r.cobertura }}</td>
                  </tr>
                </tbody>
              </table>
              <!-- Serie abierta: armonización estatal (32 entidades). Sin fuente
                   del dato todavía, se muestra "en documentación", nunca "0 de 32". -->
              <div style="margin-top:14px">
                <div class="muted" style="margin-bottom:6px">
                  {{ C.escenas.agua.contadorLabel }} ·
                  <template v-if="armonizadas != null"><b>{{ armonizadas }}</b> {{ C.escenas.agua.contadorNota }}</template>
                  <span v-else class="badge">{{ C.escenas.agua.contadorSinDato }}</span>
                </div>
                <div class="serie">
                  <span v-for="i in 32" :key="i" class="serie-box" :class="{ full: armonizadas != null && i <= armonizadas }"></span>
                </div>
              </div>
              <p style="margin-top:12px" v-if="vitrina">
                <router-link :to="{ name: 'expediente', params: { id: vitrina } }">{{ C.escenas.agua.enlace }}</router-link>
              </p>
            </div>
          </div>
        </div>

        <!-- Pasos de prosa (Acto I). Cada paso dispara un estado del panel. -->
        <div class="scrolly-steps">
          <section class="step" data-step="0" data-state="grid"><div class="step-card">
            <h2>{{ C.escenas.agenda.titulo }}</h2>
            <p>{{ fill(C.escenas.agenda.p1, { minutas: nMinutas, iniciativas: nIniciativas }) }}</p>
            <p class="muted">{{ C.escenas.agenda.p2 }}</p>
          </div></section>

          <section class="step" data-step="1" data-state="estatus"><div class="step-card">
            <h2>{{ C.escenas.estatus.titulo }}</h2>
            <p>{{ fill(C.escenas.estatus.p1, { dof: est.publicada_dof || 0, revisora: est.en_revisora || 0, devueltas: est.devuelta || 0 }) }}</p>
            <p>
              <span class="st-badge st-dof"><span class="ic"></span>{{ C.estatus.publicada_dof }}</span> ·
              <span class="st-badge st-rev"><span class="ic"></span>{{ C.estatus.en_revisora }}</span> ·
              <span class="st-badge st-dev"><span class="ic"></span>{{ C.estatus.devuelta }}</span>
            </p>
          </div></section>

          <!-- E3 · beat 1: se ordenan por objetivo, todavía sin color -->
          <section class="step" data-step="2" data-state="orden"><div class="step-card">
            <h2>{{ C.escenas.hallazgo.titulo }}</h2>
            <p>{{ C.escenas.hallazgo.p1 }}</p>
          </div></section>

          <!-- E3 · beat 2: el momento del color -->
          <section class="step" data-step="3" data-state="color"><div class="step-card">
            <p class="lede-color">{{ C.escenas.hallazgo.p2 }}</p>
          </div></section>

          <section class="step" data-step="4" data-state="singulares"><div class="step-card">
            <h2>{{ C.escenas.singulares.titulo }}</h2>
            <p>{{ fill(C.escenas.singulares.p1, { sinOds: nSinOds }) }}</p>
            <p class="muted">{{ C.escenas.singulares.p2 }}</p>
          </div></section>

          <section class="step" data-step="5" data-state="agua"><div class="step-card">
            <h2>{{ C.escenas.agua.titulo }}</h2>
            <p>{{ C.escenas.agua.p1 }}</p>
            <p class="muted">{{ C.escenas.agua.p2 }}</p>
          </div></section>
        </div>
      </div>

      <!-- ACTO II · El viaje (guion v7): camino con cuatro paradas y una figura
           mancha que avanza; sustituye a las tres columnas de "por qué importa". -->
      <div v-if="C.viaje" class="story viaje">
      <div class="scrolly">
        <div class="scrolly-graphic" :data-state="'viaje-' + viajeScene">
          <div style="width:100%">
            <div class="viaje-stage">
              <div class="viaje-path"></div>
              <!-- paradas -->
              <div v-for="(st, i) in paradas" :key="st.key" class="viaje-stop"
                   :class="{ 'is-active': i === Math.min(viajeScene,3), 'is-final': i === 3, 'reveal-ring': i === 3 && viajeScene >= 3 }"
                   :style="{ left: st.x + '%' }">
                <img v-if="i === 3" class="ring" :src="art.anillo" alt="Anillo de los 17 ODS" />
                <span class="dot"></span>
                <span class="chip">{{ st.label }}</span>
              </div>
              <!-- extras por parada -->
              <div class="viaje-mini" :class="{ show: viajeScene === 0 }" :style="{ left: paradas[0].x + '%' }">
                <span v-for="m in 12" :key="m" class="m"></span>
              </div>
              <div class="viaje-mini institucional" :class="{ show: viajeScene === 1 }" :style="{ left: paradas[1].x + '%' }">
                <span v-for="m in 12" :key="m" class="m"></span>
              </div>
              <div class="viaje-sig" :style="{ left: paradas[2].x + '%', opacity: viajeScene === 2 ? 1 : 0, transition: 'opacity .5s ease-in-out' }">
                <span v-for="s in (C.viaje.foros.chips || [])" :key="s" class="s">{{ s }}</span>
              </div>
              <div class="viaje-sig" :style="{ left: paradas[3].x + '%', top: '46%', opacity: viajeScene >= 3 ? 1 : 0, transition: 'opacity .5s ease-in-out' }">
                <span v-for="s in (C.viaje.mexico.chips || [])" :key="s" class="s">{{ s }}</span>
              </div>
              <!-- figura mancha que avanza -->
              <svg class="viaje-fig" :style="{ left: paradas[Math.min(viajeScene,3)].x + '%' }" viewBox="0 0 30 40" aria-hidden="true">
                <path class="pebble" d="M15 39 C6 39 2 31 3 22 C4 12 8 3 15 3 C22 3 26 12 27 22 C28 31 24 39 15 39 Z"/>
              </svg>
            </div>
            <p class="viaje-legend">{{ paradas[Math.min(viajeScene,3)].label }}</p>
          </div>
        </div>
        <div class="scrolly-steps">
          <section class="step" data-step="v0" data-state="viaje-0"><div class="step-card">
            <h2>{{ C.viaje.madrid.titulo }}</h2><p>{{ C.viaje.madrid.p }}</p>
          </div></section>
          <section class="step" data-step="v1" data-state="viaje-1"><div class="step-card">
            <h2>{{ C.viaje.asuncion.titulo }}</h2><p>{{ C.viaje.asuncion.p }}</p>
          </div></section>
          <section class="step" data-step="v2" data-state="viaje-2"><div class="step-card">
            <h2>{{ C.viaje.foros.titulo }}</h2><p>{{ C.viaje.foros.p }}</p>
          </div></section>
          <section class="step" data-step="v3" data-state="viaje-3"><div class="step-card">
            <h2>{{ C.viaje.mexico.titulo }}</h2><p>{{ C.viaje.mexico.p1 }}</p><p>{{ C.viaje.mexico.p2 }}</p>
          </div></section>
          <section class="step" data-step="v4" data-state="viaje-4"><div class="step-card">
            <h2>{{ C.viaje.cierre.titulo }}</h2><p>{{ C.viaje.cierre.p }}</p>
          </div></section>
        </div>
      </div>
      </div>

      <!-- Explorador (escena 7) -->
      <section class="card explorador" style="margin:0 clamp(16px,5vw,56px) 24px">
        <h3 style="margin-top:0">{{ C.explorador.titulo }}</h3>
        <p class="muted" style="max-width:36em">{{ C.explorador.intro }}</p>
        <div class="filters">
          <input v-model="q" @input="loadIniciativas" :placeholder="C.explorador.buscar" />
          <select v-model="fOds" @change="loadIniciativas">
            <option value="">{{ C.explorador.todosOds }}</option>
            <option v-for="row in agg.por_ods" :key="row.ods" :value="row.ods">ODS {{ row.ods }} — {{ odsName(row.ods) }}</option>
          </select>
          <input v-model="fMeta" @input="loadIniciativas" :placeholder="C.explorador.metaPlaceholder" style="width:120px" />
          <button class="badge" @click="clearFilters">{{ C.explorador.limpiar }}</button>
        </div>
        <table>
          <thead><tr><th>{{ C.explorador.colNum }}</th><th>{{ C.explorador.colDenominacion }}</th><th>{{ C.explorador.colOds }}</th><th>{{ C.explorador.colEstatus }}</th><th>{{ C.explorador.colConfianza }}</th></tr></thead>
          <tbody>
            <tr class="item" v-for="i in iniciativas" :key="i.id" @click="goExpediente(i.id)">
              <td>{{ i.num }}</td>
              <td>{{ i.denominacion }}<br><span class="muted">{{ i.tema }}</span></td>
              <td>
                <span v-if="i.ods_principal" class="ods-chip" :style="{background: odsColor(i.ods_principal)}">{{ i.ods_principal }}</span>
                <span v-for="s in i.ods_secundarios" :key="s" class="ods-chip" :style="{background: odsColor(s), opacity:.6, marginLeft:'3px'}">{{ s }}</span>
                <div class="muted" v-if="i.metas && i.metas.length">{{ i.metas.join(' · ') }}</div>
              </td>
              <td>{{ i.estatus }}</td>
              <td><span class="badge" :class="'badge--' + (i.confianza||'pendiente')">{{ i.confianza || C.explorador.sinCodificar }}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="muted" v-if="!iniciativas.length">{{ C.explorador.sinResultados }}</p>
        <p style="margin-top:12px"><router-link :to="{ name: 'minutas' }">{{ C.explorador.ctaMinutas }}</router-link></p>
      </section>
    </div>

    <footer class="story-method">
      {{ fill(C.metodo.pie, { corte: agg.corte || 's/f' }) }}
      <router-link :to="{ name: 'metodologia' }">{{ C.metodo.enlace }}</router-link>.
    </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';
import { content as C, fill } from '@/content';
import heroUrl from '@/assets/illustrations/hero_manchas_ods.svg?url';
import apoyoUrl from '@/assets/illustrations/apoyo.svg?url';
import ascensoUrl from '@/assets/illustrations/ascenso.svg?url';
import alcanceUrl from '@/assets/illustrations/alcance.svg?url';
import anilloUrl from '@/assets/illustrations/anillo_ods.svg?url';
import neutraUrl from '@/assets/illustrations/mancha_neutra.svg?url';

// Ilustraciones por sección (reuso, adenda v5.1 §4.3)
const art = {
  hero: heroUrl, apoyo: apoyoUrl, ascenso: ascensoUrl,
  alcance: alcanceUrl, anillo: anilloUrl, neutra: neutraUrl,
};

const router = useRouter();
const ready = ref(false);
const scene = ref(0);
const viajeScene = ref(0);
const animate = ref(true);
// Layout por objetivo en E3/E4 (escenas 2-4). El color (teñido) llega en el
// segundo beat de E3 (escena 3): ese es "el momento del color" (guion v7 E3).
const grouped = computed(() => scene.value >= 2 && scene.value <= 4);
const colored = computed(() => scene.value >= 3 && scene.value <= 4);
// Estado del panel derivado del índice de paso (máquina de estados, v7 §0.3).
const graphicState = computed(() => ['grid', 'estatus', 'orden', 'color', 'singulares', 'agua'][scene.value] || 'grid');
// Paradas del viaje (Acto II)
const paradas = computed(() => {
  const p = (C.viaje && C.viaje.paradas) || {};
  return [
    { key: 'madrid', label: p.madrid || 'Madrid', x: 15 },
    { key: 'asuncion', label: p.asuncion || 'Asunción', x: 38 },
    { key: 'foros', label: p.foros || 'Ginebra · Nueva York', x: 61 },
    { key: 'mexico', label: p.mexico || 'México', x: 84 },
  ];
});

const agg = ref({ kpis: {}, por_ods: [], corte: null });
const minAgg = ref({ kpis: {}, por_estatus: [], por_ods: [] });
const cat = ref({ ods: {}, metas: [] });
const nodes = ref([]);
const pos = reactive({});
const annotations = ref([]);
const agua = ref([]);
const vitrina = ref(null);
// Armonización estatal: sin fuente de dato todavía → null. La UI muestra "en
// documentación" y las 32 casillas vacías; nunca un "0 de 32" (afirmación sin
// fuente). Cuando exista el dato, se asigna el número y aparece "N de 32".
const armonizadas = ref(null);

const stageEl = ref(null);
let io = null;
let ro = null;

const iniciativas = ref([]);
const q = ref('');
const fOds = ref('');
const fMeta = ref('');

const nMinutas = computed(() => minAgg.value.kpis.minutas_totales || 0);
const nIniciativas = computed(() => agg.value.kpis.iniciativas_presentadas || 0);
const nLogradas = computed(() => agg.value.kpis.aprobadas || 0);
const est = computed(() => Object.fromEntries((minAgg.value.por_estatus || []).map((e) => [e.estatus, e.n])));
const odsDominante = computed(() => agg.value.kpis.ods_dominante || '16');
const nSinOds = computed(() => nodes.value.filter((n) => !n.ods).length);
// La historia nunca se dibuja con ceros del API (v4.1 §5): sin unidades, estado vacío.
const hasData = computed(() => nodes.value.length > 0);

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }

const S = 16;
function stageSize() {
  const el = stageEl.value;
  return { w: Math.max(200, el ? el.clientWidth : 560), h: Math.max(200, el ? el.clientHeight : 500) };
}
// Medición de etiqueta de grupo (v7 §0.2): ancho del texto renderizado, con el
// número + espacio delante, para decidir si cabe o se abrevia.
let _ctx = null;
function measureLabel(txt) {
  if (typeof document === 'undefined') return 0;
  if (!_ctx) { _ctx = document.createElement('canvas').getContext('2d'); }
  _ctx.font = '600 13px Inter, system-ui, sans-serif';
  return _ctx.measureText('00 ' + txt).width;
}
function gridLayout(list, x0, y0, cols) {
  const map = {};
  list.forEach((n, i) => { map[n.id] = { x: x0 + (i % cols) * S, y: y0 + Math.floor(i / cols) * S }; });
  return map;
}
function computePositions() {
  const { w, h } = stageSize();
  const out = {}; const anno = []; const sc = scene.value;
  if (sc === 0) {
    const cols = Math.max(8, Math.floor(w / S));
    const rows = Math.ceil(nodes.value.length / cols);
    Object.assign(out, gridLayout(nodes.value, Math.max(0, (w - cols * S) / 2), Math.max(0, (h - rows * S) / 2), cols));
  } else if (sc === 1) {
    const groups = [
      { key: 'publicada_dof', label: C.estatus.publicada_dof, short: 'DOF', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'publicada_dof') },
      { key: 'en_revisora', label: C.estatus.en_revisora, short: 'Senado', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'en_revisora') },
      { key: 'devuelta', label: C.estatus.devuelta, short: 'Devuelta', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'devuelta') },
      { key: 'ini', label: C.leyenda.iniciativa, short: 'Ejecutivo', nodes: nodes.value.filter((n) => n.type === 'ini') },
    ].filter((g) => g.nodes.length);
    const colW = w / groups.length;
    const perRow = Math.max(2, Math.floor((colW - 8) / S));
    groups.forEach((g, gi) => {
      const x0 = gi * colW + 4;
      Object.assign(out, gridLayout(g.nodes, x0, 40, perRow));
      // Anticolisión: si el nombre + 24px no cabe en la columna, se abrevia; el
      // completo va en title y la etiqueta se recorta al ancho de su columna.
      const fits = measureLabel(g.label) + 24 <= colW;
      anno.push({ key: g.key, x: x0, y: 14, n: g.nodes.length, text: fits ? g.label : g.short, full: g.label, w: Math.max(34, colW - 10), show: true });
    });
  } else if (sc >= 2 && sc <= 4) {
    const byOds = {};
    nodes.value.forEach((n) => { const k = n.ods || 'sin'; (byOds[k] = byOds[k] || []).push(n); });
    const keys = Object.keys(byOds).sort((a, b) => byOds[b].length - byOds[a].length);
    const rowH = Math.max(S + 2, Math.min(30, h / keys.length));
    const perRow = Math.max(6, Math.floor((w - 60) / S));
    keys.forEach((k, ri) => {
      const y0 = ri * rowH;
      byOds[k].forEach((n, i) => {
        // E4 (singulares): se atenúa lo demás y se iluminan agua y "sin casilla".
        out[n.id] = { x: 56 + (i % perRow) * S, y: y0 + Math.floor(i / perRow) * S, dim: sc === 4 && !isSingular(n), glow: sc === 4 && isSingular(n) };
      });
      anno.push({ key: 'ods' + k, x: 0, y: y0, w: 52, n: byOds[k].length, text: k === 'sin' ? 'sin ODS' : 'ODS ' + k, show: (sc === 2 || sc === 3) || (sc === 4 && (k === '6' || k === 'sin')) });
    });
  }
  Object.keys(pos).forEach((k) => delete pos[k]);
  Object.assign(pos, out);
  annotations.value = anno;
}
function isSingular(n) { return !n.ods || n.ods === '6'; }
function unitStyle(n) {
  const p = pos[n.id];
  if (!p) return { transform: 'translate(0,0)', opacity: 0 };
  const s = { transform: `translate(${p.x}px, ${p.y}px)` };
  // El color oficial del ODS solo se aplica en "el momento del color" (E3 beat 2).
  if (colored.value && n.ods) s['--ods'] = odsColor(n.ods);
  return s;
}
function setScene(i) { if (i === scene.value) return; scene.value = i; if (i <= 4) nextTick(computePositions); }
function setViaje(i) { if (i === viajeScene.value) return; viajeScene.value = i; }

function goExpediente(id) { router.push({ name: 'expediente', params: { id } }); }
function clearFilters() { q.value = ''; fOds.value = ''; fMeta.value = ''; loadIniciativas(); }
function loadIniciativas() {
  const params = {};
  if (q.value) params.q = q.value;
  if (fOds.value) params.ods = fOds.value;
  if (fMeta.value) params.meta = fMeta.value;
  api.getHuellaIniciativas(params).then((d) => (iniciativas.value = d || []));
}

onMounted(async () => {
  animate.value = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  cat.value = await api.getHuellaCatalogos();
  agg.value = await api.getHuellaEjecutivo();
  minAgg.value = await api.getMinutasResumen();
  vitrina.value = agg.value.normtrace_vitrina || null;

  const inis = (await api.getHuellaIniciativas()) || [];
  const mins = (await api.getMinutasLista()) || [];
  nodes.value = [
    ...mins.map((m) => ({ id: 'm' + m.id, type: 'min', ods: m.ods_principal || null, status: m.estatus, label: m.denominacion })),
    ...inis.map((i) => ({ id: 'i' + i.id, type: 'ini', ods: i.ods_principal || null, status: (i.seccion || '').startsWith('Aprobadas') ? 'lograda' : 'proceso', label: i.denominacion })),
  ];

  if (vitrina.value) {
    const nt = await api.getNormtraceExpediente(vitrina.value);
    agua.value = (nt && nt.registros) || [];
  }

  ready.value = true;
  loadIniciativas();
  await nextTick();
  computePositions();
  ro = new ResizeObserver(() => { if (scene.value <= 4) computePositions(); });
  if (stageEl.value) ro.observe(stageEl.value);
  // El estado cambia al cruzar el 50% del viewport (v7 §0.3): un paso, un estado.
  io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const ds = e.target.getAttribute('data-step');
      if (ds && ds[0] === 'v') setViaje(Number(ds.slice(1)));
      else setScene(Number(ds));
    });
  }, { rootMargin: '-50% 0px -50% 0px', threshold: 0 });
  document.querySelectorAll('.step').forEach((s) => io.observe(s));
});

onBeforeUnmount(() => { if (io) io.disconnect(); if (ro) ro.disconnect(); });
</script>
