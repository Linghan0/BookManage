import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

// 明确设置baseURL
axios.defaults.baseURL = 'http://localhost:5000'
import { ElMessage } from 'element-plus'

interface User {
  id: string
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
    // 将字符串编码为UTF-8
    const msgBuffer = new TextEncoder().encode(message)
    // 使用Web Crypto API计算哈希
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
    // 将ArrayBuffer转换为Hex字符串
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  }

  const init = async () => {
    console.log('检查本地token...')
    const storedToken = localStorage.getItem('token')
    token.value = storedToken
    console.log('获取到的token:', storedToken)
    
    if (storedToken) {
      console.log('设置请求头Authorization...')
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      
      try {
        console.log('调用验证接口...')
        const response = await axios.get('/api/validate')
        console.log('验证接口响应:', response.data)
        
        user.value = {
          id: response.data.user_id.toString(),
          username: response.data.username,
          role: response.data.role
        }
        isAuthenticated.value = true
        console.log('登录状态验证成功')
      } catch (error) {
        console.error('验证失败:', error)
        clearToken()
      }
    } else {
      console.log('未找到本地token')
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

  // 初始化store
  init()

  const login = async (username: string, password: string) => {
    try {
      console.log('Making request to:', axios.defaults.baseURL + '/api/login')
      const hashedPassword = await sha256(password)
      const response = await axios.post('/api/login', { 
        username, 
        password: hashedPassword 
      })
      console.log('Login response:', response)
      console.log('User data:', response.data)
      user.value = {
        id: response.data.user_id.toString(),
        username: response.data.username,
        role: response.data.role
      }
      isAuthenticated.value = true
      setToken(response.data.token)
      ElMessage.success('登录成功')
      return true
    } catch (error) {
      ElMessage.error('登录失败')
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

  const fetchUsers = async (forceRefresh = false) => {
    try {
      const response = await axios.get('/api/users', {
        params: {
          page: pagination.value.currentPage,
          size: pagination.value.pageSize
        }
      })
      users.value = response.data.users
      pagination.value.total = response.data.total
      return true
    } catch (error) {
      ElMessage.error('获取用户列表失败')
      return false
    }
  }

  const createUser = async (userData: Omit<User, 'id'> & { password: string }) => {
    try {
      await axios.post('/api/users', userData)
      ElMessage.success('创建用户成功')
      await fetchUsers(true)
      return true
    } catch (error) {
      ElMessage.error('创建用户失败')
      return false
    }
  }

  const deleteUser = async (id: string) => {
    try {
      await axios.delete(`/api/users/${id}`)
      ElMessage.success('删除用户成功')
      await fetchUsers(true)
      return true
    } catch (error) {
      ElMessage.error('删除用户失败')
      return false
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
    createUser,
    deleteUser,
    setToken,
    clearToken
  }
})
