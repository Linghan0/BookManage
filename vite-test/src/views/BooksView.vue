<script setup lang="ts">
import SearchView from './SearchView.vue';
import BooklistView from './BooklistView.vue';

</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <!-- Searh Books -->
        <SearchView />
      </el-header>
      <el-main>
        <!-- Book list -->
        <BooklistView />
      </el-main>
    </el-container>
  </div>
</template>
