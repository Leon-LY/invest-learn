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
const selectedCategory = ref('')

const difficultyLabels: Record<string, string> = { beginner: '入门', intermediate: '进阶', advanced: '高级' }

const filteredArticles = computed(() => {
  if (!selectedCategory.value) return articles.value
  return articles.value.filter(a => a.category_id === selectedCategory.value || a.tags?.some((t: string) => categories.value.find(c => c.id === selectedCategory.value)?.name === t))
})

onMounted(async () => {
  try {
    const [cats, arts] = await Promise.all([
      learnApi.getCategories(),
      learnApi.getArticles({ size: 50 }),
    ])
    categories.value = cats as unknown as any[]
    articles.value = (arts as any).items || []
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-5">
      <div>
        <h1 class="text-xl font-bold dark:text-white">投资知识库</h1>
        <p class="text-sm text-gray-400 mt-1">从零开始学习投资，建立自己的投资体系</p>
      </div>

      <!-- Categories -->
      <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <div
          v-for="cat in categories" :key="cat.id"
          @click="selectedCategory = selectedCategory === cat.slug ? '' : cat.slug"
          class="rounded-xl p-4 border transition-all cursor-pointer"
          :class="selectedCategory === cat.slug
            ? 'bg-primary/5 border-primary/30 shadow-sm dark:bg-primary/10 dark:border-primary/40'
            : 'bg-white dark:bg-gray-900 border-gray-100 dark:border-gray-800 hover:shadow-md'"
        >
          <div class="text-2xl mb-2">
            {{ cat.icon === 'rocket' ? '🚀' : cat.icon === 'chart-bar' ? '📊' : cat.icon === 'trending-up' ? '📈' : cat.icon === 'wallet' ? '💰' : cat.icon === 'shield' ? '🛡️' : cat.icon === 'heart' ? '❤️' : '📚' }}
          </div>
          <div class="font-medium text-sm dark:text-white">{{ cat.name }}</div>
          <div class="text-xs text-gray-400 mt-1 line-clamp-2">{{ cat.description }}</div>
        </div>
      </div>

      <!-- Quick links -->
      <div class="flex gap-3">
        <button @click="router.push('/learn/glossary')" class="flex-1 bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 hover:shadow-sm transition-shadow text-center">
          <div class="text-xl mb-1">📖</div>
          <div class="text-xs font-medium dark:text-white">术语百科</div>
        </button>
        <button @click="router.push('/learn/strategies')" class="flex-1 bg-white dark:bg-gray-900 rounded-xl p-3.5 border border-gray-100 dark:border-gray-800 hover:shadow-sm transition-shadow text-center">
          <div class="text-xl mb-1">🎯</div>
          <div class="text-xs font-medium dark:text-white">投资策略</div>
        </button>
      </div>

      <!-- Recent articles -->
      <section>
        <h2 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wide">全部文章</h2>
        <div v-if="loading" class="space-y-2">
          <div v-for="i in 5" :key="i" class="animate-pulse h-20 bg-gray-100 dark:bg-gray-800 rounded-xl" />
        </div>
        <EmptyState v-else-if="!filteredArticles.length" message="暂无文章" />
        <div v-else class="space-y-2">
          <div
            v-for="a in filteredArticles" :key="a.id"
            @click="router.push(`/learn/${a.slug}`)"
            class="bg-white dark:bg-gray-900 rounded-xl px-4 py-3.5 border border-gray-100 dark:border-gray-800 cursor-pointer hover:shadow-sm transition-shadow"
          >
            <div class="flex items-center gap-2 mb-1">
              <span class="px-1.5 py-0.5 text-xs rounded bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400">{{ difficultyLabels[a.level] || a.level }}</span>
              <span v-if="a.estimated_read" class="text-xs text-gray-400">阅读 {{ a.estimated_read }} 分钟</span>
            </div>
            <div class="font-medium text-sm dark:text-white">{{ a.title }}</div>
            <p class="text-xs text-gray-400 mt-1 line-clamp-2">{{ a.summary }}</p>
          </div>
        </div>
      </section>

      <div class="h-4" />
    </div>
  </AppShell>
</template>
