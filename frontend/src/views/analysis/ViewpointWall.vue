<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const viewpoints = ref<any[]>([])
const content = ref('')
const author = ref('')
const source = ref('抖音')
const link = ref('')
const submitting = ref(false)
const loading = ref(true)

onMounted(async () => {
  try { viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[] } catch(e) {}
  finally { loading.value = false }
})

async function submit() {
  if (!content.value.trim()) return
  submitting.value = true
  try {
    await newsApi.submitViewpoint({
      content: content.value,
      source: source.value,
      author: author.value,
      link: link.value,
    })
    content.value = ''; author.value = ''; link.value = ''
    viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[]
  } catch(e) { alert('提交失败') }
  finally { submitting.value = false }
}

const platforms = ['抖音', '小红书', 'B站', '微博', '雪球', '微信', '其他']
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">💬 市场声音</h1>
        <p class="text-sm text-gray-400 mt-1">刷到有价值的投资观点？贴进来，AI 帮你分析归类</p>
      </div>

      <!-- Input -->
      <div class="card p-4 space-y-2">
        <div class="flex gap-2">
          <select v-model="source" class="w-20 px-2 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white">
            <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
          </select>
          <input v-model="author" placeholder="UP主名称（选填）" class="w-32 px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white" />
          <input v-model="link" placeholder="视频/文章链接（选填）" class="flex-1 px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white min-w-0" />
        </div>
        <textarea v-model="content" placeholder="粘贴观点内容...&#10;&#10;比如：这个UP主说新能源已经见底，锂矿价格从60万跌到10万，宁德时代Q1业绩超预期，整个板块估值近5年最低" rows="5"
          class="w-full px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white resize-none" />
        <div class="flex items-center justify-between">
          <span class="text-xs text-gray-400">🤖 DeepSeek 自动分析方向、标签、关联基金</span>
          <button @click="submit" :disabled="submitting" class="px-5 py-2 bg-primary text-white text-sm font-medium rounded-lg disabled:opacity-50">
            {{ submitting ? '分析中...' : '提交' }}
          </button>
        </div>
      </div>

      <!-- List -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="skeleton h-24 rounded-xl" />
      </div>
      <div v-else-if="!viewpoints.length" class="card p-8 text-center text-sm text-gray-400">
        <div class="text-3xl mb-2">💬</div>
        <p>还没有观点，快去录入第一个吧 👆</p>
        <p class="text-xs mt-1">抖音/小红书/B站刷到的都行</p>
      </div>
      <div v-else class="space-y-3">
        <div v-for="v in viewpoints" :key="v.id" class="card p-4">
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">{{ v.source }}</span>
            <span v-if="v.author" class="text-xs text-gray-500 font-medium">{{ v.author }}</span>
            <span v-if="v.direction" class="text-xs px-2 py-0.5 rounded-full font-medium ml-auto"
              :class="v.direction==='看多'?'bg-up-bg text-up':v.direction==='看空'?'bg-down-bg text-down':'bg-gray-100 text-gray-500'">{{ v.direction }}</span>
            <span v-if="v.confidence" class="text-xs text-gray-400">🤖 {{ v.confidence }}%</span>
          </div>
          <h3 class="font-medium text-sm dark:text-white mb-1.5">{{ v.ai_title || '观点分析' }}</h3>
          <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-2 mb-2">{{ v.ai_summary || v.content.slice(0,100) }}</p>
          <div class="flex items-center gap-2 flex-wrap">
            <span v-for="t in v.tags" :key="t" class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">{{ t }}</span>
            <span v-for="f in (v.related_funds||[])" :key="typeof f==='string'?f:f.code" class="text-xs px-1.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 font-mono">{{ typeof f==='string'?f:f.code }}</span>
          </div>
          <details class="mt-2">
            <summary class="text-xs text-gray-400 cursor-pointer">查看原文</summary>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 p-2 rounded bg-gray-50 dark:bg-gray-800/50 whitespace-pre-wrap">{{ v.content }}</p>
          </details>
        </div>
      </div>
    </div>
  </AppShell>
</template>
