import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

// 请求拦截：自动携带 token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截：401 时清除登录态并记录提示信息
client.interceptors.response.use(
  (res) => res.data,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.setItem('auth_message', '登录已过期或账号已变更，请重新登录')
    }
    return Promise.reject(err)
  }
)

export default client
