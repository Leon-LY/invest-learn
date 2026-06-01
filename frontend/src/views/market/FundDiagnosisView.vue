<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import { watchlistApi } from '@/api/watchlist'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()
const navChart = ref<HTMLElement>()
const annualChart = ref<HTMLElement>()
const code = (route.params.code as string) || ''
const searchQuery = ref(code)
const fund = ref<any>(null)
const loading = ref(true)
const error = ref('')

async function loadFund(c: string) {
  loading.value = true; error.value = ''
  try {
    fund.value = await marketApi.getFundDetail(c)
    if (!fund.value?.info) error.value = '未找到该基金'
  } catch (e) { error.value = '加载失败，请检查网络' }
  finally { loading.value = false }
}

function renderNavChart() {
  if (!navChart.value || !fund.value?.nav_history?.length) return
  const c = echarts.init(navChart.value, undefined, { height: 200 })
  const navs = fund.value.nav_history
  c.setOption({
    grid: { top: 10, right: 10, bottom: 20, left: 50 },
    xAxis: { type: 'category', data: navs.map((n: any) => n.date?.slice(5) || ''), axisLabel: { fontSize: 10, color: '#999' }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f0f0f0' } }, axisLabel: { fontSize: 10, color: '#999' } },
    series: [{
      type: 'line', data: navs.map((n: any) => n.unit_nav), smooth: true,
      lineStyle: { color: '#5B6CF0', width: 2 },
      itemStyle: { color: '#5B6CF0' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{offset: 0, color: 'rgba(91,108,240,0.25)'}, {offset: 1, color: 'rgba(91,108,240,0)'}]) },
      symbol: 'none',
    }],
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].axisValue}<br/>净值: <b>${p[0].data}</b>` },
  })
}

function renderAnnualChart() {
  if (!annualChart.value || !fund.value?.performance?.annual_returns?.length) return
  const c = echarts.init(annualChart.value, undefined, { height: 160 })
  const ar = fund.value.performance.annual_returns
  c.setOption({
    grid: { top: 10, right: 10, bottom: 20, left: 50 },
    xAxis: { type: 'category', data: ar.map((r: any) => String(r.year)), axisLabel: { fontSize: 10, color: '#999' }, axisLine: { show: false }, axisTick: { show: false } },
    yAxis: { type: 'value', axisLabel: { fontSize: 10, color: '#999', formatter: '{v}%' }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [{
      type: 'bar', data: ar.map((r: any) => r.return),
      itemStyle: {
        color: (p: any) => p.data >= 0 ? '#E03131' : '#099268',
        borderRadius: [4, 4, 0, 0],
      },
      barWidth: '40%',
    }],
    tooltip: { trigger: 'axis', formatter: (p: any) => `${p[0].axisValue}年<br/>收益: <b>${p[0].data > 0 ? '+' : ''}${p[0].data}%</b>` },
  })
}

onMounted(() => { if (code) loadFund(code) })
// Render charts after fund data loads
watch(fund, async () => { await nextTick(); renderNavChart(); renderAnnualChart() })
watch(() => route.params.code, (c) => { if (c) { loadFund(c as string); searchQuery.value = c as string } })

function search() {
  const q = searchQuery.value.trim()
  if (!q) return
  router.push(`/diagnosis/${q}`)
}

async function addWatchlist() {
  if (!fund.value) return
  try {
    await watchlistApi.add({ item_type: 'fund', item_code: code, item_name: fund.value.info.name })
    alert('已添加到自选')
  } catch (e) { /* ignore */ }
}

const perf = computed(() => fund.value?.performance || {})
const info = computed(() => fund.value?.info || {})

function perfClass(v: number | null | undefined): string {
  if (v == null) return 'text-gray-400'
  return v >= 0 ? 'text-up' : 'text-down'
}
function perfSign(v: number | null | undefined): string {
  if (v == null) return '--'
  return (v >= 0 ? '+' : '') + v.toFixed(2) + '%'
}

const riskColor: Record<string, string> = {
  '低': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  '中低': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  '中': 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
  '中高': 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  '高': 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
}

const feeEstimate = computed(() => {
  const t = info.value.fund_type || ''
  if (t.includes('指数') || t.includes('ETF')) return { mgmt: '0.5%', cust: '0.1%', sub: '1.0%', total: '约0.6%/年' }
  if (t.includes('债')) return { mgmt: '0.6%', cust: '0.2%', sub: '0.8%', total: '约0.8%/年' }
  if (t.includes('货币')) return { mgmt: '0.3%', cust: '0.1%', sub: '免费', total: '约0.3%/年' }
  return { mgmt: '1.5%', cust: '0.25%', sub: '1.5%', total: '约1.75%/年' }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <!-- Search -->
      <div class="flex gap-2">
        <input v-model="searchQuery" @keyup.enter="search"
          placeholder="输入基金代码，如 005827"
          class="flex-1 px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary" />
        <button @click="search" class="px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-xl">诊断</button>
      </div>

      <!-- Quick codes -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar">
        <button v-for="c in ['005827','163406','161725','510300','000198','006961']" :key="c"
          @click="searchQuery = c; router.push(`/diagnosis/${c}`)"
          class="shrink-0 px-3 py-1.5 text-xs rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-primary hover:text-primary transition-colors"
        >{{ c }}</button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 5" :key="i" class="skeleton h-20 rounded-xl" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="card p-6 text-center text-gray-400 text-sm">{{ error }}</div>

      <!-- Fund Detail -->
      <div v-else-if="fund" class="space-y-4">
        <!-- Header -->
        <div class="card p-5">
          <div class="flex items-start justify-between mb-2">
            <div>
              <h1 class="text-lg font-bold dark:text-white">{{ info.name }}</h1>
              <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
                <span>{{ info.code }}</span>
                <span>·</span>
                <span>{{ info.fund_type || '混合型' }}</span>
                <span>·</span>
                <span :class="riskColor[info.risk_level || '中']" class="px-1.5 py-0.5 rounded text-xs font-medium">{{ info.risk_level || '中' }}风险</span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold dark:text-white tabular-nums">{{ info.latest_nav || '--' }}</div>
              <div :class="perfClass(info.latest_return)" class="text-sm font-medium tabular-nums">
                {{ perfSign(info.latest_return) }}
              </div>
              <div class="text-xs text-gray-400 mt-0.5">{{ info.nav_date ? '净值日期: ' + info.nav_date : '' }}</div>
            </div>
          </div>
          <div class="flex gap-2 mt-3">
            <button @click="addWatchlist" class="flex-1 py-2 text-sm bg-primary text-white rounded-lg font-medium">+ 加入自选</button>
          </div>
        </div>

        <!-- Performance summary -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📈 阶段涨幅</h3>
          <div class="grid grid-cols-4 gap-2 text-center">
            <div v-for="p in [
              { label: '日涨跌', key: 'd1' }, { label: '近1周', key: 'w1' },
              { label: '近1月', key: 'm1' }, { label: '近3月', key: 'm3' },
              { label: '近6月', key: 'm6' }, { label: '近1年', key: 'y1' },
              { label: '近3年', key: 'y3' },
            ]" :key="p.key" class="p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <div class="text-xs text-gray-400 mb-0.5">{{ p.label }}</div>
              <div :class="perfClass(perf[p.key])" class="text-sm font-bold tabular-nums">
                {{ perfSign(perf[p.key]) }}
              </div>
            </div>
          </div>
        </div>

        <!-- NAV trend chart -->
        <div v-if="fund.nav_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-2">📉 净值走势</h3>
          <div ref="navChart" class="w-full" style="height:200px"></div>
        </div>

        <!-- Risk metrics -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">⚠️ 风险指标</h3>
          <div class="grid grid-cols-3 gap-3">
            <div class="text-center p-3 rounded-lg bg-red-50 dark:bg-red-900/10">
              <div class="text-xs text-gray-400 mb-1">最大回撤</div>
              <div class="text-lg font-bold text-up tabular-nums">{{ perf.max_drawdown ?? '--' }}{{ perf.max_drawdown != null ? '%' : '' }}</div>
            </div>
            <div class="text-center p-3 rounded-lg bg-blue-50 dark:bg-blue-900/10">
              <div class="text-xs text-gray-400 mb-1">年化波动率</div>
              <div class="text-lg font-bold text-blue-600 dark:text-blue-400 tabular-nums">{{ perf.volatility ?? '--' }}{{ perf.volatility != null ? '%' : '' }}</div>
            </div>
            <div class="text-center p-3 rounded-lg bg-green-50 dark:bg-green-900/10">
              <div class="text-xs text-gray-400 mb-1">夏普比率</div>
              <div class="text-lg font-bold text-down tabular-nums">{{ perf.sharpe ?? '--' }}</div>
            </div>
          </div>
        </div>

        <!-- Annual returns chart -->
        <div v-if="perf.annual_returns?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-2">📊 年度收益</h3>
          <div ref="annualChart" class="w-full" style="height:160px"></div>
        </div>

        <!-- Fund Info -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📋 基金资料</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-xs text-gray-400">基金公司</span><p class="dark:text-gray-200 font-medium">{{ info.company || '--' }}</p></div>
            <div><span class="text-xs text-gray-400">基金类型</span><p class="dark:text-gray-200 font-medium">{{ info.fund_type || '--' }}</p></div>
            <div><span class="text-xs text-gray-400">风险等级</span><p class="dark:text-gray-200 font-medium">{{ info.risk_level || '中' }}风险</p></div>
            <div><span class="text-xs text-gray-400">成立日期</span><p class="dark:text-gray-200 font-medium">{{ info.inception_date || '--' }}</p></div>
          </div>
        </div>

        <!-- Fees -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💰 费率水平（估算）</h3>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div><span class="text-xs text-gray-400">管理费</span><p class="dark:text-gray-200 font-medium">{{ feeEstimate.mgmt }}</p></div>
            <div><span class="text-xs text-gray-400">托管费</span><p class="dark:text-gray-200 font-medium">{{ feeEstimate.cust }}</p></div>
            <div><span class="text-xs text-gray-400">申购费</span><p class="dark:text-gray-200 font-medium">{{ feeEstimate.sub }}</p></div>
            <div><span class="text-xs text-gray-400">年度合计</span><p class="dark:text-gray-200 font-bold">{{ feeEstimate.total }}</p></div>
          </div>
        </div>

        <!-- Current Assessment -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">⏰ 当前时机评估</h3>
          <div class="space-y-2 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-400 w-20 shrink-0">近期表现</span>
              <span :class="perfClass(perf.m3)" class="font-medium">{{ perfSign(perf.m3) }}</span>
              <span class="text-xs text-gray-400">近3月</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-400 w-20 shrink-0">风险等级</span>
              <span :class="riskColor[info.risk_level || '中']" class="px-2 py-0.5 rounded text-xs font-medium">{{ info.risk_level || '中' }}风险</span>
            </div>
            <div class="flex items-start gap-2 mt-2">
              <span class="text-xs text-gray-400 w-20 shrink-0 pt-0.5">操作建议</span>
              <span class="text-gray-600 dark:text-gray-300 leading-relaxed">
                {{ (info.risk_level || '中') === '高' ? '该基金波动较大，建议通过定投方式参与，单次投入不超过总仓位的10%。关注基金经理调仓方向和市场风格切换。' :
                   (info.risk_level || '中') === '低' ? '该基金风险较低，适合作为组合的"压舱石"配置。当前收益水平与市场利率相关，可长期持有。' :
                   '建议每月定投，分6-12个月建仓。关注基金季报披露的持仓变化，评估基金经理操作是否与你的投资目标一致。' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Disclaimer -->
        <p class="text-xs text-gray-400 text-center pb-4">⚠️ 数据仅供参考学习，不构成投资建议。基金过往业绩不代表未来表现。</p>
      </div>
    </div>
  </AppShell>
</template>
