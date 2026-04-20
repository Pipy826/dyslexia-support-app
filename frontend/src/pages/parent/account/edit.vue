<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">账号设置</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 修改用户名 -->
      <view class="section-title">基本信息</view>
      <view class="form-card">
        <view class="form-row">
          <view class="form-label">用户名</view>
          <view class="form-input-wrap" v-if="editingUsername">
            <input class="form-input" v-model="newUsername" placeholder="请输入新用户名" maxlength="20" />
            <view class="form-actions">
              <view class="action-cancel" @click="editingUsername = false; newUsername = user.username">取消</view>
              <view class="action-save" @click="saveUsername">保存</view>
            </view>
          </view>
          <view class="form-val-row" v-else @click="editingUsername = true; newUsername = user.username">
            <view class="form-val">{{ user.username }}</view>
            <text class="ph ph-pencil edit-icon"></text>
          </view>
        </view>
        <view class="form-row last">
          <view class="form-label">手机号</view>
          <view class="form-val-row" @click="showPhoneModal = true">
            <view class="form-val">{{ maskPhone(user.phone) }}</view>
            <text class="ph ph-pencil edit-icon"></text>
          </view>
        </view>
      </view>

      <!-- 修改密码 -->
      <view class="section-title">安全设置</view>
      <view class="form-card">
        <view class="form-row last" @click="showPwdModal = true">
          <view class="form-label">登录密码</view>
          <view class="form-val-row">
            <view class="form-val">••••••••</view>
            <text class="ph ph-pencil edit-icon"></text>
          </view>
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <!-- 修改手机号弹窗 -->
    <view class="modal-overlay" v-if="showPhoneModal" @click.self="showPhoneModal = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-title">修改手机号</view>
        <view class="modal-input-wrap">
          <text class="ph ph-phone modal-icon"></text>
          <input class="modal-input" v-model="newPhone" type="tel" placeholder="请输入新手机号" maxlength="11" />
        </view>
        <view class="modal-input-wrap">
          <text class="ph ph-shield-check modal-icon"></text>
          <input class="modal-input" v-model="phoneCode" type="number" placeholder="验证码" maxlength="6" />
          <view class="code-btn" @click="sendPhoneCode" :class="{ disabled: codeCooldown > 0 }">
            {{ codeCooldown > 0 ? codeCooldown + 's' : '获取验证码' }}
          </view>
        </view>
        <button class="modal-btn" @click="savePhone" :disabled="!newPhone || !phoneCode">保存修改</button>
        <button class="modal-cancel" @click="showPhoneModal = false">取消</button>
      </view>
    </view>

    <!-- 修改密码弹窗 -->
    <view class="modal-overlay" v-if="showPwdModal" @click.self="showPwdModal = false">
      <view class="modal-sheet" @click.stop>
        <view class="modal-title">修改密码</view>
        <view class="modal-input-wrap">
          <text class="ph ph-lock modal-icon"></text>
          <input class="modal-input" :type="showOldPwd ? 'text' : 'password'" v-model="oldPwd" placeholder="请输入原密码" />
          <view class="eye-btn" @click="showOldPwd = !showOldPwd">
            <text :class="showOldPwd ? 'ph ph-eye' : 'ph ph-eye-slash'"></text>
          </view>
        </view>
        <view class="modal-input-wrap">
          <text class="ph ph-lock-key modal-icon"></text>
          <input class="modal-input" :type="showNewPwd ? 'text' : 'password'" v-model="newPwd" placeholder="请输入新密码（至少6位）" />
          <view class="eye-btn" @click="showNewPwd = !showNewPwd">
            <text :class="showNewPwd ? 'ph ph-eye' : 'ph ph-eye-slash'"></text>
          </view>
        </view>
        <view class="modal-input-wrap">
          <text class="ph ph-check-circle modal-icon"></text>
          <input class="modal-input" :type="showNewPwd ? 'text' : 'password'" v-model="confirmPwd" placeholder="再次输入新密码" />
        </view>
        <button class="modal-btn" @click="savePassword" :disabled="!oldPwd || !newPwd || !confirmPwd">保存修改</button>
        <button class="modal-cancel" @click="showPwdModal = false">取消</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getUser, setUser } from '../../../utils/auth.js'
import { post, put } from '../../../api/index.js'
import { sendVerifyCode } from '../../../api/auth.js'

export default {
  data() {
    return {
      user: {},
      editingUsername: false,
      newUsername: '',
      showPhoneModal: false,
      newPhone: '',
      phoneCode: '',
      codeCooldown: 0,
      showPwdModal: false,
      oldPwd: '',
      newPwd: '',
      confirmPwd: '',
      showOldPwd: false,
      showNewPwd: false,
    }
  },
  onLoad() {
    this.user = getUser() || {}
  },
  methods: {
    maskPhone(phone) {
      if (!phone) return '未绑定'
      return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    },
    async saveUsername() {
      if (!this.newUsername.trim() || this.newUsername.length < 2) {
        uni.showToast({ title: '用户名至少2个字符', icon: 'none' }); return
      }
      try {
        const res = await put('/api/auth/profile', { username: this.newUsername })
        this.user = { ...this.user, username: res.username }
        setUser(this.user)
        this.editingUsername = false
        uni.showToast({ title: '用户名已更新', icon: 'success' })
      } catch (e) {
        // 错误已由 request 统一处理
      }
    },
    async sendPhoneCode() {
      if (!this.newPhone || this.newPhone.length !== 11) {
        uni.showToast({ title: '请输入正确的手机号', icon: 'none' }); return
      }
      if (this.codeCooldown > 0) return
      try {
        await sendVerifyCode(this.newPhone)
        uni.showToast({ title: '验证码已发送', icon: 'none' })
        this.codeCooldown = 60
        const timer = setInterval(() => {
          this.codeCooldown--
          if (this.codeCooldown <= 0) clearInterval(timer)
        }, 1000)
      } catch (e) {}
    },
    async savePhone() {
      if (!this.newPhone || !this.phoneCode) return
      try {
        const res = await put('/api/auth/profile', { phone: this.newPhone, phone_code: this.phoneCode })
        this.user = { ...this.user, phone: res.phone }
        setUser(this.user)
        this.showPhoneModal = false
        this.newPhone = ''
        this.phoneCode = ''
        uni.showToast({ title: '手机号已更新', icon: 'success' })
      } catch (e) {}
    },
    async savePassword() {
      if (this.newPwd.length < 6) {
        uni.showToast({ title: '新密码至少6位', icon: 'none' }); return
      }
      if (this.newPwd !== this.confirmPwd) {
        uni.showToast({ title: '两次密码不一致', icon: 'none' }); return
      }
      try {
        await post('/api/auth/change-password', { old_password: this.oldPwd, new_password: this.newPwd })
        this.showPwdModal = false
        this.oldPwd = ''; this.newPwd = ''; this.confirmPwd = ''
        uni.showToast({ title: '密码修改成功', icon: 'success' })
      } catch (e) {}
    },
    goBack() { uni.navigateBack() },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center; box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }
.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }
.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; }
.form-card { background: #FFFFFF; border-radius: 24rpx; overflow: hidden; margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); }
.form-row { padding: 24rpx 28rpx; border-bottom: 1rpx solid #F5F5F5; }
.form-row.last { border-bottom: none; }
.form-label { font-size: 22rpx; color: #A0AEC0; font-weight: 600; margin-bottom: 8rpx; }
.form-val-row { display: flex; align-items: center; justify-content: space-between; }
.form-val { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.edit-icon { font-size: 26rpx; color: #4F9EF8; }
.form-input-wrap { display: flex; align-items: center; background: #F8FAFF; border: 2rpx solid #E5E7EB; border-radius: 16rpx; padding: 16rpx 20rpx; margin-top: 8rpx; }
.form-input { flex: 1; font-size: 28rpx; color: #2D3748; background: transparent; }
.form-actions { display: flex; gap: 16rpx; margin-top: 12rpx; }
.action-cancel { font-size: 24rpx; color: #A0AEC0; font-weight: 600; padding: 8rpx 20rpx; }
.action-save { font-size: 24rpx; color: #4F9EF8; font-weight: 700; padding: 8rpx 20rpx; background: rgba(79,158,248,0.1); border-radius: 10rpx; }

/* 弹窗 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.4); z-index: 9999; display: flex; align-items: flex-end; }
.modal-sheet { background: #FFFFFF; width: 100%; border-radius: 32rpx 32rpx 0 0; padding: 32rpx; padding-bottom: calc(32rpx + env(safe-area-inset-bottom)); }
.modal-title { font-size: 30rpx; font-weight: 700; color: #2D3748; margin-bottom: 28rpx; text-align: center; }
.modal-input-wrap { display: flex; align-items: center; background: #F8FAFF; border: 2rpx solid #E5E7EB; border-radius: 16rpx; padding: 20rpx 24rpx; margin-bottom: 16rpx; }
.modal-icon { font-size: 30rpx; color: #A0AEC0; margin-right: 12rpx; flex-shrink: 0; }
.modal-input { flex: 1; font-size: 28rpx; color: #2D3748; background: transparent; }
.code-btn { font-size: 22rpx; font-weight: 700; color: #4F9EF8; background: rgba(79,158,248,0.1); padding: 8rpx 16rpx; border-radius: 10rpx; flex-shrink: 0; }
.code-btn.disabled { color: #A0AEC0; background: #F5F5F5; }
.eye-btn .ph { font-size: 28rpx; color: #A0AEC0; }
.modal-btn { width: 100%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700; margin-bottom: 16rpx; }
.modal-cancel { width: 100%; background: #F5F5F5; color: #718096; border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700; }
</style>
