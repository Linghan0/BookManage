<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import axios from '@/utils/http'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const addDialogVisible = ref(false)
const currentIsbn = ref('')
const bookCount = ref(1)

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
  } catch (error) {
    ElMessage.error('添加失败')
  } finally {
    loading.value = false
  }
}

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
  } catch (error) {
    ElMessage.error('获取图书列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page: number) => {
  pagination.value.page = page
  fetchBooks()
}

const handleSizeChange = (size: number) => {
  pagination.value.pageSize = size
  pagination.value.page = 1
  fetchBooks()
}

onMounted(() => {
  fetchBooks()
})
</script>


<template>
    <div class="example-pagination-block">
        <div class="example-demonstration">
            <el-table :data="tableData" height="250" style="width: 100%">
                <el-table-column prop="isbn" label="ISBN" width="180" />
                <el-table-column prop="title" label="Title" width="180" />
                <el-table-column prop="author" label="Author" width="180" />
                <el-table-column prop="translator" label="Translator" width="180" />
                <el-table-column prop="genre" label="Genre" width="180" />
                <el-table-column prop="country" Label="Country" width="180" />
                <el-table-column prop="era" label="Era" width="180" />
                <el-table-column prop="opac_nlc_class" label="中图分类号" width="180" />
                <el-table-column prop="publisher" label="Publisher" width="180" />
                <el-table-column prop="publish_year" label="Publish Year" width="180" />
                <el-table-column prop="page" label="Page" width="180" />
                <el-table-column prop="cover_url" label="封面链接" width="180" />
                <el-table-column prop="description" label="Description" width="180" />
                <el-table-column label="操作" width="150" fixed="right">
                  <template #default="{row}">
                    <el-button 
                      type="primary" 
                      size="small"
                      @click="showAddDialog(row.isbn)"
                    >
                      添加到书架
                    </el-button>
                  </template>
                </el-table-column>
            </el-table>
        </div>
    <el-pagination
      class="pagination"
      v-model:current-page="pagination.page"
      :page-size="pagination.pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="pagination.total"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      layout="total, sizes, prev, pager, next, jumper"
    />
    </div>

    <el-dialog v-model="addDialogVisible" title="添加到书架" width="30%">
      <el-form label-width="80px">
        <el-form-item label="数量">
          <el-input-number v-model="bookCount" :min="1" :max="10" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addToShelf">确定</el-button>
      </template>
    </el-dialog>
</template>

<style scoped>
.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>