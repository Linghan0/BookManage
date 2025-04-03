<template>
  <div class="home">
    <h1>欢迎使用图书管理系统</h1>
    <p class="welcome-text">请使用顶部导航栏访问系统功能</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'HomeView'
})
</script>

<style scoped>
.home {
  text-align: center;
  padding: 40px 20px;
}

.welcome-text {
  font-size: 18px;
  color: #666;
  margin-top: 20px;
}
</style>
