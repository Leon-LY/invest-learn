<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const props = defineProps<{ value: number | null }>()

const appStore = useAppStore()

const isUp = computed(() => (props.value || 0) > 0)
const isDown = computed(() => (props.value || 0) < 0)

const bgClass = computed(() => {
  if (!props.value) return 'bg-gray-100 dark:bg-gray-800 text-gray-500'
  if (appStore.colorScheme === 'red_up_green_down') {
    return isUp.value ? 'bg-market-up-bg text-market-up' : 'bg-market-down-bg text-market-down'
  }
  return isUp.value ? 'bg-market-down-bg text-market-down' : 'bg-market-up-bg text-market-up'
})

const display = computed(() => {
  if (props.value === null || props.value === undefined) return '--'
  const sign = props.value > 0 ? '+' : ''
  return `${sign}${props.value.toFixed(2)}%`
})
</script>

<template>
  <span :class="bgClass" class="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium tabular-nums font-mono">
    {{ display }}
  </span>
</template>
