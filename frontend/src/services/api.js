import axios from 'axios'

const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  const hostname = window.location.hostname
  const port = 8002
  
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `http://localhost:${port}/api/v1`
  } else {
    return `http://${hostname}:${port}/api/v1`
  }
}

const API_BASE_URL = getApiBaseUrl()

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

api.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', {
      method: config.method,
      url: config.url,
      data: config.data
    })
    return config
  },
  (error) => {
    console.error('❌ API Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    console.log('📥 API Response:', {
      status: response.status,
      data: response.data
    })
    return response
  },
  (error) => {
    console.error('❌ API Response Error:', {
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })
    return Promise.reject(error)
  }
)

export const sendMessage = async (userId, query) => {
  try {
    const response = await api.post('/query', {
      user_id: userId,
      query: query
    })
    
    return response.data
  } catch (error) {
    console.error('❌ API Error:', error)
    throw error
  }
}

export const getHealth = async () => {
  try {
    const response = await api.get('/health')
    return response.data
  } catch (error) {
    console.error('Health check failed:', error)
    throw error
  }
}