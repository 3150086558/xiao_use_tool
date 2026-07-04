import request from './request'

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
  confirm_password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    is_admin: boolean
  }
}

export interface UserInfo {
  id: number
  username: string
  is_admin: boolean
  created_at: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
  confirm_password: string
}

export const authApi = {
  login(data: LoginRequest) {
    return request.post<any, LoginResponse>('/auth/login', data)
  },

  register(data: RegisterRequest) {
    return request.post<any, LoginResponse>('/auth/register', data)
  },

  logout(refreshToken: string) {
    return request.post('/auth/logout', { refresh_token: refreshToken })
  },

  refreshToken(refreshToken: string) {
    return request.post<any, LoginResponse>('/auth/refresh', { refresh_token: refreshToken })
  },

  getMe() {
    return request.get<any, UserInfo>('/auth/me')
  },

  changePassword(data: ChangePasswordRequest) {
    return request.post('/auth/change-password', data)
  },
}
