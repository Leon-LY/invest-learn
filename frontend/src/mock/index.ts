/**
 * Mock API interceptor.
 * In production without a real backend, mock is ENABLED by default.
 * Toggle via browser console: localStorage.setItem('mock-api', 'false') → then refresh.
 */
import type { AxiosInstance } from 'axios'
import {
  mockIndices, mockFunds, mockSectors, mockCapitalFlow, getMockFundList,
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
    // Fund detail - treat stocks/{code} as fund lookup too (for watchlist navigation)
    if (path.startsWith('market/stocks/') || path.startsWith('market/funds/')) {
      const code = path.split('/')[2]
      const fund = mockFunds[code]
      if (!fund) return null
      // Return fund data in stock-compatible format for StockDetailView
      return JSON.parse(JSON.stringify({
        info: { code: fund.info.code, name: fund.info.name, market: 'CN', security_type: 'fund', sector: fund.info.category, industry: fund.info.fund_type },
        quote: { code: fund.info.code, name: fund.info.name, market: 'CN', latest_price: fund.info.latest_nav, change_pct: fund.info.latest_return, turnover_rate: null, pe_ratio: null, pb_ratio: null, total_mv: fund.info.scale },
        fundamentals: { fund_type: fund.info.fund_type, manager: fund.info.manager, company: fund.info.company, star: fund.info.star, risk: fund.info.risk_level },
        klines: [],
      }))
    }
    if (path === 'market/sectors') {
      return JSON.parse(JSON.stringify(mockSectors.map(s => ({
        sector_name: s.name,
        change_pct: s.avg_return,
        net_inflow: s.inflow * 1e8,
        top_stock: null,
        top_stock_pct: null,
      }))))
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
      const all = getMockFundList()
      return { items: all.slice(0, 15).map((f: any) => ({
        code: f.code, name: f.name, market: f.market, sector: f.type,
        latest_price: f.latest_nav, change_pct: f.latest_return,
        pe_ratio: null, pb_ratio: null, total_mv: f.scale,
      })), total: all.length, page: 1, size: 15 }
    }
    if (path === 'market/etfs') {
      return getMockFundList().filter((f: any) => f.type === 'ETF').slice(0, 10)
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
        { id: 1, name: '中国基金报', source_type: 'rss', last_fetched: new Date().toISOString() },
        { id: 2, name: '天天基金网', source_type: 'rss', last_fetched: new Date().toISOString() },
        { id: 3, name: 'Morningstar晨星', source_type: 'rss', last_fetched: new Date().toISOString() },
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
