<template>
  <view class="register-container">
    <view class="form-section">
      <view class="title">创建账号</view>

      <input
        class="input"
        type="text"
        v-model="formData.username"
        placeholder="请输入用户名"
      />
      <input
        class="input"
        type="password"
        v-model="formData.password"
        placeholder="请输入密码"
      />
      <input
        class="input"
        type="text"
        v-model="formData.phone"
        placeholder="请输入手机号（可选）"
      />

      <button class="btn btn-primary register-btn" @click="handleRegister" :loading="loading">
        注册
      </button>

      <view class="link-section">
        <text @click="goToLogin">已有账号？立即登录</text>
      </view>
    </view>
  </view>
</template>

<script>
import { register, handleLoginSuccess } from '../../../api/auth.js'

export default {
  data() {
    return {
      formData: {
        username: '',
        password: '',
        phone: ''
      },
      loading: false
    }
  },
  methods: {
    async handleRegister() {
      if (!this.formData.username || !this.formData.password) {
        uni.showToast({ title: '请填写用户名和密码', icon: 'none' })
        return
      }

      if (this.formData.password.length < 6) {
        uni.showToast({ title: '密码至少6位', icon: 'none' })
        return
      }

      this.loading = true
      try {
        const res = await register(this.formData)
        handleLoginSuccess(res)
        uni.showToast({ title: '注册成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/parent/home/index' })
        }, 1000)
      } catch (e) {
        console.error('注册失败', e)
      } finally {
        this.loading = false
      }
    },
    goToLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  padding: 80rpx 48rpx;
  background: linear-gradient(180deg, #EFF6FF 0%, #FFFFFF 100%);
}

.form-section {
  background: #fff;
  border-radius: 32rpx;
  padding: 48rpx;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #111827;
  margin-bottom: 48rpx;
  text-align: center;
}

.input {
  width: 100%;
  padding: 28rpx 32rpx;
  border: 2rpx solid #E5E7EB;
  border-radius: 16rpx;
  font-size: 28rpx;
  margin-bottom: 24rpx;
  background: #F9FAFB;
}

.register-btn {
  width: 100%;
  padding: 28rpx;
  font-size: 32rpx;
  margin-top: 24rpx;
}

.link-section {
  text-align: center;
  margin-top: 32rpx;
  color: #2563EB;
  font-size: 28rpx;
}
</style>
