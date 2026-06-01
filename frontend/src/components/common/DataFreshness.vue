<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

const props = defineProps<{ lastFetched: number; label?: string }>()

const now = ref(Date.now())
let timer: ReturnType<typeof setInterval>

onMounted(() => { timer = setInterval(() => now.value = Date.now(), 10000) })
onUnmounted(() => clearInterval(timer))

const secondsAgo = computed(() => Math.floor((now.value - props.lastFetched) / 1000))
const minutesAgo = computed(() => Math.floor(secondsAgo.value / 60))

const colorClass = computed(() => {
  if (secondsAgo.value < 300) return 'text-green-600 dark:text-green-400'
  if (secondsAgo.value < 900) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-500'
})

const display = computed(() => {
  if (secondsAgo.value < 60) return `${secondsAgo.value}秒前`
  return `${minutesAgo.value}分钟前`
})
</script>

<template>
  <span :class="colorClass" class="text-xs">
    <span class="inline-block w-1.5 h-1.5 rounded-full mr-1" :class="colorClass.replace('text-', 'bg-')" />
    {{ label || '更新于' }} {{ display }}
  </span>
</template>
