import axios from 'axios'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import router from '@/router'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器 - 添加token
http.interceptors.request.use(config => {
  const userStore = useUserStore()
  if (userStore.token) {
    config.headers.Authorization = `Bearer ${userStore.token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器 - 处理错误
http.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    const userStore = useUserStore()
    
    // 处理401未授权
    if (response?.status === 401) {
      userStore.logout()
      ElMessage.error({
        message: '登录已过期，请重新登录',
        duration: 0,
        showClose: true
      })
      router.push('/login')
    }
    // 处理403禁止访问
    else if (response?.status === 403) {
      ElMessage.error('权限不足，无法访问')
    }
    // 其他错误
    else {
      const message = error.response?.data?.message || error.message || '请求失败'
      ElMessage.error(message)
    }
    
    return Promise.reject(error)
  }
)

export default http
