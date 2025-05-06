<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  ElTable,
  ElTableColumn,
  ElButton,
  ElMessage,
  ElPagination
} from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()


onMounted(async () => {
  try {
    await userStore.fetchUsers()
  } catch (error: unknown) {
    if (error instanceof Error) {
      console.error('获取用户列表失败:', error.message)
    }
  }
})

const handlePageChange = (page: number) => {
  userStore.pagination.currentPage = page
  userStore.fetchUsers()
}

const handleSizeChange = (size: number) => {
  userStore.pagination.pageSize = size
  userStore.pagination.currentPage = 1
  userStore.fetchUsers()
}

const router = useRouter()

const handleEdit = (user_id: string) => {
  router.push(`/admin/users/edit/${user_id}`)
}

const handleDelete = async (user_id: string) => {
  const user = userStore.users.find(u => u.user_id === user_id)
  if (user?.role === 'admin') {
    ElMessage.warning('管理员用户不可删除')
    return
  }
  await userStore.deleteUser(user_id)
}


</script>

<template>
  <div class="user-management">
    <div class="page-header-container">
      <el-page-header @back="router.go(-1)">
        <template #content>
          <h1 class="page-title">用户管理</h1>
        </template>
      </el-page-header>
      <div>
        <el-button type="primary" @click="router.push('/admin/register')">
          添加用户
        </el-button>
      </div>
    </div>

    <el-table :data="userStore.users" border style="width: 100%; min-width: 600px; max-width: 1200px">
      <el-table-column prop="user_id" label="ID" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" />
      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row.user_id)">编辑</el-button>
          <el-button size="small" type="danger" :disabled="row.role === 'admin'" @click="handleDelete(row.user_id)">
            {{ row.role === 'admin' ? '不可删除' : '删除' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" :current-page="userStore.pagination.currentPage"
      :page-size="userStore.pagination.pageSize" :total="userStore.pagination.total" @current-change="handlePageChange"
      @size-change="handleSizeChange" layout="total, sizes, prev, pager, next, jumper" />


  </div>
</template>

<style scoped>
.user-management {
  padding: 20px;
}

.page-header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.page-title {
  font-size: 20px;
  font-weight: 500;
  color: #303133;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: center;
}
</style>
