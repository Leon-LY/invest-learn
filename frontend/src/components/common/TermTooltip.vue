<script setup lang="ts">
import { ref } from 'vue'
import { useAppStore } from '@/stores/app'

defineProps<{ term: string; definition: string }>()

const appStore = useAppStore()
const show = ref(false)
</script>

<template>
  <span class="relative inline-block">
    <span
      class="border-b border-dashed cursor-help"
      :class="appStore.learningMode ? 'border-primary text-primary dark:text-primary/80' : 'border-gray-400'"
      @mouseenter="show = true"
      @mouseleave="show = false"
      @click="show = !show"
    >
      {{ term }}
    </span>
    <Transition name="fade">
      <div
        v-if="show"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs rounded-lg shadow-xl z-50"
      >
        <div class="font-semibold mb-1">{{ term }}</div>
        <div class="leading-relaxed">{{ definition }}</div>
        <div class="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-gray-100" />
      </div>
    </Transition>
  </span>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
