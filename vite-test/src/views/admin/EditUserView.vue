<template>
    <el-form ref="formRef" style="max-width: 600px" :model="form" :rules="rules" label-width="auto" class="demo-form">
        <el-form-item label="用户名" prop="username">
            <el-input v-model="form.username" type="text" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
            <el-select v-model="form.role" style="width: 100%">
                <el-option label="管理员" value="admin" />
                <el-option label="普通用户" value="user" />
            </el-select>
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="submitForm(formRef)">保存</el-button>
            <el-button @click="cancel">取消</el-button>
        </el-form-item>
    </el-form>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()

const form = reactive({
    id: '',
    username: '',
    role: 'user' as 'admin' | 'user'
})

const rules = reactive<FormRules<typeof form>>({
    username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 4, max: 20, message: '用户名长度必须在4到20个字符之间', trigger: 'blur' }
    ],
    role: [
        { required: true, message: '请选择角色', trigger: 'change' }
    ]
})

onMounted(() => {
    if (route.params.id) {
        loadUser(route.params.id as string)
    }
})

const loadUser = async (id: string) => {
    const user = userStore.users.find(u => u.id === id)
    if (user) {
        form.id = user.id
        form.username = user.username
        form.role = user.role
    }
}

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            try {
                // TODO: 实现更新用户逻辑
                ElMessage.success('用户信息更新成功')
                router.push('/admin/users')
            } catch (error) {
                ElMessage.error('更新用户信息失败')
            }
        }
    })
}

const cancel = () => {
    router.push('/admin/users')
}
</script>
