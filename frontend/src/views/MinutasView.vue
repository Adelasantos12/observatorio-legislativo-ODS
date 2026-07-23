<template>
  <div class="huella-page">
    <header>
      <div class="kicker">{{ T.kicker }}</div>
      <h1 style="margin:6px 0 4px">{{ T.titulo }}</h1>
      <p class="muted" v-if="agg && hasData">{{ fill(T.sub, { total: agg.kpis.minutas_totales, corte: agg.corte || 's/f' }) }}</p>
    </header>

    <!-- v6 §2.3: skeleton loaders, nunca spinner ni "Cargando…" a secas -->
    <div v-if="loading" aria-busy="true" aria-label="Cargando minutas">
      <section class="kpis" style="margin-bottom:26px">
        <div class="card kpi skeleton sk-kpi" v-for="i in 5" :key="'skk' + i"></div>
      </section>
      <div class="card-grid">
        <div class="rec-card skeleton sk-card" v-for="i in 6" :key="'skc' + i"></div>
      </div>
    </div>

    <!-- Sin datos: nunca la vista con "0 minutas" (v4.1 §5) -->
    <div v-else-if="!hasData" class="disclaimer" style="margin-top:14px;display:flex;gap:14px;align-items:flex-start">
      <img :src="neutra" alt="" width="40" height="40" style="flex:none;opacity:.7" />
      <div><b>{{ EV.titulo }}</b> {{ EV.cuerpo }}</div>
    </div>

    <template v-else-if="agg">
      <section class="kpis" style="margin-bottom:26px">
        <div class="card kpi"><div class="v" v-countup="agg.kpis.minutas_totales">{{ agg.kpis.minutas_totales }}</div><div class="l">{{ T.kpiTotal }}</div></div>
        <div class="card kpi"><div class="v" v-countup="agg.kpis.con_correspondencia_ods">{{ agg.kpis.con_correspondencia_ods }}</div><div class="l">{{ T.kpiConOds }}</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.pct_con_correspondencia_ods }}%</div><div class="l">{{ T.kpiPct }}</div></div>
        <div class="card kpi"><div class="v"><span v-countup="agg.kpis.atribucion_documentada">{{ agg.kpis.atribucion_documentada }}</span> <span class="muted" style="font-size:14px">de {{ agg.kpis.minutas_totales }}</span></div><div class="l">{{ T.kpiAtribucion }} · <router-link :to="{ name: 'metodologia' }">{{ T.notaMetodo }}</router-link></div></div>
        <div class="card kpi"><div class="v" v-countup="agg.kpis.sin_origen_documentado">{{ agg.kpis.sin_origen_documentado }}</div><div class="l">{{ T.kpiPorDocumentar }}</div></div>
      </section>

      <!-- Por estatus -->
      <section v-reveal class="card" style="margin-bottom:22px" v-if="agg.por_estatus && agg.por_estatus.length">
        <h3 style="margin-top:0">{{ T.estatusTitulo }}</h3>
        <div class="filters">
          <button v-for="e in agg.por_estatus" :key="e.estatus" class="badge"
                  :class="{ 'is-active': fEstatus === e.estatus }"
                  @click="setEstatus(e.estatus)">
            <span class="st-badge" :class="stClass(e.estatus)"><span class="ic"></span>{{ e.etiqueta }}</span> · {{ nf(e.n) }}
          </button>
          <button v-for="a in agg.por_anio" :key="a.anio" class="badge"
                  :class="{ 'is-active': fAnio === a.anio }"
                  @click="setAnio(a.anio)">Año {{ a.anio }} · {{ nf(a.n) }}</button>
        </div>
      </section>

      <div v-reveal class="o-grid" style="display:grid;grid-template-columns:1fr;gap:22px">
        <!-- Aportación por origen -->
        <section class="card">
          <h3 style="margin-top:0">{{ T.origenTitulo }}</h3>
          <p class="muted">{{ T.origenSub }}</p>
          <div class="bars">
            <div v-for="row in agg.por_origen" :key="row.origen" class="bar-row" @click="setOrigen(row)"
                 @mouseenter="showTip($event, tipOrigenText(row))" @mousemove="moveTip" @mouseleave="hideTip">
              <span class="bar-label" :title="row.origen">
                {{ row.origen }}
                <span class="badge" v-if="row.por_documentar" style="margin-left:6px">sin documentar</span>
              </span>
              <span class="bar-track">
                <span :class="row.por_documentar ? 'bar-s' : 'bar-p'" :style="{width: pctOrigen(row.n) + '%'}"></span>
              </span>
              <span class="bar-n">{{ nf(row.n) }}</span>
            </div>
          </div>
        </section>

        <!-- Por ODS -->
        <section class="card">
          <h3 style="margin-top:0">{{ T.odsTitulo }}</h3>
          <p class="muted">{{ T.odsSub }}</p>
          <div class="bars">
            <div v-for="row in agg.por_ods" :key="row.ods" class="bar-row is-ods" :style="{ '--ods': odsColor(row.ods) }"
                 @click="setOds(row.ods)"
                 @mouseenter="showTip($event, tipOdsText(row))" @mousemove="moveTip" @mouseleave="hideTip">
              <span class="bar-label" :title="odsName(row.ods)">
                <span class="ods-chip" :title="odsName(row.ods)" :style="{background: odsColor(row.ods)}">{{ row.ods }}</span>
                {{ odsName(row.ods) }}
              </span>
              <span class="bar-track">
                <span class="bar-p" :style="{width: pctOds(row.principal) + '%'}"></span>
                <span class="bar-s" :style="{width: pctOds(row.secundario) + '%'}"></span>
              </span>
              <span class="bar-n">{{ nf(row.principal) }}+{{ nf(row.secundario) }}</span>
            </div>
          </div>
          <p class="muted" v-if="!agg.por_ods.length">Aún sin correspondencia ODS codificada.</p>
        </section>
      </div>

      <!-- Tooltip del sistema (v6 §1.5): un solo nodo reutilizable -->
      <div v-if="tip.show" class="viz-tip" :style="{ left: tip.x + 'px', top: tip.y + 'px' }" aria-hidden="true">{{ tip.text }}</div>

      <!-- Lista: tarjetas por defecto, tabla como opción (v6 §2.2) -->
      <section v-reveal class="card" style="margin-top:22px">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
          <h3 style="margin:0">{{ T.titulo }}</h3>
          <div class="view-toggle" role="group" aria-label="Cambiar vista de la lista de minutas">
            <button type="button" :class="{ 'is-active': viewMode === 'cards' }" :aria-pressed="viewMode === 'cards'" @click="viewMode = 'cards'">Tarjetas</button>
            <button type="button" :class="{ 'is-active': viewMode === 'table' }" :aria-pressed="viewMode === 'table'" @click="viewMode = 'table'">Tabla</button>
          </div>
        </div>
        <div class="filters">
          <input v-model="q" @input="loadLista" :placeholder="T.filtroBuscar" />
          <select v-model="fOrigen" @change="loadLista">
            <option value="">{{ T.filtroTodosOrigenes }}</option>
            <option v-for="row in agg.por_origen" :key="row.origen" :value="row.por_documentar ? '' : row.origen" :disabled="row.por_documentar">
              {{ row.origen }}
            </option>
          </select>
          <input v-model="fMeta" @input="loadLista" :placeholder="T.filtroMeta" style="width:120px" />
          <button class="badge" @click="clearFilters">{{ EXP.limpiar }}</button>
        </div>

        <!-- Contador vivo + filtros activos removibles (v6 §2.4) -->
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:0 0 14px">
          <span class="result-count">{{ nf(lista.length) }} de {{ nf(agg.kpis.minutas_totales) }}</span>
          <span v-for="f in activeFilters" :key="f.key" class="chip-x">
            {{ f.label }}
            <button type="button" @click="clearFilter(f.key)" aria-label="Quitar filtro">×</button>
          </span>
        </div>

        <!-- Tarjetas -->
        <div v-if="viewMode === 'cards'" class="card-grid">
          <div v-for="m in lista" :key="m.id" class="rec-card" style="cursor:default">
            <div class="clave">{{ m.clave }}</div>
            <div class="tema" :title="m.denominacion">{{ m.denominacion }}</div>
            <div class="muted" v-if="m.tema">{{ m.tema }}</div>
            <div class="meta-row">
              <span v-if="m.ods_principal" class="ods-chip" :title="odsName(m.ods_principal)" :style="{background: odsColor(m.ods_principal)}">{{ m.ods_principal }}</span>
              <span v-for="s in m.ods_secundarios" :key="s" class="ods-chip" :title="odsName(s)" :style="{background: odsColor(s), opacity:.6}">{{ s }}</span>
              <span class="st-badge" :class="stClass(m.estatus)"><span class="ic"></span>{{ m.estatus_label || m.estatus }}</span>
            </div>
            <div class="muted">
              <span v-if="tieneOrigen(m)" :title="origenTexto(m)">{{ origenTexto(m) }}</span>
              <span v-else class="badge">{{ T.porDocumentar }}</span>
            </div>
          </div>
        </div>

        <!-- Tabla densa -->
        <table v-else>
          <thead><tr><th>{{ T.colClave }}</th><th>{{ T.colDenominacion }}</th><th>{{ T.colEstatus }}</th><th>{{ T.colOrigen }}</th><th>{{ T.colOds }}</th><th>{{ T.colConfianza }}</th></tr></thead>
          <tbody>
            <tr v-for="m in lista" :key="m.id">
              <td>{{ m.clave }}</td>
              <td>{{ m.denominacion }}<br><span class="muted">{{ m.tema }}</span></td>
              <td><span class="st-badge" :class="stClass(m.estatus)"><span class="ic"></span>{{ m.estatus_label || m.estatus }}</span></td>
              <td>
                <span v-if="tieneOrigen(m)">{{ origenTexto(m) }}</span>
                <span v-else class="badge">{{ T.porDocumentar }}</span>
              </td>
              <td>
                <span v-if="m.ods_principal" class="ods-chip" :title="odsName(m.ods_principal)" :style="{background: odsColor(m.ods_principal)}">{{ m.ods_principal }}</span>
                <span v-for="s in m.ods_secundarios" :key="s" class="ods-chip" :title="odsName(s)" :style="{background: odsColor(s), opacity:.6, marginLeft:'3px'}">{{ s }}</span>
                <div class="muted" v-if="m.metas && m.metas.length">{{ m.metas.join(' · ') }}</div>
              </td>
              <td><span class="badge" :class="'badge--' + (m.confianza||'pendiente')">{{ m.confianza || 'sin codificar' }}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="muted" v-if="!lista.length">{{ T.sinResultados }}</p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import api from '@/api';
import { content, fill } from '@/content';
import neutra from '@/assets/illustrations/mancha_neutra.svg?url';

const T = content.minutas;
const EXP = content.explorador;
const EV = content.estadoVacio;
const loading = ref(true);
const agg = ref(null);
const hasData = computed(() => !!(agg.value && agg.value.kpis && agg.value.kpis.minutas_totales > 0));
const cat = ref({ ods: {}, metas: [] });
const lista = ref([]);
const q = ref('');
const fOrigen = ref('');
const fOds = ref('');
const fMeta = ref('');
const fEstatus = ref('');
const fAnio = ref('');
const viewMode = ref('cards'); // v6 §2.2: tarjetas por defecto, tabla como opción

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }
function stClass(e) { return { publicada_dof: 'st-dof', en_revisora: 'st-rev', devuelta: 'st-dev' }[e] || 'st-dev'; }

function maxOrigen() { return Math.max(1, ...agg.value.por_origen.map((r) => r.n)); }
function maxOds() { return Math.max(1, ...agg.value.por_ods.map((r) => r.principal + r.secundario)); }
function pctOrigen(n) { return (n / maxOrigen()) * 100; }
function pctOds(n) { return (n / maxOds()) * 100; }

function setOrigen(row) { if (row.por_documentar) return; fOrigen.value = row.origen; loadLista(); }
function setOds(o) { fOds.value = String(o); loadLista(); }
function setEstatus(e) { fEstatus.value = fEstatus.value === e ? '' : e; loadLista(); }
function setAnio(a) { fAnio.value = fAnio.value === a ? '' : a; loadLista(); }
function clearFilters() { q.value = ''; fOrigen.value = ''; fOds.value = ''; fMeta.value = ''; fEstatus.value = ''; fAnio.value = ''; loadLista(); }

// --- Filtros activos como chips removibles (v6 §2.4) ---
const activeFilters = computed(() => {
  const arr = [];
  if (q.value) arr.push({ key: 'q', label: '“' + q.value + '”' });
  if (fOrigen.value) arr.push({ key: 'fOrigen', label: fOrigen.value });
  if (fOds.value) arr.push({ key: 'fOds', label: 'ODS ' + fOds.value + ' · ' + odsName(fOds.value) });
  if (fEstatus.value) {
    const e = (agg.value && agg.value.por_estatus || []).find((x) => x.estatus === fEstatus.value);
    arr.push({ key: 'fEstatus', label: e ? e.etiqueta : fEstatus.value });
  }
  if (fAnio.value) arr.push({ key: 'fAnio', label: 'Año ' + fAnio.value });
  if (fMeta.value) arr.push({ key: 'fMeta', label: 'Meta ' + fMeta.value });
  return arr;
});
function clearFilter(key) {
  if (key === 'q') q.value = '';
  else if (key === 'fOrigen') fOrigen.value = '';
  else if (key === 'fOds') fOds.value = '';
  else if (key === 'fEstatus') fEstatus.value = '';
  else if (key === 'fAnio') fAnio.value = '';
  else if (key === 'fMeta') fMeta.value = '';
  loadLista();
}

// --- Formato de cifras y tooltip del sistema (v6 §1.3/§1.5) ---
const nfmt = new Intl.NumberFormat('es-MX');
function nf(n) { return nfmt.format(n); }
function tipOrigenText(row) { return row.origen + ': ' + nf(row.n); }
function tipOdsText(row) {
  return odsName(row.ods) + ': ' + nf(row.principal) + ' principal · ' + nf(row.secundario) + ' secundaria';
}
const tip = reactive({ show: false, x: 0, y: 0, text: '' });
function placeTip(e) {
  const x = Math.min(e.clientX + 14, window.innerWidth - 270);
  const y = Math.min(e.clientY + 14, window.innerHeight - 60);
  tip.x = Math.max(8, x);
  tip.y = Math.max(8, y);
}
function showTip(e, text) { tip.text = text; placeTip(e); tip.show = true; }
function moveTip(e) { if (tip.show) placeTip(e); }
function hideTip() { tip.show = false; }

// Texto de origen/grupos compartido entre tarjeta y tabla.
function tieneOrigen(m) { return !!((m.grupos_parlamentarios && m.grupos_parlamentarios.length) || m.origen); }
function origenTexto(m) {
  if (m.grupos_parlamentarios && m.grupos_parlamentarios.length) return m.grupos_parlamentarios.join(', ');
  if (m.origen) return m.origen;
  return '';
}

function loadLista() {
  const params = {};
  if (q.value) params.q = q.value;
  if (fOrigen.value) params.origen = fOrigen.value;
  if (fOds.value) params.ods = fOds.value;
  if (fMeta.value) params.meta = fMeta.value;
  if (fEstatus.value) params.estatus = fEstatus.value;
  if (fAnio.value) params.anio = fAnio.value;
  api.getMinutasLista(params).then((d) => (lista.value = d || []));
}

onMounted(async () => {
  try {
    cat.value = await api.getHuellaCatalogos();
    agg.value = await api.getMinutasResumen();
    loadLista();
  } finally {
    loading.value = false;
  }
});
</script>
