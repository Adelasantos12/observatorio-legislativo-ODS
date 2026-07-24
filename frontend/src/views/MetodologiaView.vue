<template>
  <div class="huella-page">
    <article class="prose">
      <div class="kicker">{{ T.kicker }}</div>
      <h1 class="serif" style="margin:6px 0 18px">{{ T.titulo }}</h1>
      <p class="lede-sm">{{ T.intro }}</p>

      <h2>{{ T.fuentesTitulo }}</h2>
      <p>{{ T.fuentes }}</p>

      <h2>{{ T.codificacionTitulo }}</h2>
      <p>{{ T.codificacion }}</p>

      <h2>{{ T.alcanceTitulo }}</h2>
      <p>{{ T.alcance }}</p>

      <h2>{{ T.atribucionTitulo }}</h2>
      <p>{{ fill(T.atribucion, { documentadas: documentadas, total: total }) }}</p>

      <h2>{{ T.normtraceTitulo }}</h2>
      <p>{{ T.normtrace }}</p>

      <!-- Referencias de la escena del registro (patch registro §5). Cada una
           lleva su ancla (#ref-…) a la que enlazan los tramos de esa escena. -->
      <template v-if="T.referencias && T.referencias.length">
        <h2>{{ T.referenciasTitulo }}</h2>
        <p class="lede-sm">{{ T.referenciasIntro }}</p>
        <div v-for="r in T.referencias" :key="r.id" :id="r.id" class="referencia">
          <p><b>{{ r.cita }}</b></p>
          <p><a :href="r.url" target="_blank" rel="noopener">{{ r.url }}</a></p>
          <p class="muted">{{ r.nota }}</p>
        </div>
      </template>

      <p style="margin-top:26px">
        <router-link :to="{ name: 'huella' }">← Volver a la historia</router-link>
      </p>
    </article>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';
import { content, fill } from '@/content';

const T = content.metodologia;
const documentadas = ref('—');
const total = ref('—');

onMounted(async () => {
  try {
    const agg = await api.getMinutasResumen();
    documentadas.value = agg.kpis.atribucion_documentada;
    total.value = agg.kpis.minutas_totales;
  } catch (e) {
    /* la página se lee sin cifras si el API no responde */
  }
});
</script>
