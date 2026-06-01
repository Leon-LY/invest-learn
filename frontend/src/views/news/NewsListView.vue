<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'
import EmptyState from '@/components/common/EmptyState.vue'
import type { NewsArticle } from '@/types/market'

const router = useRouter()
const route = useRoute()
const articles = ref<NewsArticle[]>([])
const loading = ref(true)
const refreshing = ref(false)
const loadingMore = ref(false)
const category = ref('')
const page = ref(1)
const total = ref(0)
const hasMore = ref(false)
const lastFetchTime = ref<Date | null>(null)

/** Format ISO timestamp to friendly display */
function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  const now = Date.now()
  const diff = now - d.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  if (d.getFullYear() === new Date().getFullYear()) return `${mm}-${dd} ${hh}:${mi}`
  return `${d.getFullYear()}-${mm}-${dd}`
}

async function doRefresh() {
  if (refreshing.value) return
  refreshing.value = true
  page.value = 1
  await fetchNews()
  refreshing.value = false
  lastFetchTime.value = new Date()
}

onMounted(() => {
  fetchNews()
  lastFetchTime.value = new Date()
})

// Auto-refresh when navigating back to news list from detail page
watch(() => route.path, (to, from) => {
  if (to === '/news' && from?.startsWith('/news/')) {
    doRefresh()
  }
})

async function fetchNews() {
  loading.value = true
  try {
    const res = (await newsApi.getList({ category: category.value || undefined, page: 1, size: 20 })) as any
    articles.value = res.items || []
    total.value = res.total || 0
    hasMore.value = articles.value.length < total.value
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  page.value++
  try {
    const res = (await newsApi.getList({ category: category.value || undefined, page: page.value, size: 20 })) as any
    const items = res.items || []
    articles.value.push(...items)
    hasMore.value = articles.value.length < (res.total || 0)
  } catch (e) { console.error(e) }
  finally { loadingMore.value = false }
}

function changeCategory(cat: string) {
  category.value = cat
  page.value = 1
  fetchNews()
}
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-4">
      <!-- Tech header card -->
      <div class="card card-glow p-4 tech-corners">
        <div class="flex items-center justify-between mb-3">
          <h1 class="text-xl font-bold dark:text-white title-underline">基金资讯</h1>
          <button @click="doRefresh" :disabled="refreshing"
            class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors disabled:opacity-50"
            title="刷新">
            <svg class="w-4 h-4 text-gray-500" :class="{ 'animate-spin': refreshing }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
          </button>
        </div>

        <!-- Category tabs -->
        <div class="flex gap-2 overflow-x-auto no-scrollbar">
          <button v-for="c in [{ v: '', l: '全部' }, { v: '基金', l: '基金' }, { v: '行业', l: '行业' }, { v: '大佬', l: '大佬' }, { v: '策略', l: '策略' }]" :key="c.v"
            @click="changeCategory(c.v)"
            class="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all duration-200"
            :class="category === c.v ? 'bg-primary text-white shadow-lg shadow-primary/25' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'"
          >{{ c.l }}</button>
          <span class="text-xs text-gray-400 self-center ml-auto">共 {{ total }} 条</span>
        </div>
      </div>

      <!-- News list -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 6" :key="i" class="animate-pulse card p-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" /><div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" /></div>
      </div>
      <EmptyState v-else-if="!articles.length" message="暂无该分类新闻" />
      <div v-else class="space-y-2 animate-in">
        <div
          v-for="a in articles" :key="a.id"
          @click="router.push(`/news/${a.id}`)"
          class="card p-4 cursor-pointer hover:shadow-md transition-shadow"
        >
          <div class="font-medium text-sm dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
          <p v-if="a.summary" class="text-xs text-gray-400 mt-1.5 line-clamp-2">{{ a.summary }}</p>
          <div class="flex items-center gap-1.5 mt-2 text-xs text-gray-400 flex-nowrap overflow-hidden">
            <span class="shrink-0">{{ a.source || '基智学' }}</span><span class="shrink-0">·</span>
            <span class="shrink-0">{{ formatTime(a.published_at) }}</span>
            <span v-if="a.sentiment === 'positive'" class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-up-bg text-up font-medium">利好</span>
            <span v-else-if="a.sentiment === 'negative'" class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-down-bg text-down font-medium">利空</span>
            <span v-else-if="a.sentiment === 'neutral'" class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400 font-medium">中性</span>
            <span v-else class="shrink-0 px-1.5 py-0.5 rounded-full text-xs bg-amber-50 text-amber-500 dark:bg-amber-900/30 dark:text-amber-400 font-medium">待分析</span>
          </div>
        </div>
      </div>

      <!-- Load more -->
      <div v-if="hasMore" class="text-center pt-2">
        <button @click="loadMore" :disabled="loadingMore"
          class="px-6 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50"
        >{{ loadingMore ? '加载中...' : '加载更多' }}</button>
      </div>
    </div>
  </AppShell>
</template>
