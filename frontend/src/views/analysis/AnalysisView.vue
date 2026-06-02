<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { experts, aiAnalyses } from '@/mock/experts'
import { newsApi } from '@/api/news'
import type { Expert, AIAnalysis } from '@/mock/experts'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const activeTab = ref<'predictions' | 'ai' | 'experts'>('predictions')
const realAnalyses = ref<any[]>([])
let refreshTimer: ReturnType<typeof setInterval> | null = null

// Collect all predictions from all experts
const allPredictions = experts.flatMap(e => e.predictions.map(p => ({ ...p, expertName: e.name, expertId: e.id, expertTitle: e.title })))
  .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())

const directionColor = (d: string) => d === '看多' ? 'text-up bg-up-bg' : d === '看空' ? 'text-down bg-down-bg' : 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/30'
const confidenceColor = (c: number) => c >= 80 ? 'text-green-600' : c >= 60 ? 'text-yellow-600' : 'text-red-500'
const riskColor = (r: string) => r === '低' ? 'text-down' : r === '中低' ? 'text-green-500' : r === '中' ? 'text-yellow-600' : r === '中高' ? 'text-orange-500' : 'text-up'
const impactColors: Record<string, string> = {
  '重大利好': 'bg-up text-white', '利好': 'bg-up-bg text-up',
  '中性': 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
  '利空': 'bg-down-bg text-down', '重大利空': 'bg-down text-white',
}

function goExpert(id: string) { router.push(`/analysis/expert/${id}`) }

async function refreshAnalyses() {
  try { realAnalyses.value = (await newsApi.getAnalyses(10)) as unknown as any[] } catch(e) {}
}

onMounted(() => {
  refreshAnalyses()
  refreshTimer = setInterval(refreshAnalyses, 300000) // every 5 min
})
onBeforeUnmount(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-5 space-y-5">
      <!-- Header -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">智能分析</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">AI驱动的基金市场分析 & 大佬观点追踪</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
        <button
          v-for="t in [{ k: 'predictions', l: '📈 大佬预测' }, { k: 'ai', l: '🤖 AI分析' }, { k: 'experts', l: '👤 大佬追踪' }]" :key="t.k"
          @click="activeTab = t.k as any"
          class="flex-1 py-2 text-sm font-medium rounded-lg transition-all"
          :class="activeTab === t.k ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'"
        >{{ t.l }}</button>
      </div>

      <!-- ===== TAB 1: Expert Predictions ===== -->
      <div v-if="activeTab === 'predictions'" class="space-y-4">
        <div
          v-for="p in allPredictions" :key="p.id"
          class="card p-4 cursor-pointer hover:shadow-md transition-shadow"
          @click="goExpert(p.expertId)"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 text-xs font-medium rounded-full" :class="directionColor(p.direction)">
              {{ p.direction }}
            </span>
            <span class="text-xs text-gray-400">{{ p.category }}</span>
            <span class="text-xs" :class="confidenceColor(p.confidence)">信心 {{ p.confidence }}%</span>
          </div>
          <h3 class="font-semibold text-sm text-gray-900 dark:text-white mb-1.5">{{ p.title }}</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-3 leading-relaxed">{{ p.content }}</p>
          <div class="flex items-center gap-2 mt-3 text-xs text-gray-400 flex-nowrap overflow-hidden">
            <div class="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold shrink-0">{{ experts.find(e => e.id === p.expertId)?.avatar }}</div>
            <span class="font-medium text-gray-700 dark:text-gray-300 shrink-0">{{ p.expertName }}</span>
            <span class="shrink-0">·</span>
            <span class="truncate">{{ p.expertTitle }}</span>
            <span class="shrink-0">·</span>
            <span class="shrink-0">{{ p.date }}</span>
          </div>
          <div v-if="p.relatedFunds.length" class="flex gap-1.5 mt-2">
            <span v-for="f in p.relatedFunds" :key="f" class="text-xs px-2 py-0.5 bg-primary-light dark:bg-primary/20 text-primary rounded-full">{{ f }}</span>
          </div>
        </div>
      </div>

      <!-- ===== TAB 2: AI Analysis ===== -->
      <div v-if="activeTab === 'ai'" class="space-y-4">
        <!-- Real analyses from DeepSeek -->
        <div v-if="realAnalyses.length" class="mb-2">
          <div class="text-xs text-gray-400 mb-2">🤖 DeepSeek 实时分析（{{ realAnalyses.length }}条）</div>
          <div v-for="a in realAnalyses.slice(0,6)" :key="'r'+a.id"
            @click="router.push(`/news/${a.news_id}`)"
            class="card p-4 cursor-pointer hover:shadow-md mb-3 border-l-4 border-l-primary">
            <div class="flex items-center gap-2 mb-2">
              <span class="px-2 py-0.5 text-xs rounded-full font-medium" :class="impactColors[a.impact_level]">{{ a.impact_level }}</span>
              <span class="text-xs text-gray-400">影响评分 {{ a.impact_score }}</span>
              <span class="text-xs text-gray-400 ml-auto">{{ a.generated_by === 'deepseek' ? '🤖 DeepSeek' : '📋 模板' }}</span>
            </div>
            <h3 class="font-semibold text-sm dark:text-white mb-1.5 line-clamp-1">{{ a.title }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">{{ a.short_term }}</p>
            <div class="flex items-start gap-2 pt-2 border-t border-gray-100 dark:border-gray-800">
              <span class="text-sm shrink-0">💡</span>
              <p class="text-sm text-gray-700 dark:text-gray-300 font-medium">{{ a.action_advice }}</p>
            </div>
          </div>
        </div>

        <!-- Mock AI analyses fallback -->
        <div class="text-xs text-gray-400 mb-2">📊 策略分析报告</div>
        <div
          v-for="a in aiAnalyses" :key="a.id"
          class="card p-4"
          :class="{ 'border-l-4 border-l-up': a.type === 'risk_alert', 'border-l-4 border-l-primary': a.type === 'market_outlook', 'border-l-4 border-l-accent': a.type === 'opportunity' }"
        >
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs px-2 py-0.5 rounded-full font-medium"
              :class="{
                'bg-blue-50 text-blue-600 dark:bg-blue-900/30': a.type === 'market_outlook',
                'bg-purple-50 text-purple-600 dark:bg-purple-900/30': a.type === 'news_impact',
                'bg-teal-50 text-teal-600 dark:bg-teal-900/30': a.type === 'sector_analysis',
                'bg-up-bg text-up': a.type === 'risk_alert',
                'bg-accent-light text-accent': a.type === 'opportunity',
              }"
            >
              {{ { market_outlook: '市场展望', news_impact: '事件解读', sector_analysis: '板块深度', risk_alert: '风险预警', opportunity: '机会挖掘' }[a.type] }}
            </span>
            <span class="text-xs text-gray-400">{{ a.date }}</span>
            <span class="text-xs" :class="confidenceColor(a.confidence)">置信度 {{ a.confidence }}%</span>
            <span class="text-xs" :class="riskColor(a.riskLevel)">风险{{ a.riskLevel }}</span>
          </div>
          <h3 class="font-semibold text-sm text-gray-900 dark:text-white mb-2">{{ a.title }}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed mb-3">{{ a.summary }}</p>

          <div class="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3 text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-wrap">{{ a.detail }}</div>

          <div class="flex flex-wrap gap-1.5 mt-3">
            <span v-for="c in a.affectedCategories" :key="c" class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">{{ c }}</span>
          </div>

          <div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800 flex items-start gap-2">
            <span class="text-sm shrink-0">💡</span>
            <p class="text-sm text-gray-700 dark:text-gray-300 font-medium">{{ a.actionSuggestion }}</p>
          </div>
        </div>
      </div>

      <!-- ===== TAB 3: Expert Overview ===== -->
      <div v-if="activeTab === 'experts'" class="space-y-3">
        <div
          v-for="e in experts" :key="e.id"
          @click="goExpert(e.id)"
          class="card p-4 cursor-pointer hover:shadow-md transition-shadow"
        >
          <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold text-lg shrink-0">{{ e.avatar }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-nowrap">
                <h3 class="font-semibold text-sm text-gray-900 dark:text-white shrink-0">{{ e.name }}</h3>
                <span class="text-yellow-500 text-xs shrink-0">{{ '⭐'.repeat(e.starRating) }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-0.5 truncate">{{ e.title }} · {{ e.company }}</p>
              <div class="flex flex-wrap gap-1.5 mt-2">
                <span class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">规模 {{ e.aum }}</span>
                <span class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">{{ e.experience }}</span>
                <span class="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-600 dark:text-gray-400">{{ e.followers > 10000 ? (e.followers / 10000).toFixed(0) + '万' : e.followers }} 关注</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 line-clamp-2">{{ e.bio.slice(0, 100) }}...</p>
              <!-- Performance preview -->
              <div class="flex gap-3 mt-2 text-xs">
                <span :class="e.performance.year1 >= 0 ? 'text-up' : 'text-down'">近1年 {{ e.performance.year1 >= 0 ? '+' : '' }}{{ e.performance.year1 }}%</span>
                <span :class="e.performance.year3 >= 0 ? 'text-up' : 'text-down'">近3年 {{ e.performance.year3 >= 0 ? '+' : '' }}{{ e.performance.year3 }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
