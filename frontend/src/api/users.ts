import request from './request'

export interface UserAdminData {
  id: number
  username: string
  is_admin: boolean
  created_at: string
  record_count: number
  todo_count: number
  note_count: number
}

export const userApi = {
  list() {
    return request.get<any, UserAdminData[]>('/users')
  },

  delete(id: number) {
    return request.delete(`/users/${id}`)
  },

  resetPassword(id: number, newPassword: string) {
    return request.post(`/users/${id}/reset-password`, { new_password: newPassword })
  },
}
