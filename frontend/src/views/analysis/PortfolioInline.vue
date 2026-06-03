<script setup lang="ts">
import { ref } from 'vue'
import { marketApi } from '@/api/market'

const funds = ref([{ code: '', amount: '' }])
const result = ref<any>(null)
const loading = ref(false)
const error = ref('')

function addRow() { funds.value.push({ code: '', amount: '' }) }
function addPreset(code: string) {
  const empty = funds.value.find(f => !f.code.trim())
  if (empty) { empty.code = code; return }
  funds.value.push({ code, amount: '' })
}
function removeRow(i: number) { funds.value.splice(i, 1) }

async function analyze() {
  loading.value = true; error.value = ''; result.value = null
  const items = funds.value.filter(f => f.code.trim() && f.amount && !isNaN(parseFloat(f.amount))).map(f => ({ code: f.code.trim(), amount: parseFloat(f.amount) }))
  if (!items.length) { error.value = '请填写基金代码和金额'; loading.value = false; return }
  try { result.value = await marketApi.portfolioSummary(items) } catch(e) { error.value = '分析失败' }
  finally { loading.value = false }
}

const presetFunds = [
  { code: '005827', name: '易方达蓝筹精选' }, { code: '161725', name: '招商中证白酒' },
  { code: '110027', name: '易方达安心回报' }, { code: '510300', name: '沪深300ETF' },
]
</script>

<template>
  <div class="space-y-4">
    <div class="card p-4">
      <div class="space-y-2">
        <div v-for="(f, i) in funds" :key="i" class="flex gap-2 items-center">
          <input v-model="f.code" placeholder="代码" maxlength="6" class="w-20 px-2.5 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white" />
          <input v-model="f.amount" placeholder="持有金额(元)" type="number" class="flex-1 px-3 py-2 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 dark:text-white min-w-0" />
          <button @click="removeRow(i)" class="shrink-0 w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:bg-red-50 hover:text-red-500">−</button>
        </div>
        <button @click="addRow" class="text-xs text-primary">+ 添加基金</button>
      </div>
      <div class="flex gap-1.5 mt-2 flex-wrap">
        <button v-for="p in presetFunds" :key="p.code" @click="addPreset(p.code)" class="text-xs px-2 py-1 rounded-full bg-gray-100 dark:bg-gray-800 text-gray-500">+ {{ p.name.slice(0,6) }}</button>
      </div>
      <button @click="analyze" :disabled="loading" class="mt-3 w-full py-2.5 bg-primary text-white text-sm font-medium rounded-xl disabled:opacity-50">{{ loading ? '分析中...' : '开始分析' }}</button>
      <p v-if="error" class="text-xs text-red-500 mt-2">{{ error }}</p>
    </div>

    <div v-if="result" class="space-y-3">
      <div class="card p-4">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
          <div class="p-2 rounded-xl bg-blue-50 dark:bg-blue-950/30"><div class="text-xs text-gray-400">基金数</div><div class="text-lg font-bold dark:text-white">{{ result.fund_count }}</div></div>
          <div class="p-2 rounded-xl bg-green-50 dark:bg-green-950/20"><div class="text-xs text-gray-400">总金额</div><div class="text-lg font-bold dark:text-white">{{ result.total_amount ? (result.total_amount/10000).toFixed(1)+'万' : '--' }}</div></div>
          <div class="p-2 rounded-xl bg-purple-50 dark:bg-purple-950/20"><div class="text-xs text-gray-400">风险评分</div><div class="text-lg font-bold dark:text-white">{{ result.risk_score }}</div></div>
          <div class="p-2 rounded-xl" :class="result.risk_level==='低'?'bg-green-50 dark:bg-green-950/20':'bg-yellow-50 dark:bg-yellow-950/20'"><div class="text-xs text-gray-400">风险等级</div><div class="text-lg font-bold dark:text-white">{{ result.risk_level }}</div></div>
        </div>
      </div>
      <div v-if="result.allocation?.length" class="card p-4">
        <h3 class="text-sm font-semibold dark:text-white mb-2">配置分布</h3>
        <div v-for="a in result.allocation" :key="a.type" class="flex items-center gap-2 mb-1">
          <span class="text-xs text-gray-500 w-16">{{ a.type }}</span>
          <div class="flex-1 h-4 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"><div class="h-full rounded-full bg-primary" :style="{width:a.ratio+'%'}" /></div>
          <span class="text-xs font-medium dark:text-white w-12 text-right">{{ a.ratio }}%</span>
        </div>
      </div>
      <div v-if="result.advice?.length" class="card p-4">
        <h3 class="text-sm font-semibold dark:text-white mb-2">💡 建议</h3>
        <div v-for="(a,i) in result.advice" :key="i" class="p-2 rounded text-sm mb-1" :class="a.level==='warning'?'bg-amber-50 dark:bg-amber-950/20':a.level==='good'?'bg-green-50 dark:bg-green-950/20':'bg-gray-50 dark:bg-gray-800/50'">{{ a.text }}</div>
      </div>
    </div>
  </div>
</template>
