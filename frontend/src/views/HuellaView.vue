<template>
  <div class="huella-page" :class="{ 'no-anim': !animate }">
    <!-- Sin datos: la historia nunca se dibuja con ceros del API (v4.1 §5) -->
    <div v-if="!ready" class="story-hero">
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ C.hero.cargando }}</h1>
    </div>
    <div v-else-if="!hasData" class="story-hero">
      <img class="section-art" :src="art.neutra" alt="" aria-hidden="true" />
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ C.estadoVacio.titulo }}</h1>
      <p class="sub">{{ C.estadoVacio.cuerpo }}</p>
    </div>

    <template v-else>
    <!-- Apertura (escena 1): hero de manchas ODS ascendiendo al anillo -->
    <header class="story-hero">
      <img class="hero-art" :src="art.hero" alt="Figuras en colores de los ODS ascendiendo hacia el anillo de los 17 Objetivos" />
      <div class="kicker">{{ C.hero.kicker }}</div>
      <h1 class="lede">{{ fill(C.hero.lede, { minutas: nMinutas, aprobadas: nLogradas, iniciativas: nIniciativas }) }}</h1>
      <p class="sub">{{ C.hero.sub }}</p>
    </header>

    <div class="story">
      <div class="scrolly">
        <!-- Gráfico fijo (un solo panel; su estado se deriva del índice de paso, v7
             §0.3). Sticky en TODOS los anchos —el gráfico se queda mientras el texto
             pasa por debajo—; en móvil su altura se contiene a 40vh (v8 §A: recupera
             el storytelling sin repetir el "head gigante" de 100vh). -->
        <div class="scrolly-graphic" :data-state="graphicState">
          <div style="width:100%">
            <div v-show="scene <= 4 || scene >= 6" class="unit-panel">
              <div ref="stageEl" class="unit-stage">
                <div v-for="n in nodes" :key="n.id" class="unit"
                  :class="[n.type === 'min' ? 'is-min' : 'is-ini', { faint: scene === 1 && n.type === 'ini', 'has-ods': colored && n.ods, outline: outlineScene && n.ods, dim: pos[n.id] && pos[n.id].dim, glow: pos[n.id] && pos[n.id].glow }]"
                  :style="unitStyle(n)" :title="n.label"></div>
                <div v-for="a in annotations" :key="a.key" class="unit-anno"
                     :class="{ 'ods-row': a.kind === 'ods' }"
                     :style="{ left: a.x + 'px', top: a.y + 'px', maxWidth: (a.w ? a.w + 'px' : undefined), opacity: a.show ? 1 : 0 }" :title="a.full || a.name || a.text">
                  <template v-if="a.kind === 'ods'">
                    <span v-if="a.odsNum" class="ods-chip" :style="{ background: a.color }">{{ a.odsNum }}</span>
                    <span class="ods-row-name">{{ a.name }}</span>
                    <b class="ods-row-count">{{ a.n }}</b>
                  </template>
                  <template v-else><b>{{ a.n }}</b> {{ a.text }}</template>
                </div>
              </div>
              <div class="unit-legend">
                <span class="k"><span class="sw" style="background:var(--ink-2);opacity:.8"></span> {{ C.leyenda.minuta }} ({{ nMinutas }})</span>
                <span class="k"><span class="sw" style="background:var(--ink-3)"></span> {{ C.leyenda.iniciativa }} ({{ nIniciativas }})</span>
                <span class="k" v-show="colored"><span class="sw" style="background:linear-gradient(90deg,#e5243b,#26bde2,#4c9f38)"></span> color por ODS · minutas a pleno, Ejecutivo tenue</span>
              </div>
            </div>

            <!-- E5: el caso del agua (invariante v6.2, no puede faltar) -->
            <div v-show="scene === 5" class="card">
              <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
                <h3 style="margin:0">{{ C.escenas.agua.fichaTitulo }}</h3>
                <span class="nt-badge nt-badge--validado">● {{ C.escenas.agua.fichaBadge }}</span>
              </div>
              <p class="muted">{{ C.escenas.agua.fichaResumen }}</p>
              <!-- data-label: en móvil (<992px) el reset de tipi-uikit apila las
                   celdas en tarjeta; con data-label cada valor lleva su rótulo
                   (Estándar/Disposición/Rol/Cobertura) en vez de texto suelto sin
                   contexto (bug v2 #1: la tabla ancha ya no desborda ni se
                   confunde). Desde 992px se ve como tabla normal (CSS nativo). -->
              <table class="nt-table" v-if="agua.length">
                <thead><tr><th>Estándar</th><th>Disposición</th><th>Rol</th><th>Cobertura</th></tr></thead>
                <tbody>
                  <tr v-for="(r,i) in agua.slice(0,6)" :key="i">
                    <td data-label="Estándar">{{ r.estandar }}</td><td data-label="Disposición">{{ r.disposicion }}</td>
                    <td data-label="Rol"><span :class="{muted: r.rol_correspondencia!=='sustantivo'}">{{ r.rol_correspondencia==='sustantivo'?'sustantivo':'contextual' }}</span></td>
                    <td data-label="Cobertura">{{ r.cobertura }}</td>
                  </tr>
                </tbody>
              </table>
              <!-- Serie abierta: armonización estatal (32 entidades). Sin fuente
                   del dato todavía, se muestra "en documentación", nunca "0 de 32". -->
              <div style="margin-top:14px">
                <div class="muted" style="margin-bottom:6px">
                  {{ C.escenas.agua.contadorLabel }} ·
                  <template v-if="armonizadas != null"><b>{{ armonizadas }}</b> {{ C.escenas.agua.contadorNota }}</template>
                  <span v-else class="badge">{{ C.escenas.agua.contadorSinDato }}</span>
                </div>
                <div class="serie">
                  <span v-for="i in 32" :key="i" class="serie-box" :class="{ full: armonizadas != null && i <= armonizadas }"></span>
                </div>
              </div>
              <p style="margin-top:12px" v-if="vitrina">
                <router-link :to="{ name: 'expediente', params: { id: vitrina } }">{{ C.escenas.agua.enlace }}</router-link>
              </p>
            </div>
          </div>
        </div>

        <!-- Pasos de prosa (Acto I). Cada paso dispara un estado del panel (mismo
             mecanismo con o sin JS de animación); el panel de arriba se queda fijo
             (sticky) mientras estos pasos pasan por debajo. -->
        <div class="scrolly-steps">
          <section class="step" data-step="0" data-state="grid"><div class="step-card">
            <h2>{{ C.escenas.agenda.titulo }}</h2>
            <p>{{ fill(C.escenas.agenda.p1, { minutas: nMinutas, iniciativas: nIniciativas }) }}</p>
            <p class="muted">{{ C.escenas.agenda.p2 }}</p>
          </div></section>

          <section class="step" data-step="1" data-state="estatus"><div class="step-card">
            <h2>{{ C.escenas.estatus.titulo }}</h2>
            <p>{{ fill(C.escenas.estatus.p1, { dof: est.publicada_dof || 0, revisora: est.en_revisora || 0, devueltas: est.devuelta || 0 }) }}</p>
            <p>
              <span class="st-badge st-dof"><span class="ic"></span>{{ C.estatus.publicada_dof }}</span> ·
              <span class="st-badge st-rev"><span class="ic"></span>{{ C.estatus.en_revisora }}</span> ·
              <span class="st-badge st-dev"><span class="ic"></span>{{ C.estatus.devuelta }}</span>
            </p>
          </div></section>

          <!-- E3 · beat 1: se ordenan por objetivo, todavía sin color -->
          <section class="step" data-step="2" data-state="orden"><div class="step-card">
            <h2>{{ C.escenas.hallazgo.titulo }}</h2>
            <p>{{ C.escenas.hallazgo.p1 }}</p>
          </div></section>

          <!-- E3 · beat 2: el momento del color -->
          <section class="step" data-step="3" data-state="color"><div class="step-card">
            <p class="lede-color">{{ C.escenas.hallazgo.p2 }}</p>
          </div></section>

          <section class="step" data-step="4" data-state="singulares"><div class="step-card">
            <h2>{{ C.escenas.singulares.titulo }}</h2>
            <p>{{ fill(C.escenas.singulares.p1, { sinOds: nSinOds }) }}</p>
            <p class="muted">{{ C.escenas.singulares.p2 }}</p>
          </div></section>

          <section class="step" data-step="5" data-state="agua"><div class="step-card">
            <h2>{{ C.escenas.agua.titulo }}</h2>
            <p>{{ C.escenas.agua.p1 }}</p>
            <p class="muted">{{ C.escenas.agua.p2 }}</p>
          </div></section>

          <!-- B · La escena del registro (el puente / la tesis). El color se pierde
               (lo hecho sin registro) y vuelve con p3 (lo documentado). -->
          <section v-if="C.escenas.registro" class="step" data-step="6" data-state="registro-sin"><div class="step-card">
            <h2>{{ reg.titulo }}</h2>
            <p>{{ regP1.pre }}<router-link v-if="regP1.mid" :to="{ name: 'metodologia', hash: '#' + reg.p1ancla }">{{ regP1.mid }}</router-link>{{ regP1.post }}</p>
            <p class="muted">{{ regP2.pre }}<router-link v-if="regP2.mid" :to="{ name: 'metodologia', hash: '#' + reg.p2ancla }">{{ regP2.mid }}</router-link>{{ regP2.post }}</p>
          </div></section>
          <section v-if="C.escenas.registro" class="step" data-step="7" data-state="registro-con"><div class="step-card">
            <p class="lede-color">{{ C.escenas.registro.p3 }}</p>
          </div></section>
        </div>
      </div>

      <!-- ACTO II · La línea de tiempo 2015→2030 (guion v7.1 A/C). Sin figura
           viajera: la línea se dibuja sola y cada hito enciende su punto. -->
      <div v-if="C.linea" class="story linea-story">
      <div class="scrolly">
        <div class="scrolly-graphic" :data-state="'linea-' + lineaScene">
          <div style="width:100%">
            <div class="linea-stage">
              <div class="linea-anio-big" :class="hitos[lineaScene] && hitos[lineaScene].t">{{ hitos[lineaScene] ? hitos[lineaScene].anio : '' }}</div>
              <div class="linea-track-wrap">
                <div class="linea-baseline"></div>
                <div class="linea-track" :style="{ transform: 'translate(-' + (lineaScene * 240) + 'px, -50%)' }">
                  <div class="linea-progress" :style="{ width: (lineaScene * 240) + 'px' }"></div>
                  <div v-for="(hi, i) in hitos" :key="i" class="linea-pt" :class="[hi.t, { active: i === lineaScene }]" :style="{ left: (i * 240) + 'px' }">
                    <span class="dot"></span>
                    <span class="yr">{{ hi.anio }}</span>
                  </div>
                </div>
              </div>
              <div class="linea-counters">
                <div class="ct"><span class="lbl">{{ C.linea.contadorDiasPre }}</span><b class="tabular linea-num">{{ diasCumbre }}</b><span class="lbl">{{ C.linea.contadorDiasSuf }}</span></div>
                <div class="ct"><span class="lbl">{{ C.linea.contador2Pre }}</span><b class="tabular linea-num">{{ asuntosDoc }}</b><span class="lbl">{{ C.linea.contador2Post }}</span></div>
              </div>
            </div>
          </div>
        </div>
        <div class="scrolly-steps">
          <section v-for="(hi, i) in hitos" :key="i" class="step" :data-step="'l' + i" :data-state="'linea-' + i"><div class="step-card">
            <div class="linea-anio" :class="hi.t">{{ hi.anio }}</div>
            <p>{{ hitoTexto(hi) }}</p>
            <a v-if="hi.fuente" :href="hi.fuente" target="_blank" rel="noopener" class="linea-fuente">{{ C.linea.fuenteEtiqueta || 'fuente' }} ↗</a>
          </div></section>
        </div>
      </div>
      </div>

      <!-- Explorador (escena 7) -->
      <section class="card explorador" style="margin:0 clamp(16px,5vw,56px) 24px">
        <h3 style="margin-top:0">{{ C.explorador.titulo }}</h3>
        <p class="muted" style="max-width:36em">{{ C.explorador.intro }}</p>
        <div class="filters">
          <input v-model="q" @input="loadIniciativas" :placeholder="C.explorador.buscar" />
          <select v-model="fOds" @change="loadIniciativas">
            <option value="">{{ C.explorador.todosOds }}</option>
            <option v-for="row in agg.por_ods" :key="row.ods" :value="row.ods">ODS {{ row.ods }} — {{ odsName(row.ods) }}</option>
          </select>
          <input v-model="fMeta" @input="loadIniciativas" :placeholder="C.explorador.metaPlaceholder" style="width:120px" />
          <button class="badge" @click="clearFilters">{{ C.explorador.limpiar }}</button>
        </div>
        <!-- Móvil: tarjetas apiladas (bug v2 #4) — la tabla ancha no cabe en un
             teléfono; escritorio conserva la tabla original. -->
        <div v-if="isMobile" class="card-grid explorador-cards">
          <div class="rec-card" v-for="i in iniciativas" :key="i.id" @click="goExpediente(i.id)">
            <div class="clave">{{ C.explorador.colNum }} {{ i.num }}</div>
            <div class="tema">{{ i.denominacion }}</div>
            <div class="muted" v-if="i.tema">{{ i.tema }}</div>
            <div class="meta-row">
              <span v-if="i.ods_principal" class="ods-chip" :style="{background: odsColor(i.ods_principal)}">{{ i.ods_principal }}</span>
              <span v-for="s in i.ods_secundarios" :key="s" class="ods-chip" :style="{background: odsColor(s), opacity:.6}">{{ s }}</span>
              <span class="badge" :class="'badge--' + (i.confianza||'pendiente')">{{ i.confianza || C.explorador.sinCodificar }}</span>
            </div>
            <div class="muted" v-if="i.metas && i.metas.length">{{ i.metas.join(' · ') }}</div>
            <div class="muted">{{ i.estatus }}</div>
          </div>
        </div>
        <table v-else>
          <thead><tr><th>{{ C.explorador.colNum }}</th><th>{{ C.explorador.colDenominacion }}</th><th>{{ C.explorador.colOds }}</th><th>{{ C.explorador.colEstatus }}</th><th>{{ C.explorador.colConfianza }}</th></tr></thead>
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
              <td><span class="badge" :class="'badge--' + (i.confianza||'pendiente')">{{ i.confianza || C.explorador.sinCodificar }}</span></td>
            </tr>
          </tbody>
        </table>
        <p class="muted" v-if="!iniciativas.length">{{ C.explorador.sinResultados }}</p>
        <p style="margin-top:12px"><router-link :to="{ name: 'minutas' }">{{ C.explorador.ctaMinutas }}</router-link></p>
      </section>
    </div>

    <footer class="story-method">
      {{ fill(C.metodo.pie, { corte: agg.corte || 's/f' }) }}
      <router-link :to="{ name: 'metodologia' }">{{ C.metodo.enlace }}</router-link>.
    </footer>
    </template>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';
import { content as C, fill } from '@/content';
import heroUrl from '@/assets/illustrations/hero_manchas_ods.svg?url';
import apoyoUrl from '@/assets/illustrations/apoyo.svg?url';
import ascensoUrl from '@/assets/illustrations/ascenso.svg?url';
import alcanceUrl from '@/assets/illustrations/alcance.svg?url';
import anilloUrl from '@/assets/illustrations/anillo_ods.svg?url';
import neutraUrl from '@/assets/illustrations/mancha_neutra.svg?url';

// Ilustraciones por sección (reuso, adenda v5.1 §4.3)
const art = {
  hero: heroUrl, apoyo: apoyoUrl, ascenso: ascensoUrl,
  alcance: alcanceUrl, anillo: anilloUrl, neutra: neutraUrl,
};

const router = useRouter();
const ready = ref(false);
const scene = ref(0);
const lineaScene = ref(0);
const animate = ref(true);
// Móvil: el panel del gráfico sigue siendo sticky (v8 §A recupera el
// storytelling), solo que con altura contenida a 40vh (CSS, identity.css). El
// breakpoint coincide con el de identity.css (max-width:720px) y con el de
// site-header.vue, que publica --nav-h para que el panel se pegue justo
// debajo de la nav (y suba cuando la nav se oculta al bajar).
const MOBILE_MQ = '(max-width: 720px)';
const isMobile = ref(typeof window !== 'undefined' && window.matchMedia && window.matchMedia(MOBILE_MQ).matches);
// Layout por objetivo en E3/E4 (escenas 2-4). El color (teñido) llega en el
// segundo beat de E3 (escena 3): ese es "el momento del color" (guion v7 E3).
// Escenas con layout por objetivo. Incluye la escena del registro (6 y 7).
const BYODS = [2, 3, 4, 6, 7];
const grouped = computed(() => BYODS.includes(scene.value));
const colored = computed(() => [3, 4, 7].includes(scene.value)); // teñido (E3 + registro con color)
const outlineScene = computed(() => scene.value === 6);           // registro sin registro: contorno
// Estado del panel derivado del índice de paso (máquina de estados, v7 §0.3).
const graphicState = computed(() => ['grid', 'estatus', 'orden', 'color', 'singulares', 'agua', 'registro-sin', 'registro-con'][scene.value] || 'grid');
// Escena del registro: ⟦…⟧ marca el tramo con enlace a una referencia en
// /metodologia. Los corchetes no se renderizan (patch registro §2).
function bracket(s) {
  const m = (s || '').match(/^([\s\S]*?)⟦([\s\S]*?)⟧([\s\S]*)$/);
  return m ? { pre: m[1], mid: m[2], post: m[3] } : { pre: s || '', mid: '', post: '' };
}
const reg = computed(() => (C.escenas && C.escenas.registro) || {});
const regP1 = computed(() => bracket(reg.value.p1));
const regP2 = computed(() => bracket(reg.value.p2));

// Línea de tiempo (Acto II, v7.1)
const hitos = computed(() => (C.linea && C.linea.hitos) || []);
// Cifras tabulares vivas: días a la Cumbre (sep 2027, día provisional 1/sep) y
// asuntos documentados (minutas + iniciativas del periodo).
const diasCumbre = computed(() => {
  const target = new Date('2027-09-01T00:00:00Z');
  const diff = Math.ceil((target - new Date()) / 86400000);
  return diff > 0 ? new Intl.NumberFormat('es-MX').format(diff) : '0';
});
const asuntosDoc = computed(() => new Intl.NumberFormat('es-MX').format(nMinutas.value + nIniciativas.value));
function hitoTexto(hi) { return fill(hi.hecho || '', { minutas: nMinutas.value, aprobadas: nLogradas.value }); }

const agg = ref({ kpis: {}, por_ods: [], corte: null });
const minAgg = ref({ kpis: {}, por_estatus: [], por_ods: [] });
const cat = ref({ ods: {}, metas: [] });
const nodes = ref([]);
const pos = reactive({});
const annotations = ref([]);
const agua = ref([]);
const vitrina = ref(null);
// Armonización estatal: sin fuente de dato todavía → null. La UI muestra "en
// documentación" y las 32 casillas vacías; nunca un "0 de 32" (afirmación sin
// fuente). Cuando exista el dato, se asigna el número y aparece "N de 32".
const armonizadas = ref(null);

const stageEl = ref(null);
let io = null;
let ro = null;

const iniciativas = ref([]);
const q = ref('');
const fOds = ref('');
const fMeta = ref('');

const nMinutas = computed(() => minAgg.value.kpis.minutas_totales || 0);
const nIniciativas = computed(() => agg.value.kpis.iniciativas_presentadas || 0);
const nLogradas = computed(() => agg.value.kpis.aprobadas || 0);
const est = computed(() => Object.fromEntries((minAgg.value.por_estatus || []).map((e) => [e.estatus, e.n])));
const odsDominante = computed(() => agg.value.kpis.ods_dominante || '16');
const nSinOds = computed(() => nodes.value.filter((n) => !n.ods).length);
// La historia nunca se dibuja con ceros del API (v4.1 §5): sin unidades, estado vacío.
const hasData = computed(() => nodes.value.length > 0);

function odsColor(n) { return (cat.value.ods[String(n)] || {}).color || 'var(--ink3)'; }
function odsName(n) { return (cat.value.ods[String(n)] || {}).nombre_es || ('ODS ' + n); }
// v7.1 E: nombre corto para el rótulo de fila (la identidad del ODS nunca se
// trunca a "O..."). Fila "sin" = "Sin correspondencia".
const ODS_CORTO = { 1:'Pobreza', 2:'Hambre', 3:'Salud', 4:'Educación', 5:'Género', 6:'Agua', 7:'Energía', 8:'Trabajo decente', 9:'Industria', 10:'Desigualdades', 11:'Ciudades', 12:'Consumo responsable', 13:'Clima', 14:'Océanos', 15:'Ecosistemas', 16:'Paz y justicia', 17:'Alianzas' };
function odsCorto(n) { return ODS_CORTO[Number(n)] || ('ODS ' + n); }

// Tamaño de celda adaptable (v8 · responsive): los cuadritos se reajustan solos
// para caber en el panel a cualquier ancho —móvil o ventana no maximizada— sin
// amontonarse ni desbordar. GAP es el aire entre cuadritos; el lado del cuadrito
// renderizado (unitPx) se recalcula por escena y se aplica inline.
const GAP = 3;
const MINCELL = 7;   // celda mínima: cuadrito de ~4px, aún legible como mancha
const MAXCELL = 16;  // celda de referencia (el look de escritorio holgado)
const unitPx = ref(MAXCELL - GAP);
function stageSize() {
  const el = stageEl.value;
  return { w: Math.max(200, el ? el.clientWidth : 560), h: Math.max(180, el ? el.clientHeight : 500) };
}
// Mayor celda en [MINCELL, MAXCELL] tal que N nodos, repartidos en las columnas
// que quepan en 'w', no superen la altura 'h'. Así la rejilla nunca desborda.
function fitCell(n, w, h) {
  for (let c = MAXCELL; c > MINCELL; c--) {
    const cols = Math.max(1, Math.floor(w / c));
    if (Math.ceil(n / cols) * c <= h) return c;
  }
  return MINCELL;
}
// Medición de etiqueta de grupo (v7 §0.2): ancho del texto renderizado, con el
// número + espacio delante, para decidir si cabe o se abrevia.
let _ctx = null;
function measureLabel(txt) {
  if (typeof document === 'undefined') return 0;
  if (!_ctx) { _ctx = document.createElement('canvas').getContext('2d'); }
  _ctx.font = '600 13px Inter, system-ui, sans-serif';
  return _ctx.measureText('00 ' + txt).width;
}
function gridLayout(list, x0, y0, cols, c) {
  const map = {};
  list.forEach((n, i) => { map[n.id] = { x: x0 + (i % cols) * c, y: y0 + Math.floor(i / cols) * c }; });
  return map;
}
function computePositions() {
  const { w, h } = stageSize();
  const out = {}; const anno = []; const sc = scene.value;
  let cell = MAXCELL;
  if (sc === 0) {
    cell = fitCell(nodes.value.length, w, h);
    const cols = Math.max(8, Math.floor(w / cell));
    const rows = Math.ceil(nodes.value.length / cols);
    Object.assign(out, gridLayout(nodes.value, Math.max(0, (w - cols * cell) / 2), Math.max(0, (h - rows * cell) / 2), cols, cell));
  } else if (sc === 1) {
    const groups = [
      { key: 'publicada_dof', label: C.estatus.publicada_dof, short: 'DOF', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'publicada_dof') },
      { key: 'en_revisora', label: C.estatus.en_revisora, short: 'Senado', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'en_revisora') },
      { key: 'devuelta', label: C.estatus.devuelta, short: 'Devuelta', nodes: nodes.value.filter((n) => n.type === 'min' && n.status === 'devuelta') },
      { key: 'ini', label: C.leyenda.iniciativa, short: 'Ejecutivo', nodes: nodes.value.filter((n) => n.type === 'ini') },
    ].filter((g) => g.nodes.length);
    const colW = w / groups.length;
    // La celda se encoge para que la columna más alta quepa bajo su rótulo (y=40).
    const maxN = Math.max(...groups.map((g) => g.nodes.length));
    for (let c = MAXCELL; c > MINCELL; c--) { const pr = Math.max(2, Math.floor((colW - 8) / c)); cell = c; if (40 + Math.ceil(maxN / pr) * c <= h) break; }
    const perRow = Math.max(2, Math.floor((colW - 8) / cell));
    groups.forEach((g, gi) => {
      const x0 = gi * colW + 4;
      Object.assign(out, gridLayout(g.nodes, x0, 40, perRow, cell));
      // Anticolisión: si el nombre + 24px no cabe en la columna, se abrevia; el
      // completo va en title y la etiqueta se recorta al ancho de su columna.
      const fits = measureLabel(g.label) + 24 <= colW;
      anno.push({ key: g.key, x: x0, y: 14, n: g.nodes.length, text: fits ? g.label : g.short, full: g.label, w: Math.max(34, colW - 10), show: true });
    });
  } else if ([2, 3, 4, 6, 7].includes(sc)) {
    const byOds = {};
    nodes.value.forEach((n) => { const k = n.ods || 'sin'; (byOds[k] = byOds[k] || []).push(n); });
    const allKeys = Object.keys(byOds).sort((a, b) => byOds[b].length - byOds[a].length);
    // E: la identidad del ODS nunca se trunca. Se intenta el layout con rótulo por
    // fila (ODS N · Nombre encima de su banda de color), encogiendo la celda para
    // que el apilado quepa a lo alto. Si el panel es bajo (móvil), los 18 rótulos
    // no caben todos: en vez de perder la identidad ODS (rejilla sin rótulo ni
    // color reconocible), se colapsan los objetivos de MENOR conteo en una sola
    // banda "Otros N objetivos" —siempre con su propio rótulo— hasta que el resto
    // SÍ quepa, cada uno con su chip de color y su nombre. ODS 6 y "sin
    // correspondencia" nunca se colapsan: E4 (singulares) los necesita nombrados
    // siempre. Se decide por la ALTURA disponible (no por el ancho): el
    // escritorio conserva los 18 rótulos completos y el móvil nunca amontona ni
    // pierde el color de los ODS que sí puede mostrar con nombre.
    const LABEL_H = 20;
    const ROW_GAP = 3; // aire entre bandas de ODS (ajustado para que 18 quepan)
    const perRowFor = (c) => Math.max(4, Math.floor((w - 12) / c));
    const heightOf = (ks, map, c) => ks.reduce((y, k) => y + LABEL_H + Math.ceil(map[k].length / perRowFor(c)) * c + ROW_GAP, 0);
    const pinned = ['6', 'sin'].filter((k) => byOds[k]);
    const others = allKeys.filter((k) => !pinned.includes(k));
    let labeledCell = 0; let shownKeys = allKeys; let groupsMap = byOds; let otrasGroups = 0;
    for (let nOthers = others.length; nOthers >= 0 && !labeledCell; nOthers--) {
      const keep = new Set([...pinned, ...others.slice(0, nOthers)]);
      const collapsed = others.slice(nOthers);
      const testMap = {}; const testKeys = [];
      allKeys.forEach((k) => { if (keep.has(k)) { testMap[k] = byOds[k]; testKeys.push(k); } });
      if (collapsed.length) { testMap.otras = collapsed.flatMap((k) => byOds[k]); testKeys.push('otras'); }
      for (let c = MAXCELL; c >= MINCELL; c--) {
        if (heightOf(testKeys, testMap, c) <= h) { labeledCell = c; shownKeys = testKeys; groupsMap = testMap; otrasGroups = collapsed.length; break; }
      }
    }
    if (labeledCell) {
      cell = labeledCell;
      const perRow = perRowFor(cell);
      const show = (sc === 2 || sc === 3);
      let y = 0;
      shownKeys.forEach((k) => {
        const list = groupsMap[k];
        const rows = Math.ceil(list.length / perRow);
        const cy = y + LABEL_H;
        list.forEach((n, i) => {
          out[n.id] = { x: 2 + (i % perRow) * cell, y: cy + Math.floor(i / perRow) * cell, dim: sc === 4 && !isSingular(n), glow: sc === 4 && isSingular(n) };
        });
        const isSin = k === 'sin';
        const isOtras = k === 'otras';
        anno.push({
          kind: 'ods', key: 'ods' + k, x: 0, y, w: w - 8,
          odsNum: (isSin || isOtras) ? '' : String(k), color: (isSin || isOtras) ? 'var(--ink-3)' : odsColor(k),
          name: isOtras ? fill(C.leyenda.otrosOds, { n: otrasGroups }) : (isSin ? 'Sin correspondencia' : ('ODS ' + k + ' · ' + odsCorto(k))),
          n: list.length,
          show: sc === 4 ? (k === '6' || k === 'sin') : (sc >= 6 ? false : show),
        });
        y += LABEL_H + rows * cell + ROW_GAP;
      });
    } else {
      // Red de seguridad última (no debería alcanzarse con las 221 unidades del
      // dataset actual): rejilla compacta ordenada por ODS, sin rótulo por fila.
      const ordered = allKeys.flatMap((k) => byOds[k]);
      cell = fitCell(ordered.length, w, h);
      const cols = Math.max(6, Math.floor(w / cell));
      const rows = Math.ceil(ordered.length / cols);
      const x0 = Math.max(0, (w - cols * cell) / 2);
      const y0 = Math.max(0, (h - rows * cell) / 2);
      ordered.forEach((n, i) => {
        out[n.id] = { x: x0 + (i % cols) * cell, y: y0 + Math.floor(i / cols) * cell, dim: sc === 4 && !isSingular(n), glow: sc === 4 && isSingular(n) };
      });
    }
  }
  unitPx.value = Math.max(4, cell - GAP);
  Object.keys(pos).forEach((k) => delete pos[k]);
  Object.assign(pos, out);
  annotations.value = anno;
}
function isSingular(n) { return !n.ods || n.ods === '6'; }
function unitStyle(n) {
  const p = pos[n.id];
  const size = { width: unitPx.value + 'px', height: unitPx.value + 'px' };
  if (!p) return { ...size, transform: 'translate(0,0)', opacity: 0 };
  const s = { ...size, transform: `translate(${p.x}px, ${p.y}px)` };
  // El color oficial del ODS solo se aplica en "el momento del color" (E3 beat 2).
  if (colored.value && n.ods) s['--ods'] = odsColor(n.ods);
  return s;
}
function setScene(i) { if (i === scene.value) return; scene.value = i; if (i <= 4 || i >= 6) nextTick(computePositions); }
function setLinea(i) { if (i === lineaScene.value) return; lineaScene.value = i; }

function goExpediente(id) { router.push({ name: 'expediente', params: { id } }); }
function clearFilters() { q.value = ''; fOds.value = ''; fMeta.value = ''; loadIniciativas(); }
function loadIniciativas() {
  const params = {};
  if (q.value) params.q = q.value;
  if (fOds.value) params.ods = fOds.value;
  if (fMeta.value) params.meta = fMeta.value;
  api.getHuellaIniciativas(params).then((d) => (iniciativas.value = d || []));
}

let mqMobile = null;
function onMqMobile() { isMobile.value = mqMobile.matches; }

onMounted(async () => {
  animate.value = !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (window.matchMedia) {
    mqMobile = window.matchMedia(MOBILE_MQ);
    onMqMobile();
    (mqMobile.addEventListener ? mqMobile.addEventListener.bind(mqMobile) : mqMobile.addListener.bind(mqMobile))('change', onMqMobile);
  }
  cat.value = await api.getHuellaCatalogos();
  agg.value = await api.getHuellaEjecutivo();
  minAgg.value = await api.getMinutasResumen();
  vitrina.value = agg.value.normtrace_vitrina || null;

  const inis = (await api.getHuellaIniciativas()) || [];
  const mins = (await api.getMinutasLista()) || [];
  nodes.value = [
    ...mins.map((m) => ({ id: 'm' + m.id, type: 'min', ods: m.ods_principal || null, status: m.estatus, label: m.denominacion })),
    ...inis.map((i) => ({ id: 'i' + i.id, type: 'ini', ods: i.ods_principal || null, status: (i.seccion || '').startsWith('Aprobadas') ? 'lograda' : 'proceso', label: i.denominacion })),
  ];

  if (vitrina.value) {
    const nt = await api.getNormtraceExpediente(vitrina.value);
    agua.value = (nt && nt.registros) || [];
  }

  ready.value = true;
  loadIniciativas();
  await nextTick();
  computePositions();
  ro = new ResizeObserver(() => { if (scene.value <= 4 || scene.value >= 6) computePositions(); });
  if (stageEl.value) ro.observe(stageEl.value);
  // El estado cambia al cruzar el 50% del viewport (v7 §0.3): un paso, un estado.
  io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const ds = e.target.getAttribute('data-step');
      if (ds && ds[0] === 'l') setLinea(Number(ds.slice(1)));
      else setScene(Number(ds));
    });
  }, { rootMargin: '-50% 0px -50% 0px', threshold: 0 });
  document.querySelectorAll('.step').forEach((s) => io.observe(s));
});

onBeforeUnmount(() => {
  if (io) io.disconnect();
  if (ro) ro.disconnect();
  if (mqMobile) (mqMobile.removeEventListener ? mqMobile.removeEventListener.bind(mqMobile) : mqMobile.removeListener.bind(mqMobile))('change', onMqMobile);
});
</script>
