<script setup lang="ts">
import AppShell from '@/layouts/AppShell.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<template>
  <AppShell showBack>
    <div class="max-w-2xl mx-auto px-4 py-4 space-y-5">
      <h1 class="text-xl font-bold dark:text-white">设置</h1>

      <!-- Appearance -->
      <section class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800 space-y-4">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">外观</h2>
        <div class="flex items-center justify-between">
          <span class="text-sm dark:text-white">主题模式</span>
          <select
            :value="appStore.theme"
            @change="appStore.setTheme(($event.target as HTMLSelectElement).value as any)"
            class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 bg-gray-50 dark:bg-gray-800 dark:text-white"
          >
            <option value="light">☀️ 亮色</option>
            <option value="dark">🌙 暗色</option>
            <option value="system">💻 跟随系统</option>
          </select>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm dark:text-white">颜色方案</span>
          <select
            :value="appStore.colorScheme"
            @change="appStore.setColorScheme(($event.target as HTMLSelectElement).value as any)"
            class="text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 bg-gray-50 dark:bg-gray-800 dark:text-white"
          >
            <option value="red_up_green_down">红涨绿跌（中国习惯）</option>
            <option value="green_up_red_down">绿涨红跌（国际习惯）</option>
          </select>
        </div>
      </section>

      <!-- Learning -->
      <section class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800 space-y-4">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">学习</h2>
        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm dark:text-white">学习模式</span>
            <p class="text-xs text-gray-400 mt-0.5">开启后，所有金融术语会高亮并可点击查看解释</p>
          </div>
          <button
            @click="appStore.toggleLearningMode()"
            class="relative w-11 h-6 rounded-full transition-colors"
            :class="appStore.learningMode ? 'bg-purple-600' : 'bg-gray-300 dark:bg-gray-600'"
          >
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="appStore.learningMode ? 'translate-x-5' : ''" />
          </button>
        </div>
      </section>

      <!-- About -->
      <section class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">关于</h2>
        <div class="text-sm dark:text-white space-y-1">
          <p>InvestLearn 投资学习平台 v0.1.0</p>
          <p class="text-xs text-gray-400">数据来源：AKShare、yfinance、各财经网站 RSS</p>
          <p class="text-xs text-gray-400">免责声明：所有数据仅供参考学习，不构成投资建议</p>
        </div>
      </section>
    </div>
  </AppShell>
</template>
