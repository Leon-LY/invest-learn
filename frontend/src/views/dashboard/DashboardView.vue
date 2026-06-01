<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import DailyBrief from '@/components/market/DailyBrief.vue'
import { watchlistApi } from '@/api/watchlist'
import { newsApi } from '@/api/news'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import type { WatchlistItem, NewsArticle } from '@/types/market'

const router = useRouter()
const watchlist = ref<WatchlistItem[]>([])
const news = ref<NewsArticle[]>([])
const greeting = ref('')

function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  const now = Date.now()
  const diff = now - d.getTime()
  const m = Math.floor(diff / 60000)
  const h = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  if (h < 24) return `${h}小时前`
  if (days < 7) return `${days}天前`
  return `${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
}

onMounted(async () => {
  const hour = new Date().getHours()
  greeting.value = hour < 12 ? '早上好' : hour < 18 ? '下午好' : '晚上好'
  await Promise.all([fetchWatchlist(), fetchNews()])
})

async function fetchWatchlist() { try { watchlist.value = (await watchlistApi.getList()) as unknown as WatchlistItem[] } catch (e) {} }
async function fetchNews() { try { news.value = ((await newsApi.getList({ page: 1, size: 3 })) as any).items || [] } catch (e) {} }
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-5 space-y-4">
      <!-- Greeting -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-bold text-gray-900 dark:text-white title-underline">{{ greeting }}，Leon 👋</h1>
          <p class="text-xs text-gray-400 mt-0.5 flex items-center gap-1.5">
            <span>基智学 · 你的基金投资学习助手</span>
            <span class="live-dot"></span>
            <span class="text-[10px] text-gray-300 dark:text-gray-600">LIVE</span>
          </p>
        </div>
      </div>

      <!-- Daily Brief -->
      <DailyBrief />

      <!-- Hot Tools -->
      <div class="grid grid-cols-3 gap-2">
        <button @click="router.push('/diagnosis')" class="card p-3 text-center hover:shadow-md transition-shadow">
          <div class="text-xl mb-0.5">🔬</div>
          <div class="text-xs font-medium text-gray-700 dark:text-gray-300">基金诊断</div>
        </button>
        <button @click="router.push('/analysis')" class="card p-3 text-center hover:shadow-md transition-shadow">
          <div class="text-xl mb-0.5">🤖</div>
          <div class="text-xs font-medium text-gray-700 dark:text-gray-300">AI分析</div>
        </button>
        <button @click="router.push('/learn')" class="card p-3 text-center hover:shadow-md transition-shadow">
          <div class="text-xl mb-0.5">📚</div>
          <div class="text-xs font-medium text-gray-700 dark:text-gray-300">知识库</div>
        </button>
      </div>

      <!-- Watchlist -->
      <section>
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400">⭐ 我的自选</h2>
          <button @click="router.push('/watchlist')" class="text-xs text-primary font-medium">管理</button>
        </div>
        <div v-if="!watchlist.length" class="card p-4 text-center">
          <p class="text-sm text-gray-400">还没有自选基金</p>
          <button @click="router.push('/watchlist')" class="mt-2 text-sm text-primary font-medium">去添加 →</button>
        </div>
        <div v-else class="space-y-1.5">
          <div v-for="item in watchlist.slice(0, 5)" :key="item.id"
            @click="router.push(`/diagnosis/${item.item_code}`)"
            class="card p-3 flex items-center justify-between cursor-pointer">
            <div class="min-w-0 flex-1">
              <div class="font-medium text-sm text-gray-900 dark:text-white truncate">{{ item.alias || item.item_name || item.item_code }}</div>
              <div class="text-xs text-gray-400">{{ item.item_code }}</div>
            </div>
            <ChangeBadge :value="item.quote?.change_pct ?? null" />
          </div>
        </div>
      </section>

      <!-- News -->
      <section>
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400">📰 基金资讯</h2>
          <button @click="router.push('/news')" class="text-xs text-primary font-medium">更多</button>
        </div>
        <div class="space-y-1.5">
          <div v-for="a in news" :key="a.id" @click="router.push(`/news/${a.id}`)" class="card p-3 cursor-pointer">
            <div class="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
            <div class="flex items-center gap-2 mt-1.5 text-xs text-gray-400">
              <span>{{ a.source }}</span><span>·</span><span>{{ formatTime(a.published_at) }}</span>
              <span v-if="a.sentiment === 'positive'" class="text-up font-medium">利好</span>
              <span v-else-if="a.sentiment === 'negative'" class="text-down font-medium">利空</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </AppShell>
</template>
