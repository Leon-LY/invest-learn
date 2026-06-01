<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { mockDiagnoses } from '@/mock/data'
import { mockFunds } from '@/mock/data'
import { watchlistApi } from '@/api/watchlist'
import type { FundDiagnosis } from '@/mock/data'

const route = useRoute()
const router = useRouter()
const code = (route.params.code as string) || ''
const searchQuery = ref(code)
const diagnosis = ref<FundDiagnosis | null>(mockDiagnoses[code] || null)
const loading = ref(false)

function search() {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push(`/diagnosis/${q}`)
  diagnosis.value = mockDiagnoses[q] || generateGenericDiagnosis(q)
}

function generateGenericDiagnosis(c: string): FundDiagnosis {
  const fund = mockFunds[c]
  const name = fund?.info?.name || c
  return {
    code: c, name, overallScore: 70, verdict: '需进一步分析', verdictColor: 'text-yellow-600',
    summary: `暂无${name}的深度诊断数据。以下为基于基金类型的通用分析，仅供参考。建议通过天天基金等平台查看详细数据。`,
    items: [
      { label: '历史业绩', score: 30, maxScore: 50, comment: '暂无足够数据，建议查看近3年完整业绩', icon: '📈' },
      { label: '风险控制', score: 12, maxScore: 20, comment: '可根据基金类型评估风险水平', icon: '📉' },
      { label: '基金经理', score: 10, maxScore: 15, comment: '请查看基金经理从业年限和历史回报', icon: '👤' },
      { label: '费率水平', score: 5, maxScore: 10, comment: '请查看基金公告中的费率信息', icon: '💰' },
      { label: '当前时机', score: 3, maxScore: 5, comment: '请结合当前市场估值水平判断', icon: '⏰' },
    ],
    pros: ['可通过定投降低风险'],
    cons: ['缺乏深度数据，建议进一步研究'],
    suggestion: '建议先少量定投观察，同时学习基金分析知识。',
  }
}

const scoreBarWidth = (score: number, max: number) => `${(score / max) * 100}%`

const verdictBg: Record<string, string> = {
  'text-green-600': 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800',
  'text-blue-600': 'bg-blue-50 border-blue-200 dark:bg-blue-900/20 dark:border-blue-800',
  'text-yellow-600': 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-800',
}

async function addWatchlist() {
  if (!diagnosis.value) return
  try {
    await watchlistApi.add({ item_type: 'fund', item_code: code, item_name: diagnosis.value.name })
    alert('已添加到自选')
  } catch (e) { /* might already exist */ }
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <!-- Search bar -->
      <div class="flex gap-2">
        <input
          v-model="searchQuery"
          @keyup.enter="search"
          placeholder="输入基金代码，如 005827"
          class="flex-1 px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button @click="search" class="px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-xl hover:bg-primary-dark transition-colors">诊断</button>
      </div>

      <!-- Quick select -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button v-for="c in ['005827','163406','510300','000198']" :key="c"
          @click="searchQuery = c; router.push(`/diagnosis/${c}`); diagnosis = mockDiagnoses[c]"
          class="shrink-0 px-3 py-1.5 text-xs rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary hover:text-primary transition-colors"
        >{{ ({ '005827': '易方达蓝筹', '163406': '兴全合润', '510300': '沪深300ETF', '000198': '余额宝' })[c] }}</button>
      </div>

      <!-- Result -->
      <div v-if="diagnosis" class="space-y-4">
        <!-- Overall Score Card -->
        <div class="card p-5 text-center" :class="verdictBg[diagnosis.verdictColor] || 'bg-gray-50 dark:bg-gray-800'">
          <div class="text-sm text-gray-500 mb-1">{{ diagnosis.name }}（{{ diagnosis.code }}）</div>
          <div class="text-5xl font-bold text-gray-900 dark:text-white mb-2">{{ diagnosis.overallScore }}<span class="text-lg text-gray-400 font-normal">/100</span></div>
          <div class="text-lg font-bold" :class="diagnosis.verdictColor">{{ diagnosis.verdict }}</div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-2 leading-relaxed">{{ diagnosis.summary }}</p>
          <button @click="addWatchlist" class="mt-3 px-4 py-1.5 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors">⭐ 加自选</button>
        </div>

        <!-- Score Breakdown -->
        <div class="card p-4 space-y-3">
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wide">诊断明细</h3>
          <div v-for="item in diagnosis.items" :key="item.label" class="space-y-1">
            <div class="flex items-center justify-between text-sm">
              <span class="text-gray-700 dark:text-gray-300">{{ item.icon }} {{ item.label }}</span>
              <span class="font-medium text-gray-900 dark:text-white">{{ item.score }}/{{ item.maxScore }}</span>
            </div>
            <div class="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :class="item.score / item.maxScore >= 0.7 ? 'bg-green-500' : item.score / item.maxScore >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'" :style="{ width: scoreBarWidth(item.score, item.maxScore) }" />
            </div>
            <p class="text-xs text-gray-400">{{ item.comment }}</p>
          </div>
        </div>

        <!-- Pros & Cons -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="card p-4">
            <h3 class="text-sm font-semibold text-green-600 mb-2">✅ 优点</h3>
            <ul class="space-y-1.5">
              <li v-for="p in diagnosis.pros" :key="p" class="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-1.5">
                <span class="text-green-500 shrink-0">•</span> {{ p }}
              </li>
            </ul>
          </div>
          <div class="card p-4">
            <h3 class="text-sm font-semibold text-red-500 mb-2">⚠️ 风险</h3>
            <ul class="space-y-1.5">
              <li v-for="c in diagnosis.cons" :key="c" class="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-1.5">
                <span class="text-red-400 shrink-0">•</span> {{ c }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Suggestion -->
        <div class="card p-4 bg-gradient-to-r from-primary-light to-purple-50 dark:from-primary/10 dark:to-purple-900/20">
          <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">💡 Leon 的建议</h3>
          <p class="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">{{ diagnosis.suggestion }}</p>
        </div>
      </div>
    </div>
  </AppShell>
</template>
