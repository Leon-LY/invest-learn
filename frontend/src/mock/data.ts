/**
 * Mock data for investment learning platform.
 * Generates realistic financial data for development and demo without a backend.
 */

// ─── Helper to generate random prices ───
function r(base: number, range: number) {
  return +(base + (Math.random() - 0.5) * range).toFixed(2)
}

function pct() {
  return +((Math.random() - 0.5) * 8).toFixed(2)
}

function sparkline(base: number, points: number = 30) {
  const vals: number[] = []
  let v = base
  for (let i = 0; i < points; i++) {
    v += (Math.random() - 0.48) * base * 0.02
    vals.push(+v.toFixed(2))
  }
  return vals
}

function vol() {
  return Math.floor(Math.random() * 50000000) + 10000000
}

// ─── Indices ───
export const mockIndices = [
  { code: '000001', name: '上证指数', market: 'A', country: 'CN', latest_price: r(3150, 40), change_pct: pct(), sparkline: sparkline(3150) },
  { code: '399001', name: '深证成指', market: 'A', country: 'CN', latest_price: r(9800, 200), change_pct: pct(), sparkline: sparkline(9800) },
  { code: '399006', name: '创业板指', market: 'A', country: 'CN', latest_price: r(1950, 50), change_pct: pct(), sparkline: sparkline(1950) },
  { code: '000688', name: '科创50', market: 'A', country: 'CN', latest_price: r(850, 30), change_pct: pct(), sparkline: sparkline(850) },
  { code: '^GSPC', name: 'S&P 500', market: 'US', country: 'US', latest_price: r(5500, 80), change_pct: pct(), sparkline: sparkline(5500) },
  { code: '^HSI', name: '恒生指数', market: 'HK', country: 'HK', latest_price: r(18500, 400), change_pct: pct(), sparkline: sparkline(18500) },
]

// ─── Stocks ───
const stockDefs = [
  { code: '600519', name: '贵州茅台', market: 'A', sector: '白酒', pe: 28.5, pb: 8.2, mv: 21000 },
  { code: '000858', name: '五粮液', market: 'A', sector: '白酒', pe: 18.2, pb: 4.5, mv: 5800 },
  { code: '300750', name: '宁德时代', market: 'A', sector: '锂电池', pe: 22.8, pb: 5.1, mv: 8200 },
  { code: '601318', name: '中国平安', market: 'A', sector: '保险', pe: 9.5, pb: 0.95, mv: 7200 },
  { code: '000001', name: '平安银行', market: 'A', sector: '银行', pe: 4.8, pb: 0.55, mv: 2100 },
  { code: 'AAPL', name: 'Apple Inc.', market: 'US', sector: 'Technology', pe: 32.1, pb: 45.2, mv: 3200000 },
  { code: 'NVDA', name: 'NVIDIA Corp.', market: 'US', sector: 'Technology', pe: 48.5, pb: 55.3, mv: 2800000 },
  { code: 'TSLA', name: 'Tesla Inc.', market: 'US', sector: 'Automotive', pe: 65.2, pb: 12.8, mv: 580000 },
  { code: '0700.HK', name: '腾讯控股', market: 'HK', sector: 'Technology', pe: 18.5, pb: 4.2, mv: 32000 },
  { code: '9988.HK', name: '阿里巴巴-SW', market: 'HK', sector: 'Technology', pe: 12.3, pb: 1.8, mv: 18000 },
]

function generateStockDetail(def: typeof stockDefs[0]) {
  const price = r(def.pe * (def.mv > 1000000 ? 8 : def.mv > 10000 ? 5 : 3), def.pe * 0.5)
  const basePrice = price
  const klines: any[] = []
  let p = basePrice * 0.85
  for (let i = 250; i >= 0; i--) {
    const change = (Math.random() - 0.48) * p * 0.03
    const open = p
    p += change
    const close = p
    const high = Math.max(open, close) * (1 + Math.random() * 0.02)
    const low = Math.min(open, close) * (1 - Math.random() * 0.02)
    const date = new Date()
    date.setDate(date.getDate() - i)
    klines.push({
      date: date.toISOString().slice(0, 10),
      open: +open.toFixed(2),
      high: +high.toFixed(2),
      low: +low.toFixed(2),
      close: +close.toFixed(2),
      volume: vol(),
      amount: +(vol() * close).toFixed(0),
    })
  }
  const changePct = +(((klines[klines.length - 1].close - klines[klines.length - 2].close) / klines[klines.length - 2].close) * 100).toFixed(2)

  return {
    info: { code: def.code, name: def.name, market: def.market, security_type: 'stock', sector: def.sector },
    quote: {
      code: def.code, name: def.name, market: def.market,
      latest_price: klines[klines.length - 1].close,
      change: +(klines[klines.length - 1].close - klines[klines.length - 2].close).toFixed(2),
      change_pct: changePct,
      volume: klines[klines.length - 1].volume,
      amount: klines[klines.length - 1].amount,
      turnover_rate: +((Math.random() * 3 + 1).toFixed(2)),
      pe_ratio: def.pe, pb_ratio: def.pb, total_mv: def.mv,
      circ_mv: def.mv * (0.6 + Math.random() * 0.3),
    },
    fundamentals: { pe: def.pe, pb: def.pb, total_mv: def.mv },
    klines: klines.slice(-250),
  }
}

export const mockStocks: Record<string, any> = {}
stockDefs.forEach(d => { mockStocks[d.code] = generateStockDetail(d) })

// ─── Funds ───
const fundDefs = [
  { code: '161725', name: '招商中证白酒', fund_type: '指数型', company: '招商基金', aum: 68000000000 },
  { code: '005827', name: '易方达蓝筹精选混合', fund_type: '混合型', company: '易方达基金', aum: 45000000000 },
  { code: '110022', name: '易方达消费行业', fund_type: '股票型', company: '易方达基金', aum: 32000000000 },
]

export const mockFunds: Record<string, any> = {}
fundDefs.forEach(f => {
  const nav = r(2.5, 1.0)
  const navHistory: any[] = []
  let n = nav * 0.7
  for (let i = 90; i >= 0; i--) {
    n += (Math.random() - 0.49) * 0.03
    const date = new Date()
    date.setDate(date.getDate() - i)
    navHistory.push({
      date: date.toISOString().slice(0, 10),
      unit_nav: +n.toFixed(4),
      acc_nav: +(n * 1.5).toFixed(4),
      daily_return: +((Math.random() - 0.5) * 3).toFixed(4),
    })
  }
  mockFunds[f.code] = {
    info: { ...f, inception_date: '2018-01-01', latest_nav: navHistory[navHistory.length - 1].unit_nav, latest_return: navHistory[navHistory.length - 1].daily_return },
    nav_history: navHistory,
  }
})

// ─── Sectors ───
export const mockSectors = [
  '白酒,半导体,光伏,锂电池,新能源汽车,AI人工智能,消费电子,创新药,医疗器械,券商,银行,保险,房地产,钢铁,煤炭,军工,游戏,传媒,旅游酒店,食品饮料'.split(',').map(name => ({
    sector_name: name,
    change_pct: pct(),
    net_inflow: +(Math.random() * 200 - 100).toFixed(2) as any * 1e8,
    top_stock: ['600519', '300750', '601318', '000858'][Math.floor(Math.random() * 4)],
    top_stock_pct: +((Math.random() * 8 + 2)).toFixed(2),
  }))
]

// ─── Capital Flow ───
export const mockCapitalFlow = {
  north: Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (29 - i))
    return {
      date: date.toISOString().slice(0, 10),
      net_inflow: +(Math.random() * 200 - 80).toFixed(2) as any * 1e8,
      balance: +(18000 + Math.random() * 2000).toFixed(2) as any * 1e8,
    }
  }),
  south: [],
}

// ─── Market Breadth ───
export const mockBreadth = {
  up_count: Math.floor(Math.random() * 2500 + 1500),
  down_count: Math.floor(Math.random() * 2000 + 800),
  flat_count: Math.floor(Math.random() * 300 + 50),
  limit_up: Math.floor(Math.random() * 60 + 20),
  limit_down: Math.floor(Math.random() * 20 + 2),
  total_amount: Math.random() * 20000 + 8000 as any * 1e8,
}

// ─── News ───
const newsTemplates = [
  { title: '中央经济工作会议：着力扩大国内需求，提振市场信心', categories: ['macro'], sentiment: 'positive' },
  { title: '央行释放流动性信号，MLF利率下调10个基点', categories: ['macro'], sentiment: 'positive' },
  { title: '北向资金连续5日净流入，外资看好A股中长期配置价值', categories: ['macro'], sentiment: 'positive' },
  { title: '美联储维持利率不变，市场预期年内降息3次', categories: ['macro'], sentiment: 'positive' },
  { title: '多家券商发布年中策略：A股下半年有望迎来修复行情', categories: ['macro'], sentiment: 'positive' },
  { title: '半导体行业景气度回升，封测产能利用率超过85%', categories: ['industry'], sentiment: 'positive' },
  { title: '光伏硅料价格跌破成本线，行业或加速产能出清', categories: ['industry'], sentiment: 'negative' },
  { title: '新能源汽车7月销量同比增长35%，渗透率突破45%', categories: ['industry'], sentiment: 'positive' },
  { title: '消费电子需求回暖，华为苹果供应链订单增加', categories: ['industry'], sentiment: 'positive' },
  { title: '白酒板块迎来旺季行情，贵州茅台股价创年内新高', categories: ['industry'], sentiment: 'positive' },
  { title: '医药板块持续回暖，创新药IND申报数量创历史新高', categories: ['industry'], sentiment: 'positive' },
  { title: '腾讯控股发布大模型应用"混元"，AI布局深化', categories: ['stock'], sentiment: 'positive' },
  { title: '宁德时代与特斯拉签下大单，储能业务增速超预期', categories: ['stock'], sentiment: 'positive' },
  { title: '茅台飞天批价企稳回升，经销商信心逐步恢复', categories: ['stock'], sentiment: 'positive' },
  { title: 'Apple 发布Vision Pro 2代，供应链有望受益', categories: ['stock'], sentiment: 'positive' },
  { title: 'NVIDIA 财报超预期，AI芯片需求持续旺盛', categories: ['stock'], sentiment: 'positive' },
  { title: '指数基金规模突破3万亿，被动投资趋势势不可挡', categories: ['fund'], sentiment: 'positive' },
  { title: '红利ETF年内吸金超千亿，高股息策略持续受追捧', categories: ['fund'], sentiment: 'positive' },
  { title: '国际油价高位震荡，能源股配置价值凸显', categories: ['macro'], sentiment: 'neutral' },
  { title: '楼市调控政策密集出台，房地产市场能否企稳？', categories: ['macro'], sentiment: 'neutral' },
]

export function generateMockNews() {
  return newsTemplates.map((t, i) => ({
    id: i + 1,
    title: t.title,
    summary: `${t.title}。据权威消息来源报道，相关政策与市场动态值得投资者密切关注。分析人士认为，这一变化将对相关板块产生重要影响。`,
    source: ['东方财富', '雪球', '华尔街见闻', '新浪财经', '财联社'][Math.floor(Math.random() * 5)],
    source_url: '#',
    author: '',
    sentiment: t.sentiment,
    categories: t.categories,
    tags: t.categories,
    related_stocks: [],
    published_at: `${new Date(Date.now() - Math.random() * 86400000 * 3).toISOString().slice(0, 19)}`,
  }))
}

// ─── Search ───
export function mockSearch(q: string) {
  const all = [...stockDefs, { code: '159915', name: '创业板ETF', market: 'A', sector: '', pe: 0, pb: 0, mv: 0 }]
  return all
    .filter(s => s.name.includes(q) || s.code.includes(q))
    .map(s => ({ code: s.code, name: s.name, market: s.market, security_type: s.code.startsWith('1') ? 'etf' : 'stock', match_score: 1.0 }))
}

// ─── Watchlist ───
let watchlistIdCounter = 100
export const mockWatchlist: any[] = []

export function mockAddWatchlist(item: any) {
  const id = ++watchlistIdCounter
  const quote = mockStocks[item.item_code]?.quote
  mockWatchlist.push({ id, ...item, tags: item.tags || [], notes: item.notes || null, sort_order: 0, quote: quote ? { latest_price: quote.latest_price, change_pct: quote.change_pct } : null, added_at: new Date().toISOString() })
  return { id, item_type: item.item_type, item_code: item.item_code }
}

export function mockRemoveWatchlist(id: number) {
  const idx = mockWatchlist.findIndex(i => i.id === id)
  if (idx >= 0) mockWatchlist.splice(idx, 1)
}

// ─── Learning Content ───
export const mockCategories = [
  { id: 1, name: '投资入门', slug: 'getting-started', description: '零基础学投资', icon: 'rocket', children: [] },
  { id: 2, name: '基本面分析', slug: 'fundamental-analysis', description: '读懂财务报表', icon: 'chart-bar', children: [] },
  { id: 3, name: '技术分析', slug: 'technical-analysis', description: 'K线图、均线、指标', icon: 'trending-up', children: [] },
  { id: 4, name: '基金投资', slug: 'fund-investing', description: '基金入门与定投', icon: 'wallet', children: [] },
  { id: 5, name: '风险管理', slug: 'risk-management', description: '控制风险是第一课', icon: 'shield', children: [] },
  { id: 6, name: '投资心态', slug: 'investor-psychology', description: '克服贪婪与恐惧', icon: 'heart', children: [] },
]

export const mockArticles = [
  { id: 1, title: '投资是什么？为什么要投资？', slug: 'what-is-investing', summary: '了解投资的基本概念，以及为什么通货膨胀会让你必须学会投资。', level: 'beginner', tags: ['投资基础'], estimated_read: 8, view_count: 15280, published_at: '2025-06-01T10:00:00' },
  { id: 2, title: '股票入门：什么是股票？', slug: 'stock-basics', summary: '通俗解释股票是什么、买卖股票如何赚钱、A股市场的基本规则。', level: 'beginner', tags: ['股票基础'], estimated_read: 10, view_count: 12350, published_at: '2025-05-28T14:00:00' },
  { id: 3, title: 'PE、PB、ROE到底是什么？', slug: 'pe-pb-roe-explained', summary: '用通俗易懂的语言解释三个最重要的估值指标。', level: 'beginner', tags: ['基本面'], estimated_read: 12, view_count: 9870, published_at: '2025-05-25T09:00:00' },
  { id: 4, title: '基金定投：新手最友好的投资方式', slug: 'fund-dca-strategy', summary: '什么是基金定投？为什么定投能降低风险？', level: 'beginner', tags: ['基金', '定投'], estimated_read: 8, view_count: 11200, published_at: '2025-05-20T16:00:00' },
  { id: 5, title: '投资第一课：如何控制风险？', slug: 'risk-management-basics', summary: '投资的首要原则不是赚钱，而是不亏钱。', level: 'beginner', tags: ['风险管理'], estimated_read: 8, view_count: 7650, published_at: '2025-05-15T11:00:00' },
  { id: 6, title: '投资心理学：克服贪婪与恐惧', slug: 'investor-psychology-101', summary: '巴菲特说：别人贪婪时我恐惧，别人恐惧时我贪婪。', level: 'beginner', tags: ['投资心态'], estimated_read: 8, view_count: 8900, published_at: '2025-05-10T08:00:00' },
]

const articleContent = `## 重要概念

在投资领域，有几个核心概念需要先理解清楚。

### 1. 投资与投机的区别

**投资**是基于对企业价值的分析，买入并长期持有，分享企业成长带来的收益。
**投机**是基于对价格波动的判断，试图通过短期买卖差价获利。

格雷厄姆说过："投资操作是经过透彻分析，承诺本金安全和满意回报的操作。不能满足这些要求的操作就是投机。"

### 2. 复利的魔力

复利是投资者最强大的武器。爱因斯坦称之为"世界第八大奇迹"。

> 每月定投1000元，年化收益8%，坚持30年，最终能积累约150万元。

### 3. 风险与收益的关系

高收益必然伴随高风险。理解自己能承受多大的风险，是投资的第一步。

记住：永远不要投资你输不起的钱。`

export const mockArticleDetail: Record<string, any> = {}
mockArticles.forEach(a => {
  mockArticleDetail[a.slug] = {
    ...a,
    content: articleContent,
    prev_article: null,
    next_article: null,
    related_articles: [],
  }
})

export const mockGlossary = [
  { term: '市盈率', term_en: 'P/E Ratio', definition: '市盈率 = 股价 ÷ 每股收益。通俗理解：按照当前盈利水平需要多少年回本。PE越低理论上越便宜。', category: 'fundamental', related_terms: ['市净率', '每股收益'] },
  { term: '市净率', term_en: 'P/B Ratio', definition: '市净率 = 股价 ÷ 每股净资产。PB<1叫"破净"，意味着股价比净资产还低。', category: 'fundamental', related_terms: ['市盈率', '净资产'] },
  { term: '净资产收益率', term_en: 'ROE', definition: 'ROE = 净利润 ÷ 净资产 × 100%。巴菲特最看重的指标，偏好ROE>15%的公司。', category: 'fundamental', related_terms: ['市盈率', '市净率'] },
  { term: 'K线图', term_en: 'Candlestick Chart', definition: '最常用的股票价格走势图。一根K线包含开盘价、收盘价、最高价、最低价。红色（阳线）表示上涨。', category: 'technical', related_terms: ['均线', 'MACD'] },
  { term: '均线', term_en: 'Moving Average', definition: '一定时期内收盘价的平均值连成的线。短期线上穿长期线叫"金叉"（看涨信号），下穿叫"死叉"（看跌信号）。', category: 'technical', related_terms: ['K线图', 'MACD'] },
  { term: 'MACD', term_en: 'MACD', definition: '最常用的技术指标之一。DIF上穿DEA（金叉）是买入信号，下穿（死叉）是卖出信号。', category: 'technical', related_terms: ['均线', 'K线图'] },
  { term: 'ETF', term_en: 'Exchange Traded Fund', definition: '交易型开放式指数基金，像买卖股票一样买卖一篮子股票。费率低、透明度高，是新手入市的最佳选择。', category: 'fund', related_terms: ['指数基金', '定投'] },
  { term: '定投', term_en: 'Dollar-Cost Averaging', definition: '定期定额投资。跌时买更多，涨时买更少。不需要择时，是新手最推荐的投资策略。', category: 'fund', related_terms: ['ETF', '基金'] },
  { term: '北向资金', term_en: 'Northbound Capital', definition: '通过沪港通、深港通从香港流入A股的外资，被称为"聪明钱"。', category: 'general', related_terms: ['南向资金'] },
  { term: '涨停/跌停', term_en: 'Limit Up/Down', definition: 'A股每日价格最大波动限制。普通股票±10%，ST股±5%。', category: 'general', related_terms: ['ST股'] },
  { term: '分红', term_en: 'Dividend', definition: '上市公司把利润的一部分以现金或股票形式分配给股东。持续高分红的公司通常是好公司。', category: 'fundamental', related_terms: ['股息率'] },
  { term: '股息率', term_en: 'Dividend Yield', definition: '股息率 = 每股分红 ÷ 当前股价 × 100%。反映买入后每年能收到多少"利息"。', category: 'fundamental', related_terms: ['分红', '市盈率'] },
  { term: '止损', term_en: 'Stop Loss', definition: '设定最大可承受亏损，一旦触及就果断卖出。是控制风险的基本纪律。', category: 'risk', related_terms: ['止盈', '仓位'] },
  { term: '仓位', term_en: 'Position Size', definition: '投入资金占总资金的比例。满仓=100%（风险大），半仓=50%（适中）。新手建议永远不要满仓。', category: 'risk', related_terms: ['止损', '分散投资'] },
  { term: '换手率', term_en: 'Turnover Rate', definition: '换手率 = 成交量 ÷ 流通股本 × 100%。反映交易活跃程度。1%-3%为正常，>10%为异常活跃。', category: 'technical', related_terms: ['成交量'] },
  { term: '总市值', term_en: 'Market Capitalization', definition: '总市值 = 股价 × 总股本。分为大盘股（>500亿）、中盘股（100-500亿）、小盘股（<100亿）。', category: 'fundamental', related_terms: ['市盈率', '流通市值'] },
  { term: '债券', term_en: 'Bond', definition: '政府或企业发行的"借条"。买债券相当于借钱给对方，对方承诺到期还本付息。国债最安全。', category: 'fundamental', related_terms: ['基金', '风险'] },
  { term: 'T+1制度', term_en: 'T+1 Settlement', definition: 'A股今天买入，最早明天才能卖出。港股和美股是T+0，当天即可买卖。', category: 'general', related_terms: ['A股'] },
  { term: '基金净值', term_en: 'Net Asset Value', definition: '基金的单位净值 = 基金总资产 ÷ 基金总份额。净值走势图反映基金业绩。净值高低与基金贵贱无关。', category: 'fund', related_terms: ['基金', 'ETF'] },
  { term: '护城河', term_en: 'Economic Moat', definition: '巴菲特提出的概念，指企业持续竞争优势。常见护城河：品牌（茅台）、网络效应（微信）、规模优势（沃尔玛）。', category: 'fundamental', related_terms: ['ROE', '价值投资'] },
]

export const mockStrategies = [
  { id: 1, name: '定投策略（DCA）', slug: 'dollar-cost-averaging', summary: '定期定额投资，摊低成本，不择时。最适合新手的懒人投资法。', difficulty: 'beginner', risk_level: 'low', suitable_for: '投资新手、上班族', key_metrics: ['定投频率', '定投金额'] },
  { id: 2, name: '价值投资', slug: 'value-investing', summary: '寻找被低估的优质公司，以合理价格买入并长期持有。巴菲特的核心理念。', difficulty: 'intermediate', risk_level: 'medium', suitable_for: '有分析能力的中长期投资者', key_metrics: ['PE', 'PB', 'ROE'] },
  { id: 3, name: '股债平衡策略', slug: 'stock-bond-balance', summary: '股票和债券按比例配置，定期再平衡，控制风险的同时获取合理收益。', difficulty: 'beginner', risk_level: 'low', suitable_for: '追求稳健收益的投资者', key_metrics: ['股债比例', '最大回撤'] },
  { id: 4, name: '网格交易策略', slug: 'grid-trading', summary: '在价格区间内低买高卖，像撒网一样捕捉震荡利润。', difficulty: 'intermediate', risk_level: 'medium', suitable_for: '有技术分析基础的投资者', key_metrics: ['网格间距', '区间设定'] },
  { id: 5, name: '红利再投资策略', slug: 'dividend-reinvestment', summary: '选择高股息公司，分红持续再投资，利用复利效应增长资产。', difficulty: 'beginner', risk_level: 'low', suitable_for: '追求稳定现金流的保守投资者', key_metrics: ['股息率', '分红稳定性'] },
]
