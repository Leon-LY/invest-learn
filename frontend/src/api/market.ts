import client from './client'

export const marketApi = {
  getSummary() { return client.get('/market/summary') },
  getIndices() { return client.get('/market/indices') },
  getIndexDetail(code: string, days = 90) { return client.get(`/market/indices/${code}`, { params: { days } }) },
  getStockDetail(code: string, klineDays = 250) { return client.get(`/market/stocks/${code}`, { params: { kline_days: klineDays } }) },
  getStockKline(code: string, params?: Record<string, any>) { return client.get(`/market/stocks/${code}/kline`, { params }) },
  getFundDetail(code: string) { return client.get(`/market/funds/${code}`) },
  searchStocks(q: string, market?: string) { return client.get('/market/search', { params: { q, market } }) },
  getSectors() { return client.get('/market/sectors') },
  getCapitalFlow(days = 30) { return client.get('/market/capital-flow', { params: { days } }) },
  getMarketBreadth() { return client.get('/market/breadth') },
  screenStocks(params: Record<string, any>) { return client.get('/market/screener', { params }) },
}
