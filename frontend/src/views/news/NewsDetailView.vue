<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    article.value = await newsApi.getDetail(Number(route.params.id))
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-6">
      <div v-if="loading" class="space-y-3 animate-pulse">
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3" />
        <div class="h-32 bg-gray-100 dark:bg-gray-800 rounded mt-4" />
      </div>
      <article v-else-if="article" class="prose dark:prose-invert max-w-none">
        <h1 class="text-xl font-bold dark:text-white mb-2">{{ article.title }}</h1>
        <div class="flex items-center gap-2 text-sm text-gray-400 mb-6">
          <span>{{ article.source || '财经媒体' }}</span>
          <span v-if="article.author">· {{ article.author }}</span>
          <span>· {{ article.published_at?.slice(0, 16) || '' }}</span>
        </div>
        <div v-if="article.content" class="text-sm leading-relaxed dark:text-gray-300 whitespace-pre-wrap" v-html="article.content" />
        <div v-else class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{{ article.summary || '暂无内容详情' }}</div>

        <!-- Related stocks -->
        <div v-if="article.related_stocks?.length" class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800">
          <h3 class="text-sm font-medium text-gray-500 mb-2">相关股票</h3>
          <div class="flex flex-wrap gap-2">
            <span v-for="s in article.related_stocks" :key="s.code" class="px-2 py-1 bg-gray-50 dark:bg-gray-800 rounded text-xs">
              {{ s.name || s.code }}
            </span>
          </div>
        </div>
      </article>
    </div>
  </AppShell>
</template>
