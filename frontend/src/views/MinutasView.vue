<template>
  <div class="huella-page">
    <header>
      <div class="kicker">Minutas · Cámara de Diputados como cámara de origen</div>
      <h1 style="margin:6px 0 4px">Aportación por origen a la Agenda 2030</h1>
      <p class="muted" v-if="agg">
        Corte: {{ agg.corte || 's/f' }} · asuntos aprobados por la Cámara de origen,
        agrupados por quién los impulsó.
      </p>
    </header>

    <div class="disclaimer">
      <b>Esto no es un ranking ni una competencia entre bancadas.</b> Es una
      lectura descriptiva de la <i>aportación por origen</i>: qué grupo
      parlamentario o el Ejecutivo Federal impulsó cada asunto y su
      correspondencia preliminar con la Agenda 2030 (protocolo NormTrace). Las
      minutas cuyo origen aún no está documentado se muestran como
      <i>«por documentar»</i>; nunca se les atribuye una bancada de forma
      inventada. La correspondencia con ODS es preliminar y revisable.
    </div>

    <div v-if="loading" class="muted">Cargando…</div>

    <template v-else-if="agg">
      <section class="kpis" style="margin-bottom:26px">
        <div class="card kpi"><div class="v">{{ agg.kpis.minutas_totales }}</div><div class="l">minutas registradas</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.con_correspondencia_ods }}</div><div class="l">con correspondencia ODS</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.pct_con_correspondencia_ods }}%</div><div class="l">del total con correspondencia</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.atribucion_documentada }} <span class="muted" style="font-size:14px">de {{ agg.kpis.minutas_totales }}</span></div><div class="l">atribución de origen documentada</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.sin_origen_documentado }}</div><div class="l">por documentar</div></div>
      </section>

      <!-- Por estatus -->
      <section class="card" style="margin-bottom:22px" v-if="agg.por_estatus && agg.por_estatus.length">
        <h3 style="margin-top:0">Estatus en el proceso legislativo</h3>
        <div class="filters">
          <button v-for="e in agg.por_estatus" :key="e.estatus" class="badge"
                  :style="fEstatus === e.estatus ? 'background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent)' : ''"
                  @click="setEstatus(e.estatus)">
            <span class="st-badge" :class="stClass(e.estatus)"><span class="ic"></span>{{ e.etiqueta }}</span> · {{ e.n }}
          </button>
          <button v-for="a in agg.por_anio" :key="a.anio" class="badge"
                  :style="fAnio === a.anio ? 'background:color-mix(in srgb,var(--accent) 12%,transparent);color:var(--accent)' : ''"
                  @click="setAnio(a.anio)">Año {{ a.anio }} · {{ a.n }}</button>
        </div>
      </section>

      <div class="o-grid" style="display:grid;grid-template-columns:1fr;gap:22px">
        <!-- Aportación por origen -->
        <section class="card">
          <h3 style="margin-top:0">Aportación por origen</h3>
          <p class="muted">
            Orden alfabético, no por volumen: la altura de cada barra describe cuántos
            asuntos impulsó cada origen, sin ordenarlos como una tabla de posiciones.
            Clic para filtrar.
          </p>
          <div v-for="row in agg.por_origen" :key="row.origen" class="bar-row" @click="setOrigen(row)">
            <span class="bar-label">
              {{ row.origen }}
              <span class="badge" v-if="row.por_documentar" style="margin-left:6px">sin documentar</span>
            </span>
            <span class="bar-track">
              <span :class="row.por_documentar ? 'bar-s' : 'bar-p'" :style="{width: pctOrigen(row.n) + '%'}"></span>
            </span>
            <span class="bar-n">{{ row.n }}</span>
          </div>
        </section>

        <!-- Por ODS -->
        <section class="card">
          <h3 style="margin-top:0">Correspondencia por ODS</h3>
          <p class="muted">Guinda = materia principal · guinda claro = secundaria. Clic para filtrar.</p>
          <div v-for="row in agg.por_ods" :key="row.ods" class="bar-row" @click="setOds(row.ods)">
            <span class="bar-label">
              <span class="ods-chip" :style="{background: odsColor(row.ods)}">{{ row.ods }}</span>
              {{ odsName(row.ods) }}
            </span>
            <span class="bar-track">
              <span class="bar-p" :style="{width: pctOds(row.principal) + '%'}"></span>
              <span class="bar-s" :style="{width: pctOds(row.secundario) + '%'}"></span>
            </span>
            <span class="bar-n">{{ row.principal }}+{{ row.secundario }}</span>
          </div>
          <p class="muted" v-if="!agg.por_ods.length">Aún sin correspondencia ODS codificada.</p>
        </section>
      </div>

      <!-- Tabla -->
      <section class="card" style="margin-top:22px">
        <h3 style="margin-top:0">Minutas</h3>
        <div class="filters">
          <input v-model="q" @input="loadLista" placeholder="Buscar por denominación…" />
          <select v-model="fOrigen" @change="loadLista">
            <option value="">Todos los orígenes</option>
            <option v-for="row in agg.por_origen" :key="row.origen" :value="row.por_documentar ? '' : row.origen" :disabled="row.por_documentar">
              {{ row.origen }}
            </option>
          </select>
          <input v-model="fMeta" @input="loadLista" placeholder="Meta (ej. 16.6)" style="width:120px" />
          <button class="badge" @click="clearFilters">Limpiar</button>
        </div>
        <table>
          <thead><tr><th>Clave</th><th>Denominación</th><th>Estatus</th><th>Origen</th><th>ODS / metas</th><th>Confianza</th></tr></thead>
          <tbody>
            <tr v-for="m in lista" :key="m.id">
              <td>{{ m.clave }}</td>
              <td>{{ m.denominacion }}<br><span class="muted">{{ m.tema }}</span></td>
              <td><span class="st-badge" :class="stClass(m.estatus)"><span class="ic"></span>{{ m.estatus_label || m.estatus }}</span></td>
              <td>
                <span v-if="m.grupos_parlamentarios && m.grupos_parlamentarios.length">{{ m.grupos_parlamentarios.join(', ') }}</span>
                <span v-else-if="m.origen">{{ m.origen }}</span>
                <span v-else class="badge">por documentar</span>
              </td>
              <td>
                <span v-if="m.ods_principal" class="ods-chip" :style="{background: odsColor(m.ods_principal)}">{{ m.ods_principal }}</span>
                <span v-for="s in m.ods_secundarios" :key="s" class="ods-chip" :style="{background: odsColor(s), opacity:.6, marginLeft:'3px'}">{{ s }}</span>
                <div class="muted" v-if="m.metas && m.metas.length">{{ m.metas.join(' · ') }}</div>
              </td>
              <td><span class="badge" :class="'badge--' + (m.confianza||'pendiente')">{{ m.confianza || 'sin codificar' }}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="muted" v-if="!lista.length">Sin resultados con los filtros actuales.</p>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const loading = ref(true);
const agg = ref(null);
const cat = ref({ ods: {}, metas: [] });
const lista = ref([]);
const q = ref('');
const fOrigen = ref('');
const fOds = ref('');
const fMeta = ref('');
const fEstatus = ref('');
const fAnio = ref('');

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
