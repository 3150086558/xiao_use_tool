import request from './request'

export interface DbConnectionData {
  id?: number
  user_id?: number
  name: string
  db_type: string
  host: string
  port: number
  username: string
  password: string
  database: string
  sqlite_path: string
  created_at?: string
  updated_at?: string
}

export interface DbQueryResult {
  columns?: string[]
  rows?: any[]
  count?: number
  tables?: string[]
  table?: string
  columns_info?: { name: string; type: string; nullable: boolean; default: string }[]
  ok?: boolean
  message?: string
}

export const dbQueryApi = {
  listConnections() {
    return request.get<any, DbConnectionData[]>('/db-query/connections')
  },

  createConnection(data: DbConnectionData) {
    return request.post<any, DbConnectionData>('/db-query/connections', data)
  },

  updateConnection(id: number, data: Partial<DbConnectionData>) {
    return request.put<any, DbConnectionData>(`/db-query/connections/${id}`, data)
  },

  deleteConnection(id: number) {
    return request.delete(`/db-query/connections/${id}`)
  },

  query(action: string, config: DbConnectionData, table?: string, sql?: string) {
    return request.post<any, DbQueryResult>(`/db-query/${action}`, {
      action,
      config,
      table,
      sql,
    })
  },
}
