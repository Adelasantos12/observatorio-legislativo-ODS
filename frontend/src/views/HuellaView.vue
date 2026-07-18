<template>
  <div class="huella-page">
    <header>
      <div class="kicker">Huella 2030 · Poder Ejecutivo Federal</div>
      <h1 style="margin:6px 0 4px">Iniciativas del Ejecutivo × Agenda 2030</h1>
      <p class="muted" v-if="agg">
        Corte: {{ agg.corte || 's/f' }} · correspondencia ODS y metas preliminar por materia.
      </p>
    </header>

    <div class="disclaimer">
      La correspondencia con ODS y metas es preliminar, por materia, asistida por
      modelo (protocolo NormTrace). No es evaluación de cumplimiento ni calificación
      de actores. Cada registro conserva su nivel de confianza; las iniciativas sin
      codificar aparecen como pendientes.
    </div>

    <div v-if="loading" class="muted">Cargando…</div>

    <template v-else-if="agg">
      <!-- KPIs -->
      <section class="kpis" style="margin-bottom:26px">
        <div class="card kpi"><div class="v">{{ agg.kpis.iniciativas_presentadas }}</div><div class="l">iniciativas presentadas por el Ejecutivo</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.aprobadas }}</div><div class="l">aprobadas y/o publicadas en DOF</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.pct_con_correspondencia_ods }}%</div><div class="l">de las aprobadas con correspondencia ODS</div></div>
        <div class="card kpi"><div class="v">{{ agg.kpis.leyes_nuevas }}</div><div class="l">leyes nuevas expedidas</div></div>
        <div class="card kpi"><div class="v">ODS {{ agg.kpis.ods_dominante }}</div><div class="l">objetivo dominante</div></div>
        <div class="card kpi" v-if="agg.kpis.iniciativas_con_normtrace != null" style="cursor:pointer" @click="verVitrina">
          <div class="v">{{ agg.kpis.iniciativas_con_normtrace }}</div>
          <div class="l">con análisis NormTrace <span class="muted">(de {{ agg.kpis.iniciativas_presentadas }})</span></div>
        </div>
      </section>

      <div class="card" v-if="agg.normtrace_vitrina" style="border-left:4px solid var(--accent-2);margin-bottom:22px">
        <b>Ficha vitrina · Análisis NormTrace validado.</b>
        La <a href="#" @click.prevent="verVitrina">Ley General de Aguas frente al ODS 6</a>
        cuenta con el análisis profundo (nivel 3) codificado y validado por la autora:
        34 disposiciones mapeadas contra las metas del ODS 6 y el derecho humano al agua.
      </div>

      <div class="o-grid" style="display:grid;grid-template-columns:1fr;gap:22px">
        <!-- Por ODS -->
        <section class="card">
          <h3 style="margin-top:0">Correspondencia por ODS</h3>
          <p class="muted">Clic en un ODS para filtrar la tabla. Guinda = materia principal · guinda claro = secundaria.</p>
          <div v-for="row in agg.por_ods" :key="row.ods" class="bar-row" @click="setOds(row.ods)">
            <span class="bar-label">
              <span class="ods-chip" :style="{background: odsColor(row.ods)}">{{ row.ods }}</span>
              {{ odsName(row.ods) }}
            </span>
            <span class="bar-track">
              <span class="bar-p" :style="{width: pct(row.principal) + '%'}"></span>
              <span class="bar-s" :style="{width: pct(row.secundario) + '%'}"></span>
            </span>
            <span class="bar-n">{{ row.principal }}+{{ row.secundario }}</span>
          </div>
        </section>

        <!-- Metas -->
        <section class="card">
          <h3 style="margin-top:0">Metas más frecuentes</h3>
          <p class="muted">{{ agg.por_meta.length }} metas distintas. Clic para filtrar.</p>
          <div v-for="row in (showAllMetas ? agg.por_meta : agg.por_meta.slice(0,10))" :key="row.meta" class="bar-row" @click="setMeta(row.meta)">
            <span class="bar-label">
              <span class="ods-chip" :style="{background: odsColor(row.meta.split('.')[0])}">{{ row.meta.split('.')[0] }}</span>
              <b>{{ row.meta }}</b> {{ metaCorto(row.meta) }}
            </span>
            <span class="bar-track"><span class="bar-p" :style="{width: pctMeta(row.n) + '%'}"></span></span>
            <span class="bar-n">{{ row.n }}</span>
          </div>
          <a href="#" @click.prevent="showAllMetas=!showAllMetas">
            {{ showAllMetas ? 'ver solo las 10 principales' : 'ver las ' + agg.por_meta.length }}
          </a>
        </section>

        <!-- Por trimestre -->
        <section class="card">
          <h3 style="margin-top:0">Presentación por trimestre</h3>
          <div class="col-chart">
            <div v-for="t in agg.por_trimestre" :key="t.periodo" style="flex:1;text-align:center">
              <div class="col" :style="{height: pctTri(t.n) + '%'}"></div>
              <div class="muted" style="margin-top:6px">{{ t.periodo }}<br>{{ t.n }}</div>
            </div>
          </div>
        </section>
      </div>

      <!-- Tabla -->
      <section class="card" style="margin-top:22px">
        <h3 style="margin-top:0">Iniciativas</h3>
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
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const router = useRouter();
const loading = ref(true);
const agg = ref(null);
const cat = ref({ ods: {}, metas: [] });
const iniciativas = ref([]);
const q = ref('');
const fOds = ref('');
const fMeta = ref('');
const showAllMetas = ref(false);

const metaMap = ref({});

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }
function metaCorto(code) { return metaMap.value[code]?.nombre_corto_es || ''; }

function maxOds() { return Math.max(1, ...agg.value.por_ods.map((r) => r.principal + r.secundario)); }
function maxMeta() { return Math.max(1, ...agg.value.por_meta.map((r) => r.n)); }
function maxTri() { return Math.max(1, ...agg.value.por_trimestre.map((t) => t.n)); }
function pct(n) { return (n / maxOds()) * 100; }
function pctMeta(n) { return (n / maxMeta()) * 100; }
function pctTri(n) { return (n / maxTri()) * 100; }

function setOds(o) { fOds.value = String(o); loadIniciativas(); }
function setMeta(m) { fMeta.value = m; loadIniciativas(); }
function clearFilters() { q.value = ''; fOds.value = ''; fMeta.value = ''; loadIniciativas(); }
function goExpediente(id) { router.push({ name: 'expediente', params: { id } }); }
function verVitrina() { if (agg.value?.normtrace_vitrina) goExpediente(agg.value.normtrace_vitrina); }

function loadIniciativas() {
  const params = {};
  if (q.value) params.q = q.value;
  if (fOds.value) params.ods = fOds.value;
  if (fMeta.value) params.meta = fMeta.value;
  api.getHuellaIniciativas(params).then((d) => (iniciativas.value = d || []));
}

onMounted(async () => {
  try {
    cat.value = await api.getHuellaCatalogos();
    (cat.value.metas || []).forEach((m) => (metaMap.value[m.codigo] = m));
    agg.value = await api.getHuellaEjecutivo();
    loadIniciativas();
  } finally {
    loading.value = false;
  }
});
</script>
