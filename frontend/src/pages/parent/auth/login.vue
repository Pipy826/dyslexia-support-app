<template>
  <view class="page-container">
    <!-- Logo区域 -->
    <view class="logo-section">
      <view class="logo-icon">
        <text class="ph ph-plant"></text>
      </view>
      <view class="logo-title">读写能力智能支持</view>
      <view class="logo-subtitle">早发现 · 可解释 · 可干预</view>
    </view>

    <!-- 登录/注册方式切换标签 -->
    <view class="tabs-section">
      <view
        :class="['tab-item', { active: loginMode === 'code' }]"
        @click="switchLoginMode('code')"
      >
        <view class="tab-text">{{ isRegisterMode ? '手机号注册' : '验证码登录' }}</view>
        <view class="tab-line" v-if="loginMode === 'code'"></view>
      </view>
      <view
        :class="['tab-item', { active: loginMode === 'pwd' }]"
        @click="switchLoginMode('pwd')"
      >
        <view class="tab-text">{{ isRegisterMode ? '账号注册' : '密码登录' }}</view>
        <view class="tab-line" v-if="loginMode === 'pwd'"></view>
      </view>
    </view>

    <!-- 表单容器：验证码登录 -->
    <view class="form-section" v-if="!isRegisterMode && loginMode === 'code'">
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-phone"></text>
        </view>
        <input
          type="tel"
          v-model="formData.phone"
          placeholder="请输入手机号码"
          maxlength="11"
          class="form-input"
        />
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-shield-check"></text>
        </view>
        <input
          type="number"
          v-model="formData.code"
          placeholder="输入验证码"
          maxlength="6"
          class="form-input flex-1"
        />
        <view class="code-btn" @click="sendCode">获取验证码</view>
      </view>
    </view>

    <!-- 表单容器：密码登录 -->
    <view class="form-section" v-if="!isRegisterMode && loginMode === 'pwd'">
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-user"></text>
        </view>
        <input
          type="text"
          v-model="formData.account"
          placeholder="手机号 / 用户名"
          class="form-input"
        />
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-lock"></text>
        </view>
        <input
          :type="showPwd ? 'text' : 'password'"
          v-model="formData.password"
          placeholder="请输入登录密码"
          class="form-input"
        />
        <view class="eye-icon" @click="showPwd = !showPwd">
          <text :class="showPwd ? 'ph ph-eye' : 'ph ph-eye-slash'"></text>
        </view>
      </view>
    </view>

    <!-- 表单容器：注册手机号 -->
    <view class="form-section" v-if="isRegisterMode && loginMode === 'code'">
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-phone"></text>
        </view>
        <input
          type="tel"
          v-model="regData.phone"
          placeholder="请输入手机号码"
          maxlength="11"
          class="form-input"
        />
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-shield-check"></text>
        </view>
        <input
          type="number"
          v-model="regData.code"
          placeholder="输入验证码"
          maxlength="6"
          class="form-input flex-1"
        />
        <view class="code-btn" @click="sendCode">获取验证码</view>
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-lock"></text>
        </view>
        <input
          :type="showPwd ? 'text' : 'password'"
          v-model="regData.password"
          placeholder="请设置登录密码"
          class="form-input"
        />
      </view>
    </view>

    <!-- 表单容器：注册账号 -->
    <view class="form-section" v-if="isRegisterMode && loginMode === 'pwd'">
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-user"></text>
        </view>
        <input
          type="text"
          v-model="regData.username"
          placeholder="请设置用户名 (作为登录账号)"
          class="form-input"
        />
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-lock"></text>
        </view>
        <input
          :type="showPwd ? 'text' : 'password'"
          v-model="regData.password"
          placeholder="请设置登录密码"
          class="form-input"
        />
      </view>
      <view class="input-item">
        <view class="input-icon">
          <text class="ph ph-check-circle"></text>
        </view>
        <input
          :type="showPwd ? 'text' : 'password'"
          v-model="regData.passwordConfirm"
          placeholder="请再次输入密码确认"
          class="form-input"
        />
      </view>
    </view>

    <!-- 协议勾选 -->
    <view class="agreement-section">
      <view class="agree-checkbox" :class="{ checked: isAgreed }" @click="toggleAgreement">
        <text class="ph ph-check" v-if="isAgreed"></text>
      </view>
      <view class="agree-text">
        <template v-if="!isRegisterMode">
          我已阅读并同意 <text class="link">《用户服务协议》</text> 和 <text class="link">《隐私政策》</text>，未注册手机号将自动创建账号。
        </template>
        <template v-else>
          我已阅读并同意 <text class="link">《用户服务协议》</text> 和 <text class="link">《隐私政策》</text>
        </template>
      </view>
    </view>

    <!-- 主按钮 -->
    <button class="main-btn" @click="handleAuthAction">
      {{ isRegisterMode ? '注 册' : '登 录' }}
    </button>

    <!-- 切换入口 -->
    <view class="switch-section">
      <text class="switch-text" v-if="!isRegisterMode">还没有账号？</text>
      <text class="switch-text" v-else>已有账号？</text>
      <text class="switch-link" @click="toggleRegisterMode">{{ isRegisterMode ? '去登录' : '立即注册' }}</text>
    </view>

    <!-- 第三方快捷登录 -->
    <view class="third-party-section" v-if="!isRegisterMode">
      <view class="divider">
        <view class="divider-line"></view>
        <view class="divider-text">其他方式登录</view>
        <view class="divider-line"></view>
      </view>
      <view class="wechat-btn">
        <text class="ph ph-chat-circle"></text>
      </view>
    </view>

    <!-- Toast提示 -->
    <view class="toast" :class="{ show: toastVisible }">{{ toastMessage }}</view>
  </view>
</template>

<script>
import { login, loginByCode, register, handleLoginSuccess, sendVerifyCode } from '../../../api/auth.js'

export default {
  data() {
    return {
      loginMode: 'code', // 'code' | 'pwd'
      isRegisterMode: false,
      isAgreed: false,
      showPwd: false,
      toastVisible: false,
      toastMessage: '',
      formData: {
        phone: '',
        code: '',
        account: '',
        password: ''
      },
      regData: {
        phone: '',
        code: '',
        username: '',
        password: '',
        passwordConfirm: ''
      }
    }
  },
  methods: {
    switchLoginMode(mode) {
      this.loginMode = mode
    },
    toggleRegisterMode() {
      this.isRegisterMode = !this.isRegisterMode
      this.loginMode = 'code'
    },
    toggleAgreement() {
      this.isAgreed = !this.isAgreed
    },
    showToastMsg(msg) {
      this.toastMessage = msg
      this.toastVisible = true
      setTimeout(() => {
        this.toastVisible = false
      }, 2000)
    },
    async sendCode() {
      const phone = this.isRegisterMode ? this.regData.phone : this.formData.phone
      if (!phone || phone.length !== 11) {
        this.showToastMsg('请输入正确的11位手机号')
        return
      }
      try {
        await sendVerifyCode(phone)
        this.showToastMsg('验证码已发送')
      } catch (e) {
        this.showToastMsg('发送失败，请重试')
      }
    },
    async handleAuthAction() {
      if (!this.isAgreed) {
        this.showToastMsg('请先勾选同意用户服务协议')
        return
      }

      if (this.isRegisterMode) {
        // 注册逻辑
        if (this.loginMode === 'code') {
          if (!this.regData.phone || this.regData.phone.length !== 11) {
            this.showToastMsg('请输入正确的11位手机号')
            return
          }
          if (!this.regData.code) {
            this.showToastMsg('请输入验证码')
            return
          }
          if (!this.regData.password) {
            this.showToastMsg('请设置密码')
            return
          }
        } else {
          if (!this.regData.username || this.regData.username.length < 4) {
            this.showToastMsg('请输入至少4位的用户名')
            return
          }
          if (!this.regData.password) {
            this.showToastMsg('请设置密码')
            return
          }
          if (this.regData.password !== this.regData.passwordConfirm) {
            this.showToastMsg('两次输入的密码不一致')
            return
          }
        }

        try {
          await register({
            username: this.regData.username || this.regData.phone,
            password: this.regData.password,
            phone: this.regData.phone,
            code: this.regData.code
          })
          uni.showToast({ title: '注册成功', icon: 'success' })
          setTimeout(() => {
            uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
          }, 1000)
        } catch (e) {
          this.showToastMsg('注册失败，请重试')
        }
      } else {
        // 登录逻辑
        if (this.loginMode === 'code') {
          if (!this.formData.phone || this.formData.phone.length !== 11) {
            this.showToastMsg('请输入正确的11位手机号')
            return
          }
          if (!this.formData.code) {
            this.showToastMsg('请输入验证码')
            return
          }
        } else {
          if (!this.formData.account) {
            this.showToastMsg('请输入账号')
            return
          }
          if (!this.formData.password) {
            this.showToastMsg('请输入密码')
            return
          }
        }

        try {
          let res
          if (this.loginMode === 'code') {
            res = await loginByCode(this.formData.phone, this.formData.code)
          } else {
            res = await login({
              username: this.formData.account,
              password: this.formData.password
            })
          }
          handleLoginSuccess(res)
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/parent/home/index' })
          }, 1000)
        } catch (e) {
          this.showToastMsg('登录失败，请检查账号或验证码')
        }
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 128rpx 64rpx 80rpx;
}

/* Logo区域 */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.logo-icon {
  width: 160rpx;
  height: 160rpx;
  border-radius: 56rpx;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
  border: 1rpx solid #DBEAFE;
}

.logo-icon .ph {
  font-size: 64rpx;
  color: #3B82F6;
}

.logo-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.logo-subtitle {
  font-size: 28rpx;
  color: #6B7280;
}

/* 标签切换 */
.tabs-section {
  display: flex;
  gap: 48rpx;
  margin-bottom: 48rpx;
  padding: 0 16rpx;
}

.tab-item {
  position: relative;
  cursor: pointer;
}

.tab-text {
  font-size: 34rpx;
  font-weight: 700;
  color: #9CA3AF;
  transition: color 0.3s;
}

.tab-item.active .tab-text {
  color: #1F2937;
}

.tab-line {
  position: absolute;
  bottom: -12rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 32rpx;
  height: 6rpx;
  background: #3B82F6;
  border-radius: 3rpx;
}

/* 表单 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  margin-bottom: 48rpx;
}

.input-item {
  position: relative;
  display: flex;
  align-items: center;
  background: #F9FAFB;
  border: 2rpx solid #F3F4F6;
  border-radius: 32rpx;
  padding: 32rpx;
  padding-left: 96rpx;
  transition: all 0.3s;
}

.input-item:focus-within {
  border-color: #3B82F6;
  box-shadow: 0 0 0 6rpx rgba(59, 130, 246, 0.1);
}

.input-icon {
  position: absolute;
  left: 32rpx;
  top: 50%;
  transform: translateY(-50%);
}

.input-icon .ph {
  font-size: 36rpx;
  color: #9CA3AF;
}

.form-input {
  flex: 1;
  font-size: 28rpx;
  color: #1F2937;
  background: transparent;
}

.form-input::placeholder {
  color: #9CA3AF;
}

.code-btn {
  padding: 16rpx 32rpx;
  background: #EFF6FF;
  color: #3B82F6;
  border-radius: 32rpx;
  font-size: 22rpx;
  font-weight: 700;
  border: 1rpx solid #DBEAFE;
  flex-shrink: 0;
}

.eye-icon {
  position: absolute;
  right: 32rpx;
  top: 50%;
  transform: translateY(-50%);
}

.eye-icon .ph {
  font-size: 36rpx;
  color: #9CA3AF;
}

/* 协议 */
.agreement-section {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 48rpx;
  padding: 0 8rpx;
}

.agree-checkbox {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  border: 4rpx solid #D1D5DB;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4rpx;
  transition: all 0.3s;
}

.agree-checkbox.checked {
  background: #3B82F6;
  border-color: #3B82F6;
}

.agree-checkbox .ph {
  font-size: 18rpx;
  color: #FFFFFF;
}

.agree-text {
  font-size: 22rpx;
  color: #9CA3AF;
  line-height: 1.6;
}

.agree-text .link {
  color: #3B82F6;
}

/* 主按钮 */
.main-btn {
  width: 100%;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 32rpx;
  font-size: 32rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

/* 切换入口 */
.switch-section {
  text-align: center;
  margin-top: 48rpx;
}

.switch-text {
  font-size: 26rpx;
  color: #6B7280;
}

.switch-link {
  font-size: 26rpx;
  font-weight: 700;
  color: #3B82F6;
}

/* 第三方登录 */
.third-party-section {
  margin-top: 96rpx;
}

.divider {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 48rpx;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background: #F3F4F6;
}

.divider-text {
  font-size: 22rpx;
  color: #9CA3AF;
}

.wechat-btn {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #ECFDF5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.wechat-btn .ph {
  font-size: 48rpx;
  color: #10B981;
}

/* Toast */
.toast {
  position: fixed;
  top: 80rpx;
  left: 50%;
  transform: translateX(-50%) translateY(-20rpx);
  background: #374151;
  color: #FFFFFF;
  padding: 24rpx 48rpx;
  border-radius: 50rpx;
  font-size: 26rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition: all 0.3s;
  pointer-events: none;
  z-index: 9999;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
