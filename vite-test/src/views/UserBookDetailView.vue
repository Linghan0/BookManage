<template>
  <div class="book-detail-view">
    <el-page-header @back="goBack">
      <template #content>
        <span class="text-large font-600 mr-3">书籍详情</span>
      </template>
    </el-page-header>

    <div v-if="book" class="book-detail-container">
      <div class="book-cover">
        <el-image 
          :src="book.cover_url" 
          fit="contain"
          style="height: 300px; width: 200px;"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>封面加载失败</span>
            </div>
          </template>
        </el-image>
      </div>

      <div class="book-info">
        <h2>{{ book.title }}</h2>
        <div class="book-meta">
          <p><strong>作者:</strong> {{ book.author }}</p>
          <p><strong>出版社:</strong> {{ book.publisher }}</p>
          <p><strong>出版年份:</strong> {{ book.publish_year }}</p>
          <p><strong>页数:</strong> {{ book.page }}</p>
          <p><strong>ISBN:</strong> {{ book.isbn }}</p>
        </div>

        <div class="book-description">
          <h3>内容简介</h3>
          <p>{{ book.description || '暂无内容简介' }}</p>
        </div>
      </div>
    </div>

    <div v-else-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else class="error-container">
      <el-empty description="获取书籍信息失败" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/utils/http'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

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

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const book = ref<Book | null>(null)

import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const fetchBookDetail = async () => {
  try {
    loading.value = true
    
    // 检查登录状态
    if (!userStore.token) {
      ElMessage.error('请先登录')
      router.push('/login')
      return
    }

    const isbn = route.params.isbn as string
    
    // 1. 验证书籍是否属于当前用户
    interface UserBookItem {
      isbn: string
      quantity: number
    }
    const shelfResponse = await axios.get<{items: UserBookItem[]}>('/api/bookshelf')
    const userBooks = shelfResponse.data.items
    if (!userBooks.some((b: UserBookItem) => b.isbn === isbn)) {
      ElMessage.error('书籍不在您的书架中')
      router.push('/userbooks')
      return
    }
    
    // 2. 获取书籍详情
    const response = await axios.get(`/api/books/${isbn}`)
    book.value = response.data
    } catch (error: any) {
      console.error('获取书籍详情失败:', error)
      if (error.response?.status === 401) {
        ElMessage.error('登录验证未通过')
      } else {
        ElMessage.error('获取书籍详情失败: ' + (error.response?.data?.message || error.message))
      }
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/userbooks')
}

onMounted(() => {
  fetchBookDetail()
})
</script>

<style scoped>
.book-detail-view {
  padding: 20px;
}

.book-detail-container {
  display: flex;
  margin-top: 20px;
  gap: 40px;
}

.book-cover {
  flex: 0 0 200px;
}

.book-info {
  flex: 1;
}

.book-meta p {
  margin: 8px 0;
}

.book-description {
  margin-top: 20px;
}

.loading-container,
.error-container {
  margin-top: 40px;
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--el-text-color-secondary);
}

.image-error .el-icon {
  font-size: 30px;
  margin-bottom: 10px;
}
</style>
