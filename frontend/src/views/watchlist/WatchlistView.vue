<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { watchlistApi } from '@/api/watchlist'
import { marketApi } from '@/api/market'
import PriceText from '@/components/common/PriceText.vue'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import type { WatchlistItem } from '@/types/market'

const router = useRouter()
const items = ref<WatchlistItem[]>([])
const loading = ref(true)
const filterType = ref('')
const searchQuery = ref('')
const searchResults = ref<Array<{ code: string; name: string; market: string; security_type: string }>>([])
const showSearch = ref(false)

onMounted(fetchData)

async function fetchData() {
  loading.value = true
  try {
    items.value = (await watchlistApi.getList(filterType.value || undefined)) as unknown as WatchlistItem[]
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

async function onSearch() {
  if (!searchQuery.value.trim()) { searchResults.value = []; return }
  try {
    searchResults.value = (await marketApi.searchStocks(searchQuery.value)) as unknown as any[]
  } catch (e) { console.error(e) }
}

async function addToWatchlist(stock: { code: string; name: string; market: string; security_type: string }) {
  try {
    await watchlistApi.add({
      item_type: stock.security_type || 'stock',
      item_code: stock.code,
      item_name: stock.name,
    })
    showSearch.value = false
    searchQuery.value = ''
    searchResults.value = []
    await fetchData()
  } catch (e) { console.error(e) }
}

async function removeItem(id: number) {
  await watchlistApi.remove(id)
  await fetchData()
}

const upCount = computed(() => items.value.filter(i => (i.quote?.change_pct || 0) > 0).length)
const downCount = computed(() => items.value.filter(i => (i.quote?.change_pct || 0) < 0).length)
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold dark:text-white">我的自选</h1>
        <button @click="showSearch = !showSearch" class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded-lg hover:bg-purple-700 transition-colors">
          + 添加
        </button>
      </div>

      <!-- Search modal -->
      <div v-if="showSearch" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700 space-y-3">
        <div class="flex gap-2">
          <input
            v-model="searchQuery"
            @input="onSearch"
            placeholder="搜索股票代码或名称..."
            class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button @click="showSearch = false" class="text-sm text-gray-400 hover:text-gray-600">取消</button>
        </div>
        <div v-if="searchResults.length" class="space-y-1 max-h-60 overflow-y-auto">
          <div
            v-for="r in searchResults" :key="r.code"
            @click="addToWatchlist(r)"
            class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer"
          >
            <div>
              <span class="text-sm font-medium dark:text-white">{{ r.name }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ r.code }} · {{ r.market }}</span>
            </div>
            <span class="text-xs text-purple-500">+ 添加</span>
          </div>
        </div>
      </div>

      <!-- Filter tabs -->
      <div class="flex gap-2">
        <button v-for="t in [{ v: '', l: '全部' }, { v: 'stock', l: '股票' }, { v: 'fund', l: '基金' }, { v: 'index', l: '指数' }]" :key="t.v"
          @click="filterType = t.v; fetchData()"
          class="px-3 py-1 rounded-full text-xs font-medium transition-colors"
          :class="filterType === t.v ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
        >{{ t.l }}</button>
        <div class="flex-1" />
        <span class="text-xs text-gray-400 self-center">
          <span class="text-market-up">{{ upCount }}涨</span> /
          <span class="text-market-down">{{ downCount }}跌</span>
        </span>
      </div>

      <!-- List -->
      <div v-if="loading" class="space-y-2">
        <div v-for="i in 5" :key="i" class="animate-pulse h-16 bg-gray-100 dark:bg-gray-800 rounded-xl" />
      </div>
      <EmptyState v-else-if="!items.length" message="还没有自选，点击右上角「添加」搜索股票" />
      <div v-else class="space-y-2">
        <div
          v-for="item in items" :key="item.id"
          class="bg-white dark:bg-gray-900 rounded-xl px-4 py-3 border border-gray-100 dark:border-gray-800 flex items-center gap-3"
        >
          <div class="flex-1 cursor-pointer" @click="router.push(`/market/${item.item_code}`)">
            <div class="flex items-center gap-2">
              <span class="font-medium text-sm dark:text-white">{{ item.alias || item.item_name || item.item_code }}</span>
              <span v-if="item.tags?.length" class="text-xs text-gray-400">{{ item.tags.join('·') }}</span>
            </div>
            <div class="text-xs text-gray-400 mt-0.5">{{ item.item_code }} · {{ item.item_type === 'fund' ? '基金' : item.item_type === 'index' ? '指数' : '股票' }}</div>
          </div>
          <div class="text-right">
            <PriceText :value="item.quote?.latest_price ?? null" size="md" />
            <div><ChangeBadge :value="item.quote?.change_pct ?? null" /></div>
          </div>
          <button @click="removeItem(item.id)" class="p-1.5 text-gray-300 hover:text-red-500 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      </div>
    </div>
  </AppShell>
</template>
