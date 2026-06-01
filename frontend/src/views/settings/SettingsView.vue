<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

const apiUrl = ref(localStorage.getItem('api-url') || '')
const mockEnabled = ref(localStorage.getItem('mock-api') !== 'false')
const saveMsg = ref('')

function saveApiConfig() {
  if (apiUrl.value) {
    localStorage.setItem('api-url', apiUrl.value)
  } else {
    localStorage.removeItem('api-url')
  }
  localStorage.setItem('mock-api', mockEnabled.value ? 'true' : 'false')
  saveMsg.value = '✅ 已保存，刷新页面生效'
  setTimeout(() => saveMsg.value = '', 3000)
}

function resetToDefault() {
  localStorage.removeItem('api-url')
  localStorage.removeItem('mock-api')
  apiUrl.value = ''
  mockEnabled.value = true
  saveMsg.value = '✅ 已恢复默认，刷新页面生效'
  setTimeout(() => saveMsg.value = '', 3000)
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-2xl mx-auto px-4 py-4 space-y-5">
      <h1 class="text-xl font-bold dark:text-white">设置</h1>

      <!-- API Connection -->
      <section class="card p-4 space-y-4">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">数据源设置</h2>

        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm dark:text-white">使用 Mock 数据</span>
            <p class="text-xs text-gray-400 mt-0.5">{{ mockEnabled ? '使用内置模拟数据，无需服务器' : '连接真实后端 API' }}</p>
          </div>
          <button
            @click="mockEnabled = !mockEnabled"
            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
            :class="mockEnabled ? 'bg-gray-300 dark:bg-gray-600' : 'bg-primary'"
          >
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="!mockEnabled ? 'translate-x-5' : ''" />
          </button>
        </div>

        <div v-if="!mockEnabled">
          <label class="text-xs text-gray-500">后端 API 地址</label>
          <input
            v-model="apiUrl"
            type="text"
            placeholder="http://49.232.49.175:8000/api/v1"
            class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
          />
          <p class="text-xs text-gray-400 mt-1">填写你的服务器 API 地址，留空使用默认</p>
        </div>

        <div class="flex items-center gap-2">
          <button @click="saveApiConfig" class="px-4 py-1.5 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors">保存</button>
          <button @click="resetToDefault" class="px-3 py-1.5 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">恢复默认</button>
          <span v-if="saveMsg" class="text-xs text-green-600">{{ saveMsg }}</span>
        </div>
      </section>

      <!-- Appearance -->
      <section class="card p-4 space-y-4">
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
      <section class="card p-4 space-y-4">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide">学习</h2>
        <div class="flex items-center justify-between">
          <div>
            <span class="text-sm dark:text-white">学习模式</span>
            <p class="text-xs text-gray-400 mt-0.5">开启后，所有金融术语会高亮并可点击查看解释</p>
          </div>
          <button
            @click="appStore.toggleLearningMode()"
            class="relative w-11 h-6 rounded-full transition-colors shrink-0"
            :class="appStore.learningMode ? 'bg-primary' : 'bg-gray-300 dark:bg-gray-600'"
          >
            <span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform" :class="appStore.learningMode ? 'translate-x-5' : ''" />
          </button>
        </div>
      </section>

      <!-- About -->
      <section class="card p-4">
        <h2 class="text-sm font-medium text-gray-500 uppercase tracking-wide mb-3">关于</h2>
        <div class="text-sm dark:text-white space-y-1">
          <p>远见 v0.3.0</p>
          <p class="text-xs text-gray-400">洞察趋势，智选未来 · AI驱动的智能投资分析</p>
          <p class="text-xs text-gray-400 mt-1">开发者：Leon</p>
          <p class="text-xs text-gray-400 mt-2">📡 后端服务器: 49.232.49.175:8000</p>
          <p class="text-xs text-gray-400">⚠️ 所有数据仅供参考学习，不构成投资建议</p>
        </div>
      </section>
    </div>
  </AppShell>
</template>
