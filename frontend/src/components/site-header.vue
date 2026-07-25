<template>
  <header class="site-header" :class="{ scrolled, 'nav-hidden': navHidden }" ref="headerEl">
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
// §A.3: en móvil la nav se oculta al bajar y reaparece al subir (nunca se
// esconde cerca del tope, para no jugarle sucio a la primera pantalla ni
// cuando el usuario "rebota" el scroll). navHidden solo aplica en móvil: en
// escritorio la nav siempre está visible (v8 §A.5).
const navHidden = ref(false);
let lastY = 0;

const onScroll = () => {
  const y = window.scrollY;
  scrolled.value = y > 24;
  if (isMobile.value) {
    const delta = y - lastY;
    if (y < 48) navHidden.value = false;
    else if (delta > 4) navHidden.value = true;   // bajando: se oculta
    else if (delta < -4) navHidden.value = false;  // subiendo: reaparece
  } else {
    navHidden.value = false;
  }
  lastY = y;
  publishNavHeight();
};
const onResize = () => {
  isMobile.value = window.matchMedia('(max-width: 720px)').matches;
  if (!isMobile.value) navHidden.value = false;
  publishNavHeight();
};
// Publica la altura "en vivo" de la nav como variable CSS global (--nav-h): así
// cualquier panel sticky de página (p. ej. el scrollytelling de /huella) puede
// pegarse justo DEBAJO de la nav en vez de quedar tapado por ella (choque de dos
// position:sticky en top:0). Se mide en vivo porque la altura cambia entre la
// nav completa y la compacta (scroll/móvil), y en móvil llega a 0 cuando la
// nav se oculta al bajar —el panel sticky sube su top para ocupar ese espacio,
// y baja de nuevo cuando la nav reaparece (transición suave, ver CSS).
function publishNavHeight() {
  const h = navHidden.value ? 0 : (headerEl.value ? headerEl.value.offsetHeight : 0);
  document.documentElement.style.setProperty('--nav-h', h + 'px');
}

onMounted(() => {
  lastY = window.scrollY;
  onScroll(); onResize();
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onResize);
  publishNavHeight();
  if (typeof ResizeObserver !== 'undefined' && headerEl.value) {
    headerRo = new ResizeObserver(publishNavHeight);
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
  transition: box-shadow .2s ease, transform .25s ease;
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
  /* §A.3: alto fijo de 48px en móvil (independiente del estado "scrolled"),
     para que --nav-h sea predecible y el panel sticky de /huella no salte. */
  .site-header__wrap { height: 48px; padding-top: 0; padding-bottom: 0; box-sizing: border-box; }
  .site-header.scrolled .site-header__wrap { padding-top: 0; padding-bottom: 0; }
  /* Se oculta al bajar, reaparece al subir (nunca position:fixed: sigue sticky,
     solo se traslada fuera del viewport con transform). */
  .site-header.nav-hidden { transform: translateY(-100%); }
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
