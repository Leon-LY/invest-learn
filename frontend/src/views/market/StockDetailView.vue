<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import { watchlistApi } from '@/api/watchlist'
import PriceText from '@/components/common/PriceText.vue'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import SkeletonCard from '@/components/common/SkeletonCard.vue'
import KLineChart from '@/components/charts/KLineChart.vue'
import type { StockDetail } from '@/types/market'

const route = useRoute()
const router = useRouter()
const code = route.params.code as string

const detail = ref<StockDetail | null>(null)
const loading = ref(true)
const inWatchlist = ref(false)
const period = ref<'daily' | 'weekly' | 'monthly'>('daily')

onMounted(async () => {
  try {
    const [data, wl] = await Promise.all([
      marketApi.getStockDetail(code),
      watchlistApi.getList(),
    ])
    detail.value = data as unknown as StockDetail
    // Check watchlist
    const items = wl as unknown as Array<{ item_code: string }>
    inWatchlist.value = items.some((i: any) => i.item_code === code)
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

async function toggleWatchlist() {
  try {
    if (inWatchlist.value) {
      // Find and delete
      const wl = await watchlistApi.getList() as unknown as Array<{ id: number; item_code: string }>
      const item = wl.find((i: any) => i.item_code === code)
      if (item) await watchlistApi.remove(item.id)
    } else {
      await watchlistApi.add({
        item_type: 'stock',
        item_code: code,
        item_name: detail.value?.info.name || code,
      })
    }
    inWatchlist.value = !inWatchlist.value
  } catch (e) {
    console.error(e)
  }
}

function formatNum(val: number | null): string {
  if (!val) return '--'
  if (val > 1e8) return (val / 1e8).toFixed(1) + '亿'
  if (val > 1e4) return (val / 1e4).toFixed(0) + '万'
  return val.toFixed(2)
}
</script>

<template>
  <AppShell showBack>
    <div v-if="loading" class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <SkeletonCard v-for="i in 3" :key="i" />
    </div>
    <div v-else-if="!detail" class="max-w-5xl mx-auto px-4 py-12 text-center text-gray-500">
      股票信息加载失败
    </div>
    <div v-else class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <!-- Header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-lg font-bold dark:text-white">{{ detail.info.name }}</h1>
          <span class="text-xs text-gray-400">{{ detail.info.code }} · {{ detail.info.market === 'A' ? 'A股' : detail.info.market === 'HK' ? '港股' : detail.info.market === 'US' ? '美股' : detail.info.market }}</span>
          <span v-if="detail.info.sector" class="ml-2 text-xs px-1.5 py-0.5 bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 rounded">{{ detail.info.sector }}</span>
        </div>
        <button
          @click="toggleWatchlist"
          class="p-2 rounded-lg transition-colors"
          :class="inWatchlist ? 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'"
        >
          <svg class="w-5 h-5" :fill="inWatchlist ? 'currentColor' : 'none'" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
      </div>

      <!-- Price -->
      <div v-if="detail.quote" class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <div class="flex items-baseline gap-3">
          <PriceText :value="detail.quote.latest_price" size="xl" />
          <ChangeBadge :value="detail.quote.change_pct" />
        </div>
        <div class="grid grid-cols-3 sm:grid-cols-6 gap-3 mt-4 text-center">
          <div><div class="text-xs text-gray-400">成交量</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ formatNum(detail.quote.volume) }}</div></div>
          <div><div class="text-xs text-gray-400">成交额</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ formatNum(detail.quote.amount) }}</div></div>
          <div><div class="text-xs text-gray-400">换手率</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ detail.quote.turnover_rate?.toFixed(2) || '--' }}%</div></div>
          <div><div class="text-xs text-gray-400">市盈率</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ detail.fundamentals?.pe?.toFixed(2) || '--' }}</div></div>
          <div><div class="text-xs text-gray-400">市净率</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ detail.fundamentals?.pb?.toFixed(2) || '--' }}</div></div>
          <div><div class="text-xs text-gray-400">总市值</div><div class="text-sm font-medium dark:text-white mt-0.5">{{ formatNum(detail.fundamentals?.total_mv ?? null) }}</div></div>
        </div>
      </div>

      <!-- K-line Chart -->
      <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <div class="flex items-center gap-3 mb-3">
          <button
            v-for="p in [{ k: 'daily', l: '日K' }, { k: 'weekly', l: '周K' }, { k: 'monthly', l: '月K' }]" :key="p.k"
            @click="period = p.k as any"
            class="px-3 py-1 rounded text-xs font-medium transition-colors"
            :class="period === p.k ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'"
          >
            {{ p.l }}
          </button>
        </div>
        <KLineChart v-if="detail.klines?.length" :data="detail.klines" height="400px" />
        <div v-else class="h-96 flex items-center justify-center text-gray-400">暂无K线数据</div>
      </div>

      <div class="h-4" />
    </div>
  </AppShell>
</template>
