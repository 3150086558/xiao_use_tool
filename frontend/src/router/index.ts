import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import NProgress from 'nprogress'
import { useAuthStore } from '@/stores/auth'

NProgress.configure({ showSpinner: false })

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/Login.vue'),
    meta: { requiresAuth: false, title: '登录' },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/login/Register.vue'),
    meta: { requiresAuth: false, title: '注册' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/home/Dashboard.vue'),
        meta: { title: '首页', icon: 'HomeFilled' },
      },
      {
        path: 'accounting',
        name: 'Accounting',
        component: () => import('@/views/accounting/Accounting.vue'),
        meta: { title: '记账', icon: 'Notebook' },
      },
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('@/views/accounting/Stats.vue'),
        meta: { title: '统计报表', icon: 'DataAnalysis' },
      },
      {
        path: 'todos',
        name: 'Todos',
        component: () => import('@/views/todo/TodoList.vue'),
        meta: { title: '待办事项', icon: 'List' },
      },
      {
        path: 'notes',
        name: 'Notes',
        component: () => import('@/views/notes/Notes.vue'),
        meta: { title: '备忘录', icon: 'Document' },
      },
      {
        path: 'db-query',
        name: 'DbQuery',
        component: () => import('@/views/db-query/DbQuery.vue'),
        meta: { title: '数据库查询', icon: 'Coin' },
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/system/UserMgmt.vue'),
        meta: { title: '用户管理', icon: 'User', requiresAdmin: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
    return
  }

  if ((to.name === 'Login' || to.name === 'Register') && authStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

router.afterEach(() => {
  NProgress.done()
})

export default router
