<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBookStore } from '@/stores/books'
import { useShelfCacheStore } from '@/stores/shelfCache'

const router = useRouter()
const loading = ref(false)
const userBooks = ref<any[]>([])
const bookStore = useBookStore()
const shelfCacheStore = useShelfCacheStore()

const fetchUserBooks = async () => {
  try {
    loading.value = true
    
    // 获取书架数据（会自动使用缓存）
    const shelfItems = await shelfCacheStore.fetchShelfItems()
    
    // 确保数据结构正确
    if (!Array.isArray(shelfItems)) {
      throw new Error('Invalid shelf items data')
    }

    // 获取书籍详情（优先使用缓存）
    const booksPromises = shelfItems.map(async (item) => {
      try {
        // 验证必要字段存在
        if (!item?.isbn || item?.nums === undefined) {
          console.warn('Invalid shelf item structure:', item)
          return null
        }

        const book = await bookStore.getBookByIsbn(item.isbn)
        if (!book) {
          return {
            isbn: item.isbn,
            title: '书籍信息缺失',
            author: '',
            quantity: item.nums // 使用nums
          }
        }

        return {
          ...book,
          quantity: item.nums, // 使用nums
          // 确保所有字段都有默认值
          title: book.title || '无书名',
          author: book.author || '未知作者',
          isbn: book.isbn || item.isbn
        }
      } catch (error) {
        console.error(`获取书籍 ${item.isbn} 详情失败:`, error)
        return {
          isbn: item.isbn,
          title: '获取详情失败',
          author: '',
          quantity: item.nums
        }
      }
    })

    // 等待所有请求完成并过滤无效数据
    const booksResults = (await Promise.all(booksPromises)).filter(Boolean)
    userBooks.value = booksResults
    } catch (error: any) {
      console.error('获取用户书籍失败:', error)
      if (error.response?.status === 401) {
        ElMessage.error('登录验证未通过')

      } else if (error.response?.status === 404) {
        // 书架为空是正常情况，不显示错误
        userBooks.value = []
      } else {
        ElMessage.error('获取用户书籍失败: ' + (error.response?.data?.message || error.message))
      }
  } finally {
    loading.value = false
  }
}

const viewBookDetail = (isbn: string) => {
  router.push(`/userbooks/${isbn}`)
}

let cleanupRefresh: () => void

onMounted(() => {
  fetchUserBooks()
  // 启动自动刷新
  cleanupRefresh = shelfCacheStore.startAutoRefresh()
})

onUnmounted(() => {
  // 组件卸载时清理定时器
  cleanupRefresh?.()
})
</script>

<template>
  <el-container class="user-books-view">
    <el-header>
      <h1>我的书架</h1>
    </el-header>
    <el-main>
      <el-table 
        :data="userBooks" 
        style="width: 100%; min-width: 800px; max-width: 1400px"
        v-loading="loading"
      >
        <el-table-column prop="title" label="书名" />
        <el-table-column prop="isbn" label="ISBN" />
        <el-table-column prop="author" label="作者" />
        <el-table-column prop="quantity" label="数量" align="center" width="120" />
        <el-table-column label="操作" align="center" fixed="right" width="150">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewBookDetail(scope.row.isbn)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-main>
  </el-container>
</template>

<style scoped>
.user-books-view {
  padding: 20px;
}

.el-header {
  text-align: center;
  padding: 0;
  height: auto;
  margin-bottom: 20px;
}

.el-main {
  padding: 0;
}
</style>
