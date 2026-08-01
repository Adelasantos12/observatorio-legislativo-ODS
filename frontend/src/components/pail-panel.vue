<template>
  <div id="pail" class="pail-panel">
    <h4>{{ t('scanner.pail.title') }}</h4>

    <tipi-message type="warning" icon>
      {{ t('scanner.pail.disclaimer') }}
    </tipi-message>

    <tipi-loader v-if="loading" :title="t('scanner.pail.loading')" />

    <template v-else-if="dictamen">
      <!-- 1. Cabecera: dictamen global + cobertura. -->
      <p class="pail-panel__head">
        <span class="badge badge--big" :class="'badge--' + globalClass">{{ dictamen.dictamen_global }}</span>
        <span class="badge" :class="'badge--' + coverageClass">
          {{ t('scanner.pail.coverage') }}: {{ Math.round((dictamen.cobertura_evaluada || 0) * 100) }}%
        </span>
      </p>

      <!-- Aviso de fallo del LLM (clave/modelo/cuota): visible para diagnóstico. -->
      <tipi-message v-if="dictamen.llm_error" type="error" icon>
        {{ dictamen.llm_error }}
      </tipi-message>

      <!-- 1.b. Puerta de insumo: si el texto no es una iniciativa, banner único y nada de tablas. -->
      <tipi-message v-if="notaInsumo" type="error" icon>
        {{ notaInsumo }}
      </tipi-message>

      <template v-else>
        <!-- 2. Red flags (lo que hay que arreglar), priorizadas. -->
        <h5>{{ t('scanner.pail.redFlagsTitle') }}</h5>
        <p v-if="!redFlags.length" class="u-color-secondary">{{ t('scanner.pail.noRedFlags') }}</p>
        <table v-else class="scanner-table pail-panel__table">
          <thead>
            <tr>
              <th>{{ t('scanner.pail.col.severity') }}</th>
              <th>{{ t('scanner.pail.col.check') }}</th>
              <th>{{ t('scanner.pail.col.finding') }}</th>
              <th>{{ t('scanner.pail.col.evidence') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in redFlags" :key="f.id">
              <td :data-label="t('scanner.pail.col.severity')">
                <span class="badge" :class="'badge--' + sevClass(f.severidad)">{{ f.severidad }}</span>
              </td>
              <td :data-label="t('scanner.pail.col.check')"><strong>{{ f.verificacion }}</strong><br /><small class="u-color-secondary">{{ f.id }}</small></td>
              <td :data-label="t('scanner.pail.col.finding')">{{ f.hallazgo }}</td>
              <td :data-label="t('scanner.pail.col.evidence')">
                <template v-if="f.evidencia_muestra">«{{ f.evidencia_muestra.cita }}»<br /><small class="u-color-secondary">{{ f.evidencia_muestra.ubicacion }}</small></template>
                <span v-else class="u-color-secondary">—</span>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 2.b. Áreas de oportunidad (incluye armonización y cableado). -->
        <h5>{{ t('scanner.pail.opportunitiesTitle') }}</h5>
        <p v-if="!oportunidades.length" class="u-color-secondary">{{ t('scanner.pail.noOpportunities') }}</p>
        <table v-else class="scanner-table pail-panel__table">
          <thead>
            <tr>
              <th>{{ t('scanner.pail.col.check') }}</th>
              <th>{{ t('scanner.pail.col.detail') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="f in oportunidades" :key="f.id">
              <td :data-label="t('scanner.pail.col.check')"><strong>{{ f.verificacion }}</strong><br /><small class="u-color-secondary">{{ f.id }}</small></td>
              <td :data-label="t('scanner.pail.col.detail')">
                <span>{{ f.hallazgo }}</span>
                <template v-if="f.armonizacion && f.armonizacion.length">
                  <br /><small><strong>{{ fill(t('scanner.pail.harmonize'), { n: f.armonizacion.length }) }}:</strong>
                  {{ f.armonizacion.slice(0, 8).map((a) => a.norma).join('; ') }}{{ f.armonizacion.length > 8 ? '…' : '' }}</small>
                </template>
                <template v-if="f.cableado">
                  <br /><small class="u-color-secondary">{{ t('scanner.pail.wiring') }}: {{ f.cableado.a_articulo }} a artículo · {{ f.cableado.en_bloque }} en bloque — {{ f.cableado.lectura }}</small>
                </template>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 3. Sin evaluar: UNA sola línea, con la razón principal. -->
        <p v-if="sinEvaluar.total" class="pail-panel__pending u-color-secondary">
          {{ fill(t('scanner.pail.pending'), { n: sinEvaluar.total, reason: razonPrincipal }) }}
        </p>

        <!-- 4. Detalle completo en acordeón colapsado. -->
        <details class="pail-panel__audit u-no-print">
          <summary>{{ t('scanner.pail.auditDetail') }} ({{ dictamen.verificaciones.length }})</summary>
          <table class="scanner-table pail-panel__table">
            <thead>
              <tr>
                <th>{{ t('scanner.pail.col.id') }}</th>
                <th>{{ t('scanner.pail.col.check') }}</th>
                <th>{{ t('scanner.pail.col.layer') }}</th>
                <th>{{ t('scanner.pail.col.result') }}</th>
                <th>{{ t('scanner.pail.col.severity') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="v in dictamen.verificaciones" :key="v.id">
                <td :data-label="t('scanner.pail.col.id')"><strong>{{ v.id }}</strong></td>
                <td :data-label="t('scanner.pail.col.check')">{{ v.nombre }}</td>
                <td :data-label="t('scanner.pail.col.layer')">{{ capaLabel(v.capa) }}</td>
                <td :data-label="t('scanner.pail.col.result')">
                  <span class="badge" :class="'badge--' + resultClass(v.resultado)">{{ v.resultado }}</span>
                </td>
                <td :data-label="t('scanner.pail.col.severity')">{{ v.severidad }}</td>
              </tr>
            </tbody>
          </table>
        </details>

        <button class="c-button c-button--primary u-no-print" @click.prevent="exportPdf">
          {{ t('scanner.pail.export') }}
        </button>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { TipiMessage, TipiLoader } from '@politicalwatch/tipi-uikit';

const props = defineProps({
  dictamen: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const { t, locale } = useI18n();

const CAPAS = {
  es: { nucleo_triaje: 'Triaje', mtl: 'Técnica legislativa', csn: 'Sistematización', racionalidad: 'Racionalidad' },
  en: { nucleo_triaje: 'Triage', mtl: 'Legislative technique', csn: 'Systematisation', racionalidad: 'Rationality' },
};

function lang() {
  return locale.value === 'en' ? 'en' : 'es';
}
function capaLabel(c) {
  return (CAPAS[lang()] || CAPAS.es)[c] || c;
}

const resumen = computed(() => props.dictamen?.resumen || {});
const notaInsumo = computed(() => resumen.value.nota_insumo || null);
const redFlags = computed(() => resumen.value.red_flags || []);
const oportunidades = computed(() => resumen.value.areas_oportunidad || []);
const sinEvaluar = computed(() => resumen.value.sin_evaluar || { total: 0, razones: [] });
const razonPrincipal = computed(() => {
  const r = sinEvaluar.value.razones || [];
  return r.length ? r[0][0] : '';
});

// Reemplaza {tokens} en las cadenas i18n (no todas las plantillas usan interpolación nativa).
function fill(str, vars) {
  return Object.entries(vars).reduce(
    (s, [k, v]) => s.replace(new RegExp(`\\{${k}\\}`, 'g'), v),
    str,
  );
}

function sevClass(s) {
  if (s === 'BLOQUEANTE') return 'low';
  if (s === 'MAYOR') return 'medium';
  return 'neutral';
}
function resultClass(r) {
  if (r === 'CUMPLE') return 'high';
  if (r === 'INCUMPLE') return 'low';
  return 'medium';
}
const globalClass = computed(() => {
  const g = props.dictamen?.dictamen_global || '';
  if (g === 'VIABLE') return 'high';
  if (g === 'NO_VIABLE_EN_SUS_TERMINOS') return 'low';
  return 'medium';
});
const coverageClass = computed(() => {
  const c = props.dictamen?.cobertura_evaluada || 0;
  if (c >= 0.7) return 'high';
  if (c >= 0.5) return 'medium';
  return 'low';
});

function exportPdf() {
  window.print();
}
</script>

<style lang="scss">
.pail-panel {
  margin-top: 3rem;

  &__head {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin: 1rem 0;
  }
  &__table {
    width: 100%;
    font-size: 0.88rem;
    margin: 0.5rem 0 1.5rem;
  }
  &__pending {
    font-size: 0.9rem;
    margin: 0.5rem 0 1.5rem;
    padding-left: 0.75rem;
    border-left: 3px solid #d68910;
  }
  &__audit {
    margin: 1rem 0;
    summary {
      cursor: pointer;
      font-weight: 600;
      padding: 0.5rem 0;
    }
  }
  h5 {
    margin: 1.5rem 0 0.25rem;
  }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;

    &--big { font-size: 0.9rem; padding: 0.25rem 0.7rem; }
    &--low { background: #c0392b; }
    &--medium { background: #d68910; }
    &--high { background: #1e8449; }
    &--neutral { background: #6b7c8c; }
  }
}

@media print {
  .u-no-print { display: none !important; }
  .pail-panel__audit { display: block !important; }
}
</style>
