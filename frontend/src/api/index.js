import axios from 'axios'
import { showToast } from 'vant'

function getBaseURL() {
  const saved = localStorage.getItem('server_url')
  if (saved) return saved
  // Default: same origin (works when served from backend or dev proxy)
  return ''
}

const client = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
})

// Dynamic baseURL update
export function setServerURL(url) {
  localStorage.setItem('server_url', url)
  client.defaults.baseURL = url
}

export function getServerURL() {
  return localStorage.getItem('server_url') || window.location.origin
}

// 请求拦截器 - 自动加 token
client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 处理错误
client.interceptors.response.use(
  response => response.data,
  error => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.hash = '#/login'
    }
    showToast({ message: msg, icon: 'fail' })
    return Promise.reject(error)
  }
)

const api = {
  get: (url, params) => client.get(url, { params }),
  post: (url, data) => client.post(url, data),
  put: (url, data) => client.put(url, data),
  delete: (url) => client.delete(url),
  upload: (url, formData) => client.post(url, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export default api
