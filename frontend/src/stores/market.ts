import { defineStore } from 'pinia'
import { ref } from 'vue'
import { marketApi } from '@/api/market'
import type { IndexInfo, StockDetail, FundDetail, MarketBreadth, SectorItem, CapitalFlowItem } from '@/types/market'

export const useMarketStore = defineStore('market', () => {
  const indices = ref<IndexInfo[]>([])
  const indicesLoading = ref(false)
  const breadth = ref<MarketBreadth | null>(null)
  const sectors = ref<SectorItem[]>([])
  const capitalFlow = ref<{ north: CapitalFlowItem[]; south: CapitalFlowItem[] }>({ north: [], south: [] })

  // Cache timestamps for SWR
  const lastFetched: Record<string, number> = {}

  function isStale(key: string, ttlMs: number): boolean {
    const last = lastFetched[key]
    if (!last) return true
    return Date.now() - last > ttlMs
  }

  async function fetchIndices(force = false) {
    if (!force && !isStale('indices', 60000) && indices.value.length > 0) return
    indicesLoading.value = true
    try {
      const data = await marketApi.getIndices() as unknown as IndexInfo[]
      indices.value = data
      lastFetched['indices'] = Date.now()
    } catch (e) {
      console.error('Failed to fetch indices:', e)
    } finally {
      indicesLoading.value = false
    }
  }

  async function fetchBreadth() {
    if (!isStale('breadth', 300000) && breadth.value) return
    try {
      breadth.value = await marketApi.getMarketBreadth() as unknown as MarketBreadth
      lastFetched['breadth'] = Date.now()
    } catch (e) {
      console.error('Failed to fetch breadth:', e)
    }
  }

  async function fetchSectors() {
    if (!isStale('sectors', 300000) && sectors.value.length > 0) return
    try {
      sectors.value = await marketApi.getSectors() as unknown as SectorItem[]
      lastFetched['sectors'] = Date.now()
    } catch (e) {
      console.error('Failed to fetch sectors:', e)
    }
  }

  async function fetchCapitalFlow(days = 30) {
    if (!isStale('capitalFlow', 300000) && capitalFlow.value.north.length > 0) return
    try {
      capitalFlow.value = await marketApi.getCapitalFlow(days) as any
      lastFetched['capitalFlow'] = Date.now()
    } catch (e) {
      console.error('Failed to fetch capital flow:', e)
    }
  }

  async function fetchAllDashboardData() {
    await Promise.all([
      fetchIndices(),
      fetchBreadth(),
      fetchSectors(),
      fetchCapitalFlow(),
    ])
  }

  return {
    indices, indicesLoading, breadth, sectors, capitalFlow,
    fetchIndices, fetchBreadth, fetchSectors, fetchCapitalFlow, fetchAllDashboardData,
  }
})
