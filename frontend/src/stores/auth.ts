import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, LoginRequest, RegisterRequest, UserInfo, LoginResponse } from '@/api/auth'
import router from '@/router'

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user_info'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const refreshToken = ref<string>(localStorage.getItem(REFRESH_TOKEN_KEY) || '')
  const userInfo = ref<UserInfo | null>(
    localStorage.getItem(USER_KEY) ? JSON.parse(localStorage.getItem(USER_KEY)!) : null
  )

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.is_admin || false)
  const username = computed(() => userInfo.value?.username || '')

  function setToken(access: string, refresh: string) {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem(TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  function setUserInfo(user: UserInfo | LoginResponse['user']) {
    userInfo.value = user as UserInfo
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }

  async function login(data: LoginRequest) {
    const result = await authApi.login(data)
    setToken(result.access_token, result.refresh_token)
    setUserInfo(result.user)
    return result
  }

  async function register(data: RegisterRequest) {
    const result = await authApi.register(data)
    setToken(result.access_token, result.refresh_token)
    setUserInfo(result.user)
    return result
  }

  async function refreshTokenAction() {
    const result = await authApi.refreshToken(refreshToken.value)
    setToken(result.access_token, result.refresh_token)
    setUserInfo(result.user)
    return result
  }

  async function fetchUserInfo() {
    const user = await authApi.getMe()
    setUserInfo(user)
    return user
  }

  function logout() {
    if (refreshToken.value) {
      authApi.logout(refreshToken.value).catch(() => {})
    }
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  function doLogout() {
    logout()
    router.push('/login')
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    isAdmin,
    username,
    login,
    register,
    refreshTokenAction,
    fetchUserInfo,
    logout,
    doLogout,
  }
})
