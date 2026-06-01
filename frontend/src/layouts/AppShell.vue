<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import BottomNav from '@/components/common/BottomNav.vue'
import SearchOverlay from '@/components/market/SearchOverlay.vue'

defineProps<{ showBack?: boolean }>()
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const searchRef = ref<InstanceType<typeof SearchOverlay>>()

const navItems = [
  { path: '/', label: '发现', icon: 'dashboard' },
  { path: '/watchlist', label: '自选', icon: 'star' },
  { path: '/analysis', label: '分析', icon: 'chart' },
  { path: '/news', label: '资讯', icon: 'news' },
  { path: '/learn', label: '学习', icon: 'book' },
]

function goBack() { router.back() }
function openSearch() { searchRef.value?.open() }

const showBottomNav = computed(() => navItems.some(item =>
  route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
))
</script>

<template>
  <div class="min-h-screen flex flex-col relative">
    <!-- Header — tech gradient accent -->
    <header class="h-12 bg-white/80 dark:bg-[#1A1B2E]/80 backdrop-blur-xl border-b border-gray-100/50 dark:border-gray-800/50 flex items-center px-4 shrink-0 z-30 sticky top-0">
      <button v-if="showBack" @click="goBack" class="mr-2 p-1.5 -ml-1 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors">
        <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-primary via-purple-500 to-cyan-400 flex items-center justify-center glow-ring">
          <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/></svg>
        </div>
        <span class="font-bold text-base text-gray-900 dark:text-white">基智学</span><span class="hidden sm:inline text-xs text-gray-400 ml-1.5 font-normal">by Leon</span>
        <div class="hidden sm:flex items-center gap-1 ml-2">
          <span class="glow-dot hidden sm:inline-block"></span>
          <span class="text-[10px] text-gray-400">LIVE</span>
        </div>
      </div>
      <div class="flex-1" />
      <button @click="openSearch" class="flex items-center gap-1.5 px-3 py-1.5 mr-1 bg-gray-100/50 dark:bg-gray-800/50 hover:bg-gray-200/50 dark:hover:bg-gray-700/50 rounded-full text-xs text-gray-500 dark:text-gray-400 transition-all hover:shadow-md">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
        <span class="hidden sm:inline">搜基金</span>
      </button>
      <button @click="router.push('/settings')" class="p-1.5 mr-1 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg text-gray-500 dark:text-gray-400 transition-colors" title="设置">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
      </button>
      <button @click="appStore.toggleTheme()" class="p-1.5 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg text-gray-500 dark:text-gray-400 transition-colors">
        <svg v-if="appStore.isDark" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><path stroke-linecap="round" d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
      </button>
    </header>

    <main class="flex-1 overflow-y-auto pb-16 md:pb-0">
      <slot />
    </main>

    <BottomNav :items="navItems" :class="showBottomNav ? '' : 'translate-y-full opacity-0 pointer-events-none'" class="transition-all duration-150" />
    <SearchOverlay ref="searchRef" />
  </div>
</template>
