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
        <!-- Gráfico fijo -->
        <div class="scrolly-graphic">
          <div style="width:100%">
            <div v-show="scene <= 3">
              <div ref="stageEl" class="unit-stage">
                <div v-for="n in nodes" :key="n.id" class="unit"
                  :class="[n.type === 'min' ? 'is-min' : 'is-ini', { 'has-ods': grouped && n.ods, dim: pos[n.id] && pos[n.id].dim, glow: pos[n.id] && pos[n.id].glow }]"
                  :style="unitStyle(n)" :title="n.label"></div>
                <div v-for="a in annotations" :key="a.key" class="unit-anno"
                     :style="{ left: a.x + 'px', top: a.y + 'px', opacity: a.show ? 1 : 0 }">
                  <b>{{ a.n }}</b> {{ a.text }}
                </div>
              </div>
              <div class="unit-legend">
                <span class="k"><span class="sw" style="background:var(--ink-2);opacity:.8"></span> {{ C.leyenda.minuta }} ({{ nMinutas }})</span>
                <span class="k"><span class="sw" style="background:var(--ink-3)"></span> {{ C.leyenda.iniciativa }} ({{ nIniciativas }})</span>
                <span class="k" v-show="grouped"><span class="sw" style="background:linear-gradient(90deg,#e5243b,#26bde2,#4c9f38)"></span> agrupadas por ODS</span>
              </div>
            </div>

            <!-- Escena 5: el caso del agua -->
            <div v-show="scene === 4" class="card">
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

        <!-- Pasos de prosa -->
        <div class="scrolly-steps">
          <section class="step" data-step="0"><div class="step-card">
            <h2>{{ C.escenas.agenda.titulo }}</h2>
            <p>{{ fill(C.escenas.agenda.p1, { minutas: nMinutas, iniciativas: nIniciativas }) }}</p>
            <p class="muted">{{ C.escenas.agenda.p2 }}</p>
          </div></section>

          <section class="step" data-step="1"><div class="step-card">
            <img class="step-art" :src="art.ascenso" alt="" aria-hidden="true" />
            <h2>{{ C.escenas.estatus.titulo }}</h2>
            <p>{{ fill(C.escenas.estatus.p1, { dof: est.publicada_dof || 0, revisora: est.en_revisora || 0, devueltas: est.devuelta || 0 }) }}</p>
            <p>
              <span class="st-badge st-dof"><span class="ic"></span>{{ C.estatus.publicada_dof }}</span> ·
              <span class="st-badge st-rev"><span class="ic"></span>{{ C.estatus.en_revisora }}</span> ·
              <span class="st-badge st-dev"><span class="ic"></span>{{ C.estatus.devuelta }}</span>
            </p>
          </div></section>

          <section class="step" data-step="2"><div class="step-card">
            <img class="step-art" :src="art.alcance" alt="" aria-hidden="true" />
            <h2>{{ C.escenas.hallazgo.titulo }}</h2>
            <p>{{ fill(C.escenas.hallazgo.p1, { odsDominanteNombre: odsName(odsDominante) }) }}</p>
            <p class="muted">{{ C.escenas.hallazgo.p2 }}</p>
          </div></section>

          <section class="step" data-step="3"><div class="step-card">
            <h2>{{ C.escenas.singulares.titulo }}</h2>
            <p>{{ fill(C.escenas.singulares.p1, { sinOds: nSinOds }) }}</p>
            <p class="muted">{{ C.escenas.singulares.p2 }}</p>
          </div></section>

          <section class="step" data-step="4"><div class="step-card">
            <img class="step-art" :src="art.alcance" alt="" aria-hidden="true" />
            <h2>{{ C.escenas.agua.titulo }}</h2>
            <p>{{ C.escenas.agua.p1 }}</p>
            <p class="muted">{{ C.escenas.agua.p2 }}</p>
          </div></section>
        </div>
      </div>

      <!-- Por qué importa (escena 6) -->
      <section v-reveal class="porque" style="margin:0 clamp(16px,5vw,56px)">
        <div class="section-head">
          <img class="section-art" :src="art.apoyo" alt="" aria-hidden="true" />
          <div>
            <h2 class="porque-h">{{ C.porque_importa.titulo }}</h2>
            <p class="porque-intro">{{ C.porque_importa.intro }}</p>
          </div>
        </div>
        <div class="porque-grid">
          <article v-for="(it, i) in C.porque_importa.items" :key="i" class="porque-item">
            <h3>{{ it.titulo }}</h3>
            <p>{{ it.cuerpo }}</p>
          </article>
        </div>
      </section>

      <!-- Quién más lo hace (prueba social, adenda v6 §3b) -->
      <section v-if="C.quien_mas_lo_hace" v-reveal class="porque" style="margin:0 clamp(16px,5vw,56px)">
        <div class="section-head">
          <img class="section-art" :src="art.alcance" alt="" aria-hidden="true" style="width:96px" />
          <div>
            <h2 class="porque-h">{{ C.quien_mas_lo_hace.titulo }}<span v-if="C.quien_mas_lo_hace._estado" class="draft-flag" title="Pendiente de visto bueno de la autora">Borrador</span></h2>
            <p class="porque-intro">{{ C.quien_mas_lo_hace.intro }}</p>
          </div>
        </div>
        <div class="porque-grid">
          <article v-for="(it, i) in C.quien_mas_lo_hace.items" :key="i" class="social-item">
            <h3>{{ it.lugar }}</h3>
            <p>{{ it.cuerpo }}</p>
          </article>
        </div>
        <p class="social-remate">{{ C.quien_mas_lo_hace.remate }}</p>
      </section>

      <!-- Cierre de la historia: el emblema (anillo de los 17 ODS) -->
      <section v-reveal style="text-align:center;margin:64px clamp(16px,5vw,56px) 0">
        <img :src="art.anillo" alt="Anillo de los 17 Objetivos de Desarrollo Sostenible" style="width:96px;height:96px" />
      </section>

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
const animate = ref(true);
// Las escenas 2 y 3 agrupan las unidades por objetivo: ahí adoptan su color ODS.
const grouped = computed(() => scene.value === 2 || scene.value === 3);

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
      { key: 'publicada_dof', label: C.estatus.publicada_dof, nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'publicada_dof') },
      { key: 'en_revisora', label: C.estatus.en_revisora, nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'en_revisora') },
      { key: 'devuelta', label: C.estatus.devuelta, nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'devuelta') },
      { key: 'ini', label: C.leyenda.iniciativa, nodes: nodes.value.filter((n) => n.type === 'ini') },
    ].filter((g) => g.nodes.length);
    const colW = w / groups.length;
    const perRow = Math.max(2, Math.floor((colW - 8) / S));
    groups.forEach((g, gi) => {
      const x0 = gi * colW + 4;
      Object.assign(out, gridLayout(g.nodes, x0, 40, perRow));
      anno.push({ key: g.key, x: x0, y: 16, n: g.nodes.length, text: g.label, show: true });
    });
  } else if (sc === 2 || sc === 3) {
    const byOds = {};
    nodes.value.forEach((n) => { const k = n.ods || 'sin'; (byOds[k] = byOds[k] || []).push(n); });
    const keys = Object.keys(byOds).sort((a, b) => byOds[b].length - byOds[a].length);
    const rowH = Math.max(S + 2, Math.min(30, h / keys.length));
    const perRow = Math.max(6, Math.floor((w - 60) / S));
    keys.forEach((k, ri) => {
      const y0 = ri * rowH;
      byOds[k].forEach((n, i) => {
        out[n.id] = { x: 56 + (i % perRow) * S, y: y0 + Math.floor(i / perRow) * S, dim: sc === 3 && !isSingular(n), glow: sc === 3 && isSingular(n) };
      });
      anno.push({ key: 'ods' + k, x: 0, y: y0, n: byOds[k].length, text: k === 'sin' ? 'sin ODS' : 'ODS ' + k, show: sc === 2 || (sc === 3 && (k === '6' || k === 'sin')) });
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
  // Al agruparse por objetivo, la unidad lleva el color oficial de su ODS.
  if (grouped.value && n.ods) s['--ods'] = odsColor(n.ods);
  return s;
}
function setScene(i) { if (i === scene.value) return; scene.value = i; if (i <= 3) nextTick(computePositions); }

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
  ro = new ResizeObserver(() => { if (scene.value <= 3) computePositions(); });
  if (stageEl.value) ro.observe(stageEl.value);
  io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) setScene(Number(e.target.getAttribute('data-step'))); });
  }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
  document.querySelectorAll('.step').forEach((s) => io.observe(s));
});

onBeforeUnmount(() => { if (io) io.disconnect(); if (ro) ro.disconnect(); });
</script>
