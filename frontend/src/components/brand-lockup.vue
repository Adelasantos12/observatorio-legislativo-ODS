<template>
  <!-- Lockup de marca (Nota v6.1): isotipo (anillo ODS) + texto VIVO.
       El texto nunca vive dentro del SVG; sale de es.json (marca.*) para que
       la autora pueda renombrar el producto sin tocar código. -->
  <component
    :is="to ? 'router-link' : 'span'"
    :to="to || undefined"
    class="brand-lockup"
    :class="{ 'is-compact': compact, 'on-dark': onDark }"
    :aria-label="M.nombre"
  >
    <img :src="anillo" class="brand-ring" alt="" aria-hidden="true" />
    <span class="brand-text">
      <span class="brand-name">{{ M.nombre }}</span>
      <span v-if="!compact" class="brand-tagline">{{ M.tagline }}</span>
    </span>
  </component>
</template>

<script setup>
import { content } from '@/content';
import anillo from '@/assets/logo_anillo_ods.svg?url';

defineProps({
  compact: { type: Boolean, default: false },
  onDark: { type: Boolean, default: false },
  to: { type: [Object, String], default: null },
});
const M = content.marca;
</script>

<style scoped>
.brand-lockup {
  display: inline-flex;
  align-items: center;
  gap: 11px;
  text-decoration: none;
  color: inherit;
  line-height: 1;
}
/* El anillo nunca se encierra en caja/chip, ni lleva contorno, sombra o
   degradado; sus 17 colores no se recolorean ni reordenan. */
.brand-ring { width: 34px; height: 34px; display: block; flex: none; }
.brand-text { display: inline-flex; flex-direction: column; gap: 3px; }
.brand-name {
  font-family: "Inter", system-ui, sans-serif;
  font-weight: 600; font-size: 16px; letter-spacing: -0.015em;
  color: var(--ink, #1B1E32);
}
.brand-tagline {
  font-family: "Inter", system-ui, sans-serif;
  font-weight: 500; font-size: 10.5px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--ink-3, #9A9DAC);
}
/* Compacta: anillo 26px + solo wordmark, sin tagline */
.brand-lockup.is-compact .brand-ring { width: 26px; height: 26px; }
.brand-lockup.is-compact .brand-text { gap: 0; }
/* Sobre tinta (pie): wordmark en blanco, tagline #7A7E92, anillo intacto */
.brand-lockup.on-dark .brand-name { color: #FFFFFF; }
.brand-lockup.on-dark .brand-tagline { color: #7A7E92; }
</style>
