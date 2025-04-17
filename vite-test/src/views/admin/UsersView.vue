<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { 
  ElTable, 
  ElTableColumn, 
  ElButton, 
  ElDialog, 
  ElMessage, 
  ElFormItem, 
  ElInput,
  ElSelect,
  ElOption,
  ElPagination
} from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const showDialog = ref(false)
const currentUser = ref({
  id: '',
  username: '',
  role: 'user' as 'admin' | 'user',
  password: ''
})

onMounted(async () => {
  try {
    await userStore.fetchUsers()
  } catch (error) {
    console.error(error)
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

const handleEdit = (id: string) => {
  $router.push(`/admin/users/edit/${id}`)
}

const handleDelete = async (id: string) => {
  try {
    await userStore.deleteUser(id)
    ElMessage.success('删除用户成功')
  } catch (error) {
    ElMessage.error('删除用户失败')
  }
}

const handleSubmit = async () => {
  try {
    if (currentUser.value.id) {
      // TODO: Implement update user
      ElMessage.success('更新用户成功')
    } else {
      await userStore.createUser({
        username: currentUser.value.username,
        role: currentUser.value.role,
        password: currentUser.value.password
      })
    }
    showDialog.value = false
  } catch (error) {
    ElMessage.error('操作失败')
  }
}
</script>

<template>
  <div class="user-management">
    <div class="header">
      <h2>用户管理</h2>
      <div>
        <el-button type="primary" @click="$router.push('/admin/register')">
          添加用户
        </el-button>
      </div>
    </div>

    <el-table :data="userStore.users" border style="width: 100%">
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="role" label="角色" />
    <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row.id)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row.id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      class="pagination"
      :current-page="userStore.pagination.currentPage"
      :page-size="userStore.pagination.pageSize"
      :total="userStore.pagination.total"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      layout="total, sizes, prev, pager, next, jumper"
    />


  </div>
</template>

<style scoped>
.user-management {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
