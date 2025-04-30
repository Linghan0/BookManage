<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from '@/utils/http'
import { ElMessage , ElMessageBox } from 'element-plus'


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

// 编辑 相关状态
const editDialogVisible = ref(false)
const currentBook = ref({
  isbn: '',
  title: '',
  author: '',
  translator: '',
  genre: '',
  country: '',
  era: '',
  opac_nlc_class: '',
  publisher:  '' ,
  publish_year: '',
  page: '',
  cover_url: '',
  description: ''
})

// 添加到书架相关状态


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
    const searchParams = { ...searchForm.value }
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

// 编辑图书
const handleEdit = (row: any) => {
  currentBook.value = { ...row }
  editDialogVisible.value = true
}

const submitEdit = async () => {
  try {
    loading.value = true
    await axios.put(`/api/books/${currentBook.value.isbn}`, currentBook.value)
    ElMessage.success('编辑成功')
    editDialogVisible.value = false
    fetchBooks()
  } catch (error: unknown) {
    ElMessage.error(`编辑失败: ${getErrorMessage(error)}`)
  } finally {
    loading.value = false
  }
}

// 删除图书
const handleDelete = async (isbn: string) => {
  try {
    await ElMessageBox.confirm('确定要删除这本书吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    loading.value = true
    const { data } = await axios.delete(`/api/books/${isbn}`)
    if (data.success) {
      ElMessage.success('删除成功')
      fetchBooks()
    } else {
      ElMessage.error(data.message || '删除失败')
    }
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error(`删除失败: ${getErrorMessage(error)}`)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <div class="admin-books-view">
    <!-- 标题 -->
    <el-page-header @back="$router.go(-1)">
      <template #content>
        <div class="page-title">
          <span>图书后台管理</span>
        </div>
      </template>
    </el-page-header>

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
    <el-table :data="tableData" height="500" style="width: 100%" v-loading="loading">
      <el-table-column prop="isbn" label="ISBN" width="150" />
      <el-table-column prop="title" label="书名" width="200" show-overflow-tooltip />
      <el-table-column prop="author" label="作者" width="150" />
      <el-table-column prop="translator" label="译者" width="150" />
      <el-table-column prop="genre" label="类型" width="120" />
      <el-table-column prop="country" label="国家" width="120" />
      <el-table-column prop="era" label="年代" width="120" />
      <el-table-column prop="opac_nlc_class" label="中图分类号" width="150" />
      <el-table-column prop="publisher" label="出版社" width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.publisher || '未知' }}
        </template>
      </el-table-column>
      <el-table-column prop="publish_year" label="出版年" width="100" />
      <el-table-column prop="page" label="页数" width="100" />
      <el-table-column prop="cover_url" label="封面链接" width="180" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            编辑
          </el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.isbn)">
            删除
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <!-- 分页 -->
    <el-pagination class="pagination" v-model:current-page="pagination.page" :page-size="pagination.pageSize"
      :page-sizes="[10, 20, 50, 100]" :total="pagination.total" @current-change="handlePageChange"
      @size-change="handleSizeChange" layout="total, sizes, prev, pager, next, jumper" />


    <!-- 编辑对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑图书信息" width="50%">
      <el-form :model="currentBook" label-width="100px">
        <el-form-item label="ISBN">
          <el-input v-model="currentBook.isbn" disabled />
        </el-form-item>
        <el-form-item label="书名">
          <el-input v-model="currentBook.title" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="currentBook.author" />
        </el-form-item>
        <el-form-item label="译者">
          <el-input v-model="currentBook.translator" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="currentBook.genre" />
        </el-form-item>
        <el-form-item label="国家">
          <el-input v-model="currentBook.country" />
        </el-form-item>
        <el-form-item label="年代">
          <el-input v-model="currentBook.era" />
        </el-form-item>
        <el-form-item label="中图分类号">
          <el-input v-model="currentBook.opac_nlc_class" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="currentBook.publisher" />
        </el-form-item>
        <el-form-item label="出版年">
          <el-input v-model="currentBook.publish_year" />
        </el-form-item>
        <el-form-item label="页数">
          <el-input v-model="currentBook.page" />
        </el-form-item>
        <el-form-item label="封面链接">
          <el-input v-model="currentBook.cover_url" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentBook.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.books-view {
  padding: 20px;
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
