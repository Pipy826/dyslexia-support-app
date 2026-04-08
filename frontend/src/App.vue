<template>
  <view id="app">
    <slot />
  </view>
</template>

<script>
import './styles/common.scss'
import './styles/icons.scss'

export default {
  onLaunch() {
    console.log('App Launch')
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  }
}
</script>

<style>
/* 全局样式已经在 common.scss 中定义 */
</style>
