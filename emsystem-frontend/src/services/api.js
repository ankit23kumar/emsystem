import axios from 'axios'
import { clearSession, getToken } from './auth'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    timeout :10000,
    headers: {
        "Content-Type": 'application/json'},
})

api.interceptors.request.use((config) => {
  const token = getToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    const url = error.config?.url || ''

    // Do not treat invalid login credentials as an expired session.
    const isPublicEndpoint =
      url.includes('/login') || url.includes('/register')

    // Only clear the session for 401 responses from other endpoints.
    // A 403 can mean that the account itself has expired.
    if (status === 401 && !isPublicEndpoint && getToken()) {
      clearSession()
      window.location.replace('/')
    }

    return Promise.reject(error)
  },
)
export default api