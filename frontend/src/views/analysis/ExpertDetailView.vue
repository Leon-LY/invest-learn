<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const route = useRoute()
const router = useRouter()
const expert = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const id = route.params.id as string
    expert.value = await newsApi.getExpertDetail(id)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 4" :key="i" class="skeleton h-24 rounded-xl" />
      </div>

      <div v-else-if="!expert || expert.error" class="card p-6 text-center text-gray-400 text-sm">{{ expert?.error || '暂无数据' }}</div>

      <div v-else class="space-y-4">
        <!-- Profile header -->
        <div class="card p-5">
          <div class="flex items-start gap-4">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold text-xl shrink-0">{{ expert.name?.[0] }}</div>
            <div>
              <h1 class="text-lg font-bold dark:text-white">{{ expert.name }}</h1>
              <p class="text-sm text-gray-400">{{ expert.title }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary font-medium">{{ expert.type }}</span>
                <span v-if="expert.fund_code" class="text-xs text-gray-400">{{ expert.fund_code }}</span>
              </div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2 leading-relaxed">{{ expert.bio }}</p>
            </div>
          </div>
        </div>

        <!-- Predictive view from DeepSeek -->
        <div v-if="expert.predictive_view?.predictions?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">🔮 DeepSeek 预测观点（{{ expert.predictive_view.predictions.length }}条）</h3>
          <div class="space-y-2">
            <div v-for="(p, i) in expert.predictive_view.predictions" :key="i"
              class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <p class="text-xs text-gray-400 mb-1">📰 {{ p.news_title }}</p>
              <p class="text-sm font-medium dark:text-white">{{ p.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ p.content }}</p>
            </div>
          </div>
        </div>

        <!-- NAV Chart -->
        <div v-if="expert.nav_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📈 净值走势（近90日）</h3>
          <div class="h-32 flex items-end gap-px">
            <div v-for="(n, i) in expert.nav_history.slice(-60)" :key="i"
              class="flex-1 rounded-t-sm transition-all"
              :class="(n.daily_return||0)>=0?'bg-up/60':'bg-down/60'"
              :style="{ height: n.nav && expert.nav_history[0]?.nav ? `${25 + ((n.nav - expert.nav_history[0].nav) / expert.nav_history[0].nav * 100) * 0.8 + 25}%` : '30%' }"
              :title="`${n.date}: ${n.nav}`" />
          </div>
          <div class="flex justify-between text-[10px] text-gray-400 mt-1">
            <span>{{ expert.nav_history[0]?.date }}</span>
            <span>{{ expert.nav_history[expert.nav_history.length-1]?.date }}</span>
          </div>
        </div>

        <!-- Size trend -->
        <div v-if="expert.size_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💰 规模变动</h3>
          <div class="space-y-2">
            <div v-for="s in expert.size_history" :key="s.date" class="flex justify-between text-sm">
              <span class="text-gray-400">{{ s.date }}</span>
              <span class="font-medium dark:text-white">{{ (s.size/1e8).toFixed(1) }}亿</span>
            </div>
          </div>
        </div>

        <!-- Fund operations (real trading data) -->
        <div v-if="expert.fund_operations?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📊 基金操盘数据（近60日真实数据）</h3>
          <div class="space-y-2">
            <div v-for="(op, i) in expert.fund_operations" :key="'f'+i" class="flex items-start gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-xs">
              <span class="text-gray-400 w-24 shrink-0">{{ op.date }}</span>
              <span class="font-medium text-gray-600 dark:text-gray-300 w-20 shrink-0">{{ op.action }}</span>
              <span class="text-gray-500 dark:text-gray-400">{{ op.detail }}</span>
            </div>
          </div>
        </div>

        <!-- Performance highlights -->
        <div v-if="expert.performance_highlights?.latest_nav" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">🏆 业绩亮点</h3>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <div class="text-xs text-gray-400 mb-1">最新净值</div>
              <div class="text-lg font-bold dark:text-white tabular-nums">{{ expert.performance_highlights.latest_nav.toFixed(4) }}</div>
              <div class="text-xs text-gray-400">{{ expert.performance_highlights.nav_date }}</div>
            </div>
            <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <div class="text-xs text-gray-400 mb-1">日涨跌</div>
              <div :class="(expert.performance_highlights.day_change||0)>=0?'text-up':'text-down'" class="text-lg font-bold tabular-nums">{{ (expert.performance_highlights.day_change||0)>=0?'+':'' }}{{ expert.performance_highlights.day_change?.toFixed(2) }}%</div>
            </div>
            <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <div class="text-xs text-gray-400 mb-1">基金代码</div>
              <div class="text-lg font-bold dark:text-white">{{ expert.fund_code }}</div>
            </div>
          </div>
        </div>

        <!-- News & Analysis timeline -->
        <div v-if="expert.operations?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📋 近期动态 & 观点</h3>
          <div class="space-y-2">
            <div v-for="(op, i) in expert.operations" :key="i" class="flex items-start gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-xs">
              <span class="text-gray-400 w-20 shrink-0">{{ op.date }}</span>
              <span class="font-medium text-gray-600 dark:text-gray-300 w-24 shrink-0">{{ op.action }}</span>
              <span class="text-gray-500 dark:text-gray-400">{{ op.detail }}</span>
            </div>
          </div>
        </div>

        <!-- Related AI Analyses -->
        <div v-if="expert.related_analyses?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">🤖 AI 分析（{{ expert.related_analyses.length }}条）</h3>
          <div class="space-y-2">
            <div v-for="(a, i) in expert.related_analyses.slice(0,6)" :key="i"
              class="flex items-center gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-xs">
              <span class="px-1.5 py-0.5 rounded text-xs font-medium"
                :class="a.impact_level?.includes('利好')?'bg-up-bg text-up':a.impact_level?.includes('利空')?'bg-down-bg text-down':'bg-gray-100 text-gray-500'">{{ a.impact_level }}</span>
              <span class="text-gray-500 dark:text-gray-400 line-clamp-1">{{ a.short_term }}</span>
              <span class="text-gray-300 dark:text-gray-600 shrink-0 ml-auto">{{ a.generated_by==='deepseek'?'🤖':'' }}</span>
            </div>
          </div>
        </div>

        <!-- Related news -->
        <div v-if="expert.related_news?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📰 相关新闻（{{ expert.related_news.length }}条）</h3>
          <div class="space-y-2">
            <div v-for="n in expert.related_news.slice(0,8)" :key="n.id"
              @click="router.push(`/news/${n.id}`)"
              class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors">
              <p class="text-sm dark:text-white line-clamp-2">{{ n.title }}</p>
              <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
                <span>{{ n.source }}</span>
                <span>·</span>
                <span>{{ n.published_at?.slice(0,10) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
