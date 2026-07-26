<template>
  <section class="ntm" :class="{ 'ntm--compact': compact }" :aria-label="regionLabel">
    <template v-if="!compact">
      <p class="ntm-resumen">{{ resumenTexto }}</p>

      <div class="ntm-leg">
        <div class="ntm-leg-row">
          <b>{{ M.leyendaAjusteLabel }}</b>
          <span class="ntm-g g-full" aria-hidden="true"></span>{{ M.ajusteFuerte }}
          <span class="ntm-g g-half" aria-hidden="true"></span>{{ M.ajusteMedio }}
          <span class="ntm-g g-out" aria-hidden="true"></span>{{ M.ajusteDebil }}
          <span class="ntm-g g-na" aria-hidden="true"></span>{{ M.ajusteNoAplica }}
        </div>
        <div class="ntm-leg-row">
          <b>{{ M.leyendaCoberturaLabel }}</b>
          <span class="ntm-g g-full" aria-hidden="true"></span>{{ M.coberturaCompleta }}
          <span class="ntm-g g-half" aria-hidden="true"></span>{{ M.coberturaParcial }}
          <span class="ntm-g g-out" aria-hidden="true"></span>{{ M.coberturaContextual }}
        </div>
        <div class="ntm-leg-row">
          <b>{{ M.leyendaColumnasLabel }}</b>
          <span v-for="(d, i) in DIMENSIONES" :key="d.key">{{ d.letra }} {{ d.nombre }}<template v-if="i < DIMENSIONES.length - 1"> · </template></span>
        </div>
        <div class="ntm-leg-row"><b>{{ M.oportunidadLabel }}</b> ▸ {{ M.leyendaOportunidadTexto }}</div>
      </div>

      <div class="ntm-actions">
        <div class="ntm-filters" role="group" :aria-label="M.filtrosLabel">
          <button
            v-for="f in FILTROS" :key="f.key" type="button"
            class="ntm-chip" :class="{ on: filtroActivo === f.key }"
            :aria-pressed="filtroActivo === f.key"
            @click="toggleFiltro(f.key)"
          >{{ f.label }}</button>
        </div>
        <div class="ntm-toolbar">
          <button type="button" class="ntm-toggle" @click="vistaTabla = !vistaTabla" :aria-pressed="vistaTabla">
            {{ vistaTabla ? M.vistaMatriz : M.vistaTabla }}
          </button>
          <button type="button" class="ntm-csv" @click="descargarCsv">{{ M.descargarCsv }}</button>
        </div>
      </div>
    </template>

    <!-- Vista de tabla: alternativa textual completa (accesibilidad + descarga visual) -->
    <div v-if="vistaTabla && !compact" class="ntm-table-wrap">
      <table class="ntm-full-table">
        <thead>
          <tr>
            <th>{{ M.tablaColEstandar }}</th>
            <th>{{ M.colDisposicion }}</th>
            <th>{{ M.tablaColRol }}</th>
            <th>{{ M.colCobertura }}</th>
            <th v-for="d in DIMENSIONES" :key="d.key">{{ d.nombre }}</th>
            <th>{{ M.tablaColNota }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in registrosFiltrados" :key="i">
            <td>{{ r.estandar }}</td>
            <td>{{ r.disposicion }}</td>
            <td>{{ rolTexto(r.rol_correspondencia) }}</td>
            <td>{{ covWord(r.cobertura) }}</td>
            <td v-for="d in DIMENSIONES" :key="d.key">{{ fitWord(r[d.key]) }}</td>
            <td>{{ r.nota || '' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Vista de matriz: glifos, sin palabras de calificación en celda -->
    <template v-else>
      <div class="ntm-colhead" :class="{ 'ntm-colhead--static': compact }">
        <span class="ntm-disp-h">{{ M.colDisposicion }}</span>
        <span class="ntm-cells-h">
          <span class="ntm-mk-h" aria-hidden="true"></span>
          <span class="ntm-ch ntm-ch--cov" :title="M.colCobertura">{{ M.colCoberturaAbrev }}</span>
          <span v-for="d in DIMENSIONES" :key="d.key" class="ntm-ch" :title="d.nombre">{{ d.letra }}</span>
        </span>
      </div>

      <p v-if="!secciones.length" class="ntm-sin-resultados">{{ M.sinResultados }}</p>

      <div v-for="(sec, si) in secciones" :key="si" class="ntm-sec">
        <h3 v-if="sec.nombre" class="ntm-sec-h" :style="{ color: sec.ods6 ? 'var(--ods6)' : 'var(--ink)' }">{{ sec.nombre }}</h3>
        <button
          v-for="(r, i) in sec.filas" :key="i" type="button" class="ntm-row"
          :aria-label="filaAriaLabel(r)"
          @click="abrir(r, $event)"
        >
          <span class="ntm-disp">{{ r.disposicion }}</span>
          <span class="ntm-cells">
            <span class="ntm-mk" :class="{ 'ntm-mk--off': !r.tipo_brecha }" :title="r.tipo_brecha ? M.oportunidadLabel : ''">{{ r.tipo_brecha ? '▸' : '' }}</span>
            <span class="ntm-g" :class="covClass(r.cobertura)" role="img" :aria-label="covAria(r.cobertura)"></span>
            <span v-for="d in DIMENSIONES" :key="d.key" class="ntm-g" :class="fitClass(r[d.key])" role="img" :aria-label="fitAria(d, r[d.key])"></span>
          </span>
        </button>
      </div>
    </template>

    <!-- Detalle: hoja inferior en móvil, panel lateral en escritorio (CSS) -->
    <div v-if="activo" class="ntm-overlay" @click.self="cerrar">
      <div class="ntm-sheet" role="dialog" :aria-label="M.detalleLabel" aria-modal="true">
        <div class="ntm-grab" aria-hidden="true"></div>
        <button type="button" class="ntm-close" ref="closeBtn" @click="cerrar" :aria-label="M.cerrar">×</button>
        <h4>{{ activo.disposicion }}</h4>
        <div class="ntm-meta">{{ activo.estandar }}</div>
        <div class="ntm-meta">{{ M.rolLabel }}: {{ rolTexto(activo.rol_correspondencia) }} · {{ M.coberturaLabel }}: {{ covWord(activo.cobertura) }}</div>
        <div v-if="activo.tipo_brecha" class="ntm-op"><b>{{ M.oportunidadLabel }}</b> {{ agendaLabel(activo.tipo_brecha) }}</div>
        <p v-if="activo.nota" class="ntm-note">{{ activo.nota }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue';
import { content as C, fill } from '@/content';

const M = C.matriz;

const props = defineProps({
  registros: { type: Array, default: () => [] },
  titulo: { type: String, default: '' },
  compact: { type: Boolean, default: false },
  previewLimit: { type: Number, default: 8 },
});

// A · actor · P · procedimiento · C · coordinación · E · exigibilidad ·
// S · salvaguarda · F · federalismo (v8 §B.3: una letra por columna, nombre
// completo en la leyenda y en el tooltip/aria-label de cada encabezado y glifo).
const DIMENSIONES = [
  { key: 'actor_fit', letra: 'A', nombre: M.dimActor },
  { key: 'procedimiento_fit', letra: 'P', nombre: M.dimProcedimiento },
  { key: 'coordinacion_fit', letra: 'C', nombre: M.dimCoordinacion },
  { key: 'enforcement_fit', letra: 'E', nombre: M.dimExigibilidad },
  { key: 'salvaguarda_derechos_fit', letra: 'S', nombre: M.dimSalvaguarda },
  { key: 'federalismo_fit', letra: 'F', nombre: M.dimFederalismo },
];

const FILTROS = [
  { key: 'procedimiento', label: M.filtroProcedimiento, test: (r) => r.procedimiento_fit === 'debil' },
  { key: 'exigibilidad', label: M.filtroExigibilidad, test: (r) => r.enforcement_fit === 'debil' },
  { key: 'oportunidad', label: M.filtroOportunidad, test: (r) => !!r.tipo_brecha },
];

const filtroActivo = ref(null);
const vistaTabla = ref(false);
const activo = ref(null);
const closeBtn = ref(null);
let lastFocus = null;

const regionLabel = computed(() => (props.titulo ? `${M.regionLabel} · ${props.titulo}` : M.regionLabel));

const resumenTexto = computed(() => {
  const regs = props.registros;
  return fill(M.resumen, {
    n: regs.length,
    sustantivas: regs.filter((r) => r.rol_correspondencia === 'sustantivo').length,
    completas: regs.filter((r) => r.cobertura === 'completa').length,
    oportunidades: regs.filter((r) => r.tipo_brecha).length,
  });
});

// Un chip a la vez, removible: tocar el chip activo lo quita.
function toggleFiltro(key) {
  filtroActivo.value = filtroActivo.value === key ? null : key;
}

const registrosFiltrados = computed(() => {
  if (props.compact) return props.registros.slice(0, props.previewLimit);
  const f = FILTROS.find((x) => x.key === filtroActivo.value);
  return f ? props.registros.filter(f.test) : props.registros;
});

// Filas agrupadas por estándar (sección), en el orden de primera aparición
// del dato vivo; en modo compacto no hay secciones (vista previa plana).
const secciones = computed(() => {
  if (props.compact) {
    return registrosFiltrados.value.length ? [{ nombre: null, ods6: false, filas: registrosFiltrados.value }] : [];
  }
  const map = new Map();
  for (const r of registrosFiltrados.value) {
    const key = r.estandar;
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(r);
  }
  return [...map.entries()].map(([nombre, filas]) => ({ nombre, ods6: /^ODS 6/.test(nombre), filas }));
});

const FIT_WORD = { fuerte: M.ajusteFuerte, medio: M.ajusteMedio, debil: M.ajusteDebil, no_aplica: M.ajusteNoAplica };
const FIT_CLASS = { fuerte: 'g-full', medio: 'g-half', debil: 'g-out', no_aplica: 'g-na' };
const COV_WORD = { completa: M.coberturaCompleta, parcial: M.coberturaParcial, contextual: M.coberturaContextual };
const COV_CLASS = { completa: 'g-full', parcial: 'g-half', contextual: 'g-out' };

function fitWord(v) { return FIT_WORD[v] || v || ''; }
function fitClass(v) { return FIT_CLASS[v] || 'g-na'; }
function fitAria(d, v) { return `${d.nombre}: ${fitWord(v)}`; }
function covWord(v) { return COV_WORD[v] || v || ''; }
function covClass(v) { return COV_CLASS[v] || 'g-out'; }
function covAria(v) { return `${M.ariaCobertura}: ${covWord(v)}`; }
function rolTexto(r) { return r === 'sustantivo' ? M.rolSustantivo : M.rolContextual; }
function agendaLabel(v) { return (M.oportunidad && M.oportunidad[v]) || ''; }
function filaAriaLabel(r) { return `${r.disposicion}, ${r.estandar}`; }

function abrir(r, evt) {
  lastFocus = (evt && evt.currentTarget) || null;
  activo.value = r;
  nextTick(() => closeBtn.value && closeBtn.value.focus());
}
function cerrar() {
  activo.value = null;
  if (lastFocus && lastFocus.focus) lastFocus.focus();
}
function onKeydown(e) {
  if (e.key === 'Escape' && activo.value) cerrar();
}

onMounted(() => window.addEventListener('keydown', onKeydown));
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown));

// Descarga CSV: la tabla completa (34 filas del dato vivo), no un texto fijo.
function descargarCsv() {
  const headers = ['estandar', 'disposicion', 'rol_correspondencia', 'cobertura',
    'actor_fit', 'procedimiento_fit', 'coordinacion_fit', 'enforcement_fit',
    'salvaguarda_derechos_fit', 'federalismo_fit', 'tipo_brecha', 'nota'];
  const esc = (v) => {
    const s = v == null ? '' : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const lines = [headers.join(','), ...props.registros.map((r) => headers.map((h) => esc(r[h])).join(','))];
  const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = M.csvNombreArchivo;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
</script>
