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
    expert.value = await newsApi.getExpertPredictionDetail(id)
  } catch(e) { console.error(e) }
  finally { loading.value = false }
})
</script>

<template>
  <AppShell showBack>
    <div class="max-w-3xl mx-auto px-4 py-5 space-y-4">
      <div v-if="loading" class="space-y-3">
        <div v-for="i in 4" :key="i" class="skeleton h-24 rounded-xl" />
      </div>

      <div v-else-if="expert?.error" class="card p-6 text-center text-gray-400 text-sm">{{ expert.error }}</div>

      <div v-else-if="expert" class="space-y-4">
        <!-- Header -->
        <div class="card p-5">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-cyan flex items-center justify-center text-white font-bold text-lg shrink-0">{{ expert.expert?.[0] }}</div>
            <div>
              <h1 class="text-lg font-bold dark:text-white">{{ expert.expert }}</h1>
              <p class="text-sm text-gray-400">{{ expert.title_role }} · 专注 {{ expert.prefers }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ expert.prediction_count }} 条分析 · 综合信心 {{ expert.confidence }}%</p>
            </div>
          </div>
        </div>

        <!-- All predictions across different news -->
        <div v-for="(p, i) in expert.predictions" :key="i" class="card p-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary font-medium">#{{ Number(i)+1 }}</span>
            <span class="text-xs text-gray-400">信心 {{ p.confidence }}%</span>
          </div>
          <p class="text-xs text-gray-400 mb-1">📰 {{ p.news_title }}</p>
          <h3 class="font-semibold text-sm dark:text-white mb-2">{{ p.title }}</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ p.content }}</p>
          <div v-if="p.relatedFunds?.length" class="flex gap-1.5 mt-2">
            <span v-for="f in p.relatedFunds" :key="f" class="text-xs px-2 py-0.5 bg-up-bg text-up rounded-full font-medium">{{ f }}</span>
          </div>
          <div class="mt-2">
            <router-link :to="`/news/${p.news_id}`" class="text-xs text-primary hover:underline">查看原文 →</router-link>
          </div>
        </div>
      </div>
    </div>
  </AppShell>
</template>
