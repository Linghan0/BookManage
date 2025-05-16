import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from '@/utils/http'
import { ElMessage } from 'element-plus'

interface ShelfItem {
  isbn: string
  nums: number
}

export const useShelfCacheStore = defineStore('shelfCache', () => {
  const shelfItems = ref<ShelfItem[]>([])
  const lastUpdated = ref<number>(0)
  const CACHE_EXPIRE_TIME = 5 * 60 * 1000 // 5分钟缓存过期

  // 获取书架数据
  const fetchShelfItems = async (forceRefresh = false) => {
    const now = Date.now()
    
    // 检查缓存是否有效
    if (!forceRefresh && 
        now - lastUpdated.value < CACHE_EXPIRE_TIME && 
        shelfItems.value.length > 0) {
      return shelfItems.value
    }

    try {
      const response = await axios.get('/api/bookshelf')
      if (!response.data || !Array.isArray(response.data)) {
        throw new Error('无效的书架数据格式')
      }
      
      shelfItems.value = response.data
      lastUpdated.value = now
      return shelfItems.value
    } catch (error) {
      console.error('获取书架数据失败:', error)
      // 仅当缓存完全为空时才显示错误
      if (shelfItems.value.length === 0) {
        ElMessage.error('获取书架数据失败')
      }
      throw error
    }
  }

  // 定时刷新
  const startAutoRefresh = () => {
    const interval = setInterval(async () => {
      try {
        await fetchShelfItems(true)
      } catch (error) {
        console.error('自动刷新书架数据失败:', error)
      }
    }, CACHE_EXPIRE_TIME)
    
    return () => clearInterval(interval)
  }

  return { 
    shelfItems,
    fetchShelfItems,
    startAutoRefresh
  }
})
