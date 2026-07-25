<template>
  <header class="site-header" :class="{ scrolled }" ref="headerEl">
    <div class="site-header__wrap">
      <!-- Escritorio: lockup completo; compacto al hacer scroll o en móvil -->
      <brand-lockup :to="{ name: 'huella' }" :compact="scrolled || isMobile" />

      <button
        class="site-header__toggle"
        :class="{ open }"
        :aria-expanded="open ? 'true' : 'false'"
        aria-label="Menú"
        @click="open = !open"
      >
        <span></span><span></span><span></span>
      </button>

      <nav class="site-header__nav" :class="{ open }">
        <router-link
          v-for="link in links"
          :key="link.route"
          v-show="link.condition"
          :to="{ name: link.route }"
          class="site-header__link"
          @click="open = false"
        >{{ link.name }}</router-link>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import config from '@/config';
import BrandLockup from '@/components/brand-lockup.vue';

const { locale } = useI18n();
const links = computed(() => config.MENU[locale.value] || config.MENU.es);

const open = ref(false);
const scrolled = ref(false);
const isMobile = ref(false);
const headerEl = ref(null);
let headerRo = null;

const onScroll = () => { scrolled.value = window.scrollY > 24; };
const onResize = () => { isMobile.value = window.matchMedia('(max-width: 720px)').matches; };
// Publica la altura real del header como variable CSS global (--header-h): así
// cualquier panel sticky de página (p. ej. el scrollytelling de /huella) puede
// pegarse justo DEBAJO del header en vez de quedar tapado por él (choque de dos
// position:sticky en top:0). Se mide en vivo porque la altura cambia entre el
// header completo y el compacto (scroll/móvil).
function publishHeaderHeight() {
  if (headerEl.value) {
    document.documentElement.style.setProperty('--header-h', headerEl.value.offsetHeight + 'px');
  }
}

onMounted(() => {
  onScroll(); onResize();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onResize);
  publishHeaderHeight();
  if (typeof ResizeObserver !== 'undefined' && headerEl.value) {
    headerRo = new ResizeObserver(publishHeaderHeight);
    headerRo.observe(headerEl.value);
  }
});
onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll);
  window.removeEventListener('resize', onResize);
  if (headerRo) headerRo.disconnect();
});
</script>

<style scoped>
.site-header {
  position: sticky; top: 0; z-index: 30;
  background: var(--bg, #fff);
  border-bottom: 1px solid var(--line, #E6E4DE);
  transition: box-shadow .2s ease;
}
.site-header.scrolled { box-shadow: 0 1px 0 var(--line, #E6E4DE), 0 6px 16px rgba(27,30,50,.05); }
.site-header__wrap {
  max-width: 1240px; margin: 0 auto;
  display: flex; align-items: center; justify-content: space-between;
  gap: 16px; padding: 14px clamp(16px, 5vw, 56px);
  /* La compactación suave del header al hacer scroll es una interacción
     distintiva del producto (decisión de diseño), no un descuido. */
  transition: padding .2s ease; /* impeccable-disable-line layout-transition: interacción de scroll distintiva */
}
.site-header.scrolled .site-header__wrap { padding-top: 10px; padding-bottom: 10px; }

.site-header__nav { display: flex; align-items: center; gap: clamp(14px, 2.2vw, 30px); }
.site-header__link {
  font-family: "Inter", system-ui, sans-serif;
  font-size: 15px; font-weight: 500; color: var(--ink-2, #565A70);
  text-decoration: none; padding: 6px 0; position: relative; white-space: nowrap;
}
.site-header__link:hover { color: var(--ink, #1B1E32); }
.site-header__link.router-link-active { color: var(--action, #009EDB); font-weight: 600; }
.site-header__link.router-link-active::after {
  content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px;
  background: var(--action, #009EDB); border-radius: 2px;
}

.site-header__toggle { display: none; background: none; border: 0; cursor: pointer; padding: 8px; }
.site-header__toggle span {
  display: block; width: 22px; height: 2px; margin: 4px 0; border-radius: 2px;
  background: var(--ink, #1B1E32); transition: transform .2s ease, opacity .2s ease;
}
.site-header__toggle.open span:nth-child(1) { transform: translateY(6px) rotate(45deg); }
.site-header__toggle.open span:nth-child(2) { opacity: 0; }
.site-header__toggle.open span:nth-child(3) { transform: translateY(-6px) rotate(-45deg); }

@media (max-width: 720px) {
  .site-header__toggle { display: block; }
  .site-header__nav {
    position: absolute; top: 100%; left: 0; right: 0;
    flex-direction: column; align-items: flex-start; gap: 4px;
    background: var(--bg, #fff); border-bottom: 1px solid var(--line, #E6E4DE);
    padding: 8px clamp(16px, 5vw, 56px) 16px;
    /* El panel está absolutamente posicionado (no empuja el contenido), así que
       se anima con transform + opacity —sin tocar layout— en vez de max-height. */
    opacity: 0; pointer-events: none; transform: translateY(-8px);
    transition: transform .22s ease, opacity .2s ease;
  }
  .site-header__nav.open { opacity: 1; pointer-events: auto; transform: translateY(0); }
  .site-header__link { padding: 10px 0; font-size: 16px; width: 100%; }
  .site-header__link.router-link-active::after { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .site-header__wrap, .site-header, .site-header__nav, .site-header__toggle span { transition: none; }
}
</style>
