import { defineStore } from 'pinia'
import { ref } from 'vue'
import { menuApi, MenuItem } from '@/api/menus'

export const useMenuStore = defineStore('menu', () => {
  const menus = ref<MenuItem[]>([])
  const activeMenu = ref('')
  const isCollapsed = ref(false)

  async function fetchMenus() {
    const data = await menuApi.getMenus()
    menus.value = data
    return data
  }

  function setActiveMenu(key: string) {
    activeMenu.value = key
  }

  function toggleCollapse() {
    isCollapsed.value = !isCollapsed.value
  }

  function reset() {
    menus.value = []
    activeMenu.value = ''
  }

  return {
    menus,
    activeMenu,
    isCollapsed,
    fetchMenus,
    setActiveMenu,
    toggleCollapse,
    reset,
  }
})
