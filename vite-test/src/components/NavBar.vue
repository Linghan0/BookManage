<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { User, Menu as MenuIcon } from '@element-plus/icons-vue'

const activeIndex = ref('1')
const userStore = useUserStore()
const router = useRouter()
const showMobileMenu = ref(false)

const handleSelect = (key: '1' | '2' | '3' | '4' | '5-1' | '5-2' | '6' ) => {
  const routes = {
    '1': '/',
    '2': '/books',
    '3': '/scan-book',
    '4': '/bookshelf',
    '5-1': '/admin/books',
    '5-2': '/admin/users',
    '6': '/login',
  }
  if (routes[key]) {
    try {
      router.push(routes[key]).catch(() => {})
    } catch (e) {
      console.error('Navigation error:', e)
    }
  }
  showMobileMenu.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}
</script>

<template>
  <div class="nav-container">
    <div class="desktop-nav">
      <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" :ellipsis="false"
        @select="handleSelect">
        <el-menu-item index="0">
          <img style="width: 50px" src="/public/vite.svg" alt="Element logo" />
        </el-menu-item>
        <el-menu-item index="1">首页</el-menu-item>
        <el-menu-item index="2">图书列表</el-menu-item>
        <el-menu-item index="3">扫描书籍</el-menu-item>
        <el-menu-item index="4">个人书架</el-menu-item>
        <el-sub-menu index="5" v-if="userStore.isAdmin()">
          <template #title>admin</template>
          <el-menu-item index="5-1">图书管理</el-menu-item>
          <el-menu-item index="5-2">用户管理</el-menu-item>
        </el-sub-menu>
        <div class="auth-buttons">
          <el-menu-item index="6" v-if="!userStore.isAuthenticated">登录</el-menu-item>
          <el-sub-menu index="7" v-else>
            <template #title>
              <el-icon>
                <User />
              </el-icon>
              <span style="margin-left: 8px">{{ userStore.user?.username }}</span>
            </template>
            <el-menu-item @click="userStore.logout()">退出登录</el-menu-item>
          </el-sub-menu>
        </div>
      </el-menu>
    </div>

    <div class="mobile-nav">
      <div class="mobile-header">
        <img style="width: 50px" src="/public/vite.svg" alt="Element logo" />
        <el-menu class="mobile-auth" mode="horizontal">
          <el-menu-item index="6" v-if="!userStore.isAuthenticated">登录</el-menu-item>
          <el-sub-menu index="7" v-else>
            <template #title>
              <el-icon>
                <User />
              </el-icon>
            </template>
            <el-menu-item @click="userStore.logout()">退出登录</el-menu-item>
          </el-sub-menu>
        </el-menu>
        <el-button @click="toggleMobileMenu" :icon="MenuIcon" circle />
      </div>
      
      <el-collapse-transition>
        <div v-show="showMobileMenu" class="mobile-menu">
          <el-menu 
            :default-active="activeIndex" 
            class="mobile-menu-list"
            @select="handleSelect">
            <el-menu-item index="1">首页</el-menu-item>
            <el-menu-item index="2">图书列表</el-menu-item>
            <el-menu-item index="3">扫描书籍</el-menu-item>
            <el-menu-item index="4">个人书架</el-menu-item>
            <el-sub-menu index="5" v-if="userStore.isAdmin()">
              <template #title>admin</template>
              <el-menu-item index="5-1">图书管理</el-menu-item>
              <el-menu-item index="5-2">用户管理</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </div>
      </el-collapse-transition>
    </div>
  </div>
</template>

<style scoped>
.nav-container {
  width: 100%;
}

.desktop-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-menu-demo {
  width: 100%;
  margin: 0;
  padding: 0;
  border: none;
}

.el-menu--horizontal {
  width: 100%;
  margin: 0;
  padding: 0;
  border: none;
}

.el-menu--horizontal>.el-menu-item {
  margin: 0;
  padding: 0 20px;
}

.el-menu-item {
  height: 60px;
  line-height: 60px;
}

.el-sub-menu {
  margin: 0;
}

.auth-buttons {
  display: flex;
  margin-left: auto;
}

.mobile-nav {
  width: 100%;
  position: relative;
  z-index: 1000;
}

.mobile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 10px;
  height: 60px;
  background-color: white;
  position: relative;
  z-index: 1001;
}

.mobile-menu {
  width: 100%;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12);
  position: relative;
  z-index: 1000;
}

.mobile-menu-list {
  border-right: none;
}

@media (min-width: 769px) {
  .mobile-nav {
    display: none;
  }
}

@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
}
</style>
