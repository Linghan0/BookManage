<template>
    <div class="login-container">
        <el-form ref="ruleFormRef" :model="ruleForm" status-icon :rules="rules" label-width="auto" class="login-form">
            <el-form-item label="Username" prop="username">
                <el-input v-model="ruleForm.username" type="text" autocomplete="off" />
                <!-- 与登录不同，管理员统一注册不自动存储账号 autocomplete设置为"off" -->
                <!-- https://developer.mozilla.org/zh-CN/docs/Web/HTML/Reference/Attributes/autocomplete -->
            </el-form-item>
            <el-form-item label="Password" prop="pass">
                <el-input v-model="ruleForm.pass" type="password" autocomplete="off" />
            </el-form-item>
            <el-form-item label="Confirm" prop="checkPass">
                <el-input v-model="ruleForm.checkPass" type="password" autocomplete="off" />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="submitForm(ruleFormRef)">
                    注册
                </el-button>
                <el-button @click="resetForm(ruleFormRef)">重置</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<style scoped>
.el-form-item__label {
    min-width: 120px;
}

.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: url('@/assets/vue.svg') center/cover no-repeat;
}

.login-form {
    max-width: 600px;
    padding: 2rem;
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
}

:deep(.el-form-item__content) {
    display: flex;
    justify-content: center;
    gap: 1rem;
}
</style>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()
const ruleFormRef = ref<FormInstance>()

async function sha256(message: string): Promise<string> {
    // 将字符串编码为UTF-8
    const msgBuffer = new TextEncoder().encode(message)

    // 使用Web Crypto API计算哈希
    const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)

    // 将ArrayBuffer转换为Hex字符串
    const hashArray = Array.from(new Uint8Array(hashBuffer))
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

// 用户名可用性检查
const checkUsernameAvailable = async (username: string) => {
    try {
        const token = userStore.token
        if (!token) {
            ElMessage.error('请先登录')
            return false
        }

        const response = await fetch(`${window.location.origin}/api/users/check?username=${encodeURIComponent(username)}`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })

        if (!response.ok) {
            return false
        }

        return (await response.json()).available
    } catch {
        return false
    }
}

const validateUsername = (_rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请输入用户名 / Please input the username'))
    }else if (value.length < 4 || value.length > 20) {
        callback(new Error('用户名长度必须在4-20个字符之间 / Username length must be between 4-20 characters'))
    }else{
        callback()
    }
}

const validatePass = (_rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请输入密码 / Please input the password'))
    } else {
        callback()
    }
}

const validatePass2 = (_rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请输入密码 / Please input the password again'))
    } else if (value !== ruleForm.pass) {
        callback(new Error("两个输入不匹配！ / Two inputs don't match!"))
    } else {
        callback()
    }
}

const ruleForm = reactive({
    username: '',
    pass: '',
    checkPass: ''
})

const rules = reactive<FormRules<typeof ruleForm>>({
    username: [{ validator: validateUsername, trigger: 'blur' }],
    pass: [{ validator: validatePass, trigger: 'blur' }],
    checkPass: [{ validator: validatePass2, trigger: 'blur' }],
})

const router = useRouter()


const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            // 严格前端验证，未通过直接拒绝
            if (!userStore.isAdmin()) {
                ElMessage({
                    showClose: true,
                    message: '错误, 只有管理员可以注册新用户。',
                    type: 'warning',
                })
                return
            }
            // 验证用户名是否可用 element plus 的验证器是同步的，所以异步函数操作移至这里
            const isAvailable = await checkUsernameAvailable(ruleForm.username)
            if (!isAvailable) {
                ElMessage({
                    showClose: true,
                    message: '用户名已被占用。',
                    type: 'warning',
                })
                return
            }
            try {
                const encryptedPass = await sha256(ruleForm.pass)
                const success = await userStore.createUser({
                    user_id: '',
                    username: ruleForm.username,
                    password: encryptedPass,
                    role: 'user'
                })

                if (success) {
                    ElMessage({
                        showClose: true,
                        message: '注册成功',
                        type: 'success',
                    })
                    formEl.resetFields()
                    router.push('/admin/users') // 跳转到用户列表
                }
            } catch (error: any) {
            if (error.response?.data?.message === '用户名已存在') {
                ElMessage.error('注册失败: 用户名已存在')
            } else {
                ElMessage.error('注册失败: 服务器错误')
            }
            }
        } else {
            ElMessage.warning('请正确填写表单')
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}
</script>
