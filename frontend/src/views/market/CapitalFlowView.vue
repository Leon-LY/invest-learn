<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/app'
import type { CapitalFlowItem } from '@/types/market'

const appStore = useAppStore()
const loading = ref(true)
const northFlow = ref<CapitalFlowItem[]>([])
const southFlow = ref<CapitalFlowItem[]>([])
const days = ref(30)
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

onMounted(async () => {
  await fetchData()
})

async function fetchData() {
  loading.value = true
  try {
    const data = (await marketApi.getCapitalFlow(days.value)) as unknown as {
      north: CapitalFlowItem[]
      south: CapitalFlowItem[]
    }
    northFlow.value = data.north || []
    southFlow.value = data.south || []
    setTimeout(renderChart, 100)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

const netNorthTotal = computed(() => {
  return northFlow.value.reduce((sum, d) => sum + (d.net_inflow || 0), 0)
})

function renderChart() {
  if (!chartRef.value || !northFlow.value.length) return
  if (!chart) chart = echarts.init(chartRef.value, appStore.isDark ? 'dark' : undefined)

  const dates = northFlow.value.map(d => d.date)
  const netData = northFlow.value.map(d => d.net_inflow)

  chart.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', top: 10, bottom: 10 },
    xAxis: { type: 'category', data: dates, axisLabel: { fontSize: 10, formatter: (v: string) => v.slice(5) } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => (v / 1e8).toFixed(1) + '亿' } },
    series: [{
      type: 'bar',
      data: netData.map(v => v || 0),
      itemStyle: {
        color: (p: any) => (p.value >= 0 ? '#CF1726' : '#19A55E'),
        borderRadius: [2, 2, 0, 0],
      },
    }],
  }, true)
}

function changeDays(d: number) {
  days.value = d
  fetchData()
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">资金流向</h1>
        <p class="text-sm text-gray-400 mt-1">追踪北向资金（外资流入A股）和南向资金（内资流入港股）</p>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 gap-3">
        <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <div class="text-xs text-gray-400 mb-1">北向资金累计净流入</div>
          <div class="text-xl font-bold" :class="netNorthTotal >= 0 ? 'text-market-up' : 'text-market-down'">
            {{ (netNorthTotal / 1e8).toFixed(2) }} 亿
          </div>
          <div class="text-xs text-gray-400 mt-1">近 {{ days }} 个交易日</div>
        </div>
        <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <div class="text-xs text-gray-400 mb-1">最新交易日</div>
          <div class="text-xl font-bold" :class="(northFlow[northFlow.length - 1]?.net_inflow || 0) >= 0 ? 'text-market-up' : 'text-market-down'">
            {{ northFlow.length ? ((northFlow[northFlow.length - 1].net_inflow || 0) / 1e8).toFixed(2) : '--' }} 亿
          </div>
          <div class="text-xs text-gray-400 mt-1">{{ northFlow[northFlow.length - 1]?.date || '--' }}</div>
        </div>
      </div>

      <!-- Time range buttons -->
      <div class="flex gap-2">
        <button v-for="d in [7, 30, 90]" :key="d"
          @click="changeDays(d)"
          class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
          :class="days === d ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
        >近 {{ d }} 天</button>
      </div>

      <!-- Chart -->
      <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <h3 class="text-sm font-medium text-gray-500 mb-3">北向资金净流入</h3>
        <div v-if="loading" class="h-80 animate-pulse bg-gray-100 dark:bg-gray-800 rounded" />
        <div v-else-if="!northFlow.length" class="h-80 flex items-center justify-center text-gray-400">暂无数据</div>
        <div v-else ref="chartRef" class="h-80 w-full" />
      </div>

      <!-- Data table -->
      <div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 overflow-hidden">
        <div class="px-4 py-2 text-sm font-medium text-gray-500 border-b">北向资金明细</div>
        <div class="max-h-96 overflow-y-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="text-xs text-gray-400">
                <th class="px-4 py-2 text-left">日期</th>
                <th class="px-4 py-2 text-right">净流入（亿）</th>
                <th class="px-4 py-2 text-right">累计余额（亿）</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!northFlow.length"><td colspan="3" class="px-4 py-8 text-center text-gray-400">暂无数据</td></tr>
              <tr v-for="f in [...northFlow].reverse().slice(0, 20)" :key="f.date" class="border-t border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-4 py-2 dark:text-white">{{ f.date }}</td>
                <td class="px-4 py-2 text-right" :class="(f.net_inflow || 0) >= 0 ? 'text-market-up' : 'text-market-down'">
                  {{ f.net_inflow ? (f.net_inflow / 1e8).toFixed(2) : '--' }}
                </td>
                <td class="px-4 py-2 text-right dark:text-white">{{ f.balance ? (f.balance / 1e8).toFixed(2) : '--' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </AppShell>
</template>
