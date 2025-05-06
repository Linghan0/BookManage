<script setup lang="ts">
import NavBar from './components/NavBar.vue'
import { ref, onMounted, onUnmounted } from 'vue'

const bgImageUrl = ref('')

function getImageSortParam() {
  const aspectRatio = window.innerWidth / window.innerHeight
  return aspectRatio > 1.33 ? 'pc' : 'mp'
}

function updateBackground() {
  const sortParam = getImageSortParam()
  const url = `https://iw233.cn/api.php?sort=${sortParam}`
  bgImageUrl.value = url
  const appContainer = document.querySelector('.app-container') as HTMLElement
  if (appContainer) {
    appContainer.style.backgroundImage = `url(${url})`
  }
}

onMounted(() => {
  updateBackground()
  window.addEventListener('resize', updateBackground)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateBackground)
})
</script>

<template>
  <div class="app-container">
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
}

.app-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0);
  z-index: 0;
}

.common-layout {
  position: relative;
  z-index: 1;
}

.el-container {
  padding: 0;
  margin: 0;
}

.el-header {
  padding: 0;
  margin: 0;
  width: 100%;
}

.common-layout {
  width: 100%;
  margin: 0;
  padding: 0;
}
</style>
