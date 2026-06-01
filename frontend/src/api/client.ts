import axios from 'axios'
import { setupMock } from '@/mock'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Response interceptor: unwrap data
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      console.error(`API Error ${error.response.status}:`, error.response.data)
    } else if (error.request) {
      console.error('Network error:', error.message)
    }
    return Promise.reject(error)
  }
)

// Always setup mock — handler will check isMockEnabled() at runtime.
// When mock is disabled (localStorage.mock-api = "false"), requests forward to real API.
setupMock(client)

export default client
