<!-- 未完成 -->
<template>
  <div class="login-container">
    <div class="common-layout">
      <el-form ref="ruleFormRef" :model="ruleForm" status-icon :rules="rules" label-width="auto" class="login-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="ruleForm.username" type="text" autocomplete="username" />
        </el-form-item>
        <el-form-item label="Password" prop="pass">
          <el-input v-model="ruleForm.pass" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item label="Confirm" prop="checkPass">
          <el-input v-model="ruleForm.checkPass" type="password" autocomplete="current-password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm(ruleFormRef)">
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

const ruleFormRef = ref<FormInstance>()



const validatePass = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('Please input the password'))
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
    callback(new Error('Please input the password again'))
  } else if (value !== ruleForm.pass) {
    callback(new Error("Two inputs don't match!"))
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
  username: [{ required: true, message: 'Please input username', trigger: 'blur' }],
  pass: [{ validator: validatePass, trigger: 'blur' }],
  checkPass: [{ validator: validatePass2, trigger: 'blur' }],
})

const submitForm = (formEl: FormInstance | undefined) => {
  if (!formEl) return
  formEl.validate((valid) => {
    if (valid) {
      console.log('submit!')
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
