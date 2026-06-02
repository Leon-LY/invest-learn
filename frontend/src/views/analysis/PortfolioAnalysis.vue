<script setup lang="ts">
import { ref } from 'vue'
import AppShell from '@/layouts/AppShell.vue'
import { marketApi } from '@/api/market'

const funds = ref([{ code: '', amount: '' }])
const result = ref<any>(null)
const loading = ref(false)
const error = ref('')

function addRow() { funds.value.push({ code: '', amount: '' }) }
function removeRow(i: number) { funds.value.splice(i, 1) }

async function analyze() {
  loading.value = true; error.value = ''; result.value = null
  const items = funds.value
    .filter(f => f.code.trim() && f.amount)
    .map(f => ({ code: f.code.trim(), amount: parseFloat(f.amount) }))
  if (!items.length) { error.value = '请至少输入一只基金'; loading.value = false; return }
  try {
    result.value = await marketApi.portfolioSummary(items)
  } catch(e) { error.value = '分析失败，请重试' }
  finally { loading.value = false }
}

const presetFunds = [
  { code: '005827', name: '易方达蓝筹精选' },
  { code: '161725', name: '招商中证白酒' },
  { code: '110027', name: '易方达安心回报' },
  { code: '510300', name: '沪深300ETF' },
  { code: '000198', name: '天弘余额宝' },
  { code: '163406', name: '兴全合润' },
]
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div>
        <h1 class="text-xl font-bold dark:text-white">📊 组合分析</h1>
        <p class="text-sm text-gray-400 mt-1">输入你的基金持仓，AI 帮你分析配置是否合理</p>
      </div>

      <!-- Input -->
      <div class="card p-4">
        <h3 class="text-sm font-semibold dark:text-white mb-3">我的持仓</h3>
        <div class="space-y-2">
          <div v-for="(f, i) in funds" :key="i" class="flex gap-2 items-center">
            <input v-model="f.code" placeholder="代码" maxlength="6"
              class="w-20 px-2.5 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white" />
            <input v-model="f.amount" placeholder="持有金额(元)" type="number"
              class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white min-w-0" />
            <button @click="removeRow(i)" class="shrink-0 w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:bg-red-50 hover:text-red-500 transition-colors text-lg leading-none">−</button>
          </div>
          <button @click="addRow" class="text-xs text-primary hover:underline">+ 添加基金</button>
        </div>

        <!-- Quick select -->
        <div class="mt-3 pt-3 border-t border-gray-100 dark:border-gray-800">
          <p class="text-xs text-gray-400 mb-2">快速填入：</p>
          <div class="flex flex-wrap gap-1.5">
            <button v-for="p in presetFunds" :key="p.code" @click="funds.push({code:p.code,amount:''})"
              class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500 hover:bg-primary/10 hover:text-primary transition-colors">
              + {{ p.name }}
            </button>
          </div>
        </div>

        <button @click="analyze" :disabled="loading"
          class="mt-3 w-full py-2.5 bg-primary text-white text-sm font-medium rounded-xl disabled:opacity-50">
          {{ loading ? '分析中...' : '开始分析' }}
        </button>
        <p v-if="error" class="text-xs text-red-500 mt-2">{{ error }}</p>
      </div>

      <!-- Results -->
      <div v-if="result" class="space-y-4">
        <!-- Overview -->
        <div class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📋 组合概览</h3>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div class="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/30">
              <div class="text-xs text-gray-400">基金数量</div>
              <div class="text-xl font-bold dark:text-white">{{ result.fund_count }}</div>
            </div>
            <div class="p-3 rounded-xl bg-green-50 dark:bg-green-950/20">
              <div class="text-xs text-gray-400">总金额</div>
              <div class="text-xl font-bold dark:text-white">{{ (result.total_amount/10000).toFixed(1) }}万</div>
            </div>
            <div class="p-3 rounded-xl bg-purple-50 dark:bg-purple-950/20">
              <div class="text-xs text-gray-400">风险评分</div>
              <div class="text-xl font-bold dark:text-white">{{ result.risk_score }}</div>
            </div>
            <div class="p-3 rounded-xl" :class="result.risk_level==='低'?'bg-green-50 dark:bg-green-950/20':'bg-yellow-50 dark:bg-yellow-950/20'">
              <div class="text-xs text-gray-400">风险等级</div>
              <div class="text-xl font-bold dark:text-white">{{ result.risk_level }}</div>
            </div>
          </div>
        </div>

        <!-- Allocation -->
        <div v-if="result.allocation?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📊 资产配置</h3>
          <div class="space-y-2">
            <div v-for="a in result.allocation" :key="a.type" class="flex items-center gap-2">
              <span class="text-xs text-gray-500 w-16">{{ a.type }}</span>
              <div class="flex-1 h-5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div class="h-full rounded-full bg-primary transition-all" :style="{width: a.ratio+'%'}" />
              </div>
              <span class="text-xs font-medium dark:text-white w-12 text-right">{{ a.ratio }}%</span>
            </div>
          </div>
        </div>

        <!-- Holdings list -->
        <div v-if="result.holdings?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💼 持仓明细</h3>
          <div class="space-y-2">
            <div v-for="h in result.holdings" :key="h.code" class="flex items-center justify-between p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50 text-sm">
              <div>
                <span class="font-medium dark:text-white">{{ h.name || h.code }}</span>
                <span class="text-xs text-gray-400 ml-2">{{ h.code }}</span>
              </div>
              <div class="text-right">
                <div class="font-medium dark:text-white">{{ (h.amount/10000).toFixed(1) }}万</div>
                <div v-if="h.nav" class="text-xs text-gray-400">净值 {{ h.nav }}</div>
                <div v-if="h.est_return != null" :class="h.est_return>=0?'text-up':'text-down'" class="text-xs font-medium">{{ h.est_return>=0?'+':'' }}{{ h.est_return?.toFixed(2) }}%</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Advice -->
        <div v-if="result.advice?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💡 优化建议</h3>
          <div class="space-y-2">
            <div v-for="(a, i) in result.advice" :key="i" class="flex items-start gap-2 text-sm">
              <span class="text-gray-400">{{ Number(i)+1 }}.</span>
              <span class="text-gray-600 dark:text-gray-400">{{ a }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
