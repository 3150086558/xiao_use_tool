<template>
  <div class="register-page">
    <div class="register-container">
      <div class="register-header">
        <h1>🛠️ 注册账号</h1>
        <p>小肖的自用工具 - 免费注册</p>
      </div>
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="3-20位字母、数字、下划线"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="8-20位，含大小写字母和数字"
            prefix-icon="Lock"
            size="large"
            show-password
            @input="checkPasswordStrength"
          />
          <div v-if="form.password" class="password-strength">
            <div class="strength-bar">
              <div
                v-for="i in 4"
                :key="i"
                class="strength-segment"
                :class="strengthClass(i)"
              ></div>
            </div>
            <span class="strength-text">{{ strengthText }}</span>
          </div>
          <ul class="password-rules">
            <li :class="{ ok: hasLength }">
              <el-icon><Check v-if="hasLength" /><Close v-else /></el-icon>
              长度 8-20 位
            </li>
            <li :class="{ ok: hasLower }">
              <el-icon><Check v-if="hasLower" /><Close v-else /></el-icon>
              包含小写字母
            </li>
            <li :class="{ ok: hasUpper }">
              <el-icon><Check v-if="hasUpper" /><Close v-else /></el-icon>
              包含大写字母
            </li>
            <li :class="{ ok: hasNumber }">
              <el-icon><Check v-if="hasNumber" /><Close v-else /></el-icon>
              包含数字
            </li>
          </ul>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            style="width: 100%"
            @click="handleRegister"
          >
            注 册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const formRef = ref<FormInstance>()
const loading = ref(false)
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: '',
  confirm_password: '',
})

const hasLength = computed(() => form.password.length >= 8 && form.password.length <= 20)
const hasLower = computed(() => /[a-z]/.test(form.password))
const hasUpper = computed(() => /[A-Z]/.test(form.password))
const hasNumber = computed(() => /[0-9]/.test(form.password))

const strengthLevel = computed(() => {
  let level = 0
  if (hasLength.value) level++
  if (hasLower.value) level++
  if (hasUpper.value) level++
  if (hasNumber.value) level++
  return level
})

const strengthText = computed(() => {
  const texts = ['', '弱', '一般', '良好', '强']
  return texts[strengthLevel.value] || ''
})

function strengthClass(level: number): string {
  if (strengthLevel.value >= level) {
    if (strengthLevel.value <= 1) return 'weak'
    if (strengthLevel.value === 2) return 'medium'
    if (strengthLevel.value === 3) return 'good'
    return 'strong'
  }
  return ''
}

function checkPasswordStrength() {}

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== form.password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (!hasLength.value || !hasLower.value || !hasUpper.value || !hasNumber.value) {
          callback(new Error('密码需包含大小写字母和数字，长度 8-20 位'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function handleRegister() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authStore.register({
      username: form.username,
      password: form.password,
      confirm_password: form.confirm_password,
    })
    ElMessage.success('注册成功')
    router.push('/dashboard')
  } catch (e: any) {
    // 错误由拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.register-page {
  width: 100%;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-container {
  width: 440px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.register-header {
  text-align: center;
  margin-bottom: 24px;

  h1 {
    font-size: 24px;
    color: $text-primary;
    margin-bottom: 8px;
  }

  p {
    color: $text-secondary;
    font-size: 14px;
  }
}

.password-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;

  .strength-bar {
    display: flex;
    gap: 4px;
    flex: 1;

    .strength-segment {
      height: 4px;
      flex: 1;
      background: #eee;
      border-radius: 2px;
      transition: background 0.3s;

      &.weak { background: #f56c6c; }
      &.medium { background: #e6a23c; }
      &.good { background: #f0c78a; }
      &.strong { background: #67c23a; }
    }
  }

  .strength-text {
    font-size: 12px;
    color: $text-secondary;
    width: 30px;
  }
}

.password-rules {
  list-style: none;
  margin-top: 10px;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 12px;
  color: $text-secondary;

  li {
    display: flex;
    align-items: center;
    gap: 4px;

    &.ok {
      color: $success-color;
    }
  }
}

.register-footer {
  text-align: center;
  color: $text-secondary;
  font-size: 14px;
  margin-top: 20px;

  a {
    color: $primary-color;
    text-decoration: none;
  }
}
</style>
