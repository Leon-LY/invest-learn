<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import SearchOverlay from '@/components/market/SearchOverlay.vue'

defineProps<{ showBack?: boolean }>()
const router = useRouter()
const appStore = useAppStore()
const searchRef = ref<InstanceType<typeof SearchOverlay>>()

function goBack() { router.back() }
function openSearch() { searchRef.value?.open() }
</script>

<template>
  <div class="min-h-screen flex flex-col relative">
    <!-- Header — tech gradient accent -->
    <header class="h-12 bg-white/80 dark:bg-[#1A1B2E]/80 backdrop-blur-xl border-b border-gray-100/50 dark:border-gray-800/50 flex items-center px-4 shrink-0 z-30 sticky top-0">
      <button v-if="showBack" @click="goBack" class="mr-2 p-1.5 -ml-1 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 rounded-lg transition-colors">
        <svg class="w-5 h-5 text-gray-600 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <div class="flex items-center gap-2">
        <!-- Logo: geometric compass + trend -->
        <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-primary via-indigo-500 to-cyan-400 flex items-center justify-center glow-ring shadow-lg shadow-primary/20">
          <svg class="w-[18px] h-[18px] text-white" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9" />
            <polyline points="7 13 10.5 9 13.5 11.5 17 7" />
            <circle cx="17" cy="7" r="1.5" fill="currentColor" stroke="none" />
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

    <main class="flex-1 overflow-y-auto pb-[4.5rem] md:pb-0">
      <slot />
    </main>

    <SearchOverlay ref="searchRef" />
  </div>
</template>
