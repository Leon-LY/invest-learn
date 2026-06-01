<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import BottomNav from '@/components/common/BottomNav.vue'
import SearchOverlay from '@/components/market/SearchOverlay.vue'

const props = defineProps<{ showBack?: boolean }>()
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const searchRef = ref<InstanceType<typeof SearchOverlay>>()

const navItems = [
  { path: '/', label: '概览', icon: 'dashboard' },
  { path: '/watchlist', label: '自选', icon: 'star' },
  { path: '/news', label: '新闻', icon: 'news' },
  { path: '/learn', label: '学习', icon: 'book' },
  { path: '/portfolio', label: '模拟', icon: 'chart' },
]

function goBack() {
  router.back()
}

function openSearch() {
  searchRef.value?.open()
}

const showBottomNav = computed(() => navItems.some(item => route.path === item.path || route.path.startsWith(item.path + '/')))
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <!-- Top header bar -->
    <header class="h-12 bg-sidebar text-white flex items-center px-4 shrink-0 z-30">
      <button v-if="showBack" @click="goBack" class="mr-3 p-1 hover:bg-white/10 rounded">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2 font-semibold text-sm">
        <svg class="w-5 h-5 text-purple-400" fill="currentColor" viewBox="0 0 24 24"><path d="M3 13h1v7c0 1.103.897 2 2 2h12c1.103 0 2-.897 2-2v-7h1a1 1 0 00.707-1.707l-9-9a.999.999 0 00-1.414 0l-9 9A1 1 0 003 13zm7 7v-5h4v5h-4zm2-15.586l6 6V20h-3v-6H9v6H6v-8.586l6-6z"/></svg>
        <span class="hidden sm:inline">InvestLearn</span>
      </div>
      <div class="flex-1" />
      <button @click="openSearch" class="hidden sm:flex items-center gap-1.5 px-3 py-1 mr-2 bg-white/10 hover:bg-white/20 rounded-lg text-xs text-gray-300 transition-colors">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        <span>搜索</span>
        <kbd class="px-1 text-xs bg-white/20 rounded">⌘K</kbd>
      </button>
      <button @click="openSearch" class="sm:hidden p-1.5 mr-1 hover:bg-white/10 rounded text-gray-300">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
      </button>
      <button @click="appStore.toggleTheme()" class="p-1.5 hover:bg-white/10 rounded text-gray-300">
        <svg v-if="appStore.isDark" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path stroke-linecap="round" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
      </button>
    </header>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto pb-14 md:pb-0">
      <slot />
    </main>

    <!-- Bottom nav (mobile) -->
    <BottomNav v-if="showBottomNav" :items="navItems" />

    <!-- Global search overlay -->
    <SearchOverlay ref="searchRef" />
  </div>
</template>
