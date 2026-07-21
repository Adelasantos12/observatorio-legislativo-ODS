<template>
  <div class="huella-page" :class="{ 'no-anim': !animate }">
    <!-- Apertura (escena 1) -->
    <header class="story-hero">
      <div class="kicker">Huella 2030 · Poder Ejecutivo y Cámara de Diputados</div>
      <h1 class="lede" v-if="ready">
        Desde octubre de 2024, la Cámara de Diputados ha aprobado
        <span class="num">{{ nMinutas }}</span> minutas; el Ejecutivo ha logrado
        <span class="num">{{ nLogradas }}</span> de sus
        <span class="num">{{ nIniciativas }}</span> iniciativas.
      </h1>
      <h1 class="lede" v-else>Cargando la huella legislativa…</h1>
      <p class="sub">
        Cada cuadrito es una minuta o una iniciativa. Desplázate: la misma
        evidencia se reordena para contar qué avanza, hacia dónde y qué casi
        nadie ve. La correspondencia con la Agenda 2030 es preliminar y
        revisable (protocolo NormTrace).
      </p>
    </header>

    <div class="story" v-if="ready">
      <div class="scrolly">
        <!-- Gráfico fijo -->
        <div class="scrolly-graphic">
          <div style="width:100%">
            <!-- Escenas 1-4: unit chart -->
            <div v-show="scene <= 3">
              <div ref="stageEl" class="unit-stage">
                <div
                  v-for="n in nodes"
                  :key="n.id"
                  class="unit"
                  :class="[n.type === 'min' ? 'is-min' : 'is-ini', { dim: pos[n.id] && pos[n.id].dim, glow: pos[n.id] && pos[n.id].glow }]"
                  :style="unitStyle(n)"
                  :title="n.label"
                ></div>
                <div v-for="a in annotations" :key="a.key" class="unit-anno"
                     :style="{ left: a.x + 'px', top: a.y + 'px', opacity: a.show ? 1 : 0 }">
                  <b>{{ a.n }}</b> {{ a.text }}
                </div>
              </div>
              <div class="unit-legend">
                <span class="k"><span class="sw" style="background:var(--accent)"></span> minuta ({{ nMinutas }})</span>
                <span class="k"><span class="sw" style="background:var(--accent-2)"></span> iniciativa del Ejecutivo ({{ nIniciativas }})</span>
              </div>
            </div>

            <!-- Escena 5: el caso del agua (mini ficha NormTrace) -->
            <div v-show="scene === 4" class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
                <h3 style="margin:0">Ley General de Aguas · ODS 6</h3>
                <span class="nt-badge nt-badge--validado">● Validado por la autora</span>
              </div>
              <p class="muted">Análisis NormTrace nivel 3: 34 disposiciones mapeadas contra las metas del ODS 6 y el derecho humano al agua.</p>
              <table class="nt-table" v-if="agua.length">
                <thead><tr><th>Estándar</th><th>Disposición</th><th>Rol</th><th>Cobertura</th></tr></thead>
                <tbody>
                  <tr v-for="(r,i) in agua.slice(0,8)" :key="i">
                    <td>{{ r.estandar }}</td><td>{{ r.disposicion }}</td>
                    <td><span :class="{muted: r.rol_correspondencia!=='sustantivo'}">{{ r.rol_correspondencia==='sustantivo'?'sustantivo':'contextual' }}</span></td>
                    <td>{{ r.cobertura }}</td>
                  </tr>
                </tbody>
              </table>
              <p style="margin-top:12px" v-if="vitrina">
                <router-link :to="{ name: 'expediente', params: { id: vitrina } }">Ver la ficha NormTrace completa →</router-link>
              </p>
            </div>
          </div>
        </div>

        <!-- Pasos de prosa -->
        <div class="scrolly-steps">
          <section class="step" data-step="0"><div class="step-card">
            <h2>La agenda, en cuadritos</h2>
            <p>Aquí está toda la producción legislativa relevante del periodo: <span class="num">{{ nMinutas }}</span> minutas aprobadas por la Cámara de origen y las <span class="num">{{ nIniciativas }}</span> iniciativas del Ejecutivo Federal.</p>
            <p class="muted">Un cuadrito, un asunto. Los guinda son minutas; los dorados, iniciativas del Ejecutivo.</p>
          </div></section>

          <section class="step" data-step="1"><div class="step-card">
            <h2>¿Cuántas se vuelven ley?</h2>
            <p>De las minutas, <span class="num">{{ est.publicada_dof || 0 }}</span> ya se publicaron en el DOF; <span class="num">{{ est.en_revisora || 0 }}</span> esperan en el Senado y <span class="num">{{ est.devuelta || 0 }}</span> fueron devueltas.</p>
            <p>
              <span class="st-badge st-dof"><span class="ic"></span>Publicada en DOF</span> ·
              <span class="st-badge st-rev"><span class="ic"></span>En revisora</span> ·
              <span class="st-badge st-dev"><span class="ic"></span>Devuelta</span>
            </p>
          </div></section>

          <section class="step" data-step="2"><div class="step-card">
            <h2>El hallazgo</h2>
            <p>Al reagrupar por Objetivo de Desarrollo Sostenible, casi la mitad de la agenda apunta a uno solo: <b>ODS {{ odsDominante }} — {{ odsName(odsDominante) }}</b>.</p>
            <p class="muted">Después vienen los otros picos: género, trabajo, infraestructura y hacienda. Cada barra son cuadritos, no una estimación.</p>
          </div></section>

          <section class="step" data-step="3"><div class="step-card">
            <h2>Lo que casi nadie ve</h2>
            <p>Entre el volumen hay piezas singulares: la única del <b>ODS 6</b> (la Ley General de Aguas), las <span class="num">{{ nSinOds }}</span> sin correspondencia con la Agenda 2030, y detalles como la meta de menstruación digna.</p>
            <p class="muted">El detalle inesperado es la recompensa del scroll, no el ruido de fondo.</p>
          </div></section>

          <section class="step" data-step="4"><div class="step-card">
            <h2>El caso del agua</h2>
            <p>La Ley General de Aguas es la primera ficha con análisis NormTrace profundo: sus disposiciones mapeadas, una por una, contra las metas 6.1 a 6.b y el derecho humano al agua.</p>
            <p class="muted">Es la demostración del nivel 3 dentro de la historia. La tabla de al lado es un extracto validado por la autora.</p>
          </div></section>

          <section class="step" data-step="5"><div class="step-card">
            <h2>Explora tú</h2>
            <p>Hasta aquí la historia; ahora el dato es tuyo. Filtra las iniciativas por ODS, meta o texto, o salta al detalle de cada expediente y a las <router-link :to="{ name: 'minutas' }">minutas de la Cámara</router-link>.</p>
          </div></section>
        </div>
      </div>

      <!-- Explorador (escena 6) -->
      <section class="card" style="margin:0 clamp(16px,5vw,56px) 24px">
        <h3 style="margin-top:0">Iniciativas del Ejecutivo — explorador</h3>
        <div class="disclaimer">
          Correspondencia ODS/metas preliminar por materia, asistida por modelo (NormTrace).
          No es evaluación de cumplimiento. Cada registro conserva su nivel de confianza.
        </div>
        <div class="filters">
          <input v-model="q" @input="loadIniciativas" placeholder="Buscar por denominación…" />
          <select v-model="fOds" @change="loadIniciativas">
            <option value="">Todos los ODS</option>
            <option v-for="row in agg.por_ods" :key="row.ods" :value="row.ods">ODS {{ row.ods }} — {{ odsName(row.ods) }}</option>
          </select>
          <input v-model="fMeta" @input="loadIniciativas" placeholder="Meta (ej. 16.6)" style="width:120px" />
          <button class="badge" @click="clearFilters">Limpiar</button>
        </div>
        <table>
          <thead><tr><th>#</th><th>Denominación</th><th>ODS / metas</th><th>Estatus</th><th>Confianza</th></tr></thead>
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
              <td><span class="badge" :class="'badge--' + (i.confianza||'pendiente')">{{ i.confianza || 'sin codificar' }}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="muted" v-if="!iniciativas.length">Sin resultados con los filtros actuales.</p>
      </section>
    </div>

    <footer class="story-method" v-if="ready">
      Corte {{ agg.corte || 's/f' }}. La correspondencia con ODS y metas es preliminar, por
      materia, asistida por modelo (protocolo NormTrace); no es dictamen jurídico ni
      evaluación de cumplimiento. Las minutas sin origen documentado aparecen como
      «por documentar»; jamás se inventa una atribución. Cada cifra proviene del dato
      vivo del API. Iniciativas con análisis NormTrace: {{ agg.kpis.iniciativas_con_normtrace }} de {{ nIniciativas }}.
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const router = useRouter();
const ready = ref(false);
const scene = ref(0);
const animate = ref(true);

const agg = ref({ kpis: {}, por_ods: [], corte: null });
const minAgg = ref({ kpis: {}, por_estatus: [], por_ods: [] });
const cat = ref({ ods: {}, metas: [] });
const nodes = ref([]);
const pos = reactive({});
const annotations = ref([]);
const agua = ref([]);
const vitrina = ref(null);

const stageEl = ref(null);
let io = null;
let ro = null;

// Explorador
const iniciativas = ref([]);
const q = ref('');
const fOds = ref('');
const fMeta = ref('');

// --- KPIs vivos ---
const nMinutas = computed(() => minAgg.value.kpis.minutas_totales || 0);
const nIniciativas = computed(() => agg.value.kpis.iniciativas_presentadas || 0);
const nLogradas = computed(() => agg.value.kpis.aprobadas || 0);
const est = computed(() => Object.fromEntries((minAgg.value.por_estatus || []).map((e) => [e.estatus, e.n])));
const odsDominante = computed(() => agg.value.kpis.ods_dominante || '16');
const nSinOds = computed(() => nodes.value.filter((n) => !n.ods).length);

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }

// --- Layout del unit chart ---
const S = 16; // paso (13px + 3px)
function stageSize() {
  const el = stageEl.value;
  const w = el ? el.clientWidth : 560;
  const h = el ? el.clientHeight : 500;
  return { w: Math.max(200, w), h: Math.max(200, h) };
}

function gridLayout(list, x0, y0, w, cols) {
  const map = {};
  list.forEach((n, i) => {
    map[n.id] = { x: x0 + (i % cols) * S, y: y0 + Math.floor(i / cols) * S };
  });
  return map;
}

function computePositions() {
  const { w, h } = stageSize();
  const out = {};
  const anno = [];
  const sc = scene.value;

  if (sc === 0) {
    // Retícula única centrada.
    const cols = Math.max(8, Math.floor(w / S));
    const total = nodes.value.length;
    const rows = Math.ceil(total / cols);
    const x0 = Math.max(0, (w - cols * S) / 2);
    const y0 = Math.max(0, (h - rows * S) / 2);
    Object.assign(out, gridLayout(nodes.value, x0, y0, w, cols));
  } else if (sc === 1) {
    // Columnas por estatus (minutas) + logradas/proceso (iniciativas).
    const groups = [
      { key: 'publicada_dof', label: 'Publicadas DOF', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'publicada_dof') },
      { key: 'en_revisora', label: 'En el Senado', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'en_revisora') },
      { key: 'devuelta', label: 'Devueltas', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'devuelta') },
      { key: 'ini', label: 'Iniciativas', nodes: nodes.value.filter((n) => n.type === 'ini') },
    ].filter((g) => g.nodes.length);
    const colW = w / groups.length;
    const perRow = Math.max(2, Math.floor((colW - 8) / S));
    groups.forEach((g, gi) => {
      const x0 = gi * colW + 4;
      Object.assign(out, gridLayout(g.nodes, x0, 40, colW, perRow));
      anno.push({ key: g.key, x: x0, y: 16, n: g.nodes.length, text: g.label, show: true });
    });
  } else if (sc === 2 || sc === 3) {
    // Filas (barras) por ODS, ordenadas por volumen; ODS 16 arriba.
    const byOds = {};
    nodes.value.forEach((n) => {
      const k = n.ods || 'sin';
      (byOds[k] = byOds[k] || []).push(n);
    });
    const keys = Object.keys(byOds).sort((a, b) => byOds[b].length - byOds[a].length);
    const rowH = Math.max(S + 2, Math.min(30, h / keys.length));
    const perRow = Math.max(6, Math.floor((w - 60) / S));
    keys.forEach((k, ri) => {
      const y0 = ri * rowH;
      byOds[k].forEach((n, i) => {
        const isHighlight = sc === 3 ? isSingular(n) : true;
        out[n.id] = {
          x: 56 + (i % perRow) * S,
          y: y0 + Math.floor(i / perRow) * S,
          dim: sc === 3 && !isHighlight,
          glow: sc === 3 && isSingular(n),
        };
      });
      anno.push({ key: 'ods' + k, x: 0, y: y0, n: byOds[k].length, text: k === 'sin' ? 'sin ODS' : 'ODS ' + k, show: sc === 2 || (sc === 3 && (k === '6' || k === 'sin')) });
    });
  }

  Object.keys(pos).forEach((k) => delete pos[k]);
  Object.assign(pos, out);
  annotations.value = anno;
}

function isSingular(n) {
  if (!n.ods) return true; // sin correspondencia
  if (n.ods === '6') return true; // el caso del agua
  return false;
}

function unitStyle(n) {
  const p = pos[n.id];
  if (!p) return { transform: 'translate(0,0)', opacity: 0 };
  return { transform: `translate(${p.x}px, ${p.y}px)` };
}

function setScene(i) {
  if (i === scene.value) return;
  scene.value = i;
  if (scene.value <= 3) nextTick(computePositions);
}

// --- Explorador ---
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
  const iniNodes = inis.map((i) => ({
    id: 'i' + i.id, type: 'ini', ods: i.ods_principal || null,
    status: (i.seccion || '').startsWith('Aprobadas') ? 'lograda' : 'proceso',
    label: i.denominacion,
  }));
  const minNodes = mins.map((m) => ({
    id: 'm' + m.id, type: 'min', ods: m.ods_principal || null,
    status: m.estatus, label: m.denominacion,
  }));
  nodes.value = [...minNodes, ...iniNodes];

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
    entries.forEach((e) => {
      if (e.isIntersecting) setScene(Number(e.target.getAttribute('data-step')));
    });
  }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
  document.querySelectorAll('.step').forEach((s) => io.observe(s));
});

onBeforeUnmount(() => { if (io) io.disconnect(); if (ro) ro.disconnect(); });
</script>
