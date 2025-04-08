<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
import axios from 'axios'
import { onMounted } from 'vue'

onMounted(async () => {
  try {
    const response = await axios.get('https://jsonplaceholder.typicode.com/todos/1')
    console.log('Axios测试成功:', response.data)
  } catch (error) {
    console.error('Axios测试失败:', error)
  }
})
</script>

<template>
  <div>
    <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
  </div>
  <HelloWorld msg="Vite + Vue" />
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
