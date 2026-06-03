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
  <router-view v-slot="{ Component, route: r }" class="overflow-x-hidden">
    <transition name="page" mode="out-in">
      <keep-alive :max="5">
        <component :is="Component" :key="r.path" />
      </keep-alive>
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
/* Page transitions — no blur to prevent horizontal overflow */
.page-enter-active {
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-leave-active {
  transition: opacity 0.12s ease-in,
              transform 0.15s ease-in;
  position: absolute;
  left: 0;
  right: 0;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* Bottom nav slide animation */
.bottom-nav-enter-active { transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1); }
.bottom-nav-leave-active { transition: transform 0.2s ease-in; }
.bottom-nav-enter-from { transform: translateY(100%); }
.bottom-nav-leave-to { transform: translateY(100%); }
</style>
