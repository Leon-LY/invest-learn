<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { experts } from '@/mock/experts'
import type { Expert } from '@/mock/experts'

const route = useRoute()
const router = useRouter()
const expert = ref<Expert | null>(null)

onMounted(() => {
  const id = route.params.id as string
  expert.value = experts.find(e => e.id === id) || null
})

const actionColors: Record<string, string> = {
  '加仓': 'border-l-up bg-up-bg/50',
  '建仓': 'border-l-up bg-up-bg/50',
  '减仓': 'border-l-down bg-down-bg/50',
  '清仓': 'border-l-down bg-down-bg/50',
  '调仓': 'border-l-yellow-500 bg-yellow-50 dark:bg-yellow-900/20',
  '持有': 'border-l-gray-400 bg-gray-50 dark:bg-gray-800/50',
}

const actionBadge: Record<string, string> = {
  '加仓': 'bg-up text-white',
  '建仓': 'bg-up text-white',
  '减仓': 'bg-down text-white',
  '清仓': 'bg-down text-white',
  '调仓': 'bg-yellow-500 text-white',
  '持有': 'bg-gray-400 text-white',
}

const directionColor = (d: string) => d === '看多' ? 'text-up bg-up-bg' : d === '看空' ? 'text-down bg-down-bg' : 'text-yellow-600 bg-yellow-50'

function goFund(code: string) { router.push(`/market/${code}`) }
</script>

<template>
  <AppShell showBack>
    <div v-if="!expert" class="text-center py-20 text-gray-400">大佬未找到</div>
    <div v-else class="max-w-3xl mx-auto px-4 py-5 space-y-5">
      <!-- Profile -->
      <div class="card p-5">
        <div class="flex items-start gap-4">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold text-2xl shrink-0">{{ expert.avatar }}</div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ expert.name }}</h1>
              <span class="text-yellow-500">{{ '⭐'.repeat(expert.starRating) }}</span>
            </div>
            <p class="text-sm text-gray-500 mt-0.5">{{ expert.title }}</p>
            <p class="text-sm text-gray-500">{{ expert.company }} · {{ expert.experience }} · 管理{{ expert.aum }}</p>
            <p class="text-xs text-primary font-medium mt-1">{{ expert.style }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-4 leading-relaxed">{{ expert.bio }}</p>
        <!-- Performance -->
        <div class="grid grid-cols-3 gap-3 mt-4">
          <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="text-xs text-gray-400">近1年收益</div>
            <div class="text-lg font-bold" :class="expert.performance.year1 >= 0 ? 'text-up' : 'text-down'">{{ expert.performance.year1 >= 0 ? '+' : '' }}{{ expert.performance.year1 }}%</div>
          </div>
          <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="text-xs text-gray-400">近3年收益</div>
            <div class="text-lg font-bold" :class="expert.performance.year3 >= 0 ? 'text-up' : 'text-down'">{{ expert.performance.year3 >= 0 ? '+' : '' }}{{ expert.performance.year3 }}%</div>
          </div>
          <div class="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <div class="text-xs text-gray-400">近5年收益</div>
            <div class="text-lg font-bold" :class="expert.performance.year5 >= 0 ? 'text-up' : 'text-down'">{{ expert.performance.year5 >= 0 ? '+' : '' }}{{ expert.performance.year5 }}%</div>
          </div>
        </div>
      </div>

      <!-- Recent Operations -->
      <section class="card p-4">
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">📋 近期操作记录</h2>
        <div class="space-y-3">
          <div
            v-for="op in expert.recentOperations" :key="op.date + op.fundCode"
            class="border-l-4 rounded-r-lg p-3"
            :class="actionColors[op.action] || 'border-l-gray-300'"
          >
            <div class="flex items-center justify-between mb-1">
              <div class="flex items-center gap-2">
                <span class="text-xs px-2 py-0.5 rounded-full text-white font-medium" :class="actionBadge[op.action]">{{ op.action }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-white cursor-pointer hover:text-primary" @click="goFund(op.fundCode)">{{ op.fundName }}</span>
                <span class="text-xs text-gray-400">{{ op.fundCode }}</span>
              </div>
              <span class="text-xs text-gray-400">{{ op.date }}</span>
            </div>
            <div class="flex items-center gap-2 text-xs text-gray-500">
              <span class="text-gray-700 dark:text-gray-300 font-medium">金额：{{ op.amount }}</span>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">💬 {{ op.reason }}</p>
          </div>
        </div>
      </section>

      <!-- Predictions -->
      <section class="card p-4">
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3">🔮 行情预测</h2>
        <div class="space-y-3">
          <div v-for="p in expert.predictions" :key="p.id" class="border border-gray-100 dark:border-gray-800 rounded-lg p-3">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs px-2 py-0.5 rounded-full font-medium" :class="directionColor(p.direction)">{{ p.direction }}</span>
              <span class="text-xs text-gray-400">{{ p.category }}</span>
              <span class="text-xs text-gray-400">信心 {{ p.confidence }}%</span>
            </div>
            <h4 class="font-semibold text-sm text-gray-900 dark:text-white mb-1">{{ p.title }}</h4>
            <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ p.content }}</p>
            <div class="flex gap-1.5 mt-2">
              <span v-for="t in p.tags" :key="t" class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">{{ t }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </AppShell>
</template>
