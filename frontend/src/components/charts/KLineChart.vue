<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as echarts from 'echarts'
import type { KLineItem } from '@/types/market'
import { useAppStore } from '@/stores/app'

const props = defineProps<{
  data: KLineItem[]
  height?: string
}>()

const appStore = useAppStore()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function initChart() {
  if (!chartRef.value || !props.data.length) return

  if (!chart) {
    chart = echarts.init(chartRef.value, appStore.isDark ? 'dark' : undefined)
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(chartRef.value)
  }

  const dates = props.data.map(d => d.date)
  const klineData = props.data.map(d => [d.open, d.close, d.low, d.high])
  const volumes = props.data.map(d => d.volume)
  const ma5 = calcMA(5)
  const ma10 = calcMA(10)
  const ma20 = calcMA(20)

  const isUp = (idx: number) => {
    if (idx >= props.data.length) return true
    const d = props.data[idx]
    return (d.close || 0) >= (d.open || 0)
  }

  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    grid: [
      { left: '8%', right: '3%', top: '5%', height: '60%' },
      { left: '8%', right: '3%', top: '75%', height: '15%' },
    ],
    xAxis: [
      { type: 'category', data: dates, gridIndex: 0, axisLine: { onZero: false }, axisTick: { show: false }, axisLabel: { show: false } },
      { type: 'category', data: dates, gridIndex: 1, axisLabel: { fontSize: 10, formatter: (v: string) => v.slice(5) } },
    ],
    yAxis: [
      { type: 'value', gridIndex: 0, scale: true, splitLine: { lineStyle: { color: appStore.isDark ? '#333' : '#eee', type: 'dashed' } } },
      { type: 'value', gridIndex: 1, axisLabel: { show: false }, splitLine: { show: false } },
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: klineData,
        xAxisIndex: 0, yAxisIndex: 0,
        itemStyle: {
          color: '#CF1726', color0: '#19A55E',
          borderColor: '#CF1726', borderColor0: '#19A55E',
        },
      },
      { name: 'MA5', type: 'line', data: ma5, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1, color: '#f5a623' }, symbol: 'none' },
      { name: 'MA10', type: 'line', data: ma10, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1, color: '#4a90d9' }, symbol: 'none' },
      { name: 'MA20', type: 'line', data: ma20, xAxisIndex: 0, yAxisIndex: 0, smooth: true, lineStyle: { width: 1, color: '#e85d9a' }, symbol: 'none' },
      {
        name: '成交量', type: 'bar', data: volumes, xAxisIndex: 1, yAxisIndex: 1,
        itemStyle: {
          color: (params: any) => isUp(params.dataIndex) ? '#CF1726' : '#19A55E',
        },
      },
    ],
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        const k = params.find((p: any) => p.seriesName === 'K线')
        if (!k) return ''
        const idx = params[0].dataIndex
        const d = props.data[idx]
        return `日期: ${d.date}<br/>
          开: ${d.open} 高: ${d.high}<br/>
          低: ${d.low} 收: ${d.close}<br/>
          量: ${(d.volume || 0).toLocaleString()}`
      },
    },
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
      { type: 'slider', xAxisIndex: [0, 1], start: 50, end: 100, height: 20, bottom: 0 },
    ],
  }

  chart.setOption(option, true)
}

function calcMA(day: number): (number | null)[] {
  const result: (number | null)[] = []
  for (let i = 0; i < props.data.length; i++) {
    if (i < day - 1) { result.push(null); continue }
    let sum = 0
    for (let j = 0; j < day; j++) sum += props.data[i - j].close || 0
    result.push(+(sum / day).toFixed(2))
  }
  return result
}

watch(() => props.data.length, () => { if (props.data.length) initChart() })
watch(() => appStore.isDark, () => { if (chart) { chart.dispose(); chart = null; initChart() } })
onMounted(() => { setTimeout(initChart, 100) })
onUnmounted(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
})
</script>

<template>
  <div ref="chartRef" :style="{ height: height || '400px', width: '100%' }" />
</template>
