<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { learnApi } from '@/api/learn'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const categories = ref<any[]>([])
const articles = ref<any[]>([])
const loading = ref(true)
const selectedCategoryId = ref<number | null>(null)

const difficultyLabels: Record<string, string> = { beginner: '入门', intermediate: '进阶', advanced: '高级' }
const iconMap: Record<string, string> = {
  rocket: '🚀', 'chart-bar': '📊', 'trending-up': '📈', wallet: '💰', shield: '🛡️', heart: '❤️',
}

const filteredArticles = computed(() => {
  if (!selectedCategoryId.value) return articles.value
  return articles.value.filter(a => a.category_id === selectedCategoryId.value)
})

function selectCategory(id: number | null) {
  selectedCategoryId.value = selectedCategoryId.value === id ? null : id
}

onMounted(async () => {
  try {
    const [cats, arts] = await Promise.all([
      learnApi.getCategories(),
      learnApi.getArticles({ size: 50 }),
    ])
    categories.value = (cats as unknown as any[]) || []
    articles.value = (arts as any)?.items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-5">
      <!-- Header -->
      <div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">📚 投资知识库</h1>
        <p class="text-sm text-gray-400 mt-1">从零开始学习投资，建立自己的投资体系</p>
      </div>

      <!-- Category chips — compact horizontal scroll -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button
          @click="selectCategory(null)"
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all"
          :class="!selectedCategoryId ? 'bg-primary text-white shadow-sm' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'"
        >全部</button>
        <button v-for="cat in categories" :key="cat.id"
          @click="selectCategory(cat.id)"
          class="shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-all flex items-center gap-1"
          :class="selectedCategoryId === cat.id ? 'bg-primary text-white shadow-sm' : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'"
        >{{ iconMap[cat.icon] || '' }} {{ cat.name }}</button>
      </div>

      <!-- Quick links -->
      <div class="flex gap-3">
        <button @click="router.push('/learn/glossary')" class="flex-1 card p-3.5 text-center hover:shadow-md transition-shadow cursor-pointer">
          <div class="text-xl mb-1">📖</div>
          <div class="text-xs font-medium dark:text-white">术语百科</div>
          <div class="text-[10px] text-gray-400 mt-0.5">40+ 金融术语</div>
        </button>
        <button @click="router.push('/learn/strategies')" class="flex-1 card p-3.5 text-center hover:shadow-md transition-shadow cursor-pointer">
          <div class="text-xl mb-1">🎯</div>
          <div class="text-xs font-medium dark:text-white">投资策略</div>
          <div class="text-[10px] text-gray-400 mt-0.5">10 套实战框架</div>
        </button>
      </div>

      <!-- Articles -->
      <section>
        <h2 class="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 flex items-center gap-2">
          {{ selectedCategoryId ? '筛选结果' : '全部文章' }}
          <span class="text-xs font-normal text-gray-400">({{ filteredArticles.length }} 篇)</span>
        </h2>
        <div v-if="loading" class="space-y-2">
          <div v-for="i in 4" :key="i" class="skeleton h-20 rounded-xl" />
        </div>
        <EmptyState v-else-if="!filteredArticles.length" message="该分类暂无文章" />
        <div v-else class="space-y-2 animate-in">
          <div v-for="a in filteredArticles" :key="a.id"
            @click="router.push(`/learn/${a.slug}`)"
            class="card p-4 cursor-pointer">
            <div class="flex items-center gap-2 mb-1.5">
              <span class="px-1.5 py-0.5 text-xs rounded-full"
                :class="a.level==='beginner'?'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400':
                       a.level==='intermediate'?'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400':
                       'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'">
                {{ difficultyLabels[a.level] || a.level }}
              </span>
              <span class="text-xs text-gray-400">阅读 {{ a.estimated_read || 10 }} 分钟</span>
              <span v-if="a.tags?.length" class="text-xs text-gray-300 dark:text-gray-600 ml-auto">{{ a.tags.slice(0,2).join(' · ') }}</span>
            </div>
            <div class="font-medium text-sm dark:text-white">{{ a.title }}</div>
            <p class="text-xs text-gray-400 mt-1.5 line-clamp-2">{{ a.summary }}</p>
          </div>
        </div>
      </section>

      <div class="h-4" />
    </div>
  </AppShell>
</template>
