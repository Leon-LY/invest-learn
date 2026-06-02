import client from './client'

export const newsApi = {
  getList(params?: Record<string, any>) { return client.get('/news', { params }) },
  getDetail(id: number) { return client.get(`/news/${id}`) },
  getAnalysis(id: number) { return client.get(`/news/${id}/analysis`) },
  getSources() { return client.get('/news/sources/list') },
  getSentimentStats(days = 7) { return client.get('/news/sentiment/stats', { params: { days } }) },
  getAnalyses(limit = 10) { return client.get('/news/analyses', { params: { limit } }) },
  getExpertPredictions(limit = 6) { return client.get('/news/expert-predictions', { params: { limit } }) },
}
