<script setup lang="ts">

import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const activeIndex = ref('1')
const userStore = useUserStore()
const router = useRouter()
const handleSelect = (key: '1' | '2' | '3' | '4-1' | '4-2' | '5') => {
  const routes = {
    '1': '/',
    '2': '/books',
    '3': '/userbooks',
    '4-1': '/admin/books',
    '4-2': '/admin/users',
    '5': '/login'
  }
  if (routes[key]) {
    router.push(routes[key])
  }
}

</script>


<template>
  <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" :ellipsis="false"
    @select="handleSelect">
    <el-menu-item index="0">
      <img style="width: 100px" src="/public/vite.svg" alt="Element logo" />
    </el-menu-item>
    <el-menu-item index="1" route="/">首页</el-menu-item>
    <el-menu-item index="2" route="/books">图书列表</el-menu-item>
    <el-menu-item index="3" route="/userbooks">个人书架</el-menu-item>
    <!-- <el-sub-menu index="4" v-if="userStore.isAdmin()"> -->
    <el-sub-menu index="4" >
        <template #title>admin</template>
        <el-menu-item index="4-1" route="/admin/books">图书管理</el-menu-item>
        <el-menu-item index="4-2" route="/admin/users">用户管理</el-menu-item>
      </el-sub-menu>
      <el-menu-item index="5" route="/login">登录</el-menu-item>
  </el-menu>
</template>



<style scoped>
.el-menu--horizontal>.el-menu-item:nth-child(3) {
  margin-right: auto;
}
</style>