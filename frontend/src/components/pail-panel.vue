<template>
  <div id="pail" class="pail-panel">
    <h4>{{ t('scanner.pail.title') }}</h4>

    <tipi-message type="warning" icon>
      {{ t('scanner.pail.disclaimer') }}
    </tipi-message>

    <tipi-loader v-if="loading" :title="t('scanner.pail.loading')" />

    <template v-else-if="dictamen">
      <div class="pail-panel__resumen">
        <p class="u-text-tbody2">
          <strong>{{ t('scanner.pail.global') }}:</strong>
          <span class="badge" :class="'badge--' + globalClass">{{ dictamen.dictamen_global }}</span>
        </p>
        <ul class="pail-panel__capas">
          <li v-for="(estado, capa) in dictamen.dictamen_por_capa" :key="capa">
            <span class="u-color-secondary">{{ capaLabel(capa) }}:</span> {{ estado }}
          </li>
        </ul>
        <p class="u-color-secondary u-text-tbody3" v-if="dictamen.contexto">
          {{ t('scanner.pail.instrumento') }}: {{ dictamen.contexto.tipo_instrumento || '—' }} ·
          {{ t('scanner.pail.articulos') }}: {{ dictamen.articulos_detectados }}
        </p>
      </div>

      <button class="c-button c-button--primary u-no-print" @click.prevent="exportPdf">
        {{ t('scanner.pail.export') }}
      </button>

      <table class="scanner-table pail-panel__table">
        <thead>
          <tr>
            <th>{{ t('scanner.pail.col.id') }}</th>
            <th>{{ t('scanner.pail.col.check') }}</th>
            <th>{{ t('scanner.pail.col.layer') }}</th>
            <th>{{ t('scanner.pail.col.result') }}</th>
            <th>{{ t('scanner.pail.col.severity') }}</th>
            <th>{{ t('scanner.pail.col.evidence') }}</th>
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
            <td :data-label="t('scanner.pail.col.evidence')">
              <span v-if="!v.evidencia || !v.evidencia.length" class="u-color-secondary">—</span>
              <ul v-else class="pail-panel__ev">
                <li v-for="(e, i) in v.evidencia" :key="i">
                  «{{ e.cita }}» <small class="u-color-secondary">({{ e.ubicacion }})</small>
                </li>
              </ul>
              <small class="u-color-secondary" v-if="v.explicacion"><br />{{ v.explicacion }}</small>
            </td>
          </tr>
        </tbody>
      </table>
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
  es: {
    nucleo_triaje: 'Triaje',
    mtl: 'Técnica legislativa',
    csn: 'Sistematización',
    racionalidad: 'Racionalidad',
  },
  en: {
    nucleo_triaje: 'Triage',
    mtl: 'Legislative technique',
    csn: 'Systematisation',
    racionalidad: 'Rationality',
  },
};

function lang() {
  return locale.value === 'en' ? 'en' : 'es';
}

function capaLabel(c) {
  return (CAPAS[lang()] || CAPAS.es)[c] || c;
}

// Verde = cumple; ámbar = parcial/pendiente/no evaluable; rojo = incumple.
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

function exportPdf() {
  window.print();
}
</script>

<style lang="scss">
.pail-panel {
  margin-top: 3rem;

  &__resumen {
    margin: 1rem 0;
  }
  &__capas {
    list-style: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 1.25rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
  }
  &__table {
    width: 100%;
    font-size: 0.88rem;
    margin-top: 1rem;
  }
  &__ev {
    margin: 0;
    padding-left: 1rem;
  }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: #fff;

    &--low { background: #c0392b; }
    &--medium { background: #d68910; }
    &--high { background: #1e8449; }
  }
}

@media print {
  .u-no-print { display: none !important; }
}
</style>
