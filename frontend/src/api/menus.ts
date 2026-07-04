import request from './request'

export interface MenuItem {
  id: number
  parent_id: number
  name: string
  icon: string
  sort_order: number
  children?: MenuItem[]
}

export const menuApi = {
  getMenus() {
    return request.get<any, MenuItem[]>('/menus')
  },
}
