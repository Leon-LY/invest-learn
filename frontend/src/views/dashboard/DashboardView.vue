<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { useMarketStore } from '@/stores/market'
import { watchlistApi } from '@/api/watchlist'
import { newsApi } from '@/api/news'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import SkeletonCard from '@/components/common/SkeletonCard.vue'
import type { IndexInfo, WatchlistItem, NewsArticle } from '@/types/market'

const router = useRouter()
const marketStore = useMarketStore()

const watchlist = ref<WatchlistItem[]>([])
const news = ref<NewsArticle[]>([])
const loading = ref(true)
const greeting = ref('')

onMounted(async () => {
  const hour = new Date().getHours()
  greeting.value = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'
  await Promise.all([marketStore.fetchAllDashboardData(), fetchWatchlist(), fetchNews()])
  loading.value = false
})

async function fetchWatchlist() { try { watchlist.value = (await watchlistApi.getList()) as unknown as WatchlistItem[] } catch (e) {} }
async function fetchNews() { try { news.value = ((await newsApi.getList({ page: 1, size: 5 })) as any).items || [] } catch (e) {} }

function goFund(code: string) { router.push(`/market/${code}`) }

function randomPct() { return +((Math.random() - 0.5) * 5).toFixed(2) }
const hotFunds = ['005827', '163406', '510300', '161725']
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-5 space-y-5">
      <!-- Greeting -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ greeting }} 👋</h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">基金投资，让专业的人帮你赚钱</p>
        </div>
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white text-lg">🧑</div>
      </div>

      <!-- Fund Index Cards -->
      <section>
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">基金市场指数</h2>
        <div v-if="loading" class="flex gap-3 overflow-x-auto no-scrollbar"><SkeletonCard v-for="i in 3" :key="i" class="min-w-[150px]" /></div>
        <div v-else class="flex gap-3 overflow-x-auto no-scrollbar scroll-snap-x pb-1">
          <div
            v-for="idx in marketStore.indices.slice(0, 4)" :key="idx.code"
            class="card min-w-[155px] p-4 snap-start cursor-pointer"
          >
            <div class="text-xs text-gray-500 dark:text-gray-400 mb-1.5 truncate">{{ idx.name }}</div>
            <div class="text-xl font-bold text-gray-900 dark:text-white">{{ idx.latest_price?.toLocaleString() || '--' }}</div>
            <div class="flex items-center gap-2 mt-2">
              <ChangeBadge :value="idx.change_pct" />
            </div>
            <!-- mini sparkline bars -->
            <div v-if="idx.sparkline?.length" class="mt-3 flex items-end gap-[2px] h-6">
              <div
                v-for="(v, j) in idx.sparkline.slice(0, 15)" :key="j"
                class="flex-1 rounded-[1px]"
                :class="(idx.change_pct || 0) >= 0 ? 'bg-primary/40' : 'bg-down/40'"
                :style="{ height: '60%' }"
              />
            </div>
          </div>
        </div>
      </section>

      <!-- Market Breadth Mini -->
      <div class="card p-4 flex items-center justify-around text-center">
        <div><div class="text-lg font-bold text-up">{{ marketStore.breadth?.up_count?.toLocaleString() || '--' }}</div><div class="text-xs text-gray-400 mt-0.5">上涨基金</div></div>
        <div class="w-px h-8 bg-gray-100 dark:bg-gray-800" />
        <div><div class="text-lg font-bold text-down">{{ marketStore.breadth?.down_count?.toLocaleString() || '--' }}</div><div class="text-xs text-gray-400 mt-0.5">下跌基金</div></div>
        <div class="w-px h-8 bg-gray-100 dark:bg-gray-800" />
        <div><div class="text-lg font-bold text-gray-600 dark:text-gray-300">{{ marketStore.breadth?.total_amount ? (marketStore.breadth.total_amount / 1e8).toFixed(0) + '亿' : '--' }}</div><div class="text-xs text-gray-400 mt-0.5">今日成交</div></div>
      </div>

      <!-- My Watchlist -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">我的自选基金</h2>
          <button @click="router.push('/watchlist')" class="text-xs text-primary font-medium hover:underline">管理</button>
        </div>
        <div v-if="!watchlist.length" class="card p-6 text-center">
          <div class="text-3xl mb-2">⭐</div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-3">还没有自选基金</p>
          <button @click="router.push('/watchlist')" class="text-sm text-white bg-primary px-4 py-2 rounded-lg hover:bg-primary-dark transition-colors">去添加</button>
        </div>
        <div v-else class="space-y-2">
          <div v-for="item in watchlist.slice(0, 5)" :key="item.id" @click="goFund(item.item_code)" class="card p-3.5 flex items-center justify-between cursor-pointer">
            <div class="flex-1 min-w-0">
              <div class="font-medium text-sm text-gray-900 dark:text-white truncate">{{ item.alias || item.item_name || item.item_code }}</div>
              <div class="text-xs text-gray-400 mt-0.5">净值 {{ item.quote?.latest_price?.toFixed(4) || '--' }}</div>
            </div>
            <ChangeBadge :value="item.quote?.change_pct ?? null" />
          </div>
        </div>
      </section>

      <!-- Hot Funds -->
      <section>
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">热门基金</h2>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="code in hotFunds" :key="code" @click="goFund(code)" class="card p-4 cursor-pointer">
            <div class="text-xs text-gray-400 mb-1">{{ ({ '005827': '易方达蓝筹精选', '163406': '兴全合润混合', '510300': '沪深300ETF', '161725': '招商白酒指数' })[code] }}</div>
            <div class="text-lg font-bold text-gray-900 dark:text-white">{{ code === '005827' ? '2.8541' : code === '163406' ? '1.9620' : code === '510300' ? '4.1235' : '1.4520' }}</div>
            <div class="mt-1.5"><ChangeBadge :value="randomPct()" /></div>
          </div>
        </div>
      </section>

      <!-- Latest News -->
      <section>
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">基金资讯</h2>
          <button @click="router.push('/news')" class="text-xs text-primary font-medium hover:underline">更多</button>
        </div>
        <div class="space-y-2">
          <div v-for="a in news" :key="a.id" @click="router.push(`/news/${a.id}`)" class="card p-3.5 cursor-pointer">
            <div class="flex items-start gap-3">
              <div class="flex-1 min-w-0">
                <div class="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
                <div class="flex items-center gap-2 mt-2 text-xs text-gray-400">
                  <span>{{ a.source }}</span><span>·</span><span>{{ a.published_at?.slice(0, 10) }}</span>
                </div>
              </div>
              <span v-if="a.sentiment === 'positive'" class="shrink-0 text-xs px-2 py-1 rounded-full bg-up-bg text-up font-medium">利好</span>
              <span v-else-if="a.sentiment === 'negative'" class="shrink-0 text-xs px-2 py-1 rounded-full bg-down-bg text-down font-medium">利空</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Quick Tools -->
      <section>
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">快捷工具</h2>
        <div class="grid grid-cols-4 gap-3">
          <button @click="router.push('/learn')" class="card p-3 text-center"><div class="text-2xl mb-1">📚</div><div class="text-xs font-medium text-gray-700 dark:text-gray-300">知识库</div></button>
          <button @click="router.push('/learn/glossary')" class="card p-3 text-center"><div class="text-2xl mb-1">📖</div><div class="text-xs font-medium text-gray-700 dark:text-gray-300">术语</div></button>
          <button @click="router.push('/compare')" class="card p-3 text-center"><div class="text-2xl mb-1">⚖️</div><div class="text-xs font-medium text-gray-700 dark:text-gray-300">对比</div></button>
          <button @click="router.push('/journal')" class="card p-3 text-center"><div class="text-2xl mb-1">📝</div><div class="text-xs font-medium text-gray-700 dark:text-gray-300">笔记</div></button>
        </div>
      </section>

      <div class="h-4" />
    </div>
  </AppShell>
</template>
