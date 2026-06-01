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
const category = ref('')
const page = ref(1)
const total = ref(0)

onMounted(() => fetchNews())

async function fetchNews() {
  loading.value = true
  try {
    const res = (await newsApi.getList({ category: category.value || undefined, page: page.value, size: 20 })) as any
    articles.value = res.items || []
    total.value = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
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
      <h1 class="text-xl font-bold dark:text-white">财经新闻</h1>

      <!-- Category tabs -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button v-for="c in [{ v: '', l: '全部' }, { v: 'macro', l: '宏观' }, { v: 'industry', l: '行业' }, { v: 'stock', l: '个股' }, { v: 'fund', l: '基金' }]" :key="c.v"
          @click="changeCategory(c.v)"
          class="px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
          :class="category === c.v ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
        >{{ c.l }}</button>
      </div>

      <!-- News list -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 6" :key="i" class="animate-pulse">
          <div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2" />
          <div class="h-3 bg-gray-100 dark:bg-gray-800 rounded w-1/2" />
        </div>
      </div>
      <EmptyState v-else-if="!articles.length" message="暂无新闻" />
      <div v-else class="space-y-2">
        <div
          v-for="a in articles" :key="a.id"
          @click="router.push(`/news/${a.id}`)"
          class="bg-white dark:bg-gray-900 rounded-xl px-4 py-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-sm transition-shadow"
        >
          <div class="font-medium text-sm dark:text-white line-clamp-2 leading-snug">{{ a.title }}</div>
          <p v-if="a.summary" class="text-xs text-gray-400 mt-1 line-clamp-2">{{ a.summary }}</p>
          <div class="flex items-center gap-2 mt-2 text-xs text-gray-400">
            <span>{{ a.source || '财经媒体' }}</span>
            <span>·</span>
            <span>{{ a.published_at?.slice(0, 16) || '' }}</span>
            <span v-if="a.sentiment" class="px-1.5 py-0.5 rounded text-xs"
              :class="{
                'bg-market-up-bg text-market-up': a.sentiment === 'positive',
                'bg-market-down-bg text-market-down': a.sentiment === 'negative',
                'bg-gray-100 dark:bg-gray-800 text-gray-500': a.sentiment === 'neutral',
              }"
            >{{ a.sentiment === 'positive' ? '利好' : a.sentiment === 'negative' ? '利空' : '中性' }}</span>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
