import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { IndexedDBHelper } from '@/utils/indexedDB'

interface Book {
  isbn: string
  title: string
  author: string
  publisher: string
  publish_year: number
  page: number
  cover_url: string
  description: string
}

export const useBookStore = defineStore('books', () => {
  // IndexedDB配置
  const DB_NAME = 'BookManagement'
  const STORE_NAME = 'books'
  const CACHE_EXPIRE_TIME = 24 * 60 * 60 * 1000 // 24小时缓存过期

  // 创建IndexedDB实例
  const dbHelper = new IndexedDBHelper(DB_NAME, STORE_NAME)
  
  // 书籍数据
  const books = ref<Book[]>([])
  // 最后更新时间
  const lastUpdated = ref<number>(0)
  // 分页信息
  const pagination = ref({
    currentPage: 1,
    pageSize: 20,
    total: 0
  })

  // 初始化IndexedDB
  const initDB = async () => {
    try {
      await dbHelper.open()
    } catch (error) {
      console.error('初始化IndexedDB失败:', error)
    }
  }

  // 从IndexedDB加载缓存
  const loadFromCache = async () => {
    await initDB()
    const now = Date.now()
    
    // 检查缓存是否过期
    if (now - lastUpdated.value < CACHE_EXPIRE_TIME) {
      const cachedBooks = await dbHelper.getAll()
      if (cachedBooks.length > 0) {
        books.value = cachedBooks
        return true
      }
    }
    return false
  }

  // 保存到IndexedDB
  const saveToCache = async (items: Book[]) => {
    await initDB()
    await dbHelper.bulkPut(items)
    lastUpdated.value = Date.now()
  }

  // 获取书籍列表
  const fetchBooks = async (forceRefresh = false) => {
    try {
      console.log('开始获取书籍数据，强制刷新:', forceRefresh)
      
      // 如果不强制刷新且缓存有效，则使用缓存
      if (!forceRefresh && await loadFromCache()) {
        console.log('使用缓存数据')
        return
      }

      console.log('从API获取数据')
      const response = await axios.get('/api/books', {
        params: {
          page: pagination.value.currentPage,
          size: pagination.value.pageSize
        }
      })
      
      console.log('获取到数据:', response.data)
      books.value = response.data.items
      pagination.value.total = response.data.total
      
      console.log('保存数据到缓存')
      await saveToCache(response.data.items)
      console.log('数据加载完成')
    } catch (error) {
      ElMessage.error('获取书籍列表失败')
      throw error
    }
  }

  // 根据ISBN获取书籍
  const getBookByIsbn = async (isbn: string) => {
    try {
      // 先检查本地缓存
      await initDB()
      const cachedBook = await dbHelper.get(isbn)
      if (cachedBook) {
        return cachedBook
      }

      // 缓存中没有则从API获取
      const response = await axios.get(`/api/books/${isbn}`)
      // 从响应中提取book对象
      const bookData = response.data?.book
      if (!bookData) {
        throw new Error('Invalid API response: missing book data')
      }
      // 添加到缓存
      await dbHelper.put(bookData)
      return bookData
    } catch (error) {
      ElMessage.error('获取书籍信息失败')
      throw error
    }
  }

  // 删除书籍
  const deleteBook = async (isbn: string) => {
    try {
      await axios.delete(`/api/books/${isbn}`)
      // 从本地缓存删除
      await initDB()
      await dbHelper.delete(isbn)
      // 从当前列表删除
      books.value = books.value.filter(book => book.isbn !== isbn)
      ElMessage.success('删除书籍成功')
    } catch (error) {
      ElMessage.error('删除书籍失败')
      throw error
    }
  }

  // 搜索书籍
  const searchBooks = async (params: { [key: string]: string }) => {
    try {
      const { data } = await axios.get('/api/books/search', {
        params: {
          ...params,
          page: 1,
          size: 20
        }
      })
      return data
    } catch (error) {
      ElMessage.error('搜索书籍失败')
      throw error
    }
  }

  return {
    books,
    pagination,
    lastUpdated,
    fetchBooks,
    getBookByIsbn,
    loadFromCache,
    deleteBook,
    searchBooks
  }
})
