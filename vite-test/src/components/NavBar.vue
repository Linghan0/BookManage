<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { User } from '@element-plus/icons-vue'

const activeIndex = ref('1')
const userStore = useUserStore()
const router = useRouter()

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
}
</script>

<template>
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
  </el-menu>
</template>

<style scoped>
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

.el-menu--horizontal>.el-menu-item:nth-child(4) {
  margin-right: auto;
}

.el-menu-item {
  height: 60px;
  line-height: 60px;
}

.el-sub-menu {
  margin: 0;
}
</style>
