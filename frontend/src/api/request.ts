import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRefreshing = false
let refreshSubscribers: ((token: string) => void)[] = []

function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  async (error) => {
    const originalRequest = error.config
    const authStore = useAuthStore()

    if (error.response?.status === 401) {
      if (!originalRequest._retry && authStore.refreshToken) {
        originalRequest._retry = true

        if (isRefreshing) {
          return new Promise((resolve) => {
            subscribeTokenRefresh((token: string) => {
              originalRequest.headers.Authorization = `Bearer ${token}`
              resolve(service(originalRequest))
            })
          })
        }

        isRefreshing = true
        try {
          const result = await authStore.refreshTokenAction()
          onRefreshed(result.access_token)
          originalRequest.headers.Authorization = `Bearer ${result.access_token}`
          return service(originalRequest)
        } catch (e) {
          authStore.logout()
          ElMessageBox.confirm('登录已过期，请重新登录', '提示', {
            confirmButtonText: '去登录',
            cancelButtonText: '取消',
            type: 'warning',
          }).then(() => {
            router.push('/login')
          })
          return Promise.reject(e)
        } finally {
          isRefreshing = false
        }
      } else {
        authStore.logout()
        router.push('/login')
      }
    } else if (error.response?.status === 403) {
      ElMessage.error('没有权限访问该资源')
    } else if (error.response?.status === 400 || error.response?.status === 422) {
      const detail = error.response.data?.detail || error.response.data?.message || '请求错误'
      if (Array.isArray(detail)) {
        ElMessage.error(detail[0]?.msg || '请求参数错误')
      } else {
        ElMessage.error(detail)
      }
    } else if (error.response?.status === 500) {
      ElMessage.error('服务器错误，请稍后再试')
    } else if (!error.response) {
      ElMessage.error('网络错误，请检查网络连接')
    }

    return Promise.reject(error)
  }
)

export default service
