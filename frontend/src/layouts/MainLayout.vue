<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapsed ? '64px' : '240px'" class="sidebar">
      <div class="logo">
        <span v-show="!isCollapsed">🛠️ 小肖工具箱</span>
        <span v-show="isCollapsed">🛠️</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapsed"
        :collapse-transition="false"
        background-color="#1f2937"
        text-color="#a1a1aa"
        active-text-color="#ffffff"
        router
        @select="handleMenuSelect"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        <template v-for="menu in menus" :key="menu.id">
          <el-sub-menu v-if="menu.children && menu.children.length > 0" :index="`menu-${menu.id}`">
            <template #title>
              <el-icon><component :is="getIcon(menu.name)" /></el-icon>
              <span>{{ menu.name }}</span>
            </template>
            <el-menu-item
              v-for="child in menu.children"
              :key="child.id"
              :index="getRoutePath(child.name)"
            >
              <el-icon><component :is="getIcon(child.name)" /></el-icon>
              <span>{{ child.name }}</span>
            </el-menu-item>
          </el-sub-menu>
        </template>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="toggleCollapse">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>{{ username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="change-password">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <ChangePasswordDialog
      v-model:visible="changePwdVisible"
      @success="handleChangePwdSuccess"
    />
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  HomeFilled,
  Fold,
  Expand,
  UserFilled,
  ArrowDown,
  Lock,
  SwitchButton,
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useMenuStore } from '@/stores/menu'
import ChangePasswordDialog from '@/components/ChangePasswordDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const menuStore = useMenuStore()

const changePwdVisible = ref(false)

const menus = computed(() => menuStore.menus)
const isCollapsed = computed(() => menuStore.isCollapsed)
const activeMenu = computed(() => route.path)
const username = computed(() => authStore.username)

const currentPageTitle = computed(() => {
  return (route.meta.title as string) || '首页'
})

function toggleCollapse() {
  menuStore.toggleCollapse()
}

function handleMenuSelect(index: string) {
  if (index.startsWith('menu-')) {
    return
  }
  router.push(index)
}

function handleCommand(command: string) {
  if (command === 'change-password') {
    changePwdVisible.value = true
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      authStore.doLogout()
      ElMessage.success('已退出登录')
    }).catch(() => {})
  }
}

function handleChangePwdSuccess() {
  changePwdVisible.value = false
}

function getIcon(name: string): string {
  const iconMap: Record<string, string> = {
    '财务管理': 'Wallet',
    '记账': 'Notebook',
    '统计报表': 'DataAnalysis',
    '日常工具': 'Tools',
    '待办事项': 'List',
    '备忘录': 'Document',
    '数据库查询': 'Coin',
    '系统管理': 'Setting',
    '用户管理': 'User',
  }
  return iconMap[name] || 'Menu'
}

function getRoutePath(name: string): string {
  const pathMap: Record<string, string> = {
    '记账': '/accounting',
    '统计报表': '/stats',
    '待办事项': '/todos',
    '备忘录': '/notes',
    '数据库查询': '/db-query',
    '用户管理': '/users',
  }
  return pathMap[name] || '/dashboard'
}

onMounted(() => {
  menuStore.fetchMenus().catch((e) => {
    ElMessage.error('加载菜单失败')
    console.error('菜单加载失败:', e)
  })
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #1f2937;
  transition: width 0.3s;
  overflow: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    border-bottom: 1px solid #374151;
  }

  :deep(.el-menu) {
    border-right: none;
  }
}

.header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #909399;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: #303133;
    }
  }
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
