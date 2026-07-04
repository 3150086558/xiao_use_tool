import request from './request'

export interface RecordData {
  id?: number
  record_date: string
  type: 'income' | 'expense'
  category: string
  sub_category?: string
  amount: number
  account?: string
  note?: string
  created_at?: string
  updated_at?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface SummaryResponse {
  income: number
  expense: number
  balance: number
  categories: { type: string; category: string; total: number }[]
}

export interface StatsResponse {
  monthly_trend: { month: string; income: number; expense: number }[]
  category_pie: { type: string; category: string; total: number }[]
  top_categories: { type: string; category: string; total: number }[]
}

export const recordApi = {
  list(params: {
    month?: string
    type?: string
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<any, PaginatedResponse<RecordData>>('/records', { params })
  },

  create(data: RecordData) {
    return request.post<any, RecordData>('/records', data)
  },

  update(id: number, data: RecordData) {
    return request.put<any, RecordData>(`/records/${id}`, data)
  },

  delete(id: number) {
    return request.delete(`/records/${id}`)
  },

  clearAll() {
    return request.delete('/records')
  },

  summary(params: { month?: string; type?: string; keyword?: string }) {
    return request.get<any, SummaryResponse>('/records/summary', { params })
  },

  stats() {
    return request.get<any, StatsResponse>('/records/stats')
  },

  export(format: 'xlsx' | 'csv', params: { month?: string; type?: string; keyword?: string } = {}) {
    return request.get('/records/export', {
      params: { format, ...params },
      responseType: 'blob',
    })
  },

  importTemplate() {
    return request.get('/records/import-template', {
      responseType: 'blob',
    })
  },

  importExcel(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, { success: number; errors: string[]; total: number }>(
      '/records/import',
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
  },
}
