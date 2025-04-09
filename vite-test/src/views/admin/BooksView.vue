<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  ElTable, 
  ElTableColumn, 
  ElButton, 
  ElDialog, 
  ElMessage, 
  ElFormItem, 
  ElInput,
  ElPagination
} from 'element-plus'
import { useBookStore } from '@/stores/books'

const bookStore = useBookStore()
const showDialog = ref(false)
const showSearchDialog = ref(false)
const currentBook = ref({
  isbn: '',
  title: '',
  author: '',
  publisher: '',
  publish_year: new Date().getFullYear(),
  page: 100,
  cover_url: '',
  description: ''
})
const searchIsbn = ref('')

// 初始化加载数据
onMounted(async () => {
  try {
    await bookStore.fetchBooks()
  } catch (error) {
    console.error(error)
  }
})

// 分页变化处理
const handlePageChange = (page: number) => {
  bookStore.pagination.currentPage = page
  bookStore.fetchBooks()
}

const handleSizeChange = (size: number) => {
  bookStore.pagination.pageSize = size
  bookStore.pagination.currentPage = 1
  bookStore.fetchBooks()
}

const handleEdit = (book: any) => {
  currentBook.value = { ...book }
  showDialog.value = true
}

const handleDelete = async (isbn: string) => {
  try {
    // 这里需要添加实际的API调用
    ElMessage.success('删除书籍成功')
    bookStore.fetchBooks(true) // 强制刷新
  } catch (error) {
    ElMessage.error('删除书籍失败')
  }
}

const handleSearchByIsbn = async () => {
  if (!searchIsbn.value) {
    ElMessage.error('请输入ISBN号')
    return
  }

  try {
    const book = await bookStore.getBookByIsbn(searchIsbn.value)
    currentBook.value = book
    showSearchDialog.value = false
    showDialog.value = true
  } catch (error) {
    console.error(error)
  }
}

const handleSubmit = async () => {
  try {
    // 这里需要添加实际的API调用
    ElMessage.success('操作成功')
    showDialog.value = false
    bookStore.fetchBooks(true) // 强制刷新
  } catch (error) {
    ElMessage.error('操作失败')
  }
}
</script>

<template>
  <div class="book-management">
    <div class="header">
      <h2>书籍管理</h2>
      <div>
        <el-button type="primary" @click="currentBook = {
          isbn: '',
          title: '',
          author: '',
          publisher: '',
          publish_year: new Date().getFullYear(),
          page: 100,
          cover_url: '',
          description: ''
        }; showDialog = true">
          添加书籍
        </el-button>
        <el-button @click="showSearchDialog = true">ISBN查询</el-button>
      </div>
    </div>

    <el-table :data="bookStore.books" border style="width: 100%">
      <el-table-column prop="isbn" label="ISBN" width="180" />
      <el-table-column prop="title" label="书名" />
      <el-table-column prop="author" label="作者" />
      <el-table-column prop="publisher" label="出版社" />
      <el-table-column prop="publish_year" label="出版年份" width="120" />
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.isbn)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination"
      :current-page="bookStore.pagination.currentPage"
      :page-size="bookStore.pagination.pageSize"
      :total="bookStore.pagination.total"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      layout="total, sizes, prev, pager, next, jumper"
    />

    <!-- 书籍编辑/添加对话框 -->
    <el-dialog v-model="showDialog" :title="currentBook.isbn ? '编辑书籍' : '添加书籍'">
      <el-form :model="currentBook">
        <el-form-item label="ISBN" required>
          <el-input v-model="currentBook.isbn" />
        </el-form-item>
        <el-form-item label="书名" required>
          <el-input v-model="currentBook.title" />
        </el-form-item>
        <el-form-item label="作者">
          <el-input v-model="currentBook.author" />
        </el-form-item>
        <el-form-item label="出版社">
          <el-input v-model="currentBook.publisher" />
        </el-form-item>
        <el-form-item label="出版年份">
          <el-input v-model.number="currentBook.publish_year" type="number" />
        </el-form-item>
        <el-form-item label="页数">
          <el-input v-model.number="currentBook.page" type="number" />
        </el-form-item>
        <el-form-item label="封面URL">
          <el-input v-model="currentBook.cover_url" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="currentBook.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- ISBN查询对话框 -->
    <el-dialog v-model="showSearchDialog" title="ISBN查询">
      <el-form>
        <el-form-item label="ISBN号">
          <el-input v-model="searchIsbn" placeholder="请输入ISBN号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSearchDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSearchByIsbn">查询</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.book-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
