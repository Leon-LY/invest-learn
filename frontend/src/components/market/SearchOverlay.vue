<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { marketApi } from '@/api/market'

const router = useRouter()
const visible = ref(false)
const query = ref('')
const results = ref<any[]>([])
const loading = ref(false)
const inputRef = ref<HTMLInputElement>()

let debounceTimer: ReturnType<typeof setTimeout>

function open() {
  visible.value = true
  query.value = ''
  results.value = []
  setTimeout(() => inputRef.value?.focus(), 50)
}

function close() {
  visible.value = false
}

function onKeydown(e: KeyboardEvent) {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    open()
  }
  if (e.key === 'Escape') {
    close()
  }
}

async function onInput() {
  clearTimeout(debounceTimer)
  if (!query.value.trim()) { results.value = []; return }
  loading.value = true
  debounceTimer = setTimeout(async () => {
    try {
      results.value = (await marketApi.searchStocks(query.value)) as unknown as any[]
    } catch (e) { console.error(e) }
    finally { loading.value = false }
  }, 250)
}

function goTo(code: string) {
  close()
  router.push(`/market/${code}`)
}

onMounted(() => { window.addEventListener('keydown', onKeydown) })
onUnmounted(() => { window.removeEventListener('keydown', onKeydown) })

defineExpose({ open, close })
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-[15vh]" @click.self="close">
        <div class="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-lg mx-4 shadow-2xl overflow-hidden">
          <!-- Search input -->
          <div class="flex items-center gap-3 px-4 py-3 border-b border-gray-100 dark:border-gray-800">
            <svg class="w-5 h-5 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              @input="onInput"
              placeholder="搜索股票代码或名称...（Esc 关闭）"
              class="flex-1 text-sm bg-transparent dark:text-white focus:outline-none placeholder-gray-400"
            />
            <kbd class="hidden sm:inline-block px-1.5 py-0.5 text-xs bg-gray-100 dark:bg-gray-800 rounded text-gray-400">ESC</kbd>
          </div>

          <!-- Results -->
          <div class="max-h-80 overflow-y-auto">
            <div v-if="loading" class="px-4 py-3 text-sm text-gray-400">搜索中...</div>
            <div v-else-if="query && !results.length" class="px-4 py-6 text-center text-sm text-gray-400">
              未找到匹配的股票
            </div>
            <div v-else-if="!query" class="px-4 py-6 text-center text-sm text-gray-400">
              输入股票代码或名称开始搜索
            </div>
            <div
              v-for="r in results" :key="r.code"
              @click="goTo(r.code)"
              class="flex items-center justify-between px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xs font-medium dark:text-white">
                  {{ r.market }}
                </div>
                <div>
                  <div class="text-sm font-medium dark:text-white">{{ r.name }}</div>
                  <div class="text-xs text-gray-400">{{ r.code }}</div>
                </div>
              </div>
              <svg class="w-4 h-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          <!-- Footer -->
          <div class="px-4 py-2 border-t border-gray-100 dark:border-gray-800 flex items-center gap-3 text-xs text-gray-400">
            <span class="flex items-center gap-1"><kbd class="px-1 rounded bg-gray-100 dark:bg-gray-800">↑↓</kbd> 导航</span>
            <span class="flex items-center gap-1"><kbd class="px-1 rounded bg-gray-100 dark:bg-gray-800">↵</kbd> 选择</span>
            <span class="flex items-center gap-1"><kbd class="px-1 rounded bg-gray-100 dark:bg-gray-800">Esc</kbd> 关闭</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
