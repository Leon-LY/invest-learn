import axios from 'axios'
import { setupMock } from '@/mock'

// Allow overriding API base URL via localStorage
// e.g. localStorage.setItem('api-url', 'http://49.232.49.175:8000/api/v1')
function getBaseURL(): string {
  const custom = localStorage.getItem('api-url')
  if (custom) return custom
  return '/api/v1'
}

const client = axios.create({
  baseURL: getBaseURL(),
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
setupMock(client)

export default client
