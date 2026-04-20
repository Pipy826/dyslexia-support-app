/**
 * 认证与用户状态 Store（Pinia）
 * 替代原来分散在各页面的 uni.getStorageSync('user_info') / uni.getStorageSync('current_child')
 *
 * 使用方式：
 *   import { useAuthStore } from '@/stores/auth.js'
 *   const auth = useAuthStore()
 *   auth.user / auth.currentChild / auth.token
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // ── State ──────────────────────────────────────────────────────────────────
  const token = ref(uni.getStorageSync('auth_token') || '')
  const user = ref(_parseJson(uni.getStorageSync('user_info')))
  const currentChild = ref(_parseJson(uni.getStorageSync('current_child')))
  const children = ref([])

  // ── Getters ────────────────────────────────────────────────────────────────
  const isLoggedIn = computed(() => !!token.value)
  const hasChild = computed(() => !!currentChild.value)

  // ── Actions ────────────────────────────────────────────────────────────────
  function setToken(t) {
    token.value = t
    uni.setStorageSync('auth_token', t)
  }

  function setUser(u) {
    user.value = u
    if (u) {
      uni.setStorageSync('user_info', JSON.stringify(u))
    } else {
      uni.removeStorageSync('user_info')
    }
  }

  function setCurrentChild(child) {
    currentChild.value = child
    if (child) {
      uni.setStorageSync('current_child', JSON.stringify(child))
    } else {
      uni.removeStorageSync('current_child')
    }
  }

  function setChildren(list) {
    children.value = list
    // 同步更新 currentChild（确保数据最新）
    if (currentChild.value && list.length > 0) {
      const updated = list.find(c => c.id === currentChild.value.id)
      if (updated) setCurrentChild(updated)
    } else if (list.length > 0 && !currentChild.value) {
      setCurrentChild(list[0])
    }
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    currentChild.value = null
    children.value = []
    uni.removeStorageSync('auth_token')
    uni.removeStorageSync('user_info')
    uni.removeStorageSync('current_child')
  }

  return {
    token, user, currentChild, children,
    isLoggedIn, hasChild,
    setToken, setUser, setCurrentChild, setChildren, clearAuth,
  }
})

function _parseJson(str) {
  if (!str) return null
  try {
    const parsed = typeof str === 'string' ? JSON.parse(str) : str
    return parsed && Object.keys(parsed).length > 0 ? parsed : null
  } catch {
    return null
  }
}
