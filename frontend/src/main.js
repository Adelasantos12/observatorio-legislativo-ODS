import { createApp } from 'vue';
import App from './App.vue';
import router from '@/router';
import { createPinia } from 'pinia';
import { createI18n } from 'vue-i18n';
import VueGtag from 'vue-gtag';
import messages from '@/i18n/messages';
import '@/styles/identity.css';

const i18n = createI18n({
  locale: import.meta.env.VITE_DEFAULT_LOCALE,
  fallbackLocale: import.meta.env.VITE_FALLBACK_LOCALE || 'es',
  messages,
});

const app = createApp(App);

// --- Motion (adenda v5.1 §5 / v6 §2.1): dos efectos y nada más ---
// prefers-reduced-motion desactiva ambos.
const reduceMotion = () =>
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// v-reveal: aparición de sección (fade + translateY 12px, 350ms, una vez).
app.directive('reveal', {
  mounted(el) {
    el.classList.add('reveal');
    if (reduceMotion() || !('IntersectionObserver' in window)) {
      el.classList.add('in');
      return;
    }
    const io = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            el.classList.add('in');
            obs.unobserve(el);
          }
        });
      },
      { rootMargin: '0px 0px -12% 0px', threshold: 0.08 }
    );
    io.observe(el);
  },
});

// v-countup: la cifra sube de 0 al valor en 600ms al entrar en viewport.
app.directive('countup', {
  mounted(el, binding) {
    const target = Number(binding.value);
    const fmt = (n) => new Intl.NumberFormat('es-MX').format(Math.round(n));
    if (!isFinite(target)) return;
    if (reduceMotion() || !('IntersectionObserver' in window)) {
      el.textContent = fmt(target);
      return;
    }
    el.textContent = fmt(0);
    let started = false;
    const run = (t0) => {
      const dur = 600;
      const tick = (now) => {
        const p = Math.min(1, (now - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(target * eased);
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((e) => {
          if (e.isIntersecting && !started) {
            started = true;
            requestAnimationFrame((now) => run(now));
            obs.unobserve(el);
          }
        });
      },
      { threshold: 0.4 }
    );
    io.observe(el);
  },
});

app.use(i18n);
app.use(router);
app.use(createPinia());
app.use(
  VueGtag,
  {
    config: { id: import.meta.env.VITE_GA_ID },
    boootstrap: false,
  },
  router
);

app.mount('#app');
