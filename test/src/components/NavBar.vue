<template>
  <nav class="navbar">
    <div class="nav-container">
      <router-link to="/" class="nav-logo">图书管理系统</router-link>
      <div class="nav-links">
        <router-link to="/books" class="nav-link">图书列表</router-link>
        <router-link to="/about" class="nav-link">关于</router-link>
      </div>
    </div>
  </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'NavBar'
})
</script>

<style scoped>
.navbar {
  background-color: #42b983;
  color: white;
  padding: 0 20px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
}

.nav-logo {
  color: white;
  font-size: 20px;
  font-weight: bold;
  text-decoration: none;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 8px 12px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.nav-link:hover {
  background-color: rgba(255,255,255,0.2);
}

.nav-link.router-link-exact-active {
  background-color: rgba(255,255,255,0.1);
}
</style>
