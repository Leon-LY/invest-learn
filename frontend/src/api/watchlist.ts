import client from './client'

export const watchlistApi = {
  getList(itemType?: string) { return client.get('/watchlist', { params: { item_type: itemType } }) },
  add(data: { item_type: string; item_code: string; item_name?: string; alias?: string; tags?: string[]; notes?: string }) {
    return client.post('/watchlist', data)
  },
  update(id: number, data: Record<string, any>) { return client.put(`/watchlist/${id}`, data) },
  remove(id: number) { return client.delete(`/watchlist/${id}`) },
  reorder(items: Array<{ id: number; sort_order: number }>) { return client.post('/watchlist/reorder', { items }) },
  getAlerts() { return client.get('/watchlist/alerts') },
  createAlert(data: { item_type: string; item_code: string; condition: string; target_value: number }) {
    return client.post('/watchlist/alerts', data)
  },
  deleteAlert(id: number) { return client.delete(`/watchlist/alerts/${id}`) },
}
