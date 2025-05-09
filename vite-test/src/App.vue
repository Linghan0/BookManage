<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import { onMounted, onUnmounted } from 'vue'

// import { ref, onMounted, onUnmounted } from 'vue'
// const bgImageUrl = ref('')
const defaultBgImages = {
  pc: new URL('./assets/default-bg-pc.jpg', import.meta.url).href,
  mp: new URL('./assets/default-bg-mp.jpg', import.meta.url).href
}
let debounceTimer: number | null = null

function getImageSortParam() {
  const aspectRatio = window.innerWidth / window.innerHeight
  return aspectRatio > 1.33 ? 'pc' : 'mp'
}

// 更新背景图片
async function updateBackground() {
  const sortParam = getImageSortParam()
  const appContainer = document.querySelector('.app-container') as HTMLElement
  
  try {
    // 先设置默认背景
    const defaultBg = defaultBgImages[sortParam]
    appContainer.style.backgroundImage = `url("${defaultBg}")`
    
    // // 尝试获取动态背景
    // const response = await fetch(`/api/img/image/${sortParam}`)
    // if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    
    // const blob = await response.blob()
    // const url = URL.createObjectURL(blob)
    // bgImageUrl.value = url
    
    // if (appContainer) {
    //   // 释放之前的Blob URL
    //   const oldBg = appContainer.style.backgroundImage
    //   if (oldBg && oldBg.startsWith('url("blob:')) {
    //     URL.revokeObjectURL(oldBg.slice(5, -2))
    //   }
    //   appContainer.style.backgroundImage = `url("${url}")`
    // }
  } catch (error) {
    console.error('Background image error:', error)
    // 确保使用默认背景
    if (appContainer) {
      appContainer.style.backgroundImage = `url("${defaultBgImages[sortParam]}")`
    }
  }
}

// 防抖函数
function debouncedUpdateBackground() {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = window.setTimeout(() => {
    updateBackground()
    debounceTimer = null
  }, 1000)
}


onMounted(() => {
  updateBackground()
  window.addEventListener('resize', debouncedUpdateBackground)
})

onUnmounted(() => {
  window.removeEventListener('resize', debouncedUpdateBackground)
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
})
</script>

<template>
  <div class="app-container" referrerPolicy="no-referrer">
    <div class="common-layout">
      <el-container>
        <el-header>
          <NavBar></NavBar>
        </el-header>
        <el-main>
          <router-view></router-view>
        </el-main>
      </el-container>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 0.5s ease;
  margin: 0;
  padding: 0;
  overflow: auto;
}

.app-container::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0);
  z-index: 0;
  pointer-events: none;
}

.common-layout {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-container {
  padding: 0;
  margin: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  padding: 0;
  margin: 0;
  width: 100%;
  flex-shrink: 0;
}

.el-main {
  flex: 1;
  overflow: auto;
}

.common-layout {
  width: 100%;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

@media (max-width: 768px) {
  .app-container {
    position: absolute;
    height: auto;
    min-height: 100vh;
  }
  
  .el-main {
    padding: 10px;
  }
}
</style>
