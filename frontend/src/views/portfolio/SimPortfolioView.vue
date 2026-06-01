<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const hasPortfolio = ref(false)
</script>

<template>
  <AppShell>
    <div class="max-w-4xl mx-auto px-4 py-4 space-y-4">
      <h1 class="text-xl font-bold dark:text-white">模拟交易</h1>
      <p class="text-sm text-gray-400">纸上练兵，零成本学习投资操作</p>
      <div class="bg-white dark:bg-gray-900 rounded-xl p-8 border border-gray-100 dark:border-gray-800 text-center">
        <EmptyState message="模拟交易功能即将上线，敬请期待！" />
        <div class="mt-4 text-xs text-gray-400">
          <p>功能预告：</p>
          <ul class="mt-2 space-y-1">
            <li>📊 创建模拟投资组合</li>
            <li>💼 买入/卖出股票</li>
            <li>📈 查看持仓盈亏与收益率曲线</li>
            <li>📋 交易记录查询</li>
          </ul>
        </div>
      </div>
    </div>
  </AppShell>
</template>
