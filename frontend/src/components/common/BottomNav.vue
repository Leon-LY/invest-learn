<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'

defineProps<{
  items: Array<{ path: string; label: string; icon: string }>
}>()

const router = useRouter()
const route = useRoute()

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

const iconMap: Record<string, string> = {
  dashboard: 'M4 6h16M4 12h16M4 18h7',
  star: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z',
  news: 'M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z',
  book: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253',
  chart: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  user: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
}

function navigate(path: string) {
  router.push(path)
}
</script>

<template>
  <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-2xl border-t border-gray-200/30 dark:border-gray-800/30 z-40 safe-area-bottom shadow-[0_-8px_32px_rgba(0,0,0,0.04)]">
    <div class="flex justify-around h-14 relative">
      <!-- Animated gradient indicator pill -->
      <div class="absolute top-1.5 h-1 rounded-full bg-gradient-to-r from-primary via-purple-400 to-cyan-400 transition-all duration-400 ease-out shadow-[0_0_8px_rgba(91,108,240,0.5)]"
        :style="{
          width: `${88 / items.length}%`,
          left: `calc(${(100 / items.length) * items.findIndex(i => isActive(i.path))}% + ${44 / items.length}%)`,
          transform: 'translateX(-50%)',
          opacity: items.some(i => isActive(i.path)) ? 1 : 0
        }" />
      <button
        v-for="item in items" :key="item.path"
        @click="navigate(item.path)"
        class="flex flex-col items-center justify-center flex-1 min-w-0 text-xs transition-all duration-300 relative group"
        :class="isActive(item.path) ? 'text-primary dark:text-indigo-400' : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'"
      >
        <div class="relative">
          <svg class="w-5 h-5 mb-0.5 transition-all duration-300"
            :class="isActive(item.path) ? 'scale-110 drop-shadow-[0_0_8px_rgba(91,108,240,0.4)]' : 'group-hover:scale-105'"
            fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" :d="iconMap[item.icon]"/>
          </svg>
          <!-- Active ring pulse -->
          <span v-if="isActive(item.path)" class="absolute inset-0 rounded-full animate-ping bg-primary/20" style="animation-duration:1.5s" />
        </div>
        <span :class="isActive(item.path) ? 'font-semibold' : ''">{{ item.label }}</span>
      </button>
    </div>
  </nav>
</template>
