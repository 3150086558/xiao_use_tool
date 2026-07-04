import request from './request'

export interface TodoData {
  id?: number
  title: string
  completed: boolean
  priority: number
  due_date?: string
  completed_at?: string
  created_at?: string
  updated_at?: string
}

export const todoApi = {
  list() {
    return request.get<any, TodoData[]>('/todos')
  },

  create(data: { title: string; priority?: number; due_date?: string }) {
    return request.post<any, TodoData>('/todos', data)
  },

  update(id: number, data: Partial<TodoData>) {
    return request.put<any, TodoData>(`/todos/${id}`, data)
  },

  delete(id: number) {
    return request.delete(`/todos/${id}`)
  },
}
