<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { newsApi } from '@/api/news'

const viewpoints = ref<any[]>([])
const author = ref('')
const source = ref('抖音')
const content = ref('')
const imageFiles = ref<File[]>([])
const imagePreviews = ref<string[]>([])
const submitting = ref(false)
const filterAuthor = ref('')

onMounted(async () => {
  try { viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[] } catch(e) {}
})

function onFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files?.length) return
  for (let i = 0; i < files.length; i++) {
    const file = files[i]; imageFiles.value.push(file)
    const reader = new FileReader(); const idx = imageFiles.value.length - 1
    reader.onload = () => { imagePreviews.value[idx] = reader.result as string }
    reader.readAsDataURL(file)
  }
}
function removeImage(idx: number) { imageFiles.value.splice(idx,1); imagePreviews.value.splice(idx,1) }

async function submit() {
  if (!content.value.trim() && !imageFiles.value.length) return
  submitting.value = true
  try {
    const payload: any = { source: source.value, author: author.value, content: content.value }
    if (imageFiles.value.length) payload.image = imagePreviews.value.map(p => p.split(',')[1]).join('||')
    await newsApi.submitViewpoint(payload)
    content.value = ''; author.value = ''; imageFiles.value = []; imagePreviews.value = []
    viewpoints.value = (await newsApi.getViewpoints(20)) as unknown as any[]
  } catch(e: any) { alert('提交失败: ' + (e?.response?.data?.error || e?.message || '')) }
  finally { submitting.value = false }
}

const filteredViewpoints = computed(() => {
  if (!filterAuthor.value) return viewpoints.value
  return viewpoints.value.filter((v: any) => v.author === filterAuthor.value)
})
const uniqueAuthors = computed(() => [...new Set(viewpoints.value.map((v: any) => v.author).filter(Boolean))])
const platforms = ['抖音','小红书','B站','微博','雪球','天天基金','支付宝','其他']
</script>

<template>
  <div class="space-y-3">
    <!-- Input -->
    <div class="card p-4 space-y-2">
      <div class="grid grid-cols-2 gap-2">
        <select v-model="source" class="px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white">
          <option v-for="p in platforms" :key="p" :value="p">{{ p }}</option>
        </select>
        <input v-model="author" placeholder="大神名称" class="px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white" />
      </div>
      <div class="flex gap-2 text-xs">
        <button @click="content='买入 '" class="px-2 py-1 rounded bg-up-bg text-up">买入</button>
        <button @click="content='卖出 '" class="px-2 py-1 rounded bg-down-bg text-down">卖出</button>
        <button @click="content='调仓 '" class="px-2 py-1 rounded bg-blue-50 text-blue-600">调仓</button>
        <button @click="content='加仓 '" class="px-2 py-1 rounded bg-orange-50 text-orange-600">加仓</button>
      </div>
      <textarea v-model="content" placeholder="如：买入 005827 50000 看到1116今天建仓了张坤" rows="3"
        class="w-full px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white resize-none" />
      <div class="flex items-center justify-between">
        <label class="flex items-center gap-1 px-3 py-1.5 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:border-primary text-xs text-gray-500">
          📷 {{ imageFiles.length ? imageFiles.length+'张' : '截图' }}
          <input type="file" accept="image/*" @change="onFileChange" multiple class="hidden" />
        </label>
        <button @click="submit" :disabled="submitting || (!content.trim() && !imageFiles.length)"
          class="px-4 py-2 bg-primary text-white text-xs font-medium rounded-lg disabled:opacity-50">{{ submitting?'分析中...':'提交' }}</button>
      </div>
      <div v-if="imagePreviews.length" class="flex gap-2 overflow-x-auto">
        <div v-for="(p,i) in imagePreviews" :key="i" class="relative shrink-0">
          <img :src="p" class="h-20 rounded" /><button @click="removeImage(i)" class="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white rounded-full text-[10px]">x</button>
        </div>
      </div>
    </div>

    <!-- Filter -->
    <div v-if="uniqueAuthors.length" class="flex gap-1 overflow-x-auto">
      <button @click="filterAuthor=''" class="shrink-0 text-xs px-2.5 py-1 rounded-full" :class="!filterAuthor?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-500'">全部</button>
      <button v-for="a in uniqueAuthors" :key="a" @click="filterAuthor=a" class="shrink-0 text-xs px-2.5 py-1 rounded-full" :class="filterAuthor===a?'bg-primary text-white':'bg-gray-100 dark:bg-gray-800 text-gray-500'">{{ a }}</button>
    </div>
    <div v-if="filterAuthor" class="text-xs text-gray-400">追踪 <span class="font-medium text-primary">{{ filterAuthor }}</span> · {{ filteredViewpoints.length }} 条</div>

    <!-- List -->
    <div v-for="v in filteredViewpoints" :key="v.id" class="card p-3">
      <div class="flex items-center gap-2 mb-1 flex-wrap">
        <span class="text-xs text-gray-400">{{ v.source }}</span>
        <span v-if="v.author" class="text-xs font-medium text-gray-500">{{ v.author }}</span>
        <span v-if="v.direction" class="text-xs px-1.5 py-0.5 rounded-full ml-auto font-medium" :class="v.direction==='看多'?'bg-up-bg text-up':v.direction==='看空'?'bg-down-bg text-down':'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400'">{{ v.direction }}</span>
        <span v-if="v.created_at" class="text-xs text-gray-400">{{ v.created_at?.slice(0,16)?.replace('T',' ') }}</span>
      </div>
      <h3 class="font-medium text-sm dark:text-white mb-1">{{ v.ai_title || '观点' }}</h3>
      <p class="text-xs text-gray-500 line-clamp-2 mb-1">{{ v.ai_summary || v.content.slice(0,100) }}</p>
      <div class="flex gap-1 flex-wrap">
        <span v-for="t in v.tags" :key="t" class="text-xs px-1.5 py-0.5 rounded-full bg-primary/10 text-primary">{{ t }}</span>
        <span v-for="f in (v.related_funds||[])" :key="typeof f==='string'?f:f.code" class="text-xs px-1.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 font-mono">{{ typeof f==='string'?f:f.code }}</span>
      </div>
      <details class="mt-1">
        <summary class="text-xs text-primary cursor-pointer">展开</summary>
        <div class="mt-2 space-y-2 text-sm">
          <div v-if="v.ai_summary" class="p-2 rounded bg-blue-50 dark:bg-blue-900/20"><span class="text-xs font-medium text-blue-600">🤖</span> {{ v.ai_summary }}</div>
          <div v-if="v.original_content" class="p-2 rounded bg-gray-50 dark:bg-gray-800/50 whitespace-pre-wrap text-gray-600 dark:text-gray-400">{{ v.original_content }}</div>
          <div v-if="v.image_base64" class="flex gap-2 overflow-x-auto">
            <img v-for="(img,i) in v.image_base64.split('||')" :key="i" :src="'data:image/jpeg;base64,'+img" class="max-h-32 rounded" />
          </div>
        </div>
      </details>
    </div>
  </div>
</template>
