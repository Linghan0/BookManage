<template>
  <div class="test-view">
    <h1>测试页面 - 条形码扫描</h1>
    
    <div class="scanner-container">
      <div id="scanner"></div>
      <el-button 
        type="primary" 
        @click="startScanner"
        :disabled="isScanning"
      >
        开始扫描
      </el-button>
      <el-button 
        type="danger" 
        @click="stopScanner"
        :disabled="!isScanning"
      >
        停止扫描
      </el-button>
    </div>

    <div class="result-section" v-if="scanResult">
      <h3>扫描结果</h3>
      <p>ISBN: {{ scanResult }}</p>
    </div>

    <div class="test-section">
      <p v-if="clickCount > 0">按钮点击次数: {{ clickCount }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Quagga from '@ericblade/quagga2'

const clickCount = ref(0)
const isScanning = ref(false)
const scanResult = ref<string>('')

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

function isValidISBN(code: string | null): boolean {
  if (!code) return false
  // 简单验证ISBN格式
  return /^(97(8|9))?\d{9}(\d|X)$/.test(code)
}
</script>

<style scoped>
.test-view {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
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

.test-section {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
