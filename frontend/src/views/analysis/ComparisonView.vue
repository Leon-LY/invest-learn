<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import { watchlistApi } from '@/api/watchlist'
import PriceText from '@/components/common/PriceText.vue'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const compareList = ref<any[]>([])
const compareData = ref<any[]>([])
const loading = ref(false)

let debounceTimer: ReturnType<typeof setTimeout>

function onSearchInput() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (!searchQuery.value.trim()) { searchResults.value = []; return }
    try {
      searchResults.value = (await marketApi.searchStocks(searchQuery.value)) as unknown as any[]
    } catch (e) { console.error(e) }
  }, 300)
}

function addToCompare(stock: any) {
  if (compareList.value.length >= 5) {
    alert('最多对比 5 只股票')
    return
  }
  if (compareList.value.find(s => s.code === stock.code)) return
  compareList.value.push(stock)
  searchQuery.value = ''
  searchResults.value = []
  fetchCompareData()
}

function removeFromCompare(code: string) {
  compareList.value = compareList.value.filter(s => s.code !== code)
  fetchCompareData()
}

async function fetchCompareData() {
  if (compareList.value.length < 2) { compareData.value = []; return }
  loading.value = true
  try {
    const results = await Promise.all(
      compareList.value.map(s => marketApi.getStockDetail(s.code, 30))
    )
    compareData.value = results.map((r: any) => ({
      info: r.info,
      quote: r.quote,
      fundamentals: r.fundamentals,
      totalReturn: r.klines?.length
        ? ((r.klines[r.klines.length - 1].close - r.klines[0].close) / r.klines[0].close * 100).toFixed(2)
        : null,
    }))
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const metrics = [
  { key: 'latest_price', label: '最新价', format: (v: any) => v?.toFixed(2) || '--' },
  { key: 'change_pct', label: '涨跌幅', format: (v: any) => v != null ? (v >= 0 ? '+' : '') + v.toFixed(2) + '%' : '--', color: true },
  { key: 'pe_ratio', label: '市盈率', format: (v: any) => v?.toFixed(2) || '--' },
  { key: 'pb_ratio', label: '市净率', format: (v: any) => v?.toFixed(2) || '--' },
  { key: 'total_mv', label: '总市值', format: (v: any) => v ? (v / 1e8).toFixed(1) + '亿' : '--' },
  { key: 'turnover_rate', label: '换手率', format: (v: any) => v ? v.toFixed(2) + '%' : '--' },
]
</script>

<template>
  <AppShell showBack>
    <div class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <h1 class="text-xl font-bold dark:text-white">对比分析</h1>

      <!-- Search -->
      <div class="relative">
        <input
          v-model="searchQuery"
          @input="onSearchInput"
          placeholder="搜索股票添加到对比列表（最多 5 只）..."
          :disabled="compareList.length >= 5"
          class="w-full px-4 py-2.5 text-sm border border-gray-200 dark:border-gray-700 rounded-xl bg-white dark:bg-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
        />
        <div v-if="searchResults.length" class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg z-20 max-h-60 overflow-y-auto">
          <div
            v-for="r in searchResults" :key="r.code"
            @click="addToCompare(r)"
            class="px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer flex items-center justify-between"
          >
            <div>
              <span class="text-sm font-medium dark:text-white">{{ r.name }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ r.code }} · {{ r.market }}</span>
            </div>
            <span class="text-xs text-purple-500">添加</span>
          </div>
        </div>
      </div>

      <!-- Selected stocks -->
      <div v-if="compareList.length" class="flex flex-wrap gap-2">
        <span
          v-for="s in compareList" :key="s.code"
          class="inline-flex items-center gap-1 px-3 py-1.5 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-full text-sm"
        >
          {{ s.name || s.code }}
          <button @click="removeFromCompare(s.code)" class="ml-1 hover:text-red-500">×</button>
        </span>
      </div>

      <EmptyState v-if="compareList.length < 2" message="请添加至少 2 只股票开始对比" />
      <div v-else-if="loading" class="space-y-2">
        <div v-for="i in 3" :key="i" class="h-12 animate-pulse bg-gray-100 dark:bg-gray-800 rounded-lg" />
      </div>
      <div v-else class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800">
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-400">指标</th>
              <th v-for="s in compareData" :key="s.info.code" class="px-4 py-3 text-center text-xs font-medium text-gray-400">
                <div class="cursor-pointer hover:text-purple-500" @click="router.push(`/diagnosis/${s.info.code}`)">
                  {{ s.info.name }}
                </div>
                <div class="text-gray-500">{{ s.info.code }}</div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="m in metrics" :key="m.key" class="border-b border-gray-50 dark:border-gray-800">
              <td class="px-4 py-3 text-gray-500 dark:text-gray-400">{{ m.label }}</td>
              <td v-for="s in compareData" :key="s.info.code + m.key" class="px-4 py-3 text-center dark:text-white">
                <template v-if="m.key === 'change_pct'">
                  <ChangeBadge :value="s.quote?.[m.key]" />
                </template>
                <template v-else>
                  {{ m.format(s.quote?.[m.key]) }}
                </template>
              </td>
            </tr>
            <tr class="border-b border-gray-50 dark:border-gray-800">
              <td class="px-4 py-3 text-gray-500 dark:text-gray-400">30日收益</td>
              <td v-for="s in compareData" :key="s.info.code + 'ret'" class="px-4 py-3 text-center">
                <ChangeBadge :value="parseFloat(s.totalReturn)" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppShell>
</template>
