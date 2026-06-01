<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import type { SectorItem } from '@/types/market'

const router = useRouter()
const sectors = ref<SectorItem[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    sectors.value = (await marketApi.getSectors()) as unknown as SectorItem[]
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function getHeatColor(pct: number | null): string {
  if (!pct) return 'bg-gray-100 dark:bg-gray-800'
  if (pct > 5) return 'bg-market-up/30 dark:bg-market-up/40'
  if (pct > 2) return 'bg-market-up/20 dark:bg-market-up/25'
  if (pct > 0) return 'bg-market-up/10 dark:bg-market-up/15'
  if (pct > -2) return 'bg-market-down/10 dark:bg-market-down/15'
  if (pct > -5) return 'bg-market-down/20 dark:bg-market-down/25'
  return 'bg-market-down/30 dark:bg-market-down/40'
}

function goToStock(code: string) {
  router.push(`/diagnosis/${code}`)
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">板块分析</h1>
        <p class="text-sm text-gray-400 mt-1">行业板块涨跌热力图与资金流向</p>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-3">
        <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
          <div class="text-xs text-gray-400">上涨板块</div>
          <div class="text-lg font-bold text-market-up mt-1">
            {{ sectors.filter(s => (s.change_pct || 0) > 0).length }}
          </div>
        </div>
        <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
          <div class="text-xs text-gray-400">下跌板块</div>
          <div class="text-lg font-bold text-market-down mt-1">
            {{ sectors.filter(s => (s.change_pct || 0) < 0).length }}
          </div>
        </div>
        <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
          <div class="text-xs text-gray-400">板块总数</div>
          <div class="text-lg font-bold dark:text-white mt-1">{{ sectors.length }}</div>
        </div>
      </div>

      <!-- Sector Heat Grid -->
      <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800">
        <h3 class="text-sm font-medium text-gray-500 mb-3">行业板块涨跌幅</h3>
        <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <div v-for="i in 12" :key="i" class="h-14 animate-pulse bg-gray-100 dark:bg-gray-800 rounded-lg" />
        </div>
        <div v-else-if="!sectors.length" class="py-8 text-center text-gray-400">暂无数据</div>
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
          <div
            v-for="s in sectors" :key="s.sector_name"
            class="rounded-lg p-3 transition-all hover:scale-105 cursor-pointer"
            :class="getHeatColor(s.change_pct)"
            @click="s.top_stock && goToStock(s.top_stock)"
          >
            <div class="font-medium text-sm dark:text-white truncate">{{ s.sector_name }}</div>
            <div class="flex items-center justify-between mt-1">
              <span class="text-sm font-semibold" :class="(s.change_pct || 0) >= 0 ? 'text-market-up' : 'text-market-down'">
                {{ s.change_pct ? (s.change_pct >= 0 ? '+' : '') + s.change_pct.toFixed(2) + '%' : '--' }}
              </span>
              <span class="text-xs text-gray-400">{{ s.net_inflow ? (s.net_inflow / 1e8).toFixed(1) + '亿' : '' }}</span>
            </div>
            <div v-if="s.top_stock" class="text-xs text-gray-400 mt-0.5 truncate">
              领涨: {{ s.top_stock }}
              <span :class="(s.top_stock_pct || 0) >= 0 ? 'text-market-up' : 'text-market-down'">
                {{ s.top_stock_pct ? (s.top_stock_pct >= 0 ? '+' : '') + s.top_stock_pct.toFixed(2) + '%' : '' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
