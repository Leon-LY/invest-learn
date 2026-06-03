<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import PriceText from '@/components/common/PriceText.vue'
import ChangeBadge from '@/components/common/ChangeBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()
const results = ref<any[]>([])
const loading = ref(false)
const total = ref(0)

const filters = ref({
  market: 'A',
  pe_min: null as number | null,
  pe_max: null as number | null,
  pb_min: null as number | null,
  pb_max: null as number | null,
  roe_min: null as number | null,
  sort: 'pe',
  order: 'asc',
})

async function search() {
  loading.value = true
  try {
    const res = (await marketApi.screenStocks({
      ...filters.value,
      pe_min: filters.value.pe_min || undefined,
      pe_max: filters.value.pe_max || undefined,
      pb_min: filters.value.pb_min || undefined,
      pb_max: filters.value.pb_max || undefined,
      roe_min: filters.value.roe_min || undefined,
    })) as any
    results.value = res.items || []
    total.value = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

function resetFilters() {
  filters.value = { market: 'A', pe_min: null, pe_max: null, pb_min: null, pb_max: null, roe_min: null, sort: 'pe', order: 'asc' }
}
</script>

<template>
  <AppShell showBack>
    <div class="max-w-5xl mx-auto px-4 py-4 space-y-4">
      <h1 class="text-xl font-bold dark:text-white">股票筛选器</h1>

      <!-- Filters -->
      <div class="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-100 dark:border-gray-800 space-y-3">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div>
            <label class="text-xs text-gray-400">市盈率(PE) 最小</label>
            <input v-model.number="filters.pe_min" type="number" step="1" placeholder="0" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div>
            <label class="text-xs text-gray-400">市盈率(PE) 最大</label>
            <input v-model.number="filters.pe_max" type="number" step="1" placeholder="50" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div>
            <label class="text-xs text-gray-400">市净率(PB) 最小</label>
            <input v-model.number="filters.pb_min" type="number" step="0.1" placeholder="0" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
          <div>
            <label class="text-xs text-gray-400">市净率(PB) 最大</label>
            <input v-model.number="filters.pb_max" type="number" step="0.1" placeholder="10" class="w-full mt-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-1 focus:ring-primary" />
          </div>
        </div>
        <div class="flex gap-2">
          <button @click="search" class="flex-1 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary-dark transition-colors">筛选</button>
          <button @click="resetFilters" class="px-4 py-2 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">重置</button>
        </div>
      </div>

      <!-- Results -->
      <div v-if="loading" class="space-y-2">
        <div v-for="i in 5" :key="i" class="animate-pulse h-12 bg-gray-100 dark:bg-gray-800 rounded-lg" />
      </div>
      <EmptyState v-else-if="results.length === 0 && total === 0" message="设置筛选条件后点击「筛选」查找股票" />
      <div v-else class="bg-white dark:bg-gray-900 rounded-xl border border-gray-100 dark:border-gray-800 overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100 dark:border-gray-800 text-xs text-gray-400">
              <th class="px-3 py-2 text-left">名称</th>
              <th class="px-3 py-2 text-right">最新价</th>
              <th class="px-3 py-2 text-right">涨跌幅</th>
              <th class="px-3 py-2 text-right">PE</th>
              <th class="px-3 py-2 text-right">PB</th>
              <th class="px-3 py-2 text-right">总市值</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="s in results" :key="s.code"
              @click="router.push(`/diagnosis/${s.code}`)"
              class="border-t border-gray-50 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer"
            >
              <td class="px-3 py-2.5">
                <div class="font-medium dark:text-white text-xs">{{ s.name }}</div>
                <div class="text-xs text-gray-400">{{ s.code }}</div>
              </td>
              <td class="px-3 py-2.5 text-right"><PriceText :value="s.latest_price" size="sm" /></td>
              <td class="px-3 py-2.5 text-right"><ChangeBadge :value="s.change_pct" /></td>
              <td class="px-3 py-2.5 text-right text-xs dark:text-white">{{ s.pe_ratio?.toFixed(1) || '--' }}</td>
              <td class="px-3 py-2.5 text-right text-xs dark:text-white">{{ s.pb_ratio?.toFixed(2) || '--' }}</td>
              <td class="px-3 py-2.5 text-right text-xs dark:text-white">{{ s.total_mv ? (s.total_mv / 1e8).toFixed(0) + '亿' : '--' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </AppShell>
</template>
