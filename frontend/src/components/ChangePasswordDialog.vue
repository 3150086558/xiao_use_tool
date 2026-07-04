<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改密码"
    width="400px"
    :close-on-click-modal="false"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
      <el-form-item label="原密码" prop="old_password">
        <el-input v-model="form.old_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="form.new_password" type="password" show-password />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm_password">
        <el-input v-model="form.confirm_password" type="password" show-password />
      </el-form-item>
      <div class="tip">
        <el-icon><InfoFilled /></el-icon>
        密码长度 8-20 位，需包含大小写字母和数字
      </div>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { ElMessage, FormInstance } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'

const props = defineProps<{
  visible: boolean
}>()
const emit = defineEmits(['update:visible', 'success'])

const formRef = ref<FormInstance>()
const loading = ref(false)

const dialogVisible = ref(props.visible)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

watch(() => props.visible, (val) => {
  dialogVisible.value = val
  if (!val && formRef.value) {
    formRef.value.resetFields()
    form.old_password = ''
    form.new_password = ''
    form.confirm_password = ''
  }
})

watch(dialogVisible, (val) => {
  emit('update:visible', val)
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== form.new_password) {
    callback(new Error('两次密码输入不一致'))
  } else {
    callback()
  }
}

const rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value.length < 8 || value.length > 20) {
          callback(new Error('密码长度必须在 8-20 位之间'))
        } else if (!/[a-z]/.test(value)) {
          callback(new Error('密码必须包含小写字母'))
        } else if (!/[A-Z]/.test(value)) {
          callback(new Error('密码必须包含大写字母'))
        } else if (!/[0-9]/.test(value)) {
          callback(new Error('密码必须包含数字'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}

async function handleSubmit() {
  if (!formRef.value) return
  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    await authApi.changePassword({
      old_password: form.old_password,
      new_password: form.new_password,
      confirm_password: form.confirm_password,
    })
    ElMessage.success('密码修改成功')
    emit('success')
    dialogVisible.value = false
  } catch (e) {
    // 错误由拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.tip {
  font-size: 12px;
  color: $text-secondary;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: -4px;
}
</style>
