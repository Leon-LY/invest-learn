<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const viewpoints = ref<any[]>([])
const author = ref('')
const source = ref('抖音')
const link = ref('')
const content = ref('')
const imageFile = ref<File | null>(null)
const imagePreview = ref('')
const submitting = ref(false)
const loading = ref(true)

onMounted(async () => {
  try { viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[] } catch(e) {}
  finally { loading.value = false }
})

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  imageFile.value = file
  const reader = new FileReader()
  reader.onload = () => { imagePreview.value = reader.result as string }
  reader.readAsDataURL(file)
}

async function submit() {
  if (!content.value.trim() && !imageFile.value) return
  submitting.value = true
  try {
    const payload: Record<string, any> = { source: source.value, author: author.value, link: link.value, content: content.value }
    if (imageFile.value) {
      const b64 = imagePreview.value.split(',')[1]
      payload.image = b64
      payload.image_analysis = true
    }
    await newsApi.submitViewpoint(payload)
    content.value = ''; author.value = ''; link.value = ''
    imageFile.value = null; imagePreview.value = ''
    viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[]
  } catch(e: any) { alert('提交失败: ' + (e?.response?.data?.error || e?.message || '未知错误')) }
  finally { submitting.value = false }
}

const platforms = ['抖音', '小红书', 'B站', '微博', '雪球', '微信', '其他']
const presetFunds = ['005827','161725','110027','510300','163406']
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">💬 市场声音</h1>
        <p class="text-sm text-gray-400 mt-1">刷到有价值的观点或截图？贴进来，AI 帮你分析</p>
      </div>

      <!-- Input card -->
      <div class="card p-5 space-y-4">
        <!-- Row 1: Platform + Author + Link -->
        <div class="grid grid-cols-2 gap-3">
          <select v-model="source" class="px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white">
            <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
          </select>
          <input v-model="author" placeholder="UP主名称（选填）" class="px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white" />
        </div>

        <!-- Row 2: Link -->
        <input v-model="link" placeholder="视频 / 文章链接（选填）" class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white" />

        <!-- Row 3: Content textarea -->
        <textarea v-model="content" placeholder="粘贴观点内容...&#10;&#10;例如：这个UP主说新能源已经见底了，锂矿价格从60万跌到10万，宁德时代Q1业绩超预期" rows="5"
          class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white resize-none" />

        <!-- Row 4: Image upload -->
        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl cursor-pointer hover:border-primary transition-colors text-sm text-gray-500">
            <span>📷</span>
            <span>{{ imageFile ? imageFile.name.slice(0,20) : '上传截图（选填）' }}</span>
            <input type="file" accept="image/*" @change="onFileChange" class="hidden" />
          </label>
          <button v-if="imagePreview" @click="imageFile=null;imagePreview=''" class="text-xs text-red-400 hover:text-red-500">清除</button>
        </div>
        <!-- Preview -->
        <div v-if="imagePreview" class="relative">
          <img :src="imagePreview" class="max-h-48 rounded-lg border border-gray-200 dark:border-gray-700" />
        </div>

        <!-- Submit -->
        <div class="flex items-center gap-3 pt-2">
          <span class="text-xs text-gray-400 truncate">🤖 AI 自动分析 {{ imageFile ? '· 截图视觉识别' : '' }}</span>
          <button @click="submit" :disabled="submitting || (!content.trim() && !imageFile)"
            class="shrink-0 px-6 py-2.5 bg-primary text-white text-sm font-medium rounded-xl disabled:opacity-50 transition-opacity">
            {{ submitting ? '分析中...' : '提交分析' }}
          </button>
        </div>
      </div>

      <!-- Quick presets -->
      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <span class="text-xs text-gray-400 self-center shrink-0">常见基金：</span>
        <button v-for="c in presetFunds" :key="c" @click="content=content+' '+c"
          class="shrink-0 text-xs px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 hover:bg-primary/10 hover:text-primary transition-colors">{{ c }}</button>
      </div>

      <!-- List -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="skeleton h-24 rounded-xl" />
      </div>
      <div v-else-if="!viewpoints.length" class="card p-10 text-center text-sm text-gray-400">
        <div class="text-4xl mb-3">💬</div>
        <p>还没有观点，快去录入第一个吧</p>
        <p class="text-xs mt-1">抖音/小红书/B站刷到的都行，截图也能分析</p>
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
          <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 mb-2 leading-relaxed">{{ v.ai_summary || v.content.slice(0,150) }}</p>
          <div class="flex items-center gap-2 flex-wrap mb-2">
            <span v-for="t in v.tags" :key="t" class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">{{ t }}</span>
            <span v-for="f in (v.related_funds||[])" :key="typeof f==='string'?f:f.code" class="text-xs px-1.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 font-mono">{{ typeof f==='string'?f:f.code }}</span>
          </div>
          <details class="mt-1">
            <summary class="text-xs text-primary cursor-pointer hover:underline">查看完整分析</summary>
            <div class="mt-3 space-y-3">
              <!-- AI Analysis -->
              <div v-if="v.ai_summary" class="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800">
                <div class="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">🤖 AI 分析</div>
                <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{{ v.ai_summary }}</p>
              </div>
              <!-- Affected funds -->
              <div v-if="v.related_funds?.length" class="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800">
                <div class="text-xs font-medium text-amber-600 dark:text-amber-400 mb-1">📊 相关影响</div>
                <div class="space-y-1.5">
                  <div v-for="f in v.related_funds" :key="typeof f==='string'?f:f.code" class="text-sm">
                    <span class="font-mono font-medium text-gray-800 dark:text-gray-200">{{ typeof f==='string'?f:f.code }}</span>
                    <span v-if="typeof f!=='string' && f.name" class="text-gray-500 ml-1">- {{ f.name }}</span>
                    <span v-if="typeof f!=='string' && f.impact" class="text-xs text-gray-400 block mt-0.5">{{ f.impact }}</span>
                  </div>
                </div>
              </div>
              <!-- Tags -->
              <div v-if="v.tags?.length" class="flex flex-wrap gap-1.5">
                <span v-for="t in v.tags" :key="t" class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">{{ t }}</span>
              </div>
              <!-- Original content -->
              <div class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <div class="text-xs font-medium text-gray-400 mb-1">📝 原文 / 提取内容</div>
                <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap leading-relaxed">{{ v.content }}</p>
              </div>
            </div>
          </details>
        </div>
      </div>
    </div>
  </AppShell>
</template>
