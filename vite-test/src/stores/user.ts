import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface User {
  username: string
  role: 'admin' | 'user'
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post('/api/login', { username, password })
      user.value = response.data.user
      isAuthenticated.value = true
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
  }

  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
    isAdmin
  }
})
