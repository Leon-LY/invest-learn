<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'
import type { FundDetail } from '@/types/market'

const route = useRoute()
const detail = ref<FundDetail | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    detail.value = (await marketApi.getFundDetail(route.params.code as string)) as unknown as FundDetail
  } catch (e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-4 space-y-4">
      <div v-if="loading" class="space-y-2"><div v-for="i in 3" :key="i" class="animate-pulse h-20 bg-gray-100 dark:bg-gray-800 rounded-xl" /></div>
      <div v-else-if="!detail" class="text-center py-12 text-gray-400">基金信息加载失败</div>
      <div v-else>
        <h1 class="text-lg font-bold dark:text-white">{{ detail.info.name }}</h1>
        <span class="text-xs text-gray-400">{{ detail.info.code }} · {{ detail.info.fund_type || '基金' }}</span>
        <div class="grid grid-cols-3 gap-3 mt-4">
          <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
            <div class="text-xs text-gray-400">最新净值</div>
            <div class="text-lg font-bold dark:text-white mt-1">{{ detail.info.latest_nav?.toFixed(4) || '--' }}</div>
          </div>
          <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
            <div class="text-xs text-gray-400">日涨跌</div>
            <div class="text-lg font-bold mt-1" :class="(detail.info.latest_return || 0) >= 0 ? 'text-market-up' : 'text-market-down'">{{ detail.info.latest_return ? (detail.info.latest_return >= 0 ? '+' : '') + detail.info.latest_return.toFixed(2) + '%' : '--' }}</div>
          </div>
          <div class="bg-white dark:bg-gray-900 rounded-xl p-3 border text-center">
            <div class="text-xs text-gray-400">基金规模</div>
            <div class="text-lg font-bold dark:text-white mt-1">{{ detail.info.aum ? (detail.info.aum / 1e8).toFixed(1) + '亿' : '--' }}</div>
          </div>
        </div>
        <!-- NAV history table -->
        <div v-if="detail.nav_history?.length" class="mt-4 bg-white dark:bg-gray-900 rounded-xl border overflow-hidden">
          <div class="px-4 py-2 text-xs font-medium text-gray-500 border-b">净值走势（最近记录）</div>
          <div class="max-h-80 overflow-y-auto">
            <table class="w-full text-sm">
              <thead><tr class="text-xs text-gray-400"><th class="px-4 py-2 text-left">日期</th><th class="px-4 py-2 text-right">单位净值</th><th class="px-4 py-2 text-right">累计净值</th><th class="px-4 py-2 text-right">日增长率</th></tr></thead>
              <tbody>
                <tr v-for="n in detail.nav_history.slice(-20)" :key="n.date" class="border-t border-gray-50 dark:border-gray-800">
                  <td class="px-4 py-2 dark:text-white">{{ n.date }}</td>
                  <td class="px-4 py-2 text-right dark:text-white">{{ n.unit_nav?.toFixed(4) || '--' }}</td>
                  <td class="px-4 py-2 text-right dark:text-white">{{ n.acc_nav?.toFixed(4) || '--' }}</td>
                  <td class="px-4 py-2 text-right" :class="(n.daily_return || 0) >= 0 ? 'text-market-up' : 'text-market-down'">{{ n.daily_return ? (n.daily_return >= 0 ? '+' : '') + n.daily_return.toFixed(2) + '%' : '--' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
