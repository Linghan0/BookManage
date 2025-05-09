import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

import { ElMessage, ElMessageBox } from 'element-plus'

// 类型守卫函数
function isErrorWithMessage(error: unknown): error is { message: string } {
  return typeof error === 'object' && error !== null && 'message' in error
}

function getErrorMessage(error: unknown): string {
  if (isErrorWithMessage(error)) return error.message
  if (error instanceof Error) return error.message
  return '未知错误'
}

interface User {
  user_id: string
  username: string
  role: 'admin' | 'user'
  createdAt?: string
}

interface Pagination {
  currentPage: number
  pageSize: number
  total: number
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)
  const users = ref<User[]>([])
  const token = ref<string | null>(null)
  const pagination = ref<Pagination>({
    currentPage: 1,
    pageSize: 10,
    total: 0
  })

  const sha256 = async (message: string): Promise<string> => {
    try {
      // 首选方案：使用Web Crypto API
      if (window.crypto?.subtle) {
        const msgBuffer = new TextEncoder().encode(message)
        const hashBuffer = await window.crypto.subtle.digest('SHA-256', msgBuffer)
        const hashArray = Array.from(new Uint8Array(hashBuffer))
        return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
      }
      // 备用方案：使用js-sha256库
      const { sha256 } = await import('js-sha256')
      return sha256(message)
      
    } catch (error) {
      console.error('加密失败:', error)
      throw new Error('密码加密处理失败')
    }
  }

  const init = async () => {
    const storedToken = localStorage.getItem('token')
    token.value = storedToken
    
    if (storedToken) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      try {
        const response = await axios.get('/api/validate')
        user.value = {
          user_id: response.data.user_id.toString(),
          username: response.data.username,
          role: response.data.role
        }
        isAuthenticated.value = true
        console.log('登录状态验证成功')
      } catch (error) {
        console.error('验证失败:', error)
        clearToken()
      }
    }
  }

  const clearToken = () => {
    token.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  }

  // 添加全局错误处理
  axios.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        clearToken()
        ElMessageBox.confirm(
          '登录已过期，请重新登录',
          '提示',
          {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(() => {
          window.location.href = '/login'
        }).catch(() => {
          // 用户取消操作
        })
      }
      return Promise.reject(error)
    }
  )

  // 初始化store
  init()

  const login = async (username: string, password: string) => {
    try {
      const hashedPassword = await sha256(password)
      const response = await axios.post('/api/login', { 
        username, 
        password: hashedPassword 
      })
      
      // 验证token是否存在
      if (!response.data.token) {
        throw new Error('登录响应中未包含token')
      }

      // 设置用户信息和token
      user.value = {
        user_id: response.data.user_id.toString(),
        username: response.data.username,
        role: response.data.role
      }
      isAuthenticated.value = true
      
      // 确保token保存到localStorage和axios headers
      setToken(response.data.token)
      
      // 验证token是否设置成功
      if (!localStorage.getItem('token') || !axios.defaults.headers.common['Authorization']) {
        throw new Error('token设置失败')
      }

      ElMessage.success('登录成功')
      return true
    } catch (error: unknown) {
      console.error('登录失败:', error)
      // 登录失败时清除可能存在的token
      clearToken()
      ElMessage.error(getErrorMessage(error))
      return false
    }
  }

  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  const lastUpdated = ref<number>(0)
  const CACHE_EXPIRY = 5 * 60 * 1000 // 5分钟缓存有效期

  const fetchUsers = async (forceRefresh = false) => {
    try {
      // 强制刷新或缓存过期时重新获取
      if (forceRefresh || Date.now() - lastUpdated.value > CACHE_EXPIRY) {
        const response = await axios.get('/api/users', {
          params: {
            page: pagination.value.currentPage,
            size: pagination.value.pageSize
          }
        })
        
        // 确保响应数据格式正确
        if (!response.data?.users) {
          throw new Error('无效的用户数据格式')
        }

        // 转换并存储用户数据
        users.value = response.data.users.map((user: {
          user_id: number | string
          username: string
          role: 'admin' | 'user'
          createdAt?: string
        }) => ({
          user_id: String(user.user_id),
          username: user.username,
          role: user.role,
          createdAt: user.createdAt
        }))

        console.log('用户数据已缓存:', users.value)
        pagination.value.total = response.data.total
        lastUpdated.value = Date.now()
      }
      return true
    } catch (error: unknown) {
      console.error('获取用户列表失败:', error)
      ElMessage.error(`获取用户列表失败: ${getErrorMessage(error)}`)
      return false
    }
  }

  const getCachedUser = (user_id: string) => {
    // 缓存有效时返回本地数据
    if (Date.now() - lastUpdated.value <= CACHE_EXPIRY) {
      return users.value.find(u => u.user_id === user_id)
    }
    return undefined
  }

  const createUser = async (userData: Omit<User, 'id'> & { password: string }) => {
    try {
      await axios.post('/api/users', userData)
      ElMessage.success('创建用户成功')
      await fetchUsers(true)
      return true
    } catch (error: unknown) {
      ElMessage.error(getErrorMessage(error))
      return false
    }
  }

  const deleteUser = async (user_id: string) => {
    try {
      await axios.delete(`/api/users/${user_id}`)
      ElMessage.success('删除用户成功')
      await fetchUsers(true)
      return true
    } catch (error: unknown) {
      ElMessage.error(getErrorMessage(error))
      return false
    }
  }

  const fetchUserById = async (user_id: string) => {
    try {
      const response = await axios.get(`/api/users/${user_id}`)
      return response.data
    } catch (error: unknown) {
      ElMessage.error(getErrorMessage(error))
      throw error
    }
  }

  return {
    user,
    isAuthenticated,
    users,
    pagination,
    token,
    login,
    logout,
    isAdmin,
    fetchUsers,
    getCachedUser,
    fetchUserById,
    createUser,
    deleteUser,
    setToken,
    clearToken,
    init
  }
})
