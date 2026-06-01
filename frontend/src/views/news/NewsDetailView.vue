<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'
import { newsImpactAnalyses } from '@/mock/experts'
import type { NewsImpactAnalysis } from '@/mock/experts'

// Configure marked for safe rendering
marked.setOptions({ breaks: true, gfm: true })

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)
const aiAnalysis = ref<NewsImpactAnalysis | null>(null)

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return marked.parse(article.value.content) as string
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
    // Generate AI analysis for every article
    aiAnalysis.value = generateImpactAnalysis(id, article.value)
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})

function generateImpactAnalysis(id: number, art: any): NewsImpactAnalysis {
  const matched = newsImpactAnalyses.find(a => a.newsId === id)
  if (matched) return matched

  const sentiment = art.sentiment || 'neutral'
  const title = art.title || ''
  const pos = sentiment === 'positive'
  const neg = sentiment === 'negative'
  const impactScore = pos ? 55 : neg ? -35 : 10
  const impactLevel = pos ? '利好' : neg ? '利空' : '中性'

  return {
    newsId: id, title: 'AI自动分析: ' + title.slice(0, 20),
    newsTitle: title, impactScore, impactLevel,
    affectedFunds: [
      { code: '510300', name: '沪深300ETF', impact: pos ? '市场情绪改善利好核心资产' : neg ? '短期承压但长期价值不变' : '影响有限' },
      { code: '005827', name: '易方达蓝筹精选', impact: pos ? '重仓蓝筹有望受益' : neg ? '重仓消费可能承压' : '维持中性' },
      { code: '110027', name: '易方达安心回报债', impact: pos ? '风险偏好改善利好信用债' : neg ? '资金避险利好利率债' : '波动较小' },
    ],
    shortTerm: pos ? '预计1-2周内偏股基金有望小幅上涨1-2%，市场情绪改善将带动资金流入。' : neg ? '短期1-2周内市场可能承压，偏股基金或回调1-3%。不建议恐慌赎回。' : '短期市场维持震荡，方向不明朗，建议观望等待更明确信号。',
    mediumTerm: pos ? '未来1-3个月，如果积极因素持续兑现，偏股基金有望获得3-5%的超额收益。重点关注消费和科技板块。' : neg ? '未来1-3个月市场将逐渐消化利空，估值合理的优质基金将率先企稳。可利用定投在低位积累份额。' : '中期方向取决于后续数据和政策，建议保持灵活仓位，做好两手准备。',
    actionAdvice: pos ? '继续定投，但不要追高一次性加仓。保持现有仓位，让利润奔跑。' : neg ? '坚持定投不要停，下跌是积累份额的好机会。如果有闲置资金，可分批加仓。' : '按原计划执行定投，不急于加仓或减仓。等待趋势明朗后再调整。',
    keyPoints: [title.slice(0, 30), '关注后续市场反应', '定投投资者无需过度反应', '做好仓位管理'],
  }
}

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
