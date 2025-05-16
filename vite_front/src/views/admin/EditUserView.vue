<template>
    <div class="edit-container">
        <h2 class="edit-title">编辑用户</h2>
        <div class="edit-content">
            <div class="original-info">
                <h3>原用户信息</h3>
                <el-descriptions :column="1" border>
                    <el-descriptions-item label="用户ID">{{ originalUser.user_id }}</el-descriptions-item>
                    <el-descriptions-item label="用户名">{{ originalUser.username }}</el-descriptions-item>
                    <el-descriptions-item label="角色">{{ originalUser.role === 'admin' ? '管理员' : '普通用户' }}</el-descriptions-item>
                <el-descriptions-item label="创建时间">
                  {{ originalUser.createdAt ? new Date(originalUser.createdAt).toLocaleString() : '未知' }}
                </el-descriptions-item>
                </el-descriptions>
            </div>

            <div class="edit-form">
                <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
                    <el-form-item label="用户名" prop="username">
                        <el-input v-model="form.username" />
                    </el-form-item>
                    <el-form-item label="角色" prop="role">
                        <el-select v-model="form.role">
                            <el-option label="管理员" value="admin" />
                            <el-option label="普通用户" value="user" />
                        </el-select>
                    </el-form-item>
                <el-form-item>
                    <el-checkbox v-model="form.showPassword">修改密码</el-checkbox>
                </el-form-item>
                <el-form-item 
                    v-if="form.showPassword"
                    label="新密码" 
                    prop="password"
                >
                    <el-input v-model="form.password" type="password" show-password />
                </el-form-item>
                <el-form-item 
                    v-if="form.showPassword"
                    label="确认密码" 
                    prop="confirmPassword"
                >
                    <el-input v-model="form.confirmPassword" type="password" show-password />
                </el-form-item>
                    <el-form-item>
                        <el-button type="primary" @click="submitForm(formRef)">保存</el-button>
                        <el-button @click="cancel">取消</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </div>
    </div>
</template>

<style scoped>
.edit-container {
    padding: 20px;
}

.edit-title {
    margin-bottom: 20px;
    text-align: center;
}

.edit-content {
    display: flex;
    gap: 30px;
}

.original-info {
    width: 300px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
}

.edit-form {
    flex: 1;
    padding: 20px;
    background-color: #fff;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
    .edit-content {
        flex-direction: column;
    }
    
    .original-info {
        width: 100%;
    }
}
</style>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { AxiosError } from 'axios';
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()

const originalUser = reactive({
    user_id: '',
    username: '',
    role: 'user',
    createdAt: ''
})

const form = reactive({
    id: '',
    username: '',
    role: 'user' as 'admin' | 'user',
    password: '',
    confirmPassword: '',
    showPassword: false
})

const validatePass = (_rule: any, value: string, callback: any) => {
    if (value !== form.password) {
        callback(new Error('两次输入的密码不一致!'))
    } else {
        callback()
    }
}

const rules = reactive<FormRules<typeof form>>({
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 4, max: 20, message: '用户名长度必须在4到20个字符之间', trigger: 'blur' }
    ],
    role: [
        { required: true, message: '请选择角色', trigger: 'change' }
    ],
    password: [
        { min: 6, max: 20, message: '密码长度必须在6到20个字符之间', trigger: 'blur' }
    ],
    confirmPassword: [
        { validator: validatePass, trigger: 'blur' }
    ]
})

onMounted(() => {
    if (route.params.id) {
        loadUser(route.params.id as string)
    }
})

const loading = ref(false)

const loadUser = async (id: string) => {
    loading.value = true
    try {
        // 确保用户列表已加载
        await userStore.fetchUsers()
        const user = userStore.getCachedUser(id)
        if (!user) {
            throw new Error('用户不存在')
        }
        if (user) {
            originalUser.user_id = user.user_id
            originalUser.username = user.username
            originalUser.role = user.role
            originalUser.createdAt = user.createdAt || new Date().toISOString()
            
            form.id = user.user_id
            form.username = user.username
            form.role = user.role
        }
    } catch (error) {
        ElMessage.error('获取用户信息失败')
        console.error('加载用户失败:', error)
    } finally {
        loading.value = false
    }
}

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            try {
                // 准备更新数据
                const updateData: {
                  username: string
                  role: string
                  password?: string
                } = {
                  username: form.username,
                  role: form.role
                }

                // 如果有新密码则加密并更新
                if (form.showPassword && form.password) {
                  const msgBuffer = new TextEncoder().encode(form.password)
                  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
                  const hashArray = Array.from(new Uint8Array(hashBuffer))
                  updateData.password = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
                } else {
                  // 不修改密码时移除password字段
                  delete updateData.password
                }

                // 调用API更新用户
                await axios.put(`/api/users/${form.id}`, updateData, {
                  headers: {
                    'Authorization': `Bearer ${userStore.token}`,
                    'Content-Type': 'application/json'
                  }
                })
                
                // 刷新用户列表
                await userStore.fetchUsers(true)
                
                ElMessage.success('用户信息更新成功')
                router.push('/admin/users')
            } catch (error) {
                console.error('更新用户失败:', error)
                if (error instanceof AxiosError) {
                    const axiosError = error as AxiosError<any>
                    const errorMsg = axiosError.response?.data?.message || '更新用户信息失败，请稍后重试'
                    ElMessage.error(errorMsg)
                } else {
                    ElMessage.error('更新用户信息失败，请稍后重试')
                }
            }
        }
    })
}

const cancel = () => {
    router.push('/admin/users')
}
</script>
