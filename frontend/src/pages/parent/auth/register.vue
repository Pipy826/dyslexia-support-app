<template>
  <view></view>
</template>

<script>
// 注册功能已集成到 login.vue，此页面自动跳转
export default {
  onLoad() {
    uni.redirectTo({ url: '/pages/parent/auth/login' })
  }
}
</script>
