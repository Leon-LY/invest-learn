<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { learnApi } from '@/api/learn'

const terms = ref<any[]>([])
const query = ref('')
const category = ref('')
const loading = ref(true)

const categories = [
  { v: '', l: '全部' }, { v: 'fundamental', l: '基本面' }, { v: 'technical', l: '技术分析' }, { v: 'fund', l: '基金' }, { v: 'risk', l: '风险管理' }, { v: 'general', l: '通用' },
]

onMounted(() => fetchTerms())

async function fetchTerms() {
  loading.value = true
  try {
    terms.value = (await learnApi.searchGlossary({ q: query.value || undefined, category: category.value || undefined })) as unknown as any[]
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

let debounceTimer: ReturnType<typeof setTimeout>
function onInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(fetchTerms, 300)
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-4 space-y-4">
      <h1 class="text-xl font-bold dark:text-white">术语百科</h1>

      <div class="flex gap-2">
        <input
          v-model="query" @input="onInput"
          placeholder="搜索术语..."
          class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
      </div>

      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button v-for="c in categories" :key="c.v" @click="category = c.v; fetchTerms()"
          class="px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors"
          :class="category === c.v ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
        >{{ c.l }}</button>
      </div>

      <div v-if="loading" class="space-y-2">
        <div v-for="i in 8" :key="i" class="animate-pulse h-16 bg-gray-100 dark:bg-gray-800 rounded-xl" />
      </div>
      <div v-else-if="!terms.length" class="text-center py-12 text-gray-400">未找到相关术语</div>
      <div v-else class="space-y-3">
        <div v-for="t in terms" :key="t.term" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
          <div class="flex items-center gap-2 mb-2">
            <h3 class="font-semibold text-sm dark:text-white">{{ t.term }}</h3>
            <span v-if="t.term_en" class="text-xs text-gray-400">{{ t.term_en }}</span>
            <span class="px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded text-gray-500">{{ t.category || '通用' }}</span>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ t.definition }}</p>
        </div>
      </div>
    </div>
  </AppShell>
</template>
