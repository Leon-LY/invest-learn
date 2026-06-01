/**
 * Mock API interceptor.
 * In production without a real backend, mock is ENABLED by default.
 * Toggle via browser console: localStorage.setItem('mock-api', 'false') → then refresh.
 */
import type { AxiosInstance } from 'axios'
import {
  mockIndices, mockStocks, mockFunds, mockSectors, mockCapitalFlow,
  mockBreadth, generateMockNews, mockSearch, mockWatchlist, mockAddWatchlist, mockRemoveWatchlist,
  mockCategories, mockArticles, mockArticleDetail, mockGlossary, mockStrategies,
} from './data'

/** Check at runtime whether mock is enabled. Default = true. */
function isMockEnabled(): boolean {
  const val = localStorage.getItem('mock-api')
  if (val === null) return true  // default: mock ON
  return val === 'true'
}

function delay(ms = 200): Promise<void> {
  return new Promise(r => setTimeout(r, ms + Math.random() * 200))
}

function paginate(items: any[], page = 1, size = 20) {
  const start = (page - 1) * size
  return { items: items.slice(start, start + size), total: items.length, page, size }
}

export function setupMock(axios: AxiosInstance) {
  const originalGet = axios.get.bind(axios)
  const originalPost = axios.post.bind(axios)
  const originalPut = axios.put.bind(axios)
  const originalDelete = axios.delete.bind(axios)

  const handler = async (method: string, url: string, data?: any): Promise<any> => {
    // If user explicitly disabled mock AND we're in production → use real API
    if (!isMockEnabled()) {
      if (method === 'get') return originalGet(url, data)
      if (method === 'post') return originalPost(url, data)
      if (method === 'put') return originalPut(url, data)
      if (method === 'delete') return originalDelete(url)
    }

    // Strip baseURL prefix
    const path = url.replace('/api/v1', '').replace(/^\//, '')

    await delay()

    // ===== MARKET =====
    if (path === 'market/indices') {
      return JSON.parse(JSON.stringify(mockIndices.map(i => ({
        ...i,
        change: i.latest_price ? +(i.latest_price * i.change_pct! / 100).toFixed(2) : 0,
      }))))
    }
    if (path.startsWith('market/indices/')) {
      const code = path.split('/')[2]
      const idx = mockIndices.find(i => i.code === code)
      if (!idx) return { info: null, klines: [] }
      return { info: idx, klines: [] }
    }
    if (path.startsWith('market/stocks/') && path.endsWith('/kline')) {
      const code = path.split('/')[2]
      const stock = mockStocks[code]
      return stock ? { klines: stock.klines || [] } : { klines: [] }
    }
    if (path.startsWith('market/stocks/')) {
      const code = path.split('/')[2]
      const stock = mockStocks[code]
      return stock ? JSON.parse(JSON.stringify(stock)) : null
    }
    if (path.startsWith('market/funds/')) {
      const code = path.split('/')[2]
      const fund = mockFunds[code]
      return fund ? JSON.parse(JSON.stringify(fund)) : null
    }
    if (path === 'market/sectors') {
      return JSON.parse(JSON.stringify(mockSectors))
    }
    if (path.startsWith('market/capital-flow')) {
      return JSON.parse(JSON.stringify(mockCapitalFlow))
    }
    if (path === 'market/breadth') {
      return JSON.parse(JSON.stringify(mockBreadth))
    }
    if (path === 'market/search') {
      const params = data as any
      return JSON.parse(JSON.stringify(mockSearch(params?.params?.q || '')))
    }
    if (path === 'market/screener') {
      const all = Object.values(mockStocks).slice(0, 10)
      return {
        items: all.map((s: any) => ({
          code: s.info.code, name: s.info.name, market: s.info.market, sector: s.info.sector,
          latest_price: s.quote.latest_price, pe_ratio: s.quote.pe_ratio, pb_ratio: s.quote.pb_ratio,
          change_pct: s.quote.change_pct, total_mv: s.quote.total_mv,
        })), total: all.length, page: 1, size: 20,
      }
    }
    if (path === 'market/etfs') {
      return [{ code: '159915', name: '创业板ETF', market: 'A' }, { code: '510050', name: '上证50ETF', market: 'A' }, { code: '510300', name: '沪深300ETF', market: 'A' }]
    }

    // ===== NEWS =====
    if (path === 'news') {
      const params = (data as any)?.params || {}
      const all = generateMockNews()
      let filtered = all
      if (params.category) filtered = filtered.filter(n => n.categories.includes(params.category))
      return paginate(filtered, params.page || 1, params.size || 20)
    }
    if (/^news\/\d+$/.test(path)) {
      const id = parseInt(path.split('/')[1])
      const all = generateMockNews()
      const article = all.find(n => n.id === id)
      if (!article) return null
      return { ...article, content: article.summary, related_news: all.slice(0, 3) }
    }
    if (path === 'news/sources/list') {
      return [
        { id: 1, name: '东方财富', source_type: 'rss', last_fetched: new Date().toISOString() },
        { id: 2, name: '雪球', source_type: 'rss', last_fetched: new Date().toISOString() },
        { id: 3, name: '华尔街见闻', source_type: 'rss', last_fetched: new Date().toISOString() },
      ]
    }
    if (path === 'news/sentiment/stats') {
      return { positive_count: 12, negative_count: 3, neutral_count: 5 }
    }

    // ===== WATCHLIST =====
    if (path === 'watchlist' && method === 'get') {
      return JSON.parse(JSON.stringify(mockWatchlist))
    }
    if (path === 'watchlist' && method === 'post') {
      const body = (data as any) || {}
      return mockAddWatchlist(body)
    }
    if (/^watchlist\/\d+$/.test(path) && method === 'put') {
      return { success: true }
    }
    if (/^watchlist\/\d+$/.test(path) && method === 'delete') {
      mockRemoveWatchlist(parseInt(path.split('/')[1]))
      return { success: true }
    }
    if (path === 'watchlist/reorder' && method === 'post') {
      return { success: true }
    }

    // ===== ALERTS =====
    if (path === 'watchlist/alerts' && method === 'get') return []
    if (path === 'watchlist/alerts' && method === 'post') return { id: 1, condition: 'above', target_value: 100 }
    if (/^watchlist\/alerts\/\d+$/.test(path) && method === 'delete') return { success: true }

    // ===== LEARN =====
    if (path === 'learn/categories') {
      return JSON.parse(JSON.stringify(mockCategories))
    }
    if (path === 'learn/articles') {
      const params = (data as any)?.params || {}
      let filtered = [...mockArticles]
      if (params.level) filtered = filtered.filter(a => a.level === params.level)
      return paginate(filtered, params.page || 1, params.size || 50)
    }
    if (path.startsWith('learn/articles/')) {
      const slug = path.split('/')[2]
      return JSON.parse(JSON.stringify(mockArticleDetail[slug] || null))
    }
    if (path === 'learn/glossary') {
      const params = (data as any)?.params || {}
      let filtered = [...mockGlossary]
      if (params.q) {
        const q = params.q.toLowerCase()
        filtered = filtered.filter(g => g.term.includes(q) || (g.term_en || '').toLowerCase().includes(q) || g.definition.includes(q))
      }
      if (params.category) filtered = filtered.filter(g => g.category === params.category)
      return JSON.parse(JSON.stringify(filtered))
    }
    if (path === 'learn/strategies') {
      return JSON.parse(JSON.stringify(mockStrategies))
    }
    if (path.startsWith('learn/strategies/')) {
      const slug = path.split('/')[2]
      const s = mockStrategies.find(x => x.slug === slug)
      return s ? { ...s, content: '## 策略详解\n\n详细内容正在编写中，敬请期待。\n\n### 核心要点\n\n该策略的核心思想是建立一套系统化的投资方法论，通过纪律性的执行来获取长期稳定收益。\n\n### 适用场景\n\n适合有一定投资基础、能够坚持执行的投资者。' } : null
    }
    if (path === 'learn/calendar') {
      return [
        { id: 1, event_date: new Date(Date.now() + 86400000 * 5).toISOString().slice(0, 10), event_type: 'earnings', title: '上市公司年报密集发布', importance: 'high', country: 'CN' },
        { id: 2, event_date: new Date(Date.now() + 86400000 * 12).toISOString().slice(0, 10), event_type: 'economic', title: 'CPI / PPI 数据公布', importance: 'high', country: 'CN' },
        { id: 3, event_date: new Date(Date.now() + 86400000 * 20).toISOString().slice(0, 10), event_type: 'dividend', title: '多家银行股除权除息', importance: 'medium', country: 'CN' },
      ]
    }

    // Fallback: real API
    if (method === 'get') return originalGet(url, data)
    if (method === 'post') return originalPost(url, data)
    if (method === 'put') return originalPut(url, data)
    if (method === 'delete') return originalDelete(url)
  }

  // Override axios methods
  axios.get = ((url: string, config?: any) => handler('get', url, config)) as any
  axios.post = ((url: string, data?: any, config?: any) => handler('post', url, data)) as any
  axios.put = ((url: string, data?: any, config?: any) => handler('put', url, data)) as any
  axios.delete = ((url: string, config?: any) => handler('delete', url)) as any

  console.log('[InvestLearn] Mock API ready. Data will display automatically.')
  console.log('[InvestLearn] To switch to real API: localStorage.setItem("mock-api", "false")')
}
