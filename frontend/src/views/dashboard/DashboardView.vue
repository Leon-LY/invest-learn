<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { useMarketStore } from '@/stores/market'
import { useAppStore } from '@/stores/app'
import { watchlistApi } from '@/api/watchlist'
import { newsApi } from '@/api/news'
import PriceText from '@/components/common/PriceText.vue'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import DataFreshness from '@/components/common/DataFreshness.vue'
import SkeletonCard from '@/components/common/SkeletonCard.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LineChart from '@/components/charts/LineChart.vue'
import type { IndexInfo, WatchlistItem, NewsArticle } from '@/types/market'

const router = useRouter()
const marketStore = useMarketStore()
const appStore = useAppStore()

const watchlist = ref<WatchlistItem[]>([])
const news = ref<NewsArticle[]>([])
const lastFetched = ref(Date.now())
const loading = ref(true)

onMounted(async () => {
  await Promise.all([
    marketStore.fetchAllDashboardData(),
    fetchWatchlist(),
    fetchNews(),
  ])
  lastFetched.value = Date.now()
  loading.value = false
})

async function fetchWatchlist() {
  try {
    watchlist.value = (await watchlistApi.getList()) as unknown as WatchlistItem[]
  } catch (e) { console.error(e) }
}

async function fetchNews() {
  try {
    const res = (await newsApi.getList({ page: 1, size: 6 })) as any
    news.value = res.items || []
  } catch (e) { console.error(e) }
}

function goToStock(code: string) {
  router.push(`/market/${code}`)
}

function formatAmount(val: number | null): string {
  if (!val) return '--'
  if (val > 1e8) return (val / 1e8).toFixed(1) + '亿'
  if (val > 1e4) return (val / 1e4).toFixed(0) + '万'
  return val.toFixed(0)
}
</script>

<template>
  <AppShell>
    <div class="max-w-7xl mx-auto px-4 py-4 space-y-5">
      <!-- Page title -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold dark:text-white">市场概览</h1>
          <DataFreshness :lastFetched="lastFetched" />
        </div>
        <button
          @click="router.push('/settings')"
          class="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
        >
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>
      </div>

      <!-- Index Overview -->
      <section>
        <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">主要指数</h2>
        <div v-if="loading" class="flex gap-3 overflow-x-auto no-scrollbar">
          <SkeletonCard v-for="i in 4" :key="i" :lines="2" class="min-w-[150px]" />
        </div>
        <div v-else class="flex gap-3 overflow-x-auto no-scrollbar scroll-snap-x pb-2">
          <div
            v-for="idx in marketStore.indices" :key="idx.code"
            class="min-w-[160px] bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 snap-start cursor-pointer hover:shadow-md transition-shadow"
            @click="goToStock(idx.code)"
          >
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1 truncate">{{ idx.name }}</div>
            <PriceText :value="idx.latest_price" size="lg" class="mb-1 block" />
            <div class="flex items-center gap-2">
              <ChangeBadge :value="idx.change_pct" />
            </div>
            <LineChart v-if="idx.sparkline?.length" :data="idx.sparkline.map((v, i) => ({ date: String(i), value: v }))" :color="(idx.change_pct || 0) >= 0 ? '#CF1726' : '#19A55E'" class="mt-2" />
          </div>
        </div>
      </section>

      <!-- Market Breadth -->
      <section v-if="marketStore.breadth" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">涨跌统计</h2>
        <div class="flex justify-around text-center">
          <div>
            <div class="text-2xl font-bold text-market-up">{{ marketStore.breadth.up_count }}</div>
            <div class="text-xs text-gray-500 mt-1">上涨</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-market-down">{{ marketStore.breadth.down_count }}</div>
            <div class="text-xs text-gray-500 mt-1">下跌</div>
          </div>
          <div>
            <div class="text-2xl font-bold text-gray-400">{{ marketStore.breadth.flat_count }}</div>
            <div class="text-xs text-gray-500 mt-1">平盘</div>
          </div>
          <div>
            <div class="text-xl font-semibold dark:text-white">{{ formatAmount(marketStore.breadth.total_amount) }}</div>
            <div class="text-xs text-gray-500 mt-1">成交额</div>
          </div>
        </div>
      </section>

      <!-- My Watchlist Snapshot -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">我的自选</h2>
          <button @click="router.push('/watchlist')" class="text-xs text-purple-600 dark:text-purple-400 hover:underline">查看全部</button>
        </div>
        <div v-if="!watchlist.length" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <EmptyState message="还没有自选，去添加你关注的股票吧" />
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="item in watchlist.slice(0, 5)" :key="item.id"
            class="bg-white dark:bg-gray-900 rounded-xl px-4 py-3 border border-gray-100 dark:border-gray-800 flex items-center justify-between cursor-pointer hover:shadow-sm transition-shadow"
            @click="goToStock(item.item_code)"
          >
            <div>
              <div class="font-medium text-sm dark:text-white">{{ item.alias || item.item_name || item.item_code }}</div>
              <div class="text-xs text-gray-400">{{ item.item_code }}</div>
            </div>
            <div class="text-right">
              <PriceText :value="item.quote?.latest_price ?? null" size="md" />
              <div><ChangeBadge :value="item.quote?.change_pct ?? null" /></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Latest News -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">最新资讯</h2>
          <button @click="router.push('/news')" class="text-xs text-purple-600 dark:text-purple-400 hover:underline">更多新闻</button>
        </div>
        <div v-if="!news.length" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <EmptyState message="暂无新闻" />
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="article in news" :key="article.id"
            class="bg-white dark:bg-gray-900 rounded-xl px-4 py-3 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-sm transition-shadow"
            @click="router.push(`/news/${article.id}`)"
          >
            <div class="font-medium text-sm dark:text-white line-clamp-2">{{ article.title }}</div>
            <div class="flex items-center gap-2 mt-1.5 text-xs text-gray-400">
              <span>{{ article.source || '财经媒体' }}</span>
              <span>·</span>
              <span>{{ article.published_at?.slice(0, 10) || '' }}</span>
              <span
                v-if="article.sentiment"
                class="px-1.5 py-0.5 rounded text-xs"
                :class="{
                  'bg-market-up-bg text-market-up': article.sentiment === 'positive',
                  'bg-market-down-bg text-market-down': article.sentiment === 'negative',
                  'bg-gray-100 dark:bg-gray-800 text-gray-500': article.sentiment === 'neutral',
                }"
              >
                {{ article.sentiment === 'positive' ? '利好' : article.sentiment === 'negative' ? '利空' : '中性' }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Analysis Tools -->
      <section>
        <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">分析工具</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div @click="router.push('/sectors')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">🔥</div>
            <div class="text-xs font-medium dark:text-white">板块分析</div>
          </div>
          <div @click="router.push('/capital-flow')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">💰</div>
            <div class="text-xs font-medium dark:text-white">资金流向</div>
          </div>
          <div @click="router.push('/compare')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">⚖️</div>
            <div class="text-xs font-medium dark:text-white">对比分析</div>
          </div>
          <div @click="router.push('/screener')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">🔍</div>
            <div class="text-xs font-medium dark:text-white">股票筛选</div>
          </div>
        </div>
      </section>

      <!-- Quick learn access -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">快速学习</h2>
          <button @click="router.push('/learn')" class="text-xs text-purple-600 dark:text-purple-400 hover:underline">知识库</button>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div @click="router.push('/learn/glossary')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">📖</div>
            <div class="text-xs font-medium dark:text-white">术语百科</div>
          </div>
          <div @click="router.push('/learn/strategies')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">🎯</div>
            <div class="text-xs font-medium dark:text-white">投资策略</div>
          </div>
          <div @click="router.push('/portfolio')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">📊</div>
            <div class="text-xs font-medium dark:text-white">模拟交易</div>
          </div>
          <div @click="router.push('/journal')" class="bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-md transition-shadow text-center">
            <div class="text-2xl mb-1">📝</div>
            <div class="text-xs font-medium dark:text-white">投资笔记</div>
          </div>
        </div>
      </section>

      <div class="h-4" />
    </div>
  </AppShell>
</template>
