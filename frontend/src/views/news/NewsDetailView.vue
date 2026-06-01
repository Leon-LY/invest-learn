<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

// Configure marked for safe rendering
marked.setOptions({ breaks: true, gfm: true })

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked.parse(article.value.content) as string
})

/** Get AI analysis from API response, with minimal fallback */
const aiAnalysis = computed(() => {
  const a = article.value?.ai_analysis
  if (a) return a
  // Fallback: if API returns no analysis (should not happen in production)
  if (!article.value) return null
  return null
})

/** Format ISO timestamp to friendly display */
function formatTime(iso: string | undefined | null): string {
  if (!iso) return ''
  const d = new Date(iso)
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mi = String(d.getMinutes()).padStart(2, '0')
  return `${d.getFullYear()}-${mm}-${dd} ${hh}:${mi}`
}

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    article.value = await newsApi.getDetail(id)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

const impactColors: Record<string, string> = {
  '重大利好': 'bg-up text-white',
  '利好': 'bg-up-bg text-up',
  '中性': 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400',
  '利空': 'bg-down-bg text-down',
  '重大利空': 'bg-down text-white',
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-6">
      <div v-if="loading" class="space-y-3 animate-pulse">
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
        <div class="h-4 bg-gray-100 dark:bg-gray-800 rounded w-1/3" />
        <div class="h-32 bg-gray-100 dark:bg-gray-800 rounded mt-4" />
      </div>
      <article v-else-if="article" class="max-w-none">
        <h1 class="text-xl font-bold dark:text-white mb-2">{{ article.title }}</h1>
        <div class="flex items-center gap-2 text-sm text-gray-400 mb-6">
          <span>{{ article.source || '财经媒体' }}</span>
          <span v-if="article.author">· {{ article.author }}</span>
          <span>· {{ formatTime(article.published_at) }}</span>
          <span v-if="article.sentiment === 'positive'" class="px-1.5 py-0.5 text-xs rounded-full bg-up-bg text-up font-medium">利好</span>
          <span v-else-if="article.sentiment === 'negative'" class="px-1.5 py-0.5 text-xs rounded-full bg-down-bg text-down font-medium">利空</span>
        </div>
        <!-- Content (rendered from Markdown) -->
        <div v-if="article.content" class="max-w-none dark:text-gray-300 markdown-body" v-html="renderedContent" />
        <div v-else class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{{ article.summary || '暂无内容详情' }}</div>

        <!-- 🤖 AI Impact Analysis -->
        <div v-if="aiAnalysis" class="mt-6 rounded-2xl border-2 border-primary/20 bg-gradient-to-br from-primary-light to-purple-50 dark:from-primary/10 dark:to-purple-900/20 p-5">
          <div class="flex items-center gap-2 mb-3">
            <span class="text-xl">🤖</span>
            <h3 class="font-bold text-sm text-gray-900 dark:text-white">AI 影响分析</h3>
            <span class="text-xs text-gray-400">· 基于大数据和NLP模型</span>
          </div>

          <div class="flex items-center gap-3 mb-4">
            <span class="text-sm text-gray-600 dark:text-gray-400">综合影响评估：</span>
            <span class="text-sm px-3 py-1 rounded-full font-bold" :class="impactColors[aiAnalysis.impact_level]">{{ aiAnalysis.impact_level }}</span>
            <span class="text-sm text-gray-400">评分 {{ aiAnalysis.impact_score }}/100</span>
          </div>

          <!-- Affected Funds -->
          <div class="mb-4">
            <h4 class="text-xs font-semibold text-gray-500 mb-2 uppercase">📊 受影响基金</h4>
            <div class="space-y-1.5">
              <div v-for="f in aiAnalysis.affected_funds" :key="f.code" class="flex items-center justify-between text-sm bg-white/60 dark:bg-gray-800/50 rounded-lg px-3 py-2">
                <div>
                  <span class="font-medium text-gray-800 dark:text-gray-200">{{ f.name }}</span>
                  <span class="text-xs text-gray-400 ml-2">{{ f.code }}</span>
                </div>
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ f.impact }}</span>
              </div>
            </div>
          </div>

          <!-- Analysis Timeline -->
          <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="bg-white/60 dark:bg-gray-800/50 rounded-lg p-3">
              <h4 class="text-xs font-semibold text-gray-500 mb-1">⏱ 短期影响（1-2周）</h4>
              <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{{ aiAnalysis.short_term }}</p>
            </div>
            <div class="bg-white/60 dark:bg-gray-800/50 rounded-lg p-3">
              <h4 class="text-xs font-semibold text-gray-500 mb-1">📅 中期影响（1-3月）</h4>
              <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{{ aiAnalysis.medium_term }}</p>
            </div>
          </div>

          <!-- Key Points -->
          <div class="mb-4">
            <h4 class="text-xs font-semibold text-gray-500 mb-2 uppercase">🔑 关键要点</h4>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="(kp, i) in aiAnalysis.key_points" :key="i" class="text-xs px-2 py-1 bg-white/60 dark:bg-gray-800/50 rounded-full text-gray-700 dark:text-gray-300">{{ Number(i) + 1 }}. {{ kp }}</span>
            </div>
          </div>

          <!-- Advice -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-3 flex items-start gap-2">
            <span class="text-lg shrink-0">💡</span>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 mb-0.5">操作建议</h4>
              <p class="text-sm text-gray-800 dark:text-gray-200 font-medium">{{ aiAnalysis.action_advice }}</p>
            </div>
          </div>
        </div>

        <!-- Related stocks -->
        <div v-if="article.related_stocks?.length" class="mt-6 pt-4 border-t border-gray-100 dark:border-gray-800">
          <h3 class="text-sm font-medium text-gray-500 mb-2">相关标的</h3>
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

<style scoped>
.markdown-body :deep(h2) { font-size: 1.15rem; font-weight: 700; margin: 1.2em 0 0.4em; color: #1a1a2e; }
.markdown-body :deep(h3) { font-size: 1.05rem; font-weight: 600; margin: 1em 0 0.3em; color: #16213e; }
.markdown-body :deep(h4) { font-size: 0.95rem; font-weight: 600; margin: 0.8em 0 0.2em; }
.markdown-body :deep(p) { margin: 0.4em 0; line-height: 1.7; }
.markdown-body :deep(strong) { font-weight: 600; color: #e67e22; }
.markdown-body :deep(blockquote) {
  border-left: 3px solid #e67e22; margin: 0.6em 0; padding: 0.4em 0.8em;
  background: #fff8f0; border-radius: 0 6px 6px 0; color: #6b4226;
}
.markdown-body :deep(hr) { border: none; border-top: 1px dashed #e0e0e0; margin: 1em 0; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 1.3em; margin: 0.3em 0; }
.markdown-body :deep(li) { margin: 0.15em 0; line-height: 1.6; }
.markdown-body :deep(table) { width: 100%; border-collapse: collapse; margin: 0.6em 0; font-size: 0.85rem; }
.markdown-body :deep(th) { background: #f5f5f5; padding: 6px 10px; text-align: left; font-weight: 600; border: 1px solid #e0e0e0; }
.markdown-body :deep(td) { padding: 5px 10px; border: 1px solid #e0e0e0; }
.markdown-body :deep(code) { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 0.85em; }
.markdown-body :deep(a) { color: #e67e22; text-decoration: underline; }

.dark .markdown-body :deep(h2) { color: #e8e8e8; }
.dark .markdown-body :deep(h3) { color: #d0d0d0; }
.dark .markdown-body :deep(strong) { color: #f0a050; }
.dark .markdown-body :deep(blockquote) { background: #1a1a2e; color: #c0a080; border-color: #f0a050; }
.dark .markdown-body :deep(th) { background: #1e1e2e; border-color: #333; }
.dark .markdown-body :deep(td) { border-color: #333; }
.dark .markdown-body :deep(code) { background: #1e1e2e; }
.dark .markdown-body :deep(hr) { border-color: #333; }
.dark .markdown-body :deep(a) { color: #f0a050; }
</style>
