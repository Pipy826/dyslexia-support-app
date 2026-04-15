<template>
  <view id="app">
    <slot />
  </view>
</template>

<script>
import './styles/common.scss'
import './styles/icons.scss'
import { getToken, getCurrentChild } from './utils/auth.js'

export default {
  onLaunch() {
    // 启动时检查登录状态，未登录跳转到登录页
    const token = getToken()
    if (!token) {
      uni.reLaunch({ url: '/pages/parent/auth/login' })
    }
  },
  onShow() {},
  onHide() {}
}
</script>

<style>
/* 全局样式已经在 common.scss 中定义 */
</style>
