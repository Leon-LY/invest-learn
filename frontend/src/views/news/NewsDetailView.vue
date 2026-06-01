<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'
import { newsImpactAnalyses } from '@/mock/experts'
import type { NewsImpactAnalysis } from '@/mock/experts'

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)
const aiAnalysis = ref<NewsImpactAnalysis | null>(null)

onMounted(async () => {
  try {
    const id = Number(route.params.id)
    article.value = await newsApi.getDetail(id)
    // Match AI analysis by news ID
    aiAnalysis.value = newsImpactAnalyses.find(a => a.newsId === id) || null
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
          <span>· {{ article.published_at?.slice(0, 16) || '' }}</span>
          <span v-if="article.sentiment === 'positive'" class="px-1.5 py-0.5 text-xs rounded-full bg-up-bg text-up font-medium">利好</span>
          <span v-else-if="article.sentiment === 'negative'" class="px-1.5 py-0.5 text-xs rounded-full bg-down-bg text-down font-medium">利空</span>
        </div>
        <div v-if="article.content" class="text-sm leading-relaxed dark:text-gray-300 whitespace-pre-wrap" v-html="article.content" />
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
            <span class="text-sm px-3 py-1 rounded-full font-bold" :class="impactColors[aiAnalysis.impactLevel]">{{ aiAnalysis.impactLevel }}</span>
            <span class="text-sm text-gray-400">评分 {{ aiAnalysis.impactScore }}/100</span>
          </div>

          <!-- Affected Funds -->
          <div class="mb-4">
            <h4 class="text-xs font-semibold text-gray-500 mb-2 uppercase">📊 受影响基金</h4>
            <div class="space-y-1.5">
              <div v-for="f in aiAnalysis.affectedFunds" :key="f.code" class="flex items-center justify-between text-sm bg-white/60 dark:bg-gray-800/50 rounded-lg px-3 py-2">
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
              <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{{ aiAnalysis.shortTerm }}</p>
            </div>
            <div class="bg-white/60 dark:bg-gray-800/50 rounded-lg p-3">
              <h4 class="text-xs font-semibold text-gray-500 mb-1">📅 中期影响（1-3月）</h4>
              <p class="text-xs text-gray-700 dark:text-gray-300 leading-relaxed">{{ aiAnalysis.mediumTerm }}</p>
            </div>
          </div>

          <!-- Key Points -->
          <div class="mb-4">
            <h4 class="text-xs font-semibold text-gray-500 mb-2 uppercase">🔑 关键要点</h4>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="(kp, i) in aiAnalysis.keyPoints" :key="i" class="text-xs px-2 py-1 bg-white/60 dark:bg-gray-800/50 rounded-full text-gray-700 dark:text-gray-300">{{ i + 1 }}. {{ kp }}</span>
            </div>
          </div>

          <!-- Advice -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-3 flex items-start gap-2">
            <span class="text-lg shrink-0">💡</span>
            <div>
              <h4 class="text-xs font-semibold text-gray-500 mb-0.5">操作建议</h4>
              <p class="text-sm text-gray-800 dark:text-gray-200 font-medium">{{ aiAnalysis.actionAdvice }}</p>
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
