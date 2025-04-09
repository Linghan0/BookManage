<script setup lang="ts">
import NavBar from './components/NavBar.vue'
</script>

<template>
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
</template>
