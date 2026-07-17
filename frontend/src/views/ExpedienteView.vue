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

      <div class="disclaimer">
        Registra correspondencia preliminar entre la materia de la iniciativa y los
        estándares de la Agenda 2030 (protocolo NormTrace). No es dictamen jurídico ni
        evaluación de cumplimiento; requiere revisión de especialista.
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api';

const route = useRoute();
const loading = ref(true);
const ini = ref(null);
const cat = ref({ ods: {}, metas: [] });
const metaMap = ref({});

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }
function metaCorto(code) { return metaMap.value[code]?.nombre_corto_es || ''; }
function metaOficial(code) { return metaMap.value[code]?.nombre_oficial_es || null; }

onMounted(async () => {
  try {
    cat.value = await api.getHuellaCatalogos();
    (cat.value.metas || []).forEach((m) => (metaMap.value[m.codigo] = m));
    ini.value = await api.getHuellaIniciativa(route.params.id);
  } catch (e) {
    ini.value = null;
  } finally {
    loading.value = false;
  }
});
</script>
