<template>
  <div>
    <div
      id="footer"
      class="o-container o-container--fluid o-section u-bg-white"
    >
      <div class="o-container">
        <div class="o-grid">
          <div class="o-grid__col u-12@sm u-margin-top-4">
            <p class="u-text-tbody2">{{ $t('common.footer.disclaimer') }}</p>
            <p class="u-color-secondary-dark u-text-tbody2 u-margin-top-2">
              {{ new Date().getFullYear() }} · {{ $t('common.footer.copy') }}
            </p>
            <p class="u-color-secondary-dark u-text-tbody2">
              {{ $t('common.footer.tech') }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div
      class="c-decorator"
      style="background-image: url('/img/multicolor.jpg')"
    ></div>

    <vue-cookie-accept-decline
      :debug="false"
      :disableDecline="false"
      :showPostponeButton="false"
      @clicked-accept="cookieClickedAccept"
      @clicked-decline="cookieClickedDecline"
      @status="cookieStatus"
      elementId="cookiePanel"
      ref="cookiePanel"
      transitionName="slideFromBottom"
      type="floating"
    >
      <template #message>
        {{ $t('common.cookies.info') }}
      </template>

      <template #declineContent>{{ $t('common.cookies.decline') }}</template>
      <template #acceptContent>{{ $t('common.cookies.accept') }}</template>
    </vue-cookie-accept-decline>
  </div>
</template>

<script>
import VueCookieAcceptDecline from 'vue-cookie-accept-decline';
import 'vue-cookie-accept-decline/dist/vue-cookie-accept-decline.css';
import { bootstrap } from 'vue-gtag';

import { TipiIcon } from '@politicalwatch/tipi-uikit';

export default {
  name: 'footer-block',
  components: {
    VueCookieAcceptDecline,
    TipiIcon,
  },
  methods: {
    cookieStatus: (val) => {
      // console.log('Cookie status: ' + val);
      if (val === 'decline' || val == null) {
        if (gtag) {
          gtag('consent', 'default', {
            ad_storage: 'denied',
            analytics_storage: 'denied',
          });
        }
      } else if (val === 'accept') {
        bootstrap().then(() => {
          gtag('consent', 'update', {
            ad_storage: 'granted',
            analytics_storage: 'granted',
          });
        });
      }
    },
    cookieClickedAccept: () => {
      bootstrap().then(() => {
        gtag('consent', 'update', {
          ad_storage: 'granted',
          analytics_storage: 'granted',
        });
      });
    },
    cookieClickedDecline: () => {
      gtag('consent', 'default', {
        ad_storage: 'denied',
        analytics_storage: 'denied',
      });
    },
  },
};
</script>

<style scoped lang="scss">
#footer {
  .o-container {
    border-top: 1px solid #ddd;
  }
}
</style>
