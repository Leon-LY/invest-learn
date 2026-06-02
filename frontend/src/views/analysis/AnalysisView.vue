<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const router = useRouter()
const activeTab = ref<'predictions' | 'ai' | 'experts'>('ai')
const realAnalyses = ref<any[]>([])
const lastRefresh = ref('')
let refreshTimer: ReturnType<typeof setInterval> | null = null

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

onMounted(async () => {
  await refreshAnalyses()
  refreshTimer = setInterval(refreshAnalyses, 300000)
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

      <!-- TAB 1: Predictions — real data pending -->
      <div v-if="activeTab === 'predictions'" class="card p-8 text-center">
        <div class="text-3xl mb-3">🔮</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">大佬预测数据暂未接入实时源</p>
        <p class="text-xs text-gray-400 mt-1">我们正在接入专业财经数据源，届时将提供大咖观点追踪</p>
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

      <!-- TAB 3: Expert Overview — real data pending -->
      <div v-if="activeTab === 'experts'" class="card p-8 text-center">
        <div class="text-3xl mb-3">👤</div>
        <p class="text-sm text-gray-500 dark:text-gray-400">大佬追踪数据暂未接入实时源</p>
        <p class="text-xs text-gray-400 mt-1">正在接入权威数据源，将提供基金经理、经济学家实时观点</p>
      </div>
    </div>
  </AppShell>
</template>
