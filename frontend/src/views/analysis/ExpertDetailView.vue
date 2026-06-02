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
        <!-- ===== 1. PROFILE ===== -->
        <div class="card p-5">
          <div class="flex items-start gap-4">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold text-xl shrink-0">{{ expert.name?.[0] }}</div>
            <div>
              <h1 class="text-lg font-bold dark:text-white">{{ expert.name }}</h1>
              <p class="text-sm text-gray-400">{{ expert.title }}</p>
              <div class="flex items-center gap-2 mt-1">
                <span class="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">{{ expert.type }}</span>
                <span v-if="expert.fund_code" class="text-xs text-gray-400 font-mono">{{ expert.fund_code }}</span>
              </div>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-2 leading-relaxed">{{ expert.bio }}</p>
              <!-- Fund style tags -->
              <div v-if="expert.fund_style?.length" class="flex gap-1.5 mt-2">
                <span v-for="kw in expert.fund_style" :key="kw" class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">{{ kw }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 2. PERFORMANCE HIGHLIGHTS ===== -->
        <div v-if="expert.performance_highlights?.latest_nav" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📈 基金表现</h3>
          <div class="grid grid-cols-3 gap-3 text-center">
            <div class="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/30">
              <div class="text-xs text-gray-400 mb-1">最新净值</div>
              <div class="text-xl font-bold dark:text-white tabular-nums">{{ expert.performance_highlights.latest_nav.toFixed(4) }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ expert.performance_highlights.nav_date }}</div>
            </div>
            <div class="p-3 rounded-xl" :class="(expert.performance_highlights.day_change||0)>=0?'bg-red-50 dark:bg-red-950/20':'bg-green-50 dark:bg-green-950/20'">
              <div class="text-xs text-gray-400 mb-1">日涨跌</div>
              <div :class="(expert.performance_highlights.day_change||0)>=0?'text-up':'text-down'" class="text-xl font-bold tabular-nums">{{ (expert.performance_highlights.day_change||0)>=0?'+':'' }}{{ expert.performance_highlights.day_change?.toFixed(2) }}%</div>
            </div>
            <div class="p-3 rounded-xl bg-purple-50 dark:bg-purple-950/20">
              <div class="text-xs text-gray-400 mb-1">基金类型</div>
              <div class="text-sm font-bold dark:text-white">{{ expert.fund_name?.slice(0,6) || '--' }}</div>
              <div class="text-[10px] text-gray-400 mt-0.5">{{ expert.fund_code }}</div>
            </div>
          </div>
          <!-- NAV mini chart -->
          <div v-if="expert.nav_history?.length" class="mt-3 h-24 flex items-end gap-px">
            <div v-for="(n, i) in expert.nav_history.slice(-60)" :key="i" class="flex-1 rounded-t-sm"
              :class="(n.daily_return||0)>=0?'bg-up/50':'bg-down/50'"
              :style="{height: expert.nav_history[0]?.nav ? `${15 + Math.abs((n.nav - expert.nav_history[0].nav) / expert.nav_history[0].nav * 100) * 0.5 + 20}%` : '30%'}" />
          </div>
        </div>

        <!-- ===== 3. FUND OPERATIONS (REAL DATA) ===== -->
        <div v-if="expert.operations?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📊 近期基金表现</h3>
          <p class="text-xs text-gray-400 mb-2">以下数据来自基金实际净值走势（近60日），反映该基金的波动特征：</p>
          <div class="space-y-2">
            <div v-for="(op, i) in expert.operations" :key="i" class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-sm">
              <span class="shrink-0 mt-0.5">{{ op.action?.slice(0,2) }}</span>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs text-gray-400 w-20">{{ op.date }}</span>
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400">{{ op.action?.slice(3) }}</span>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ op.detail }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 3.5 HOLDINGS ===== -->
        <div v-if="expert.holdings?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📋 {{ expert.fund_name || '基金' }} 前十大重仓股</h3>
          <p class="text-xs text-gray-400 mb-2">基金经理实际持仓 · {{ expert.holdings?.[0]?.quarter || '最新季报' }}</p>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="text-gray-400 border-b border-gray-100 dark:border-gray-800">
                  <th class="text-left py-2 font-medium">股票</th>
                  <th class="text-right py-2 font-medium">代码</th>
                  <th class="text-right py-2 font-medium">占净值比</th>
                  <th class="text-right py-2 font-medium">持仓市值</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in expert.holdings" :key="h.code" class="border-b border-gray-50 dark:border-gray-800/30">
                  <td class="py-2 dark:text-white">{{ h.stock }}</td>
                  <td class="py-2 text-right text-gray-400 font-mono">{{ h.code }}</td>
                  <td class="py-2 text-right font-medium dark:text-white">{{ h.ratio?.toFixed(2) }}%</td>
                  <td class="py-2 text-right text-gray-400">{{ h.market_value }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="text-[10px] text-gray-400 mt-2">数据来源：基金定期报告（AKShare），每季度更新</p>
        </div>

        <!-- ===== 4. SCALE TREND ===== -->
        <div v-if="expert.size_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💰 规模变动（亿元）</h3>
          <div class="flex items-end gap-2 h-20">
            <div v-for="s in expert.size_history" :key="s.date" class="flex-1 flex flex-col items-center">
              <div class="text-[10px] text-gray-500 tabular-nums mb-0.5">{{ (s.size/1e8).toFixed(0) }}</div>
              <div class="w-full rounded-t-sm bg-primary/40" :style="{height: `${Math.max(8, (s.size/1e8)/Math.max(...expert.size_history.map((x:any)=>x.size/1e8))*100)}%`}" />
              <div class="text-[10px] text-gray-400 mt-0.5">{{ s.date?.slice(0,7) }}</div>
            </div>
          </div>
        </div>

        <!-- ===== 5. MARKET CONTEXT ===== -->
        <div v-if="expert.market_context" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-2">🌐 市场环境</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ expert.market_context }}</p>
        </div>

        <!-- ===== 6. NEWS DIGEST ===== -->
        <div v-if="expert.news_digest?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📰 相关动态（{{ expert.news_digest.length }}条）</h3>
          <div class="space-y-2">
            <div v-for="n in expert.news_digest" :key="n.news_id"
              @click="router.push(`/news/${n.news_id}`)"
              class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors">
              <span v-if="n.tag" class="shrink-0 text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary mt-0.5">{{ n.tag }}</span>
              <div class="flex-1 min-w-0">
                <p class="text-sm dark:text-white line-clamp-2 leading-snug">{{ n.title }}</p>
                <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
                  <span>{{ n.date }}</span>
                  <span v-if="n.sentiment==='positive'" class="text-up font-medium">利好</span>
                  <span v-else-if="n.sentiment==='negative'" class="text-down font-medium">利空</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ===== 7. PREDICTIVE VIEWS ===== -->
        <div v-if="expert.predictive_view?.predictions?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">🔮 DeepSeek 预测（{{ expert.predictive_view.predictions.length }}条）</h3>
          <div class="space-y-2">
            <div v-for="(p, i) in expert.predictive_view.predictions" :key="i" class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-sm">
              <p class="text-xs text-gray-400 mb-1">📰 {{ p.news_title }}</p>
              <p class="font-medium dark:text-white">{{ p.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ p.content }}</p>
            </div>
          </div>
        </div>

        <!-- ===== 8. INVESTMENT INSIGHTS ===== -->
        <div v-if="expert.insights?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💡 投资启示</h3>
          <div class="space-y-3">
            <div v-for="(ins, i) in expert.insights" :key="i" class="flex items-start gap-3">
              <span class="text-lg shrink-0">{{ ins.icon }}</span>
              <div>
                <p class="text-sm font-medium dark:text-white">{{ ins.title }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 leading-relaxed">{{ ins.detail }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
