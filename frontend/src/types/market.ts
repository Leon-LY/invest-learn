export interface IndexInfo {
  code: string
  name: string
  market?: string
  country?: string
  latest_price: number | null
  change: number | null
  change_pct: number | null
  sparkline: number[]
}

export interface StockInfo {
  code: string
  name: string
  market: string
  security_type?: string
  sector?: string
  industry?: string
}

export interface StockQuote {
  code: string
  name: string
  market: string
  latest_price: number | null
  change: number | null
  change_pct: number | null
  volume: number | null
  amount: number | null
  turnover_rate: number | null
  pe_ratio: number | null
  pb_ratio: number | null
  total_mv: number | null
  circ_mv: number | null
}

export interface KLineItem {
  date: string
  open: number | null
  high: number | null
  low: number | null
  close: number | null
  volume: number | null
  amount: number | null
}

export interface StockDetail {
  info: StockInfo
  quote: StockQuote | null
  fundamentals: Record<string, number | null> | null
  klines: KLineItem[]
}

export interface FundInfo {
  code: string
  name: string
  fund_type: string | null
  company: string | null
  inception_date: string | null
  aum: number | null
  latest_nav: number | null
  latest_return: number | null
}

export interface FundDetail {
  info: FundInfo
  nav_history: Array<{
    date: string
    unit_nav: number | null
    acc_nav: number | null
    daily_return: number | null
  }>
}

export interface WatchlistItem {
  id: number
  item_type: string
  item_code: string
  item_name: string | null
  alias: string | null
  tags: string[]
  notes: string | null
  sort_order: number
  quote: { latest_price: number | null; change_pct: number | null } | null
  added_at: string | null
}

export interface NewsArticle {
  id: number
  title: string
  summary: string | null
  source: string | null
  source_url: string | null
  author: string | null
  sentiment: string | null
  categories: string[]
  tags: string[]
  related_stocks: string[]
  published_at: string | null
}

export interface SectorItem {
  sector_name: string
  change_pct: number | null
  net_inflow: number | null
  top_stock: string | null
  top_stock_pct: number | null
}

export interface CapitalFlowItem {
  date: string
  net_inflow: number | null
  balance: number | null
}

export interface MarketBreadth {
  up_count: number
  down_count: number
  flat_count: number
  limit_up: number
  limit_down: number
  total_amount: number | null
}
