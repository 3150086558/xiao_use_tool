import request from './request'

export interface NoteData {
  id?: number
  title: string
  content: string
  created_at?: string
  updated_at?: string
}

export const noteApi = {
  list(keyword?: string) {
    return request.get<any, NoteData[]>('/notes', { params: { keyword } })
  },

  create(data: { title: string; content?: string }) {
    return request.post<any, NoteData>('/notes', data)
  },

  update(id: number, data: Partial<NoteData>) {
    return request.put<any, NoteData>(`/notes/${id}`, data)
  },

  delete(id: number) {
    return request.delete(`/notes/${id}`)
  },
}
