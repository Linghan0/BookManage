<!-- 未完成 -->
<template>
  <div class="login-container">
    <div class="common-layout">
      <el-form ref="ruleFormRef" :model="ruleForm" status-icon :rules="rules" label-width="auto" class="login-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="ruleForm.username" type="text" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="ruleForm.password" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="submitForm(ruleFormRef)"
            :loading="loading"
          >
            登录
          </el-button>
          <el-button @click="resetForm(ruleFormRef)">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
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
import type { FormInstance, FormRules } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const ruleFormRef = ref<FormInstance>()
const loading = ref(false)

const validateUsername = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (value.length < 3) {
    callback(new Error('用户名至少3个字符'))
  } else {
    callback()
  }
}

const validatePassword = (rule: any, value: any, callback: any) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6个字符'))
  } else {
    callback()
  }
}

const ruleForm = reactive({
  username: '',
  password: ''
})

const rules = reactive<FormRules<typeof ruleForm>>({
  username: [{ validator: validateUsername, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }]
})

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  try {
    loading.value = true
    const valid = await formEl.validate()
    if (valid) {
      const success = await userStore.login(ruleForm.username, ruleForm.password)
      if (success) {
        await router.push('/')
      }
    }
  } finally {
    loading.value = false
  }
}

const resetForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.resetFields()
}
</script>