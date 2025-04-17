import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
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
  const pagination = ref<Pagination>({
    currentPage: 1,
    pageSize: 10,
    total: 0
  })

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
    login,
    logout,
    isAdmin,
    fetchUsers,
    createUser,
    deleteUser
  }
})
