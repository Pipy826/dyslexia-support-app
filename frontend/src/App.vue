<template>
  <view id="app">
    <slot />
  </view>
</template>

<script>
import './styles/common.scss'
import './styles/icons.scss'
import { getToken, clearAuth } from './utils/auth.js'
import { getCurrentUser } from './api/auth.js'

export default {
  onLaunch() {
    const token = getToken()
    if (!token) {
      uni.reLaunch({ url: '/pages/parent/auth/login' })
      return
    }
    // 验证 token 是否仍然有效（静默请求，不弹 toast）
    getCurrentUser().catch(() => {
      // 401 时 request 拦截器会自动清除认证并跳转登录
    })
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
/* 全局样式已经在 common.scss 中定义 */
</style>
