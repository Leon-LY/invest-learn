import client from './client'

export const learnApi = {
  getCategories() { return client.get('/learn/categories') },
  getArticles(params?: Record<string, any>) { return client.get('/learn/articles', { params }) },
  getArticleBySlug(slug: string) { return client.get(`/learn/articles/${slug}`) },
  searchGlossary(params?: Record<string, any>) { return client.get('/learn/glossary', { params }) },
  getStrategies(params?: Record<string, any>) { return client.get('/learn/strategies', { params }) },
  getStrategy(slug: string) { return client.get(`/learn/strategies/${slug}`) },
  getCalendar() { return client.get('/learn/calendar') },
}
