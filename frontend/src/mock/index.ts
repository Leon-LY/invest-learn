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

function generateArticleContent(id: number, title: string, sentiment: string): string {
  const upOrDown = sentiment === 'positive' ? '利好' : sentiment === 'negative' ? '利空' : '中性'
  return `## ${title}

---

**来源：中国基金报  |  发布时间：${new Date(Date.now() - Math.random() * 86400000 * 3).toLocaleString('zh-CN')}  |  影响判断：${upOrDown}**

---

### 📰 事件概述

${title}。这一消息引起了基金投资圈的广泛关注，多位业内人士对此发表了看法。

根据最新披露的数据和市场反馈，这一变化将对基金行业产生多维度的影响。以下是我们从多个角度进行的详细分析。

### 📊 对基金市场的影响

**1. 权益类基金（偏股基金、混合基金）**

${sentiment === 'positive' ? '这一消息对权益类基金构成正面催化。从历史数据来看，类似事件发生后偏股基金指数1个月内平均上涨2-3%。当前市场整体估值处于历史中低位，利好因素的出现可能加速估值修复。' : sentiment === 'negative' ? '这一消息对权益类基金构成短期压力。投资者情绪可能受到影响，部分资金可能选择暂时观望。建议持有偏股基金的投资者不要恐慌性赎回，等待市场消化利空后再做判断。' : '这一消息对权益类基金的影响偏中性。短期市场可能维持震荡格局，但中长期走势仍取决于基本面和流动性。'}

具体来看，消费主题基金和科技主题基金可能受益最为明显。消费板块受益于内需复苏和政策支持，而科技板块则受益于AI产业链的持续景气。

**2. 债券型基金**

${sentiment === 'positive' ? '债券基金同样受益于这一利好。市场风险偏好的改善会带动信用债价格上升，纯债基金和二级债基短期净值有望上涨0.3-0.8%。' : sentiment === 'negative' ? '债券基金可能成为资金的避风港。在权益市场承压时，资金往往会流向债市避险，纯债基金短期可能获得超额收益。' : '债券基金受影响有限。利率债短期内可能维持窄幅震荡，信用债则需关注个券风险。'}

**3. ETF和指数基金**

${sentiment === 'positive' ? '宽基ETF有望持续获得资金流入。沪深300ETF、科创50ETF等核心品种的成交量和规模可能进一步增长。ETF作为便捷的配置工具，在市场情绪改善时往往最先受益。' : 'ETF可能出现短期赎回压力，但不会改变被动投资长期增长的趋势。对于定投ETF的投资者，无需因短期波动而改变计划。' : 'ETF市场整体平稳，行业轮动可能加快，建议关注均衡配置的宽基ETF。'}

### 👤 基金经理观点

**张坤**（易方达基金）："市场短期是投票机，长期是称重机。${sentiment === 'positive' ? '当前的积极变化有助于改善市场情绪，但我们更应该关注企业的长期价值创造能力。' : '短期的扰动不会改变优质企业的长期价值。' : '我们更应该关注企业基本面的变化，而非短期消息面。'}"

**谢治宇**（兴证全球基金）："${sentiment === 'positive' ? '我们注意到市场情绪正在改善，估值修复行情有望延续。但投资者应该保持理性，不要追涨杀跌。' : '市场波动是正常的，重要的是坚持自己的投资框架，不被短期消息左右。' : '我们维持均衡配置的策略，不去预判短期市场方向。'}建议普通投资者坚持定投，用时间换空间。"

### 💡 对基民的操作建议

**如果你是定投型投资者：**
> ${sentiment === 'positive' ? '按原计划继续定投即可，不要因为好消息而一次性加仓太多。定投的核心优势就是纪律性，不要打破它。' : '继续定投，不要恐慌暂停。市场下跌时你买到的其实是更便宜的份额。' : '继续按计划执行，不需要因为中性消息而调整策略。'}

**如果你是一次性投资者：**
> ${sentiment === 'positive' ? '当前市场估值仍处于历史中低位，可以考虑分批建仓。建议将资金分成3-6份，每月投入一份，降低单点风险。' : '建议暂时观望，等待市场充分消化后再考虑建仓。或者采用定投方式逐步入场。' : '建议保持现有仓位，不急于加仓或减仓。等待更明确的信号。'}

**如果你持有相关基金：**
> 检查你的持仓是否过于集中在某个行业或主题。单一赛道持仓不超过总仓位的20%是基本原则。如果过于集中，可以趁反弹适当调整。

### 📈 历史复盘

回顾过去3年类似事件的市场表现：

| 时间 | 事件 | 偏股基金1月后表现 |
|------|------|:--:|
| 2025年3月 | 央行降准 | +3.2% |
| 2025年6月 | 新"国九条"发布 | +5.8% |
| 2025年9月 | 美联储降息 | +4.1% |
| 2026年1月 | PMI超预期 | +2.5% |

> ⚠️ **免责声明**：以上分析仅供参考学习，历史表现不代表未来收益。投资有风险，入市需谨慎。

### 总结

> ${title}。总体来说，${sentiment === 'positive' ? '这是一个积极信号，但投资者应保持冷静，避免追高。坚持长期投资和资产配置才是制胜之道。' : sentiment === 'negative' ? '短期承压但不改长期趋势。投资者应该保持耐心，利用定投平摊成本。' : '市场需要更多时间来消化这一信息。投资者应保持灵活，做好仓位管理。'}

---
*本文由基智学AI分析引擎生成，内容仅供参考，不构成投资建议。*
`
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
      return {
        ...article,
        content: generateArticleContent(id, article.title, article.sentiment),
        related_news: all.filter(n => n.id !== id).slice(0, 3),
      }
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
