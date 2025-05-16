<template>
  <!-- 使用正确的prop/emit模式 -->
  <el-dialog v-model="dialogVisible" title="书籍详情" width="60%">
    <div v-if="book" class="book-detail-container" ref="dialogContent">

      <div class="book-cover-container">
        <div class="book-cover-wrapper">
          <el-image :src="getCoverUrl(book)" fit="contain" class="book-cover" :preview-src-list="[getCoverUrl(book)]"
            :lazy="true">
            <template #error>
              <div class="image-error">
                <el-icon>
                  <Picture />
                </el-icon>
                <span>封面加载失败</span>
              </div>
            </template>
            <template #placeholder>
              <div class="image-loading">
                <el-icon>
                  <Loading />
                </el-icon>
                <span>封面加载中...</span>
              </div>
            </template>
          </el-image>
        </div>
      </div>

      <el-descriptions :column="1" border class="book-info">
        <el-descriptions-item label="书名">{{ book?.title || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="作者">{{ book?.author || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="译者">{{ book?.translator || '无' }}</el-descriptions-item>
        <el-descriptions-item label="出版社">{{ book?.publisher || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="出版年份">{{ book?.publish_year || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="页数">{{ book?.page || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="ISBN">{{ book?.isbn || '未知' }}</el-descriptions-item>
        <el-descriptions-item label="类型">{{ book?.genre || '无' }}</el-descriptions-item>
        <el-descriptions-item label="国家">{{ book?.country || '无' }}</el-descriptions-item>
        <el-descriptions-item label="年代">{{ book?.era || '无' }}</el-descriptions-item>
        <el-descriptions-item label="中图分类号">{{ book?.opac_nlc_class || '无' }}</el-descriptions-item>
        <el-descriptions-item label="内容简介">
          {{ book?.description || '暂无内容简介' }}
        </el-descriptions-item>
        <el-descriptions-item label="拥有数量">
          <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <span style="margin-left: 0;">{{ getBookCount(book?.isbn) }}</span>
            <div style="display: flex; gap: 10px;">
              <el-button size="small" @click="book?.isbn && showAddDialog(book.isbn)" :disabled="!book?.isbn">
                添加到书架
              </el-button>
            </div>

            <!-- 添加到书架对话框 -->
            <el-dialog v-model="addDialogVisible" title="添加到书架" width="30%">
              <el-form label-width="80px">
                <el-form-item label="数量" prop="count">
                  <el-input-number v-model="bookCount" :min="1" :max="10" controls-position="right" />
                  <div class="el-form-item__tip">每次最多可添加10本</div>
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="addDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="addToShelf">确定</el-button>
              </template>
            </el-dialog>
            <el-button size="small" type="danger" @click="book?.isbn && showRemoveDialog(book.isbn)"
              :disabled="!book?.isbn" v-if="getBookCount(book?.isbn) > 0">
              从书架移除
            </el-button>

            <!-- 从书架移除对话框 -->
            <el-dialog v-model="removeDialogVisible" title="从书架移除" width="30%">
              <el-form label-width="80px">
                <el-form-item label="数量" prop="count">
                  <el-input-number v-model="removeCount" :min="1" :max="getBookCount(removeIsbn)"
                    controls-position="right" />
                  <div class="el-form-item__tip">当前拥有: {{ getBookCount(removeIsbn) }}本</div>
                </el-form-item>
              </el-form>
              <template #footer>
                <el-button @click="removeDialogVisible = false">取消</el-button>
                <el-button type="danger" @click="removeFromShelf">确定移除</el-button>
              </template>
            </el-dialog>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="个人备注">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color:#999">(预留字段，暂未使用)</span>
            <el-button size="small" type="text" @click="handleEditRemark">
              编辑
            </el-button>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <div v-else-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <div v-else class="error-container">
      <el-empty description="获取书籍信息失败" />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import axiox from '@/utils/http'
import { ElMessage } from 'element-plus'
import { Picture, Loading } from '@element-plus/icons-vue'
import { useShelfCacheStore } from '@/stores/shelfCache'

interface Book {
  isbn: string
  title: string
  author: string
  translator?: string
  publisher: string
  publish_year: number
  page: number
  cover_url: string
  description: string
  genre?: string
  country?: string
  era?: string
  opac_nlc_class?: string
}

const props = defineProps<{
  isbn: string
  visible: boolean
}>()

const emit = defineEmits(['update:visible'])

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const loading = ref(false)
const book = ref<Book | null>(null)

let lastRequestIsbn = ''

const fetchBookDetail = async (isbn: string) => {
  // 记录当前请求的ISBN
  lastRequestIsbn = isbn

  try {
    loading.value = true
    const response = await axiox.get(`/api/books/${isbn}`)

    // 只有当返回的ISBN与当前请求匹配时才更新数据
    if (response.data.book?.isbn === lastRequestIsbn) {
      book.value = { ...response.data.book }
    }
  } catch (error: any) {
    // 忽略过期的响应
    if (isbn !== lastRequestIsbn) return;
    console.error('获取书籍详情失败:', error);
    ElMessage.error('获取书籍详情失败: ' + (error.response?.data?.message || error.message));
  } finally {
    loading.value = false;
  }
}

const openDialog = async () => {
  dialogVisible.value = true
  try {
    // 强制刷新书架数据
    await shelfCacheStore.fetchShelfItems(true)
    if (props.isbn) {
      await fetchBookDetail(props.isbn)
    }
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
}

const closeDialog = () => {
  dialogVisible.value = false
}

// 暴露方法给父组件
defineExpose({
  openDialog,
  closeDialog
})

// 缓存已获取的书籍数据
const shelfCacheStore = useShelfCacheStore()
const bookCache = new Map<string, Book>()

const addDialogVisible = ref(false)
const bookCount = ref(1)
const currentIsbn = ref('')

const showAddDialog = (isbn: string) => {
  currentIsbn.value = isbn
  bookCount.value = 1
  addDialogVisible.value = true
}

const addToShelf = async () => {
  if (!currentIsbn.value) return

  try {
    loading.value = true
    await axiox.post(`/api/bookshelf/${currentIsbn.value}`, {
      quantity: bookCount.value
    })
    ElMessage.success(`成功添加${bookCount.value}本书籍`)
    await shelfCacheStore.fetchShelfItems(true)
    addDialogVisible.value = false
  } catch (error: any) {
    console.error('添加到书架失败:', error)
    ElMessage.error(`添加到书架失败: ${error.response?.data?.message || error.message}`)
  } finally {
    loading.value = false
  }
}

const getBookCount = (isbn?: string) => {
  if (!isbn) return 0
  return shelfCacheStore.shelfItems.find(item => item.isbn === isbn)?.nums || 0
}

const removeDialogVisible = ref(false)
const removeCount = ref(1)
const removeIsbn = ref('')

const showRemoveDialog = (isbn: string) => {
  removeIsbn.value = isbn
  const currentCount = getBookCount(isbn)
  removeCount.value = Math.min(1, currentCount)
  removeDialogVisible.value = true
}

const getCoverUrl = (book: Book | null) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '';
  const defaultCover = `${baseUrl}/api/img/cover/default_cover.jpg`;

  if (!book) return defaultCover;

  // 如果cover_url为空或undefined，使用默认封面
  if (!book.cover_url) {
    return defaultCover;
  }

  // 处理相对路径
  if (book.cover_url.startsWith('/')) {
    return `${baseUrl}${book.cover_url}`;
  }

  // 处理完整URL
  if (book.cover_url.startsWith('http')) {
    return book.cover_url;
  }

  // 其他情况直接返回
  return book.cover_url;
}

const handleEditRemark = () => {
  ElMessage.info('备注编辑功能暂未实现')
}

const removeFromShelf = async () => {
  if (!removeIsbn.value) return

  try {
    loading.value = true
    await axiox.delete(`/api/bookshelf/${removeIsbn.value}`, {
      data: { quantity: removeCount.value }
    })
    ElMessage.success(`成功移除${removeCount.value}本书籍`)
    await shelfCacheStore.fetchShelfItems(true)
    removeDialogVisible.value = false
  } catch (error: any) {
    console.error('从书架移除失败:', error)
    ElMessage.error(`从书架移除失败: ${error.response?.data?.message || error.message}`)
  } finally {
    loading.value = false
  }
}

watch(() => props.isbn, (newIsbn) => {
  if (newIsbn) {
    // 检查缓存
    if (bookCache.has(newIsbn)) {
      book.value = bookCache.get(newIsbn)!
      return
    }
    fetchBookDetail(newIsbn).then(() => {
      if (book.value) {
        bookCache.set(newIsbn, book.value)
      }
    })
  }
}, { immediate: true })

watch(() => props.visible, (visible) => {
  if (visible && props.isbn) {
    fetchBookDetail(props.isbn)
  }
})
</script>

<style scoped>
/* 强制弹窗显示和样式 */
:deep(.el-dialog) {
  z-index: 2000 !important;
  position: fixed !important;
  top: 50% !important;
  left: 50% !important;
  transform: translate(-50%, -50%) !important;
  display: block !important;
  opacity: 1 !important;
  visibility: visible !important;
}

/* 确保遮罩层显示 */
:deep(.el-overlay) {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  background-color: rgba(0, 0, 0, 0.5) !important;
  z-index: 1999 !important;
}

/* 弹窗内容样式 */
.book-detail-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  min-height: 400px;
}

.book-cover-container {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.book-cover-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 300px;
  width: 200px;
  margin: 0 auto;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.book-cover {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.book-cover:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.2);
}

.image-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-secondary);
}

.image-loading .el-icon {
  font-size: 30px;
  margin-bottom: 10px;
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.book-info {
  margin-top: 20px;
}

/* 错误状态样式 */
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

.loading-container,
.error-container {
  padding: 40px 0;
  text-align: center;
}
</style>
