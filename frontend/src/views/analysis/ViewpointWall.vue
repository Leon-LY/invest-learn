<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const viewpoints = ref<any[]>([])
const author = ref('')
const source = ref('抖音')
const link = ref('')
const content = ref('')
const imageFiles = ref<File[]>([])
const imagePreviews = ref<string[]>([])
const submitting = ref(false)
const loading = ref(true)

onMounted(async () => {
  try { viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[] } catch(e) {}
  finally { loading.value = false }
})

function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files || !files.length) return
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    imageFiles.value.push(file)
    const reader = new FileReader()
    const idx = imageFiles.value.length - 1
    reader.onload = () => { imagePreviews.value[idx] = reader.result as string }
    reader.readAsDataURL(file)
  }
}
function removeImage(idx: number) {
  imageFiles.value.splice(idx, 1)
  imagePreviews.value.splice(idx, 1)
}

async function submit() {
  if (!content.value.trim() && !imageFiles.value.length) return
  submitting.value = true
  try {
    const payload: Record<string, any> = { source: source.value, author: author.value, link: link.value, content: content.value }
    if (imageFiles.value.length) {
      payload.image = imagePreviews.value.map(p => p.split(',')[1]).join('||')
    }
    await newsApi.submitViewpoint(payload)
    content.value = ''; author.value = ''; link.value = ''
    imageFiles.value = []; imagePreviews.value = []
    viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[]
  } catch(e: any) { alert('提交失败: ' + (e?.response?.data?.error || e?.message || '未知错误')) }
  finally { submitting.value = false }
}

const platforms = ['抖音', '小红书', 'B站', '微博', '雪球', '天天基金', '支付宝', '微信', '其他']
const presetFunds = ['005827','161725','110027','510300','163406']
const filterAuthor = ref('')

const filteredViewpoints = computed(() => {
  if (!filterAuthor.value) return viewpoints.value
  return viewpoints.value.filter((v: any) => v.author === filterAuthor.value)
})
const uniqueAuthors = computed(() => [...new Set(viewpoints.value.map((v: any) => v.author).filter(Boolean))])
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">💬 市场声音</h1>
        <p class="text-sm text-gray-400 mt-1">刷到观点或截图？贴进来，AI 帮你分析</p>
      </div>

      <!-- Input card -->
      <div class="card p-5 space-y-4">
        <div class="grid grid-cols-2 gap-3">
          <select v-model="source" class="px-3 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white">
            <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
          </select>
          <input v-model="author" placeholder="大神名称（统一用同一个名）" class="px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white" />
        </div>
        <input v-model="link" placeholder="链接（选填）" class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white" />
        <div class="flex gap-2 text-xs flex-wrap">
          <button @click="content='买入 '" class="px-2 py-1 rounded bg-up-bg text-up">买入</button>
          <button @click="content='卖出 '" class="px-2 py-1 rounded bg-down-bg text-down">卖出</button>
          <button @click="content='调仓 '" class="px-2 py-1 rounded bg-blue-50 text-blue-600">调仓</button>
          <button @click="content='加仓 '" class="px-2 py-1 rounded bg-orange-50 text-orange-600">加仓</button>
        </div>
        <textarea v-model="content" placeholder="如：买入 005827 50000 看到1116今天建仓了张坤" rows="4"
          class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white resize-none" />
        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 px-4 py-2.5 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl cursor-pointer hover:border-primary transition-colors text-sm text-gray-500">
            <span>📷</span>
            <span>{{ imageFiles.length ? imageFiles.length + '张' : '上传截图（可多选）' }}</span>
            <input type="file" accept="image/*" @change="onFileChange" multiple class="hidden" />
          </label>
        </div>
        <div v-if="imagePreviews.length" class="flex gap-2 overflow-x-auto pb-1">
          <div v-for="(p, i) in imagePreviews" :key="i" class="relative shrink-0">
            <img :src="p" class="h-32 rounded-lg border border-gray-200 dark:border-gray-700" />
            <button @click="removeImage(i)" class="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full text-xs">x</button>
          </div>
        </div>
        <div class="flex items-center gap-3 pt-2">
          <span class="text-xs text-gray-400 truncate">🤖 AI 自动分析 {{ imageFiles.length ? '· ' + imageFiles.length + '张截图' : '' }}</span>
          <button @click="submit" :disabled="submitting || (!content.trim() && !imageFiles.length)"
            class="shrink-0 px-6 py-2.5 bg-primary text-white text-sm font-medium rounded-xl disabled:opacity-50">
            {{ submitting ? '分析中...' : '提交分析' }}
          </button>
        </div>
      </div>

      <!-- Author filter -->
      <div v-if="uniqueAuthors.length" class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button @click="filterAuthor=''" class="shrink-0 text-xs px-3 py-1 rounded-full transition-all"
          :class="!filterAuthor?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-500'">全部</button>
        <button v-for="a in uniqueAuthors" :key="a" @click="filterAuthor=a"
          class="shrink-0 text-xs px-3 py-1 rounded-full transition-all"
          :class="filterAuthor===a?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-500'">{{ a }}</button>
      </div>
      <div v-if="filterAuthor" class="text-xs text-gray-400">
        追踪 <span class="font-medium text-primary">{{ filterAuthor }}</span> · {{ filteredViewpoints.length }} 条记录
      </div>

      <!-- List -->
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="skeleton h-24 rounded-xl" />
      </div>
      <div v-else-if="!filteredViewpoints.length" class="card p-10 text-center text-sm text-gray-400">
        <div class="text-4xl mb-3">💬</div>
        <p>还没有观点，快去录入第一个吧</p>
      </div>
      <div v-else class="space-y-3">
        <div v-for="v in filteredViewpoints" :key="v.id" class="card p-4">
          <div class="flex items-center gap-2 mb-2 flex-wrap">
            <span class="text-xs px-2 py-0.5 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">{{ v.source }}</span>
            <span v-if="v.author" class="text-xs text-gray-500 font-medium">{{ v.author }}</span>
            <span v-if="v.direction" class="text-xs px-2 py-0.5 rounded-full font-medium ml-auto"
              :class="v.direction==='看多'?'bg-up-bg text-up':v.direction==='看空'?'bg-down-bg text-down':'bg-gray-100 text-gray-500'">{{ v.direction }}</span>
            <span v-if="v.confidence" class="text-xs text-gray-400">🤖 {{ v.confidence }}%</span>
            <span v-if="v.created_at" class="text-xs text-gray-400">{{ v.created_at?.slice(0,16)?.replace('T',' ') }}</span>
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
              <div v-if="v.ai_summary" class="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800">
                <div class="text-xs font-medium text-blue-600 dark:text-blue-400 mb-1">🤖 AI 分析</div>
                <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{{ v.ai_summary }}</p>
              </div>
              <div v-if="v.related_funds?.length" class="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-800">
                <div class="text-xs font-medium text-amber-600 dark:text-amber-400 mb-1">📊 相关基金</div>
                <div v-for="f in v.related_funds" :key="typeof f==='string'?f:f.code" class="text-sm">
                  <span class="font-mono font-medium text-gray-800 dark:text-gray-200">{{ typeof f==='string'?f:f.code }}</span>
                  <span v-if="typeof f!=='string' && f.name" class="text-gray-500 ml-1">- {{ f.name }}</span>
                  <span v-if="typeof f!=='string' && f.impact" class="text-xs text-gray-400 block mt-0.5">{{ f.impact }}</span>
                </div>
              </div>
              <div v-if="v.original_content || v.image_base64" class="p-3 rounded-lg bg-gray-50 dark:bg-gray-800/50">
                <div class="text-xs font-medium text-gray-400 mb-2">📝 原始提交</div>
                <p v-if="v.original_content" class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap leading-relaxed">{{ v.original_content }}</p>
                <div v-if="v.image_base64" class="flex gap-2 overflow-x-auto mt-2">
                  <img v-for="(img, i) in v.image_base64.split('||')" :key="i" :src="'data:image/jpeg;base64,'+img" class="max-h-48 rounded-lg border border-gray-200 dark:border-gray-700" />
                </div>
              </div>
            </div>
          </details>
        </div>
      </div>
    </div>
  </AppShell>
</template>
