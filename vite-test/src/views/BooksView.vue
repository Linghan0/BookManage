<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/utils/http'
import BookDetailView from './BookDetailView.vue'
import { ElMessage } from 'element-plus'

// 类型守卫函数
function isErrorWithMessage(error: unknown): error is { message: string } {
  return typeof error === 'object' && error !== null && 'message' in error
}

function getErrorMessage(error: unknown): string {
  if (isErrorWithMessage(error)) return error.message
  if (error instanceof Error) return error.message
  return '未知错误'
}

// 搜索相关状态
const searchForm = ref({
  field: 'isbn',
  value: ''
})
const searchOptions = [
  { value: 'isbn', label: 'ISBN' },
  { value: 'title', label: '书名' },
  { value: 'author', label: '作者' }
]
const isSearching = ref(false)

// 书籍列表相关状态
const loading = ref(false)
const tableData = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 添加到书架相关状态
const addDialogVisible = ref(false)
const detailVisible = ref(false)
const currentIsbn = ref('')
const currentBookIsbn = ref('')
const bookCount = ref(1)
const bookDetailDialog = ref()

const viewBookDetail = (isbn: string) => {
  currentBookIsbn.value = isbn
  bookDetailDialog.value?.openDialog()
}

// 获取书籍列表
const fetchBooks = async () => {
  try {
    loading.value = true
    const { data } = await axios.get('/api/books', {
      params: {
        page: pagination.value.page,
        per_page: pagination.value.pageSize
      }
    })
    tableData.value = data.items
    pagination.value.total = data.total
  } catch (error: unknown) {
    ElMessage.error(`获取图书列表失败: ${getErrorMessage(error)}`)
  } finally {
    loading.value = false
  }
}

// 搜索书籍
const formatISBN = (isbn: string) => {
  // 移除所有非数字字符
  return isbn.replace(/[^\d]/g, '')
}

const handleSearch = async () => {
  if (!searchForm.value.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  try {
    isSearching.value = true
    loading.value = true
    
    // 处理ISBN搜索的特殊情况
    const searchParams = {...searchForm.value}
    if (searchParams.field === 'isbn') {
      try {
        searchParams.value = formatISBN(searchParams.value)
      } catch (error) {
        ElMessage.error('ISBN必须是10位或13位数字')
        return
      }
    }

    const { data } = await axios.get('/api/books/search', {
      params: searchParams
    })

    if (data && data.length > 0) {
      tableData.value = data
      pagination.value.total = data.length
      if (data[0].from_external) {
        ElMessage.success('从外部API获取到数据')
      }
    } else {
      tableData.value = []
      pagination.value.total = 0
      ElMessage.warning('未找到相关书籍')
    }
  } catch (error: unknown) {
    console.error('搜索错误:', error)
    if (isErrorWithMessage(error) && error.message.includes('404')) {
      ElMessage.warning('未找到相关书籍')
    } else {
      ElMessage.error(`搜索失败: ${getErrorMessage(error)}`)
    }
  } finally {
    loading.value = false
  }
}
// 重置搜索
const resetSearch = async () => {
  searchForm.value = { field: 'title', value: '' }
  isSearching.value = false
  await fetchBooks()
}

// 分页处理
const handlePageChange = (page: number) => {
  pagination.value.page = page
  if (isSearching.value) {
    handleSearch()
  } else {
    fetchBooks()
  }
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  if (isSearching.value) {
    handleSearch()
  } else {
    fetchBooks()
  }
}

// 添加到书架功能
const showAddDialog = (isbn: string) => {
  currentIsbn.value = isbn
  bookCount.value = 1
  addDialogVisible.value = true
}

const addToShelf = async () => {
  try {
    loading.value = true
    await axios.post(`/api/bookshelf/${currentIsbn.value}`, {
      quantity: bookCount.value
    })
    ElMessage.success('添加成功')
    addDialogVisible.value = false
  } catch (error: unknown) {
    ElMessage.error(`添加到书架失败: ${getErrorMessage(error)}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <div class="books-view">
    <!-- 标题 -->
    <div class="page-header-container">
      <el-page-header @back="$router.go(-1)">
        <template #content>
          <h1 class="page-title">图书列表</h1>
        </template>
      </el-page-header>
    </div>
    
    <!-- 搜索栏 -->
    <div class="search-container">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索字段：">
          <el-select v-model="searchForm.field">
            <el-option v-for="item in searchOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索内容：">
          <el-input v-model="searchForm.value" placeholder="请输入搜索内容" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 书籍表格 -->
    <el-table :data="tableData" height="600" style="width: 100%; min-width: 400px; max-width: 1400px" v-loading="loading">
      <el-table-column prop="isbn" label="ISBN" min-width="150" />
      <el-table-column prop="title" label="书名" min-width="200" show-overflow-tooltip />
      <el-table-column prop="author" label="作者" min-width="150" />
      <el-table-column prop="translator" label="译者" min-width="150" />
      <el-table-column prop="genre" label="类型" min-width="120" />
      <el-table-column prop="era" label="年代" min-width="120" />
      <el-table-column prop="publisher.name" label="出版社" min-width="180" show-overflow-tooltip>
        <template #default="{row}">
          {{ row.publisher?.name || row.publisher || '未知' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right" align="center">
        <template #default="{row}">
          <el-button size="small" @click="showAddDialog(row.isbn)">
            添加到书架
          </el-button>
          <el-button type="primary" size="small" @click="viewBookDetail(row.isbn)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 书籍详情弹窗 -->
    <BookDetailView
      v-model:visible="detailVisible"
      :isbn="currentBookIsbn"
      ref="bookDetailDialog"
    />

    <!-- 分页 -->
    <el-pagination class="pagination" v-model:current-page="pagination.page" :page-size="pagination.pageSize"
      :page-sizes="[10, 20, 50, 100]" :total="pagination.total" @current-change="handlePageChange"
      @size-change="handleSizeChange" layout="total, sizes, prev, pager, next, jumper" />

    <!-- 添加到书架对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加到书架" width="30%">
      <el-form label-width="80px">
        <el-form-item label="数量" prop="count">
          <el-input-number 
            v-model="bookCount" 
            :min="1" 
            :max="10" 
            controls-position="right"
          />
          <div class="el-form-item__tip">每次最多可添加10本</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addToShelf">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.books-view {
  padding: 20px;
}

.page-header-container {
  background-color: rgba(255, 255, 255, 0.85);
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.search-container,
.el-table,
.pagination {
  background-color: rgba(255, 255, 255, 0.85);
  padding: 15px;
  border-radius: 4px;
  margin: 0 auto 15px;
  max-width: 1400px;
  text-align: center;
}

.search-form {
  justify-content: center;
}

.page-title {
  color: #333;
}

.el-table {
  background-color: rgba(255, 255, 255, 0.9);
}

.el-table th {
  background-color: rgba(245, 245, 245, 0.9);
}

.page-header-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 4px;
  border-bottom: 1px solid #ebeef5;
}

.page-title {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.search-container {
  margin-bottom: 20px;
}

.search-form {
  display: flex;
  align-items: center;
  
  :deep(.el-select) {
    min-width: 120px;
  }
  
  :deep(.el-input) {
    min-width: 200px;
  }
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
