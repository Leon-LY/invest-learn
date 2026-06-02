<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '@/layouts/AppShell.vue'
import { newsApi } from '@/api/news'

const route = useRoute()
const expert = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const id = route.params.id as string
    expert.value = await newsApi.getExpertDetail(id)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 4" :key="i" class="skeleton h-20 rounded-xl" />
      </div>

      <div v-else-if="expert?.error" class="card p-6 text-center text-gray-400 text-sm">{{ expert.error }}</div>

      <div v-else-if="expert" class="space-y-4">
        <!-- Header -->
        <div class="card p-5">
          <div class="flex items-start gap-3">
            <div class="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-purple-500 flex items-center justify-center text-white font-bold text-xl shrink-0">{{ expert.name?.[0] }}</div>
            <div>
              <h1 class="text-lg font-bold dark:text-white">{{ expert.name }}</h1>
              <p class="text-sm text-gray-400 mt-0.5">{{ expert.type || '基金经理' }} · {{ expert.bio }}</p>
              <p v-if="expert.fund_code" class="text-xs text-gray-400 mt-1">管理基金：{{ expert.fund_name }}（{{ expert.fund_code }}）</p>
              <p v-if="expert.note" class="text-xs text-gray-400 mt-1">⚠️ {{ expert.note }}</p>
            </div>
          </div>
        </div>

        <!-- NAV Chart (fund managers only) -->
        <div v-if="expert.nav_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📈 净值走势（近90日）</h3>
          <div class="h-40 flex items-end gap-px">
            <div v-for="(n, i) in expert.nav_history.slice(-60)" :key="i"
              class="flex-1 rounded-t-sm transition-all"
              :class="(n.daily_return||0)>=0?'bg-up/60':'bg-down/60'"
              :style="{ height: `${30 + (n.nav - expert.nav_history[0].nav) / expert.nav_history[0].nav * 100 + 20}%` }"
              :title="`${n.date}: ${n.nav} (${(n.daily_return||0)>=0?'+':''}${(n.daily_return||0)?.toFixed(2)}%)`" />
          </div>
          <div class="flex justify-between text-[10px] text-gray-400 mt-1">
            <span>{{ expert.nav_history[0]?.date }}</span>
            <span>{{ expert.nav_history[expert.nav_history.length-1]?.date }}</span>
          </div>
        </div>

        <!-- Fund Size History -->
        <div v-if="expert.size_history?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">💰 规模变动</h3>
          <div class="space-y-2">
            <div v-for="s in expert.size_history" :key="s.date" class="flex items-center justify-between text-sm">
              <span class="text-gray-400">{{ s.date }}</span>
              <span class="font-medium dark:text-white">{{ (s.size / 1e8).toFixed(1) }}亿</span>
            </div>
          </div>
        </div>

        <!-- Operations -->
        <div v-if="expert.operations?.length" class="card p-4">
          <h3 class="text-sm font-semibold dark:text-white mb-3">📋 近期动态</h3>
          <div class="space-y-2">
            <div v-for="(op, i) in expert.operations" :key="i" class="flex items-start gap-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-800/50">
              <span class="text-xs text-gray-400 w-20 shrink-0">{{ op.date }}</span>
              <span class="text-xs font-medium text-gray-600 dark:text-gray-300 w-16 shrink-0">{{ op.action }}</span>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ op.detail }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
