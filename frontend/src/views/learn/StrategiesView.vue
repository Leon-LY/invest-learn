<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { learnApi } from '@/api/learn'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const strategies = ref<any[]>([])
const loading = ref(true)

const difficultyLabel: Record<string, string> = { beginner: '入门', intermediate: '进阶', advanced: '高级' }
const riskLabel: Record<string, string> = { low: '低风险', medium: '中风险', high: '高风险' }
const riskColor: Record<string, string> = { low: 'text-market-down', medium: 'text-yellow-500', high: 'text-market-up' }

onMounted(async () => {
  try {
    strategies.value = (await learnApi.getStrategies()) as unknown as any[]
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-4 space-y-4">
      <h1 class="text-xl font-bold dark:text-white">投资策略库</h1>
      <p class="text-sm text-gray-400">了解不同的投资策略，找到适合自己的方式</p>

      <div v-if="loading" class="space-y-2">
        <div v-for="i in 5" :key="i" class="animate-pulse h-24 bg-gray-100 dark:bg-gray-800 rounded-xl" />
      </div>
      <EmptyState v-else-if="!strategies.length" message="暂无策略" />
      <div v-else class="space-y-3">
        <div
          v-for="s in strategies" :key="s.id"
          @click="router.push(`/learn/strategies/${s.slug}`)"
          class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-sm transition-shadow"
        >
          <div class="flex items-center gap-2 mb-2">
            <h3 class="font-semibold text-sm dark:text-white">{{ s.name }}</h3>
            <span class="px-1.5 py-0.5 text-xs bg-purple-50 dark:bg-purple-900/30 text-purple-600 rounded">{{ difficultyLabel[s.difficulty] || s.difficulty }}</span>
            <span :class="riskColor[s.risk_level]" class="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded">{{ riskLabel[s.risk_level] || s.risk_level }}</span>
          </div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">{{ s.summary }}</p>
          <div class="text-xs text-gray-400">适合：{{ s.suitable_for }}</div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
