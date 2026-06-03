<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { generateDailyBrief } from '@/mock/data'
import type { DailyBrief } from '@/mock/data'

const brief = ref<DailyBrief | null>(null)

onMounted(() => {
  brief.value = generateDailyBrief()
})

const dirColors: Record<string, string> = {
  '强势': 'bg-up text-white', '偏强': 'bg-up-bg text-up', '震荡': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  '偏弱': 'bg-down-bg text-down', '弱势': 'bg-down text-white',
}
</script>

<template>
  <div v-if="brief" class="card p-4 bg-gradient-to-br from-primary-light to-cyan/10 dark:from-primary/10 dark:to-cyan/10 border-primary/10">
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2">
        <span class="text-sm font-bold text-gray-900 dark:text-white">📅 {{ brief.date }} {{ brief.weekday }}</span>
        <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="dirColors[brief.marketDirection]">{{ brief.marketDirection }}</span>
      </div>
    </div>

    <!-- Key info rows -->
    <div class="space-y-2 text-sm">
      <div class="flex items-start gap-2">
        <span class="shrink-0">📈</span>
        <span class="text-gray-700 dark:text-gray-300">{{ brief.marketSummary }}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="shrink-0">🔥</span>
        <span class="text-gray-700 dark:text-gray-300">资金热点：{{ brief.hotInflow }}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="shrink-0">📰</span>
        <span class="text-gray-700 dark:text-gray-300">{{ brief.importantNews }}</span>
      </div>
      <div class="flex items-center gap-2">
        <span class="shrink-0">💡</span>
        <span class="text-gray-700 dark:text-gray-300 font-medium">{{ brief.todayAdvice }}</span>
      </div>
    </div>

    <!-- Learning tip -->
    <div class="mt-3 pt-3 border-t border-primary/20">
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">{{ brief.learningTip }}</p>
    </div>
  </div>
</template>
