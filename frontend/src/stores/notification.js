/**
 * 通知状态 Store（Pinia）
 * 统一管理未读数量，避免各页面重复请求
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)

  async function fetchUnreadCount() {
    try {
      const { getUnreadCount } = await import('../api/notification.js')
      const res = await getUnreadCount()
      unreadCount.value = res.unread_count || 0
    } catch {
      // 静默失败
    }
  }

  function decrement(n = 1) {
    unreadCount.value = Math.max(0, unreadCount.value - n)
  }

  function reset() {
    unreadCount.value = 0
  }

  return { unreadCount, fetchUnreadCount, decrement, reset }
})
