<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import BottomNav from '@/components/common/BottomNav.vue'

const appStore = useAppStore()
const route = useRoute()

const navItems = [
  { path: '/', label: '发现', icon: 'dashboard' },
  { path: '/watchlist', label: '自选', icon: 'star' },
  { path: '/analysis', label: '分析', icon: 'chart' },
  { path: '/news', label: '资讯', icon: 'news' },
  { path: '/learn', label: '学习', icon: 'book' },
]

const showBottomNav = computed(() => navItems.some(item =>
  route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
))
</script>

<template>
  <router-view v-slot="{ Component, route: r }">
    <transition name="page" mode="out-in">
      <component :is="Component" :key="r.path" />
    </transition>
  </router-view>
  <!-- Global BottomNav — rendered once, never unmounts -->
  <BottomNav
    :items="navItems"
    class="fixed bottom-0 left-0 right-0 transition-transform duration-150 z-50 safe-area-bottom"
    :class="showBottomNav ? 'translate-y-0' : 'translate-y-full'"
  />
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
