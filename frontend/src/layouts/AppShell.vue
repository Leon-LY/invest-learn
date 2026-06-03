<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import SearchOverlay from '@/components/market/SearchOverlay.vue'

defineProps<{ showBack?: boolean }>()
const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const searchRef = ref<InstanceType<typeof SearchOverlay>>()

function goBack() { router.back() }
function openSearch() { searchRef.value?.open() }
</script>

<template>
  <div class="min-h-screen flex flex-col relative">
    <!-- Header — tech gradient accent -->
    <header class="h-12 backdrop-blur-xl border-b flex items-center px-4 shrink-0 z-30 sticky top-0" style="background: var(--app-header-bg); border-color: var(--app-border);">
      <button v-if="showBack" @click="goBack" class="mr-2 p-1.5 -ml-1 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors">
        <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2">
        <!-- Logo: geometric radar/crosshair — symbolizing foresight & precision -->
        <div class="relative w-8 h-8 rounded-xl bg-gradient-to-br from-[#1a1a3e] via-[#2d3a8c] to-[#0f172a] flex items-center justify-center shadow-lg shadow-primary/25 overflow-hidden">
          <!-- Outer ring -->
          <svg class="w-7 h-7" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="logoSvg" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#818CF8"/>
                <stop offset="50%" stop-color="#06B6D4"/>
                <stop offset="100%" stop-color="#F59E0B"/>
              </linearGradient>
            </defs>
            <!-- Concentric circles (radar/target) -->
            <circle cx="14" cy="14" r="11" stroke="url(#logoSvg)" stroke-width="1.8" fill="none" opacity="0.9"/>
            <circle cx="14" cy="14" r="6" stroke="url(#logoSvg)" stroke-width="1.2" fill="none" opacity="0.5"/>
            <!-- Rising trend line -->
            <polyline points="6,18 11,13 15,15 22,8" stroke="url(#logoSvg)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <!-- Focal point -->
            <circle cx="22" cy="8" r="2.5" fill="#F59E0B" stroke="#fff" stroke-width="0.8"/>
          </svg>
        </div>
        <span class="font-bold text-base text-gray-900 dark:text-white tracking-wide">远见</span>
        <span class="hidden sm:inline text-[11px] text-gray-400 ml-1.5 font-normal tracking-wider">FarSight</span>
        <div class="hidden sm:flex items-center gap-1 ml-2">
          <span class="glow-dot hidden sm:inline-block"></span>
          <span class="text-[10px] text-gray-300 dark:text-gray-600">LIVE</span>
        </div>
      </div>
      <div class="flex-1" />
      <!-- Desktop nav links -->
      <nav class="hidden md:flex items-center gap-1 mr-2">
        <button v-for="item in [
          { path: '/', label: '发现' },
          { path: '/watchlist', label: '自选' },
          { path: '/analysis', label: '分析' },
          { path: '/news', label: '资讯' },
          { path: '/learn', label: '学习' },
        ]" :key="item.path"
          @click="router.push(item.path)"
          class="px-3 py-1.5 text-xs rounded-lg transition-colors"
          :class="route.path === item.path || (item.path !== '/' && route.path.startsWith(item.path))
            ? 'bg-primary/10 text-primary font-medium'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100/50 dark:hover:bg-gray-800/50'"
        >{{ item.label }}</button>
      </nav>
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

    <main class="flex-1 pb-[4.5rem] md:pb-0">
      <slot />
    </main>

    <SearchOverlay ref="searchRef" />
  </div>
</template>
