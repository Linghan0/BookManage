<template>
  <div class="scan-book-view">
    <div class="page-header-container">
      <el-page-header @back="$router.go(-1)">
        <template #content>
          <h1 class="page-title">扫描搜索书籍</h1>
        </template>
      </el-page-header>
    </div>

    <div class="scanner-container">
      <el-alert 
        title="摄像头使用提示" 
        type="warning" 
        show-icon
        :closable="false"
        class="camera-notice">
        <p>1. 非HTTPS环境下浏览器默认禁止使用摄像头</p>
        <p>2. Edge浏览器解禁方法：</p>
        <p>&nbsp;&nbsp;- 访问 edge://flags/</p>
        <p>&nbsp;&nbsp;- 找到"Insecure origins treated as secure"选项</p>
        <p>&nbsp;&nbsp;- 设为启用并添加网站IP到白名单</p>
      </el-alert>
      <div id="scanner"></div>
      <el-button type="primary" @click="startScanner" :disabled="isScanning">
        开始扫描
      </el-button>
      <el-button type="danger" @click="stopScanner" :disabled="!isScanning">
        停止扫描
      </el-button>
    </div>

    <div class="result-section" v-if="scanResult">
      <h3>扫描结果</h3>
      <p>ISBN: {{ scanResult }}</p>
      <el-button type="primary" @click="handleScanResult(scanResult)" :loading="isLoading">
        搜索书籍
      </el-button>
    </div>
    <!-- 书籍详情弹窗 -->
    <BookDetailView v-model:visible="detailVisible" :isbn="currentBookIsbn" ref="bookDetailDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Quagga from '@ericblade/quagga2'
import { ElMessageBox } from 'element-plus'
import BookDetailView from './BookDetailView.vue'
import { useBookStore } from '@/stores/books'


const booksStore = useBookStore()
const isScanning = ref(false)
const scanResult = ref<string>('')
const isLoading = ref(false)

const detailVisible = ref(false)
const currentBookIsbn = ref('')
const bookDetailDialog = ref()

const viewBookDetail = (isbn: string) => {
  currentBookIsbn.value = isbn
  bookDetailDialog.value?.openDialog()
}


function startScanner() {
  isScanning.value = true
  scanResult.value = ''
  
  const scannerElement = document.querySelector('#scanner')
  if (!scannerElement) {
    console.error('Scanner element not found')
    isScanning.value = false
    return
  }

  Quagga.init({
    inputStream: {
      name: "Live",
      type: "LiveStream",
      target: scannerElement,
      constraints: {
        width: 480,
        height: 320,
        facingMode: "environment"
      },
    },
    decoder: {
      readers: ["ean_reader", "ean_8_reader", "code_128_reader"]
    },
  }, function(err) {
    if (err) {
      console.error(err)
      isScanning.value = false
      return
    }
    Quagga.start()
  })

  Quagga.onDetected((data) => {
    const code = data.codeResult?.code
    if (code && isValidISBN(code)) {
      scanResult.value = code
      stopScanner()
    }
  })
}

function stopScanner() {
  Quagga.stop()
  isScanning.value = false
}

async function handleScanResult(isbn: string) {
  try {
    isLoading.value = true
    await ElMessageBox.confirm(
      `确认搜索 ISBN: ${isbn} 吗?`,
      '扫描结果确认',
      {
        confirmButtonText: '确认搜索',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 调用搜索API
    const data = await booksStore.searchBooks({
        field: 'isbn',
        value: isbn
    })
    if (data.length > 0 && data[0].isbn) {
      // 使用弹窗显示书籍详情
      viewBookDetail(data[0].isbn)
    } else {
      ElMessageBox.alert('未找到匹配的书籍', '提示', {
        confirmButtonText: '确定'
      })
    }
  } catch (error) {
    console.error('搜索失败:', error)
  } finally {
    isLoading.value = false
  }
}

function isValidISBN(code: string | null): boolean {
  if (!code) return false
  // 简单验证ISBN格式
  return /^(97(8|9))?\d{9}(\d|X)$/.test(code)
}

// 自动处理扫描结果
watch(scanResult, (newVal) => {
  if (newVal) {
    handleScanResult(newVal)
  }
})
</script>

<style scoped>
.scan-book-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 4px;
}

.scanner-container {
  margin: 20px 0;
}

#scanner {
  width: 100%;
  height: 300px;
  margin: 10px 0;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
}

.result-section {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
