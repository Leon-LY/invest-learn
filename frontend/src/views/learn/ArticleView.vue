<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { learnApi } from '@/api/learn'

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)

const levelLabel: Record<string, string> = { beginner: '入门', intermediate: '进阶', advanced: '高级' }

onMounted(async () => {
  try {
    article.value = await learnApi.getArticleBySlug(route.params.slug as string)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

function renderMarkdown(text: string): string {
  // Simple markdown rendering for MVP
  return text
    .replace(/### (.+)/g, '<h3 class="text-lg font-semibold mt-6 mb-2">$1</h3>')
    .replace(/## (.+)/g, '<h2 class="text-xl font-bold mt-8 mb-3">$1</h2>')
    .replace(/# (.+)/g, '<h1 class="text-2xl font-bold mt-8 mb-4">$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n- (.+)/g, '\n<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul class="list-disc pl-5 space-y-1 my-2">$1</ul>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\|(.+)\|/g, (match) => {
      if (match.includes('---')) return ''
      const cells = match.split('|').filter(c => c.trim())
      return '<tr>' + cells.map(c => {
        const trimmed = c.trim()
        return trimmed.startsWith('**') ? `<th class="px-3 py-2 text-left font-semibold">${trimmed.replace(/\*\*/g, '')}</th>` : `<td class="px-3 py-2 border-t border-gray-200 dark:border-gray-700">${trimmed}</td>`
      }).join('') + '</tr>'
    })
    .replace(/>(.+)/g, '<blockquote class="border-l-4 border-primary/40 pl-4 italic text-gray-600 dark:text-gray-400 my-3">$1</blockquote>')
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-6">
      <div v-if="loading" class="space-y-3 animate-pulse">
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3" />
        <div class="h-48 bg-gray-100 dark:bg-gray-800 rounded mt-6" />
      </div>
      <article v-else-if="article" class="prose dark:prose-invert max-w-none">
        <div class="mb-2">
          <span class="px-2 py-1 text-xs rounded bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80">{{ levelLabel[article.level] || article.level }}</span>
          <span v-if="article.estimated_read" class="ml-2 text-xs text-gray-400">阅读约 {{ article.estimated_read }} 分钟</span>
        </div>
        <h1 class="text-xl font-bold dark:text-white mb-4">{{ article.title }}</h1>
        <p v-if="article.summary" class="text-sm text-gray-500 dark:text-gray-400 mb-6 leading-relaxed">{{ article.summary }}</p>
        <div v-if="article.content" class="text-sm leading-relaxed dark:text-gray-300" v-html="renderMarkdown(article.content)" />
      </article>
    </div>
  </AppShell>
</template>
