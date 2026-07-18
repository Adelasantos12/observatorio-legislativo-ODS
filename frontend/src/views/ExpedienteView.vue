<template>
  <div class="huella-page">
    <p><router-link :to="{ name: 'huella' }">← Huella 2030</router-link></p>

    <div v-if="loading" class="muted">Cargando expediente…</div>
    <div v-else-if="!ini" class="disclaimer">No se encontró el expediente.</div>

    <template v-else>
      <header>
        <div class="kicker">Expediente · Iniciativa del Ejecutivo Federal</div>
        <h1 class="serif" style="margin:6px 0">{{ ini.denominacion }}</h1>
        <p class="muted">{{ ini.tema }}</p>
      </header>

      <div class="o-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px">
        <div class="card"><div class="muted">Presentación</div><div class="serif" style="font-size:20px">{{ ini.fecha_presentacion || '—' }}</div></div>
        <div class="card"><div class="muted">Publicación DOF</div><div class="serif" style="font-size:20px">{{ ini.fecha_dof || '—' }}</div></div>
        <div class="card"><div class="muted">Estatus</div><div>{{ ini.estatus || '—' }}</div></div>
        <div class="card"><div class="muted">Confianza de la codificación</div>
          <span class="badge" :class="'badge--' + (ini.confianza||'pendiente')">{{ ini.confianza || 'sin codificar' }}</span>
        </div>
      </div>

      <section class="card" style="margin-top:18px">
        <h3 style="margin-top:0">Objetivos de Desarrollo Sostenible</h3>
        <div v-if="ini.ods_principal" style="margin:8px 0">
          <span class="ods-chip" :style="{background: odsColor(ini.ods_principal)}">{{ ini.ods_principal }}</span>
          <b>ODS {{ ini.ods_principal }}</b> — {{ odsName(ini.ods_principal) }} <span class="muted">(principal)</span>
        </div>
        <div v-for="s in ini.ods_secundarios" :key="s" style="margin:6px 0">
          <span class="ods-chip" :style="{background: odsColor(s), opacity:.7}">{{ s }}</span>
          ODS {{ s }} — {{ odsName(s) }} <span class="muted">(secundario)</span>
        </div>
        <p class="muted" v-if="!ini.ods_principal && !(ini.ods_secundarios||[]).length">Sin correspondencia ODS codificada.</p>
      </section>

      <section class="card" style="margin-top:18px">
        <h3 style="margin-top:0">Metas relacionadas</h3>
        <div v-for="m in ini.metas" :key="m" style="margin:6px 0">
          <span class="ods-chip" :style="{background: odsColor(m.split('.')[0])}">{{ m.split('.')[0] }}</span>
          <b>{{ m }}</b> {{ metaCorto(m) }}
          <span class="badge" style="margin-left:6px" v-if="!metaOficial(m)">denominación abreviada</span>
        </div>
        <p class="muted" v-if="!(ini.metas||[]).length">Sin metas codificadas.</p>
      </section>

      <!-- Análisis NormTrace (nivel 3): solo si existe corrida -->
      <section class="card" style="margin-top:18px" v-if="nt">
        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px">
          <h3 style="margin:0">Análisis NormTrace</h3>
          <span class="nt-badge" :class="ntValidado ? 'nt-badge--validado' : 'nt-badge--preliminar'">
            {{ ntValidado ? '● Validado por la autora' : '◐ Corrida automática preliminar' }}
          </span>
        </div>
        <p class="muted">Fuente del texto: {{ nt.fuente_texto }} · marco {{ (nt.marco||'').toUpperCase() }} · {{ nt.registros.length }} registros.</p>

        <div style="overflow-x:auto">
        <table class="nt-table">
          <thead><tr>
            <th>Estándar</th><th>Disposición</th><th>Rol</th><th>Cobertura</th>
            <th>Actor</th><th>Proc.</th><th>Coord.</th><th>Exig.</th><th>Salvag.</th><th>Feder.</th><th>Brecha</th>
          </tr></thead>
          <tbody>
            <tr v-for="(r,i) in nt.registros" :key="i">
              <td>{{ r.estandar }}</td>
              <td>{{ r.disposicion }}</td>
              <td><span :class="{muted: r.rol_correspondencia !== 'sustantivo'}">{{ rolCorto(r.rol_correspondencia) }}</span></td>
              <td>{{ r.cobertura }}</td>
              <td v-for="f in FITS" :key="f"><span class="nt-fit"><span class="nt-dot" :class="'nt-dot--'+r[f]"></span>{{ fitCorto(r[f]) }}</span></td>
              <td class="muted">{{ r.tipo_brecha || '—' }}</td>
            </tr>
          </tbody>
        </table>
        </div>

        <div v-if="anyNota" style="margin-top:10px">
          <p class="muted" v-for="(r,i) in nt.registros.filter(x=>x.nota)" :key="'nt'+i">
            <b>{{ r.estandar }} · {{ r.disposicion }}:</b> {{ r.nota }}
          </p>
        </div>

        <p style="margin-top:12px" v-if="nt.brief">
          <a href="#" @click.prevent="toggleBrief">{{ showBrief ? 'ocultar' : 'ver' }} el análisis completo (brief)</a>
        </p>
        <div class="nt-brief" v-if="showBrief" v-html="briefHtml"></div>

        <div class="disclaimer">{{ nt.descargo }}</div>
      </section>

      <div class="disclaimer">
        Registra correspondencia preliminar entre la materia de la iniciativa y los
        estándares de la Agenda 2030 (protocolo NormTrace). No es dictamen jurídico ni
        evaluación de cumplimiento; requiere revisión de especialista.
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api';

const route = useRoute();
const loading = ref(true);
const ini = ref(null);
const cat = ref({ ods: {}, metas: [] });
const metaMap = ref({});

// --- Análisis NormTrace ---
const nt = ref(null);
const showBrief = ref(false);
const briefMd = ref('');
const FITS = ['actor_fit', 'procedimiento_fit', 'coordinacion_fit', 'enforcement_fit', 'salvaguarda_derechos_fit', 'federalismo_fit'];

const ntValidado = computed(() => nt.value && nt.value.nivel_revision === 'validado_autora');
const anyNota = computed(() => nt.value && nt.value.registros.some((r) => r.nota));
const briefHtml = computed(() => renderMd(briefMd.value));

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }
function metaCorto(code) { return metaMap.value[code]?.nombre_corto_es || ''; }
function metaOficial(code) { return metaMap.value[code]?.nombre_oficial_es || null; }

function rolCorto(r) { return r === 'sustantivo' ? 'sustantivo' : 'contextual'; }
function fitCorto(f) { return ({ fuerte: 'fuerte', medio: 'medio', debil: 'débil', no_aplica: 'n/a' })[f] || f; }

async function toggleBrief() {
  showBrief.value = !showBrief.value;
  if (showBrief.value && !briefMd.value && nt.value?.brief) {
    briefMd.value = (await api.getNormtraceBrief(nt.value.brief)) || '';
  }
}

// Renderizador markdown mínimo (encabezados, tablas, negritas, párrafos).
function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
function inline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`(.+?)`/g, '<code>$1</code>'); }
function renderMd(md) {
  if (!md) return '';
  const lines = md.split('\n');
  const out = [];
  let tbl = [];
  const flushTbl = () => {
    if (!tbl.length) return;
    const rows = tbl.filter((r) => !/^\s*\|?\s*-{2,}/.test(r));
    const cells = (r) => r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
    out.push('<table>' + rows.map((r, i) => '<tr>' + cells(r).map((c) => (i === 0 ? `<th>${inline(c)}</th>` : `<td>${inline(c)}</td>`)).join('') + '</tr>').join('') + '</table>');
    tbl = [];
  };
  for (const ln of lines) {
    if (ln.trim().startsWith('|')) { tbl.push(ln); continue; }
    flushTbl();
    if (/^#{1,6}\s/.test(ln)) { const l = ln.match(/^#+/)[0].length; out.push(`<h${l}>${inline(ln.replace(/^#+\s/, ''))}</h${l}>`); }
    else if (ln.trim() === '') { /* skip */ }
    else out.push(`<p>${inline(ln)}</p>`);
  }
  flushTbl();
  return out.join('\n');
}

onMounted(async () => {
  try {
    cat.value = await api.getHuellaCatalogos();
    (cat.value.metas || []).forEach((m) => (metaMap.value[m.codigo] = m));
    ini.value = await api.getHuellaIniciativa(route.params.id);
    nt.value = await api.getNormtraceExpediente(route.params.id);
  } catch (e) {
    ini.value = null;
  } finally {
    loading.value = false;
  }
});
</script>
