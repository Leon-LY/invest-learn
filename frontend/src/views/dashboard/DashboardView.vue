<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { watchlistApi } from '@/api/watchlist'
import { newsApi } from '@/api/news'
import { marketApi } from '@/api/market'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import type { NewsArticle } from '@/types/market'

const router = useRouter()
const watchlist = ref<any[]>([])
const news = ref<NewsArticle[]>([])
const summary = ref<any>(null)
const greeting = ref('')
let refreshTimer: ReturnType<typeof setInterval> | null = null

function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso); const now = Date.now(); const diff = now - d.getTime()
  const m = Math.floor(diff / 60000); const h = Math.floor(diff / 36000000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  if (h < 24) return `${h}小时前`
  if (h < 168) return `${Math.floor(h/24)}天前`
  return `${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

async function refreshSummary() {
  try {
    const data = await marketApi.getSummary()
    if (data) summary.value = data
  } catch(e) { console.error('Summary load failed:', e) }
}

onMounted(() => {
  const hour = new Date().getHours()
  greeting.value = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'
  // Fire all requests without blocking render
  refreshSummary()
  setTimeout(() => { fetchWatchlist(); fetchNews() }, 100)
  refreshTimer = setInterval(refreshSummary, 180000)
})
onBeforeUnmount(() => { if (refreshTimer) clearInterval(refreshTimer) })

async function fetchWatchlist() { try { watchlist.value = ((await watchlistApi.getList()) as unknown as any[]) } catch(e){} }
async function fetchNews() { try { news.value = ((await newsApi.getList({ page:1, size:4 })) as any).items || [] } catch(e){} }

const dirColors: Record<string,string> = {
  '强势':'bg-up text-white','偏强':'bg-up-bg text-up','震荡':'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  '偏弱':'bg-down-bg text-down','弱势':'bg-down text-white',
}
const indexNames: Record<string,string> = {
  '000001':'上证','399001':'深证','399006':'创业板','000688':'科创50','000300':'沪深300','000905':'中证500',
  '^GSPC':'标普500','^IXIC':'纳指','^HSI':'恒生','.INX':'标普500','.IXIC':'纳指','HSI':'恒生',
}
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-4">
      <!-- Greeting -->
      <div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ greeting }}，Leon 👋</h1>
        <p class="text-xs text-gray-400 mt-0.5 flex items-center gap-1.5">
          <span>远见 · 洞察趋势，智选未来</span>
          <span class="live-dot" />
          <span class="text-[10px] text-gray-300 dark:text-gray-600">LIVE</span>
        </p>
      </div>

      <!-- Market Overview -->
      <div class="card overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/20 border-b border-blue-100/50 dark:border-blue-900/20">
          <div class="flex items-center gap-2">
            <span class="text-sm font-bold text-gray-800 dark:text-gray-100">{{ summary?.date || '--' }}</span>
            <span class="text-xs text-gray-400">{{ summary?.weekday ? '周' + summary.weekday : '' }}</span>
          </div>
          <span v-if="summary?.direction" class="px-2.5 py-1 text-xs font-semibold rounded-full" :class="dirColors[summary.direction]">{{ summary.direction }}</span>
        </div>

        <!-- Index cards -->
        <div class="grid grid-cols-3 sm:grid-cols-6 divide-x divide-gray-100 dark:divide-gray-800/30">
          <div v-for="idx in (summary?.indices?.length ? summary.indices.slice(0,6) : [])" :key="idx.code"
            class="text-center py-3 px-2">
            <div class="text-[11px] text-gray-400 mb-1 truncate">{{ indexNames[idx.code] || idx.name?.slice(0,4) || '-' }}</div>
            <div class="text-base font-bold text-gray-900 dark:text-gray-100 tabular-nums">{{ idx.close ?? '--' }}</div>
            <div v-if="idx.change_pct != null" :class="idx.change_pct>=0?'text-up':'text-down'" class="text-xs font-semibold tabular-nums mt-0.5">
              {{ idx.change_pct>=0?'+':'' }}{{ idx.change_pct.toFixed(1) }}%
            </div>
            <div v-else class="text-xs text-gray-300 mt-0.5">--</div>
          </div>
        </div>

        <!-- Hot sectors -->
        <div v-if="summary?.sectors?.length" class="flex items-center gap-2 px-4 py-2 text-xs border-t border-gray-100 dark:border-gray-800/30 overflow-x-auto no-scrollbar">
          <span class="text-gray-400 shrink-0">🔥</span>
          <span v-for="s in summary.sectors.slice(0,5)" :key="s.name"
            class="shrink-0 px-2 py-0.5 rounded-full text-[11px] font-medium"
            :class="(s.change_pct||0)>=0?'bg-up-bg text-up':'bg-down-bg text-down'"
          >{{ s.name.slice(0,6) }} {{ (s.change_pct||0)>=0?'+':'' }}{{ s.change_pct?.toFixed(1) }}%</span>
        </div>
        <!-- Market advice -->
        <div class="flex items-start gap-2 px-4 py-2.5 bg-gray-50/50 dark:bg-gray-800/30 text-xs border-t border-gray-100 dark:border-gray-800/20">
          <span class="shrink-0 mt-0.5">💡</span>
          <p class="text-gray-600 dark:text-gray-400 leading-relaxed">{{ summary?.advice || '市场数据加载中，请稍后刷新...' }}</p>
        </div>
        <!-- Market stats -->
        <div v-if="summary" class="flex items-center gap-3 px-4 py-2 text-[11px] text-gray-400 border-t border-gray-100 dark:border-gray-800/20">
          <span>📰 近期新闻 {{ summary.hot_news_count || 0 }} 条</span>
          <span>📊 利好 {{ summary.sentiment?.positive || 0 }}</span>
          <span>📉 利空 {{ summary.sentiment?.negative || 0 }}</span>
        </div>
      </div>

      <!-- Tools -->
      <div class="grid grid-cols-4 gap-2">
        <button v-for="t in [
          { icon:'🔬', label:'基金诊断', to:'/diagnosis' },
          { icon:'👤', label:'大佬分析', to:'/analysis' },
          { icon:'📊', label:'组合分析', to:'/portfolio-analysis' },
          { icon:'📚', label:'知识库', to:'/learn' },
        ]" :key="t.to" @click="router.push(t.to)"
          class="card p-3 text-center hover:shadow-md transition-shadow">
          <div class="text-lg mb-0.5">{{ t.icon }}</div>
          <div class="text-[11px] font-medium text-gray-600 dark:text-gray-300">{{ t.label }}</div>
        </button>
      </div>

      <!-- Watchlist + News side by side on desktop -->
      <div class="grid md:grid-cols-2 gap-4">
        <!-- Watchlist -->
        <section>
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400">⭐ 自选</h2>
            <button @click="router.push('/watchlist')" class="text-xs text-primary">管理</button>
          </div>
          <div v-if="!watchlist.length" class="card p-4 text-center text-sm text-gray-400">
            还没有自选 <button @click="router.push('/watchlist')" class="text-primary">去添加 →</button>
          </div>
          <div v-else class="space-y-1.5">
            <div v-for="item in watchlist.slice(0,5)" :key="item.id"
              @click="router.push(`/diagnosis/${item.item_code}`)"
              class="card p-3 flex items-center justify-between cursor-pointer">
              <div class="min-w-0 flex-1">
                <div class="font-medium text-sm dark:text-white truncate">{{ item.alias || item.item_name || item.item_code }}</div>
                <div class="text-xs text-gray-400">{{ item.item_code }}</div>
              </div>
              <ChangeBadge :value="item.quote?.change_pct ?? null" />
            </div>
          </div>
        </section>

        <!-- News -->
        <section>
          <div class="flex items-center justify-between mb-2">
            <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400">📰 资讯</h2>
            <button @click="router.push('/news')" class="text-xs text-primary">更多 →</button>
          </div>
          <div class="space-y-1.5">
            <div v-for="a in news" :key="a.id" @click="router.push(`/news/${a.id}`)"
              class="card p-3 cursor-pointer">
              <div class="text-sm dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
              <div class="flex items-center gap-1.5 mt-1.5 text-xs text-gray-400">
                <span class="shrink-0">{{ formatTime(a.published_at) }}</span>
                <span v-if="a.sentiment==='positive'" class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-up-bg text-up font-medium ml-auto">利好</span>
                <span v-else-if="a.sentiment==='negative'" class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-down-bg text-down font-medium ml-auto">利空</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </AppShell>
</template>
