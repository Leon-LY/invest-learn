<script setup lang="ts">
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<template>
  <router-view v-slot="{ Component, route: r }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="r.path" />
    </transition>
  </router-view>
</template>

<style>
/* Fast page transitions — no more flicker */
.page-enter-active {
  transition: opacity 0.15s ease-out, transform 0.15s ease-out;
}
.page-leave-active {
  transition: opacity 0.1s ease-in, transform 0.1s ease-in;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-2px);
}
</style>
