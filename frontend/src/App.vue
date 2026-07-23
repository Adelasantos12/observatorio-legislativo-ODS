<template>
  <div id="app">
    <site-header />
    <transition name="fade" mode="out-in">
      <div>
        <router-view />
        <footer-block />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';

import { useScannerStore } from '@/stores/scanner';
import SiteHeader from '@/components/site-header.vue';
import FooterBlock from '@/components/footer-block.vue';

const store = useScannerStore();

onMounted(() => {
  store.getTopics();
});
</script>

<style lang="scss"></style>
