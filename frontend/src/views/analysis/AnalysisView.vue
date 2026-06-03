<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'
import PortfolioInline from './PortfolioInline.vue'
import VoiceInline from './VoiceInline.vue'

const router = useRouter()
const activeTab = ref<'predictions' | 'experts' | 'portfolio' | 'voice'>('predictions')
const predictions = ref<any[]>([])
const experts = ref<any[]>([])
const predRefresh = ref('')
let refreshTimer: ReturnType<typeof setInterval> | null = null

async function refreshPredictions() {
  try {
    predictions.value = (await newsApi.getExpertPredictions(6)) as unknown as any[]
    predRefresh.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } catch(e) {}
}
async function refreshExperts() {
  try { experts.value = (await newsApi.getExpertTracker()) as unknown as any[] } catch(e) {}
}

onMounted(() => {
  refreshPredictions(); refreshExperts()
  refreshTimer = setInterval(() => { refreshPredictions(); refreshExperts() }, 300000)
})
onBeforeUnmount(() => { if (refreshTimer) clearInterval(refreshTimer) })
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-5 space-y-5">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">智能分析</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">大佬观点追踪 & 投资组合参考</p>
      </div>

      <!-- Tab Switcher -->
      <div class="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 overflow-x-auto">
        <button v-for="t in [
          { k: 'predictions', l: '📈 大佬预测' },
          { k: 'experts', l: '👤 大佬追踪' },
          { k: 'portfolio', l: '📊 组合分析' },
          { k: 'voice', l: '💬 市场声音' },
        ]" :key="t.k" @click="activeTab = t.k as any"
          class="flex-1 py-2 text-sm font-medium rounded-lg transition-all whitespace-nowrap px-2"
          :class="activeTab === t.k ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm' : 'text-gray-500'"
        >{{ t.l }}</button>
      </div>

      <!-- Tab Content with smooth transition -->
      <Transition name="tab-fade" mode="out-in">
        <!-- TAB 1: Predictions -->
        <div v-if="activeTab === 'predictions'" key="predictions" class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">🤖 6位大佬 × 多角度分析（{{ predictions.length }}位）{{ predRefresh ? '· ' + predRefresh : '' }}</span>
          <button @click="refreshPredictions()" class="text-xs text-primary hover:underline">刷新</button>
        </div>
        <div v-if="!predictions.length" class="card p-6 text-center">
          <div class="text-2xl mb-2">⏳</div>
          <p class="text-sm text-gray-500 dark:text-gray-400">正在加载大佬分析...</p>
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
          <div class="flex items-center justify-between">
            <span class="text-xs text-primary">查看全部 {{ p.prediction_count }} 条分析 →</span>
            <div class="flex gap-1">
              <span v-for="t in p.tags?.slice(0,2)" :key="t" class="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 rounded-full text-gray-500">{{ t }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 2: Expert Tracker -->
      <div v-if="activeTab === 'experts'" key="experts" class="space-y-3">
        <div class="text-xs text-gray-400">📊 实时追踪（AKShare/天天基金，每2小时更新）</div>
        <div v-if="!experts.length" class="card p-6 text-center text-xs text-gray-400">正在加载大佬数据...</div>
        <div v-for="e in experts" :key="e.name"
          @click="router.push(`/analysis/expert/${e.id || e.name}`)"
          class="card p-4 cursor-pointer hover:shadow-md">
          <div class="flex items-start gap-3">
            <div class="w-11 h-11 rounded-xl bg-gradient-to-br from-primary to-cyan flex items-center justify-center text-white font-bold shrink-0">{{ e.name[0] }}</div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <h3 class="font-semibold text-sm dark:text-white">{{ e.name }}</h3>
                <span class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">{{ e.type }}</span>
                <span class="text-xs text-gray-400">{{ e.title }}</span>
              </div>
              <p class="text-xs text-gray-400 mt-1 line-clamp-1">{{ e.bio }}</p>
              <div v-if="e.fund_code" class="mt-2 flex items-center gap-3 text-xs flex-wrap">
                <span class="text-gray-500">📊 {{ e.fund_name }}（{{ e.fund_code }}）</span>
                <span v-if="e.performance?.year1 != null" :class="e.performance.year1>=0?'text-up':'text-down'" class="font-medium">近1年 {{ e.performance.year1>=0?'+':'' }}{{ e.performance.year1 }}%</span>
              </div>
              <div class="flex items-center justify-between mt-2">
                <span class="text-[10px] text-gray-400">📡 {{ e.source || '公开资料' }}</span>
                <span class="text-xs text-primary">查看详情 →</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: Portfolio Analysis -->
      <div v-if="activeTab === 'portfolio'" key="portfolio" class="space-y-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">输入你的基金持仓，AI 分析配置是否合理</p>
        <PortfolioInline />
      </div>

      <!-- TAB 4: Market Voice -->
      <div v-if="activeTab === 'voice'" key="voice" class="space-y-4">
        <p class="text-sm text-gray-500 dark:text-gray-400">录入手动看到的观点或截图</p>
        <VoiceInline />
      </div>
      </Transition>
    </div>
  </AppShell>
</template>
