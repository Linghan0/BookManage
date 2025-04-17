<template>
    <el-form ref="ruleFormRef" style="max-width: 600px" :model="ruleForm" status-icon :rules="rules" label-width="auto"
        class="demo-ruleForm">
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
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import axios from 'axios'

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

const validateUsername = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请输入用户名 / Please input the username'))
    } else {
        if ( value.length < 4 || value.length > 20) {
            callback(new Error('用户名长度必须在4-20个字符之间 / Username length must be between 4-20 characters'))
        }else if (ruleForm.username !== '') {
            if (!ruleFormRef.value) return
            ruleFormRef.value.validateField('username')
        }
        callback()
    }
}
const validatePass = (rule: any, value: any, callback: any) => {
    if (value === '') {
        callback(new Error('请输入密码 / Please input the password'))
    } else {
        if (ruleForm.checkPass !== '') {
            if (!ruleFormRef.value) return
            ruleFormRef.value.validateField('checkPass')
        }
        callback()
    }
}
const validatePass2 = (rule: any, value: any, callback: any) => {
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

const submitForm = async (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.validate(async (valid) => {
        if (valid) {
            try {
                const encryptedPass = await sha256(ruleForm.pass)
                const response = await axios.post('/api/register', {
                    username: ruleForm.username,
                    password: encryptedPass
                    // 需要管理员验证
                })
                console.log('Registration successful', response.data)
            } catch (error) {
                console.error('Registration failed', error)
            }
        } else {
            console.log('error submit!')
        }
    })
}

const resetForm = (formEl: FormInstance | undefined) => {
    if (!formEl) return
    formEl.resetFields()
}
</script>
