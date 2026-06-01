<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { useAppStore } from '@/stores/app'

const props = defineProps<{
  data: Array<{ date: string; value: number; name?: string }>
  title?: string
  color?: string
  height?: string
}>()

const appStore = useAppStore()
const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

function init() {
  if (!chartRef.value || !props.data.length) return
  if (!chart) chart = echarts.init(chartRef.value, appStore.isDark ? 'dark' : undefined)

  chart.setOption({
    backgroundColor: 'transparent',
    grid: { left: '3%', right: '3%', top: 10, bottom: 10 },
    xAxis: { type: 'category', data: props.data.map(d => d.date), show: false },
    yAxis: { type: 'value', show: false, scale: true },
    series: [{
      type: 'line', data: props.data.map(d => d.value),
      smooth: true, symbol: 'none',
      lineStyle: { width: 2, color: props.color || '#8b5cf6' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: props.color ? props.color + '40' : '#8b5cf640' },
        { offset: 1, color: 'transparent' },
      ])},
    }],
  }, true)
}

watch(() => props.data, init, { deep: true })
onMounted(() => setTimeout(init, 50))
onUnmounted(() => chart?.dispose())
</script>

<template>
  <div ref="chartRef" :style="{ height: height || '40px', width: '100%' }" />
</template>
