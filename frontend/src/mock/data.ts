/**
 * Fund-centric mock data for InvestLearn.
 * All data focuses on fund investing for beginners.
 */

function r(base: number, range: number) { return +(base + (Math.random() - 0.5) * range).toFixed(2) }
function pct() { return +((Math.random() - 0.5) * 5).toFixed(2) }
function sparkline(base: number, points = 30) {
  const vals: number[] = []; let v = base
  for (let i = 0; i < points; i++) { v += (Math.random() - 0.48) * base * 0.015; vals.push(+v.toFixed(4)) }
  return vals
}

// ─── Fund Market Indices ───
export const mockIndices = [
  { code: 'CNFI', name: '中证基金指数', market: 'CN', country: 'CN', latest_price: r(6850, 80), change_pct: pct(), sparkline: sparkline(6850) },
  { code: 'CSI885', name: '偏股基金指数', market: 'CN', country: 'CN', latest_price: r(11280, 150), change_pct: pct(), sparkline: sparkline(11280) },
  { code: 'CSI886', name: '偏债基金指数', market: 'CN', country: 'CN', latest_price: r(5320, 30), change_pct: pct(), sparkline: sparkline(5320) },
  { code: 'CSI887', name: '货币基金指数', market: 'CN', country: 'CN', latest_price: r(1820, 5), change_pct: pct(), sparkline: sparkline(1820) },
  { code: 'CSI888', name: 'QDII基金指数', market: 'CN', country: 'CN', latest_price: r(4250, 60), change_pct: pct(), sparkline: sparkline(4250) },
  { code: 'ETF50', name: 'ETF综合指数', market: 'CN', country: 'CN', latest_price: r(2980, 40), change_pct: pct(), sparkline: sparkline(2980) },
]

// ─── Fund Database ───
const fundDefs = [
  // 指数型
  { code: '161725', name: '招商中证白酒指数(LOF)A', type: '指数型', category: '消费', company: '招商基金', manager: '侯昊', scale: 680, star: 4, risk: '高', inception: '2015-05-27' },
  { code: '110003', name: '易方达上证50指数A', type: '指数型', category: '宽基', company: '易方达基金', manager: '张胜记', scale: 230, star: 4, risk: '高', inception: '2004-03-22' },
  { code: '502010', name: '易方达沪深300ETF联接A', type: '指数型', category: '宽基', company: '易方达基金', manager: '余海燕', scale: 180, star: 5, risk: '中高', inception: '2012-03-22' },
  { code: '000311', name: '华泰柏瑞沪深300ETF联接A', type: '指数型', category: '宽基', company: '华泰柏瑞基金', manager: '柳军', scale: 350, star: 5, risk: '中高', inception: '2012-05-04' },
  // 混合型
  { code: '005827', name: '易方达蓝筹精选混合', type: '混合型', category: '偏股', company: '易方达基金', manager: '张坤', scale: 450, star: 5, risk: '中高', inception: '2018-09-05' },
  { code: '163406', name: '兴全合润混合(LOF)', type: '混合型', category: '偏股', company: '兴证全球基金', manager: '谢治宇', scale: 280, star: 5, risk: '中高', inception: '2010-04-22' },
  { code: '002939', name: '广发创新升级混合', type: '混合型', category: '偏股', company: '广发基金', manager: '刘格菘', scale: 120, star: 4, risk: '高', inception: '2017-06-15' },
  { code: '001475', name: '易方达国防军工混合A', type: '混合型', category: '行业', company: '易方达基金', manager: '何崇恺', scale: 95, star: 4, risk: '高', inception: '2015-06-19' },
  { code: '320007', name: '诺安成长混合', type: '混合型', category: '行业', company: '诺安基金', manager: '蔡嵩松', scale: 180, star: 4, risk: '高', inception: '2009-03-10' },
  // 债券型
  { code: '110027', name: '易方达安心回报债券A', type: '债券型', category: '混合债', company: '易方达基金', manager: '张清华', scale: 320, star: 5, risk: '中低', inception: '2011-06-21' },
  { code: '000290', name: '鹏华全球高收益债(QDII)', type: '债券型', category: 'QDII债', company: '鹏华基金', manager: '尤柏年', scale: 45, star: 4, risk: '中', inception: '2013-10-22' },
  // 货币型
  { code: '000198', name: '天弘余额宝货币', type: '货币型', category: '货币', company: '天弘基金', manager: '王登峰', scale: 7500, star: 5, risk: '低', inception: '2013-05-29' },
  // ETF
  { code: '510050', name: '华夏上证50ETF', type: 'ETF', category: '宽基', company: '华夏基金', manager: '张弘弢', scale: 550, star: 5, risk: '中高', inception: '2004-12-30' },
  { code: '510300', name: '华泰柏瑞沪深300ETF', type: 'ETF', category: '宽基', company: '华泰柏瑞基金', manager: '柳军', scale: 1200, star: 5, risk: '中高', inception: '2012-05-04' },
  { code: '159915', name: '易方达创业板ETF', type: 'ETF', category: '宽基', company: '易方达基金', manager: '成曦', scale: 350, star: 4, risk: '高', inception: '2011-09-20' },
  { code: '588000', name: '华夏科创50ETF', type: 'ETF', category: '宽基', company: '华夏基金', manager: '荣膺', scale: 680, star: 4, risk: '高', inception: '2020-09-28' },
  // QDII
  { code: '513100', name: '国泰纳斯达克100ETF', type: 'QDII', category: '海外', company: '国泰基金', manager: '吴向军', scale: 120, star: 5, risk: '中高', inception: '2013-05-15' },
  { code: '513500', name: '博时标普500ETF', type: 'QDII', category: '海外', company: '博时基金', manager: '万琼', scale: 85, star: 5, risk: '中高', inception: '2015-05-27' },
]

function generateFundDetail(f: typeof fundDefs[0]) {
  const nav = r(f.type === '货币型' ? 1.0 : f.type === '债券型' ? 1.5 : 2.5, f.type === '货币型' ? 0.001 : 0.8)
  const navHistory: any[] = []
  let n = nav * 0.75
  for (let i = 180; i >= 0; i--) {
    const vol = f.type === '货币型' ? 0.00002 : f.type === '债券型' ? 0.003 : 0.015
    n += (Math.random() - 0.48) * vol * n
    const date = new Date(); date.setDate(date.getDate() - i)
    navHistory.push({ date: date.toISOString().slice(0, 10), unit_nav: +n.toFixed(4), acc_nav: +(n * 1.8).toFixed(4), daily_return: +((Math.random() - 0.5) * (f.type === '货币型' ? 0.01 : f.type === '债券型' ? 0.3 : 2.5)).toFixed(4) })
  }
  const latestNav = navHistory[navHistory.length - 1]
  const latestReturn = latestNav.daily_return

  return {
    info: {
      code: f.code, name: f.name, fund_type: f.type, category: f.category,
      company: f.company, manager: f.manager, scale: f.scale, star: f.star,
      risk_level: f.risk, inception_date: f.inception,
      latest_nav: latestNav.unit_nav, latest_return: latestReturn,
    },
    nav_history: navHistory,
  }
}

export const mockFunds: Record<string, any> = {}
fundDefs.forEach(f => { mockFunds[f.code] = generateFundDetail(f) })

// ─── Fund Categories ───
export const mockSectors = [
  { name: '指数型基金', count: 1580, avg_return: pct(), inflow: +(Math.random() * 500 + 200).toFixed(1) },
  { name: '混合型基金', count: 4200, avg_return: pct(), inflow: +(Math.random() * 300 + 100).toFixed(1) },
  { name: '债券型基金', count: 2800, avg_return: pct(), inflow: +(Math.random() * 800 + 500).toFixed(1) },
  { name: '货币型基金', count: 680, avg_return: 0.02, inflow: +(Math.random() * 2000 + 1000).toFixed(1) },
  { name: 'ETF基金', count: 890, avg_return: pct(), inflow: +(Math.random() * 600 + 300).toFixed(1) },
  { name: 'QDII基金', count: 320, avg_return: pct(), inflow: +(Math.random() * 150 + 50).toFixed(1) },
  { name: 'FOF基金', count: 450, avg_return: pct(), inflow: +(Math.random() * 100 + 30).toFixed(1) },
  { name: 'REITs', count: 35, avg_return: pct(), inflow: +(Math.random() * 50 + 10).toFixed(1) },
  { name: '量化基金', count: 220, avg_return: pct(), inflow: +(Math.random() * 80 + 20).toFixed(1) },
  { name: '红利基金', count: 180, avg_return: pct(), inflow: +(Math.random() * 200 + 80).toFixed(1) },
  { name: '养老目标基金', count: 260, avg_return: pct(), inflow: +(Math.random() * 120 + 40).toFixed(1) },
  { name: '同业存单基金', count: 95, avg_return: +((Math.random() * 0.5 + 1.5).toFixed(2)), inflow: +(Math.random() * 400 + 200).toFixed(1) },
]

// ─── Market Breadth ───
export const mockBreadth = {
  up_count: Math.floor(Math.random() * 3000 + 2000),
  down_count: Math.floor(Math.random() * 1500 + 500),
  flat_count: Math.floor(Math.random() * 500 + 100),
  total_amount: Math.random() * 5000 + 3000,
}

// ─── Capital Flow ───
export const mockCapitalFlow = {
  north: Array.from({ length: 30 }, (_, i) => {
    const date = new Date(); date.setDate(date.getDate() - (29 - i))
    return { date: date.toISOString().slice(0, 10), net_inflow: +(Math.random() * 100 - 30).toFixed(2), balance: +(12000 + Math.random() * 1000).toFixed(2) }
  }),
  south: [],
}

// ─── Fund News ───
const newsTemplates = [
  { title: '多只权益基金一季度规模翻倍，资金持续涌入优质产品', sentiment: 'positive', cat: 'industry' },
  { title: 'ETF总规模突破3万亿，被动投资已成主流配置方式', sentiment: 'positive', cat: 'industry' },
  { title: '公募基金降费潮来袭，管理费托管费双双下调利好投资者', sentiment: 'positive', cat: 'industry' },
  { title: '基金投顾业务试点扩大，帮你选基金的"管家"来了', sentiment: 'positive', cat: 'industry' },
  { title: '张坤最新季报：增持消费医药，看好长期价值回归', sentiment: 'positive', cat: 'manager' },
  { title: '谢治宇致投资者信：在震荡中保持定力，定投是最佳策略', sentiment: 'positive', cat: 'manager' },
  { title: '基金经理变更潮：年内已有200+位基金经理离任，如何应对？', sentiment: 'neutral', cat: 'manager' },
  { title: '债券基金为何持续吸金？10张图看懂债基投资价值', sentiment: 'positive', cat: 'bond' },
  { title: '红利基金今年平均收益超15%，高股息策略还能追吗？', sentiment: 'positive', cat: 'strategy' },
  { title: '新手必看：基金定投选周投还是月投？回测数据告诉你答案', sentiment: 'positive', cat: 'beginner' },
  { title: 'QDII基金限购频发，海外投资热情高涨但额度告急', sentiment: 'neutral', cat: 'qdii' },
  { title: '同业存单基金规模破万亿，"闲钱理财"新选择来了', sentiment: 'positive', cat: 'product' },
  { title: '养老FOF基金Y份额：每年最高省税5400元，你开通了吗？', sentiment: 'positive', cat: 'product' },
  { title: '基金清盘数量创新高：为什么迷你基金越来越多？投资者该跑吗', sentiment: 'negative', cat: 'risk' },
  { title: '量化基金超额收益持续衰减，行业格局面临重塑', sentiment: 'neutral', cat: 'industry' },
  { title: '北向资金连续买入，外资通过ETF布局中国资产的逻辑', sentiment: 'positive', cat: 'macro' },
  { title: '个人养老金制度全面铺开：每年12000额度，选什么基金最划算？', sentiment: 'positive', cat: 'pension' },
  { title: '基金公司自购潮再起：20家公司自购超30亿元，释放什么信号？', sentiment: 'positive', cat: 'industry' },
  { title: 'REITs市场持续扩容：消费基础设施REITs来了，普通人如何参与？', sentiment: 'positive', cat: 'product' },
  { title: '基金净值"回本"了该不该卖？三个问题帮你做决定', sentiment: 'neutral', cat: 'beginner' },
]

export function generateMockNews() {
  return newsTemplates.map((t, i) => ({
    id: i + 1,
    title: t.title,
    summary: `${t.title.slice(0, 30)}...基金投资需关注长期价值与资产配置，建议投资者根据自身风险承受能力做出理性判断。`,
    source: ['中国基金报', '证券时报', '天天基金网', '雪球基金', '华尔街见闻', 'Morningstar'][i % 6],
    sentiment: t.sentiment,
    categories: [t.cat],
    tags: [t.cat],
    related_stocks: [],
    published_at: `${new Date(Date.now() - Math.random() * 86400000 * 5).toISOString().slice(0, 19)}`,
  }))
}

// ─── Search ───
export function mockSearch(q: string) {
  return fundDefs.filter(f => f.name.includes(q) || f.code.includes(q) || f.type.includes(q) || f.company.includes(q) || f.manager.includes(q))
    .map(f => ({ code: f.code, name: f.name, market: 'CN', security_type: f.type === 'ETF' ? 'etf' : 'fund', match_score: 1.0 }))
}

// ─── Watchlist ───
let watchlistIdCounter = 100
export const mockWatchlist: any[] = []
export function mockAddWatchlist(item: any) {
  const id = ++watchlistIdCounter
  const fund = mockFunds[item.item_code]
  const quote = fund ? { latest_price: fund.info.latest_nav, change_pct: fund.info.latest_return } : null
  mockWatchlist.push({ id, ...item, tags: item.tags || [], notes: item.notes || null, sort_order: 0, quote, added_at: new Date().toISOString() })
  return { id, item_type: item.item_type, item_code: item.item_code }
}
export function mockRemoveWatchlist(id: number) {
  const idx = mockWatchlist.findIndex(i => i.id === id)
  if (idx >= 0) mockWatchlist.splice(idx, 1)
}

// ─── Screeener results (fund list) ───
export function getMockFundList() {
  return fundDefs.map(f => ({
    code: f.code, name: f.name, market: 'CN', type: f.type, category: f.category,
    company: f.company, manager: f.manager, scale: f.scale, star: f.star, risk: f.risk,
    latest_nav: mockFunds[f.code]?.info.latest_nav, latest_return: mockFunds[f.code]?.info.latest_return,
  }))
}

// ─── Learning ───
export const mockCategories = [
  { id: 1, name: '基金入门', slug: 'fund-basics', description: '什么是基金？基金怎么买？', icon: 'rocket', children: [] },
  { id: 2, name: '基金类型', slug: 'fund-types', description: '股票基金、债券基金、混合基金等', icon: 'layers', children: [] },
  { id: 3, name: '选基方法论', slug: 'fund-selection', description: '如何挑选好基金？看什么指标？', icon: 'search', children: [] },
  { id: 4, name: '定投策略', slug: 'dca-strategies', description: '定期定额投资，懒人理财法', icon: 'calendar', children: [] },
  { id: 5, name: '资产配置', slug: 'asset-allocation', description: '构建自己的基金组合', icon: 'pie-chart', children: [] },
  { id: 6, name: '避坑指南', slug: 'common-mistakes', description: '基金投资中常见的误区', icon: 'alert', children: [] },
]

export const mockArticles = [
  { id: 1, title: '基金是什么？3分钟搞懂基金投资', slug: 'what-is-fund', summary: '基金是集合投资工具，让普通人也能享受专业管理和分散投资的优势。', level: 'beginner', tags: ['基金基础'], estimated_read: 6, view_count: 25680, published_at: '2026-05-28T10:00:00' },
  { id: 2, title: '基金类型大全：股票基金、债券基金、混合基金怎么选？', slug: 'fund-types-guide', summary: '不同类型的基金风险和收益差异巨大，选对类型是投资成功的第一步。', level: 'beginner', tags: ['基金分类'], estimated_read: 12, view_count: 18920, published_at: '2026-05-25T14:00:00' },
  { id: 3, title: '基金定投终极指南：为什么它是新手最友好的策略', slug: 'fund-dca-ultimate', summary: '定投 = 定时 + 定额 + 投基金。不择时、摊成本、强制储蓄。', level: 'beginner', tags: ['定投', '策略'], estimated_read: 10, view_count: 32100, published_at: '2026-05-20T09:00:00' },
  { id: 4, title: '挑选基金的5个核心指标：净值、收益率、最大回撤、夏普比率、规模', slug: 'fund-metrics', summary: '看懂这5个指标，你就能独立判断一只基金的好坏。', level: 'intermediate', tags: ['选基', '指标'], estimated_read: 15, view_count: 14500, published_at: '2026-05-15T16:00:00' },
  { id: 5, title: '基金组合配置：鸡蛋不要放在一个篮子里', slug: 'portfolio-building', summary: '学会用不同基金构建组合，降低风险，稳健增值。', level: 'intermediate', tags: ['资产配置', '组合'], estimated_read: 12, view_count: 11200, published_at: '2026-05-10T11:00:00' },
  { id: 6, title: '基金亏钱了怎么办？5个常见错误和应对方法', slug: 'fund-loss-handling', summary: '基金亏损时最忌讳恐慌赎回，学会理性应对才能长期盈利。', level: 'beginner', tags: ['风险管理', '心态'], estimated_read: 8, view_count: 19800, published_at: '2026-05-05T08:00:00' },
]

const articleBody = `## 基金投资的核心要点

### 1. 什么是基金？

基金（Fund）是一种**集合投资工具**。简单来说就是：

> 很多人把钱凑在一起，交给专业的基金经理去投资。

这就像请了一个专业的理财师帮你管钱。你自己不需要研究每一只股票，不需要每天盯盘，基金经理和他的研究团队会帮你做这些事。

### 2. 基金的三大优势

**专业管理**：基金经理是金融专业的硕士博士，有多年投资经验，比普通人更懂投资。

**分散风险**：一只基金通常持有几十到上百只股票/债券。即使其中一两只出了问题，对整体影响也很小。

**门槛低**：大多数基金10元起投，让普通人也能参与资本市场。

### 3. 买基金前必问的三个问题

1. **我的钱多久不用？** 3年以内选债基，3-5年选混合基，5年以上可以多配股票基金。

2. **我能承受多大亏损？** 最大回撤10%选债基，20%选混合基，30%以上才能考虑高仓位的股票基金。

3. **我的目标是什么？** 保值选货币/短债，稳健增值选混合基，追求高收益选行业主题基金。

### 4. 新手黄金法则

> **定投宽基指数基金，坚持3年以上，是普通人最容易赚钱的方式。**

- 宽基指数 = 沪深300、中证500这类覆盖面广的指数
- 定投 = 每月固定时间投固定金额
- 3年以上 = 给复利足够的时间发挥作用`

export const mockArticleDetail: Record<string, any> = {}
mockArticles.forEach(a => {
  mockArticleDetail[a.slug] = { ...a, content: articleBody, prev_article: null, next_article: null, related_articles: [] }
})

export const mockGlossary = [
  { term: '基金净值', term_en: 'Net Asset Value (NAV)', definition: '基金的单位净值 = 基金总资产 ÷ 基金总份额。就是你买入/卖出基金的价格。注意：净值高低不代表基金贵贱，1元的基金不一定比3元的便宜。', category: 'fundamental', related_terms: ['累计净值', '估算净值'] },
  { term: '累计净值', term_en: 'Accumulated NAV', definition: '累计净值 = 单位净值 + 历史累计分红。反映基金成立以来的总回报。如果累计净值远高于单位净值，说明基金分过很多次红。', category: 'fundamental', related_terms: ['基金净值', '分红'] },
  { term: '最大回撤', term_en: 'Maximum Drawdown', definition: '基金净值从最高点到最低点的最大跌幅。比如最大回撤20%，意味着最坏情况下投入1万会变成8000元。这是衡量基金风险最重要的指标。', category: 'fundamental', related_terms: ['波动率', '夏普比率'] },
  { term: '夏普比率', term_en: 'Sharpe Ratio', definition: '衡量基金"性价比"的指标。夏普比率 = (收益率 - 无风险利率) ÷ 波动率。夏普比率越高，说明承担同样风险获得的回报越多。一般>1就算不错，>2就是优秀。', category: 'fundamental', related_terms: ['最大回撤', '波动率'] },
  { term: '基金经理', term_en: 'Fund Manager', definition: '负责基金投资决策的人。基金经理的经验、风格和能力决定了基金的业绩表现。选基金很大程度上是在选基金经理。关注：从业年限、历史业绩、投资风格是否稳定。', category: 'fundamental', related_terms: ['基金公司', '任期回报'] },
  { term: '定投', term_en: 'Dollar-Cost Averaging (DCA)', definition: '定期定额投资。每月固定时间投入固定金额买基金。跌时自动多买份额，涨时自动少买份额，长期下来平均成本低于平均价格。是新手最推荐的投资方式。', category: 'strategy', related_terms: ['微笑曲线', '止盈'] },
  { term: '微笑曲线', term_en: 'Smile Curve', definition: '基金定投的理想走势：先跌后涨，形成U型曲线。跌的时候你买到了便宜份额，涨回来时赚得更多。即使最终净值回到原点，定投者已经盈利。', category: 'strategy', related_terms: ['定投', '摊低成本'] },
  { term: '基金分红', term_en: 'Fund Dividend', definition: '基金把收益的一部分以现金或份额形式分给投资者。现金分红=钱到你账户；红利再投资=自动用分红的钱再买基金份额（推荐）。分红后净值会下降，你的总资产不变。', category: 'fundamental', related_terms: ['累计净值', '红利再投资'] },
  { term: '认购/申购/赎回', term_en: 'Subscribe/Purchase/Redeem', definition: '认购=新基金发行时买入（费率通常优惠）；申购=基金成立后买入；赎回=卖出基金拿回现金。赎回通常在T+1到T+7个工作日到账。', category: 'general', related_terms: ['费率', 'T+1'] },
  { term: '基金费率', term_en: 'Fund Fees', definition: '买基金需要支付的费用：管理费（基金公司收，每年0.5%-1.5%）、托管费（银行收，每年0.1%-0.25%）、申购费（买入时收，0-1.5%）、赎回费（卖出时收，持有越短越高）。选费率低的！', category: 'general', related_terms: ['管理费', '指数基金'] },
  { term: '指数基金', term_en: 'Index Fund', definition: '跟踪特定指数的基金。如沪深300指数基金，就是按沪深300指数的成分股配比去买入。优势：费率低（没有昂贵的基金经理）、不依赖经理能力、风格稳定。巴菲特推荐普通人买指数基金。', category: 'fund-type', related_terms: ['ETF', '被动投资'] },
  { term: 'ETF', term_en: 'Exchange Traded Fund', definition: '交易所交易基金。可以像股票一样在证券账户里买卖的基金。买入一手（100份）即可。优势：交易灵活（盘中随时买卖）、费率最低（管理费通常<0.5%）、持仓透明。是新手入门的最佳选择。', category: 'fund-type', related_terms: ['指数基金', 'LOF'] },
  { term: 'LOF', term_en: 'Listed Open-Ended Fund', definition: '上市型开放式基金。既可以在基金平台申购赎回（按净值），也可以在交易所买卖（按市价）。两个价格不同时会产生套利机会。', category: 'fund-type', related_terms: ['ETF', '套利'] },
  { term: 'FOF', term_en: 'Fund of Funds', definition: '基金中的基金。不是直接投资股票/债券，而是投资其他基金。相当于请了一个"基金买手"帮你选基金。适合完全不想自己选基金的投资者。', category: 'fund-type', related_terms: ['资产配置', '养老FOF'] },
  { term: 'QDII基金', term_en: 'QDII Fund', definition: '合格境内机构投资者基金。投资海外市场的基金（美股、港股、德国股市等）。用人民币就能投全球，不需要开海外账户。注意：QDII赎回到账时间较长（T+7到T+10）。', category: 'fund-type', related_terms: ['海外投资', '汇率风险'] },
  { term: '货币基金', term_en: 'Money Market Fund', definition: '投资短期债券、银行存款等低风险品种的基金。余额宝、零钱通都是货币基金。特点：几乎不会亏损、随时赎回（T+1到账）、收益比活期高（年化1.5%-2.5%）。适合放短期闲置资金。', category: 'fund-type', related_terms: ['七日年化', '万份收益'] },
  { term: '债券基金', term_en: 'Bond Fund', definition: '主要投资债券的基金。分为纯债基金（只投债券）、一级债基（债券+打新）、二级债基（债券+少量股票）。风险低于股票基金，收益高于货币基金（年化3%-6%），适合稳健投资者。', category: 'fund-type', related_terms: ['利率风险', '信用风险'] },
  { term: '基金规模', term_en: 'Fund Size (AUM)', definition: '基金管理的总资产规模。规模太小（<5000万）有清盘风险；规模太大（>100亿）可能影响操作灵活性。一般5-50亿是比较舒适的范围。', category: 'fundamental', related_terms: ['清盘', '流动性'] },
  { term: '基金评级', term_en: 'Fund Rating', definition: '第三方机构对基金的综合评价。最常见的是晨星（Morningstar）的1-5星评级。5星=同类型中表现最好的前10%。但评级是"后视镜"，过去5星不代表未来5星。', category: 'fundamental', related_terms: ['晨星', '最大回撤'] },
  { term: '资产配置', term_en: 'Asset Allocation', definition: '把资金分配到不同类型的基金中（股票型+债券型+货币型），降低整体组合的波动。经典的60/40组合就是60%股票基金+40%债券基金。资产配置决定了90%以上的投资回报。', category: 'strategy', related_terms: ['分散投资', '再平衡'] },
]

export const mockStrategies = [
  { id: 1, name: '定投策略', slug: 'dca-strategy', summary: '定期定额投资基金，摊低成本，不择时。是新手最推荐的懒人投资法。', difficulty: 'beginner', risk_level: 'low', suitable_for: '所有投资者，尤其新手和上班族', key_metrics: ['定投周期', '定投金额', '止盈目标'] },
  { id: 2, name: '核心-卫星策略', slug: 'core-satellite', summary: '大部分资金配宽基指数基金(核心)，小部分配行业主题基金(卫星)增强收益。', difficulty: 'intermediate', risk_level: 'medium', suitable_for: '有一定选基能力的投资者', key_metrics: ['核心比例', '卫星数量'] },
  { id: 3, name: '股债平衡策略', slug: 'stock-bond-balance', summary: '股票基金+债券基金按比例配置，定期再平衡，自动实现高抛低吸。', difficulty: 'beginner', risk_level: 'low', suitable_for: '追求稳健收益的投资者', key_metrics: ['股债比例', '再平衡频率'] },
  { id: 4, name: '全天候策略', slug: 'all-weather', summary: '桥水基金达利欧的经典策略，将资金分配到股票、债券、黄金、商品等不同资产。', difficulty: 'advanced', risk_level: 'medium', suitable_for: '有一定资金量，希望穿越牛熊的投资者', key_metrics: ['资产种类', '配比', '再平衡'] },
  { id: 5, name: '红利再投资策略', slug: 'dividend-reinvestment', summary: '选择高分红基金，分红持续再投资，利用复利效应积累更多份额。', difficulty: 'beginner', risk_level: 'low', suitable_for: '追求长期复利增长的稳健投资者', key_metrics: ['分红频率', '红利收益率'] },
]
