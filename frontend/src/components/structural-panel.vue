<template>
  <div id="structural" class="structural-panel">
    <h4>{{ t('scanner.structural.title') }}</h4>

    <!-- Descargo fijo: la codificación es preliminar y asistida por modelo. -->
    <tipi-message type="warning" icon>
      {{ t('scanner.structural.disclaimer') }}
    </tipi-message>

    <!-- Estado de carga (el análisis profundo llega después del rápido). -->
    <tipi-loader
      v-if="loading"
      :title="t('scanner.structural.loading')"
    />

    <template v-else-if="units.length">
      <div class="structural-panel__bar u-no-print">
        <p class="u-color-secondary-dark u-text-tbody2">
          {{
            t('scanner.structural.summary', {
              analyzed: structural.units_analyzed,
              skipped: structural.units_skipped,
            })
          }}
        </p>
        <button class="c-button c-button--primary" @click.prevent="exportPdf">
          {{ t('scanner.structural.export') }}
        </button>
      </div>

      <table class="scanner-table structural-panel__table">
        <thead>
          <tr>
            <th>{{ t('scanner.structural.col.unit') }}</th>
            <th>{{ t('scanner.structural.col.actor') }}</th>
            <th>{{ t('scanner.structural.col.duty') }}</th>
            <th>{{ t('scanner.structural.col.procedure') }}</th>
            <th>{{ t('scanner.structural.col.coordination') }}</th>
            <th>{{ t('scanner.structural.col.gap') }}</th>
            <th>{{ t('scanner.structural.col.confidence') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in units" :key="u.unit_id">
            <td :data-label="t('scanner.structural.col.unit')">
              <strong>{{ unitLabel(u) }}</strong>
              <br />
              <small class="u-color-secondary">{{ u.unit_id }}</small>
              <br v-if="u.topics && u.topics.length" />
              <small class="u-color-secondary" v-if="u.topics && u.topics.length">{{
                u.topics.join(' · ')
              }}</small>
            </td>
            <td :data-label="t('scanner.structural.col.actor')">
              {{ u.analysis.actor_mentioned || '—' }}
            </td>
            <td :data-label="t('scanner.structural.col.duty')">
              {{ dutyOrPower(u.analysis) }}
            </td>
            <td :data-label="t('scanner.structural.col.procedure')">
              {{ u.analysis.procedure_created || '—' }}
            </td>
            <td :data-label="t('scanner.structural.col.coordination')">
              {{ u.analysis.coordination_mechanism || '—' }}
            </td>
            <td :data-label="t('scanner.structural.col.gap')">
              {{ gapLabels(u.analysis.gap_type) }}
            </td>
            <td :data-label="t('scanner.structural.col.confidence')">
              <span class="badge" :class="'badge--' + u.analysis.confidence_level">
                {{ confidenceLabel(u.analysis.confidence_level) }}
              </span>
              <br />
              <small class="u-color-secondary">{{
                reviewLabel(u.analysis.review_status)
              }}</small>
            </td>
          </tr>
        </tbody>
      </table>
    </template>

    <tipi-message v-else type="info" icon>
      {{ t('scanner.structural.empty') }}
    </tipi-message>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { TipiMessage, TipiLoader } from '@politicalwatch/tipi-uikit';

const props = defineProps({
  structural: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const { t, locale } = useI18n();

const units = computed(() => props.structural?.units || []);

// Etiquetas legibles de la tipología de brechas (methodology_note §3).
const GAP_LABELS = {
  es: {
    legal_silence: 'Silencio legal',
    competence_ambiguity: 'Ambigüedad de competencia',
    administrative_only_anchoring: 'Anclaje solo administrativo',
    procedural_gap: 'Brecha de procedimiento',
    coordination_gap: 'Brecha de coordinación',
    federal_implementation_gap: 'Brecha de implementación federal',
    rights_safeguard_gap: 'Brecha de salvaguarda de derechos',
    oversight_gap: 'Brecha de control',
    budget_capacity_gap: 'Brecha de presupuesto/capacidad',
    update_review_needed: 'Requiere actualización',
  },
  en: {
    legal_silence: 'Legal silence',
    competence_ambiguity: 'Competence ambiguity',
    administrative_only_anchoring: 'Administrative-only anchoring',
    procedural_gap: 'Procedural gap',
    coordination_gap: 'Coordination gap',
    federal_implementation_gap: 'Federal implementation gap',
    rights_safeguard_gap: 'Rights-safeguard gap',
    oversight_gap: 'Oversight gap',
    budget_capacity_gap: 'Budget/capacity gap',
    update_review_needed: 'Update-review needed',
  },
};

const CONFIDENCE_LABELS = {
  es: { low: 'Baja', medium: 'Media', high: 'Alta' },
  en: { low: 'Low', medium: 'Medium', high: 'High' },
};

const REVIEW_LABELS = {
  es: {
    needs_human_review: 'Requiere revisión de especialista',
    reviewed: 'Revisado',
    auto_accepted: 'Aceptado automáticamente',
  },
  en: {
    needs_human_review: 'Needs specialist review',
    reviewed: 'Reviewed',
    auto_accepted: 'Auto-accepted',
  },
};

function lang() {
  return locale.value === 'en' ? 'en' : 'es';
}

function unitLabel(u) {
  const type = u.unit_type || '';
  const number = u.number ? ` ${u.number}` : '';
  return `${type}${number}`.trim() || u.unit_id;
}

function dutyOrPower(a) {
  return [a.duty_created, a.power_granted].filter(Boolean).join(' / ') || '—';
}

function gapLabels(gaps) {
  if (!gaps || !gaps.length) return '—';
  const map = GAP_LABELS[lang()];
  return gaps.map((g) => map[g] || g).join(', ');
}

function confidenceLabel(c) {
  return CONFIDENCE_LABELS[lang()][c] || c;
}

function reviewLabel(r) {
  return REVIEW_LABELS[lang()][r] || r;
}

function exportPdf() {
  // La unidad de entrega política es el brief en PDF: usamos la impresión del
  // navegador (Guardar como PDF) con una hoja de estilos de impresión.
  window.print();
}
</script>

<style lang="scss">
.structural-panel {
  margin-top: 3rem;

  &__bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    margin: 1rem 0;
  }

  &__table {
    width: 100%;
    font-size: 0.9rem;
  }

  .badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #fff;

    &--low {
      background: #c0392b;
    }
    &--medium {
      background: #d68910;
    }
    &--high {
      background: #1e8449;
    }
  }
}

@media print {
  .u-no-print {
    display: none !important;
  }
}
</style>
