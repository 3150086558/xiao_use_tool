<template>
  <div class="user-mgmt-page">
    <h2 class="page-title">用户管理</h2>

    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" size="small" @click="loadUsers">刷新</el-button>
        </div>
      </template>

      <el-table :data="users" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column label="角色" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.is_admin" type="danger" size="small">管理员</el-tag>
            <el-tag v-else size="small" type="info">普通用户</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180" />
        <el-table-column prop="record_count" label="记账数" width="100" align="center" />
        <el-table-column prop="todo_count" label="待办数" width="100" align="center" />
        <el-table-column prop="note_count" label="备忘录数" width="110" align="center" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="resetPassword(row)">重置密码</el-button>
            <el-button
              type="danger"
              link
              size="small"
              :disabled="row.is_admin"
              @click="deleteUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi, UserAdminData } from '@/api/users'
import { useAuthStore } from '@/stores/auth'

const users = ref<UserAdminData[]>([])
const loading = ref(false)
const authStore = useAuthStore()

async function loadUsers() {
  loading.value = true
  try {
    users.value = await userApi.list()
  } finally {
    loading.value = false
  }
}

async function resetPassword(row: UserAdminData) {
  try {
    const { value } = await ElMessageBox.prompt(
      `为用户 ${row.username} 重置密码`,
      '重置密码',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'password',
        inputPlaceholder: '请输入新密码',
        inputValidator: (val) => {
          if (!val || val.length < 8) return '密码至少 8 位'
          if (!/[a-z]/.test(val)) return '需包含小写字母'
          if (!/[A-Z]/.test(val)) return '需包含大写字母'
          if (!/[0-9]/.test(val)) return '需包含数字'
          return true
        },
      }
    )
    await userApi.resetPassword(row.id, value)
    ElMessage.success('密码重置成功')
  } catch {
    // 用户取消
  }
}

async function deleteUser(row: UserAdminData) {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？所有相关数据将被删除，不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'error',
      }
    )
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch {}
}

onMounted(() => {
  loadUsers()
})
</script>

<style lang="scss" scoped>
.user-mgmt-page {
  .page-title {
    margin-bottom: 20px;
    font-size: 22px;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-weight: bold;
  }
}
</style>
