<script setup lang="ts">
defineProps<{ lines?: number }>()
</script>

<template>
  <div class="animate-pulse bg-white dark:bg-gray-900 rounded-lg p-4 border border-gray-100 dark:border-gray-800">
    <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-3" />
    <div v-for="i in (lines || 3)" :key="i" class="h-2 bg-gray-100 dark:bg-gray-800 rounded mb-2" :class="i === lines ? 'w-2/3' : 'w-full'" />
  </div>
</template>
