<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const router = useRouter()
const activeTab = ref<'predictions' | 'ai' | 'experts'>('ai')
const realAnalyses = ref<any[]>([])
const predictions = ref<any[]>([])
const experts = ref<any[]>([])
const lastRefresh = ref('')
const predRefresh = ref('')
let refreshTimer: ReturnType<typeof setInterval> | null = null

const directionColor: Record<string, string> = {
  '看多': 'text-up bg-up-bg', '看空': 'text-down bg-down-bg',
  '震荡': 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/30',
}

const impactColors: Record<string, string> = {
  '重大利好': 'bg-up text-white', '利好': 'bg-up-bg text-up',
  '中性': 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
  '利空': 'bg-down-bg text-down', '重大利空': 'bg-down text-white',
}

async function refreshAnalyses() {
  try {
    realAnalyses.value = (await newsApi.getAnalyses(10)) as unknown as any[]
    lastRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch(e) {}
}

async function refreshPredictions() {
  try {
    predictions.value = (await newsApi.getExpertPredictions(6)) as unknown as any[]
    predRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch(e) {}
}
async function refreshExperts() {
  try { experts.value = (await newsApi.getExpertTracker()) as unknown as any[] } catch(e) {}
}

onMounted(async () => {
  await Promise.all([refreshAnalyses(), refreshPredictions(), refreshExperts()])
  refreshTimer = setInterval(() => { refreshAnalyses(); refreshPredictions(); refreshExperts() }, 300000)
})
onBeforeUnmount(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-5 space-y-5">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">智能分析</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">AI驱动的基金市场分析</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
        <button v-for="t in [{ k: 'predictions', l: '📈 大佬预测' }, { k: 'ai', l: '🤖 AI分析' }, { k: 'experts', l: '👤 大佬追踪' }]" :key="t.k"
          @click="activeTab = t.k as any"
          class="flex-1 py-2 text-sm font-medium rounded-lg transition-all"
          :class="activeTab === t.k ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'"
        >{{ t.l }}</button>
      </div>

      <!-- TAB 1: Predictions — per-expert cards with detail links -->
      <div v-if="activeTab === 'predictions'" class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">🤖 6位大佬 × 多角度分析（{{ predictions.length }}位）{{ predRefresh ? '· ' + predRefresh : '' }}</span>
          <button @click="refreshPredictions()" class="text-xs text-primary hover:underline">刷新</button>
        </div>
        <div v-if="!predictions.length" class="card p-6 text-center">
          <div class="text-2xl mb-2">{{ predRefresh ? '📭' : '⏳' }}</div>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ predRefresh ? '暂无数据' : '正在生成大佬分析...' }}</p>
        </div>
        <div v-for="p in predictions" :key="p.id"
          @click="router.push(`/analysis/expert-prediction/${p.id}`)"
          class="card p-4 cursor-pointer hover:shadow-md">
          <div class="flex items-center gap-2 mb-2">
            <span class="font-semibold text-sm dark:text-white">{{ p.expert }}</span>
            <span class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">{{ p.prefers }}</span>
            <span class="text-xs text-gray-400 ml-auto">{{ p.prediction_count }}条分析 · 信心 {{ p.confidence }}%</span>
          </div>
          <h3 class="font-semibold text-sm text-gray-900 dark:text-white mb-1">「{{ p.latest_title }}」</h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 leading-relaxed mb-2">{{ p.latest_content }}</p>
          <div class="flex items-center gap-2 text-xs">
            <span class="text-primary">查看全部 {{ p.prediction_count }} 条分析 →</span>
            <div class="flex gap-1 ml-auto">
              <span v-for="t in p.tags?.slice(0,2)" :key="t" class="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-500">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: AI Analysis — real DeepSeek data -->
      <div v-if="activeTab === 'ai'" class="space-y-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-xs text-gray-400">🤖 DeepSeek 实时分析（{{ realAnalyses.length }}条）{{ lastRefresh ? '· ' + lastRefresh : '' }}</span>
          <button @click="refreshAnalyses()" class="text-xs text-primary hover:underline">刷新</button>
        </div>

        <div v-if="!realAnalyses.length" class="card p-6 text-center">
          <div class="text-2xl mb-2">{{ lastRefresh ? '📭' : '⏳' }}</div>
          <p class="text-sm text-gray-500 dark:text-gray-400">{{ lastRefresh ? '暂无分析数据，请稍后刷新' : '正在加载...' }}</p>
          <p class="text-xs text-gray-400 mt-1">AI分析由DeepSeek自动生成，每5分钟处理新文章</p>
        </div>

        <div v-for="a in realAnalyses" :key="'r'+a.id"
          @click="router.push(`/news/${a.news_id}`)"
          class="card p-4 cursor-pointer hover:shadow-md border-l-4 border-l-primary">
          <div class="flex items-center gap-2 mb-2">
            <span class="px-2 py-0.5 text-xs rounded-full font-medium" :class="impactColors[a.impact_level]">{{ a.impact_level }}</span>
            <span class="text-xs text-gray-400">评分 {{ a.impact_score }}</span>
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

      <!-- TAB 3: Expert Tracker — real scraped data -->
      <div v-if="activeTab === 'experts'" class="space-y-3">
        <div class="text-xs text-gray-400">📊 实时追踪（AKShare/天天基金/公开数据，每2小时更新）</div>
        <div v-if="!experts.length" class="card p-6 text-center text-xs text-gray-400">正在加载大佬数据...</div>
        <div v-for="e in experts" :key="e.name"
          class="card p-4">
          <div class="flex items-start gap-3">
            <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold shrink-0">{{ e.name[0] }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="font-semibold text-sm dark:text-white">{{ e.name }}</h3>
                <span class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary dark:text-primary border border-primary/20">{{ e.type }}</span>
                <span class="text-xs text-gray-400">{{ e.title }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1 leading-relaxed">{{ e.bio }}</p>
              <!-- Fund manager specific data -->
              <div v-if="e.fund_code" class="mt-2 flex items-center gap-3 text-xs flex-wrap">
                <span class="text-gray-500">📊 {{ e.fund_name }}</span>
                <span v-if="e.performance?.latest_nav" class="font-mono text-gray-600 dark:text-gray-300">净值 {{ e.performance.latest_nav.toFixed(4) }}</span>
                <span v-if="e.performance?.year1 != null" :class="e.performance.year1>=0?'text-up':'text-down'" class="font-medium">
                  近1年 {{ e.performance.year1>=0?'+':'' }}{{ e.performance.year1 }}%
                </span>
                <span v-if="e.performance?.year3 != null" :class="e.performance.year3>=0?'text-up':'text-down'" class="font-medium">
                  近3年 {{ e.performance.year3>=0?'+':'' }}{{ e.performance.year3 }}%
                </span>
              </div>
              <div class="flex items-center gap-2 mt-2 text-[10px] text-gray-400">
                <span>📡 {{ e.source || '公开资料' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
