<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'
import EmptyState from '@/components/common/EmptyState.vue'
import type { NewsArticle } from '@/types/market'

const router = useRouter()
const articles = ref<NewsArticle[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const category = ref('')
const page = ref(1)
const total = ref(0)
const hasMore = ref(false)

onMounted(() => fetchNews())

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
      <h1 class="text-xl font-bold dark:text-white">基金资讯</h1>

      <!-- Category tabs -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button v-for="c in [{ v: '', l: '全部' }, { v: '基金', l: '基金' }, { v: '行业', l: '行业' }, { v: '大佬', l: '大佬' }, { v: '策略', l: '策略' }]" :key="c.v"
          @click="changeCategory(c.v)"
          class="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
          :class="category === c.v ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
        >{{ c.l }}</button>
        <span class="text-xs text-gray-400 self-center ml-2">共 {{ total }} 条</span>
      </div>

      <!-- News list -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 6" :key="i" class="animate-pulse card p-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" /><div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" /></div>
      </div>
      <EmptyState v-else-if="!articles.length" message="暂无该分类新闻" />
      <div v-else class="space-y-2">
        <div
          v-for="a in articles" :key="a.id"
          @click="router.push(`/news/${a.id}`)"
          class="card p-4 cursor-pointer hover:shadow-md transition-shadow"
        >
          <div class="font-medium text-sm dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
          <p v-if="a.summary" class="text-xs text-gray-400 mt-1.5 line-clamp-2">{{ a.summary }}</p>
          <div class="flex items-center gap-2 mt-2 text-xs text-gray-400">
            <span>{{ a.source || '基智学' }}</span><span>·</span>
            <span>{{ a.published_at?.slice(0, 10) || '' }}</span>
            <span v-if="a.sentiment === 'positive'" class="px-1.5 py-0.5 rounded text-xs bg-up-bg text-up font-medium">利好</span>
            <span v-else-if="a.sentiment === 'negative'" class="px-1.5 py-0.5 rounded text-xs bg-down-bg text-down font-medium">利空</span>
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
