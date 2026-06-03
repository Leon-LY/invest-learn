<script setup lang="ts">
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'

const props = defineProps<{
  value: number | null
  type?: 'price' | 'percent'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showSign?: boolean
}>()

const appStore = useAppStore()

const colorClass = computed(() => {
  if (props.value === null || props.value === undefined) return 'text-flat'
  const v = props.value
  if (v === 0) return 'text-flat'
  return v > 0 ? 'text-up' : 'text-down'
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '--'
  if (props.type === 'percent') {
    const sign = props.showSign !== false && props.value > 0 ? '+' : ''
    return `${sign}${props.value.toFixed(2)}%`
  }
  return props.value.toFixed(2)
})

const sizeClass = computed(() => ({
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-lg font-semibold',
  xl: 'text-2xl font-bold',
}[props.size || 'md']))
</script>

<template>
  <span :class="[colorClass, sizeClass, props.value != null && props.value > 0 ? 'price-up' : props.value != null && props.value < 0 ? 'price-down' : '']" class="tabular-nums font-mono">
    {{ displayValue }}
  </span>
</template>
