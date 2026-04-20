<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">联系客服</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 客服头像 -->
      <view class="avatar-section">
        <view class="cs-avatar">
          <text class="ph ph-headset"></text>
        </view>
        <view class="cs-name">悦读小灯塔客服</view>
        <view class="cs-status">
          <view class="status-dot" :class="isOnline ? 'online' : 'offline'"></view>
          {{ isOnline ? '在线中' : '当前离线（工作日 9:00-18:00）' }}
        </view>
      </view>

      <!-- 留言表单 -->
      <view class="form-card">
        <view class="form-title">发送留言</view>
        <view class="form-group">
          <view class="form-label">问题类型</view>
          <view class="type-grid">
            <view
              v-for="t in types"
              :key="t"
              :class="['type-option', { active: selectedType === t }]"
              @click="selectedType = t"
            >{{ t }}</view>
          </view>
        </view>
        <view class="form-group">
          <view class="form-label">问题描述</view>
          <textarea
            class="form-textarea"
            v-model="message"
            placeholder="请详细描述您遇到的问题，我们将尽快回复..."
            maxlength="500"
          />
          <view class="char-count">{{ message.length }}/500</view>
        </view>
        <view class="form-group">
          <view class="form-label">联系手机号（选填）</view>
          <view class="form-input-wrap">
            <input class="form-input" v-model="phone" type="tel" placeholder="方便我们回电联系" maxlength="11" />
          </view>
        </view>
        <button class="submit-btn" @click="submitMessage" :disabled="!message.trim() || submitting">
          <text class="ph ph-paper-plane-tilt" v-if="!submitting"></text>
          <text class="ph ph-circle-notch spin" v-else></text>
          {{ submitting ? '提交中...' : '提交留言' }}
        </button>
      </view>

      <!-- 其他联系方式 -->
      <view class="section-title">其他联系方式</view>
      <view class="contact-list">
        <view class="contact-item">
          <view class="contact-icon blue"><text class="ph ph-envelope"></text></view>
          <view class="contact-info">
            <view class="contact-label">邮件支持</view>
            <view class="contact-val">support@dyslexia-app.com</view>
          </view>
        </view>
        <view class="contact-item">
          <view class="contact-icon green"><text class="ph ph-clock"></text></view>
          <view class="contact-info">
            <view class="contact-label">服务时间</view>
            <view class="contact-val">工作日 9:00 - 18:00</view>
          </view>
        </view>
        <view class="contact-item last">
          <view class="contact-icon orange"><text class="ph ph-timer"></text></view>
          <view class="contact-info">
            <view class="contact-label">响应时间</view>
            <view class="contact-val">通常在1个工作日内回复</view>
          </view>
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      selectedType: '使用问题',
      message: '',
      phone: '',
      submitting: false,
      types: ['使用问题', '筛查报告', '账号问题', '数据安全', '其他'],
    }
  },
  computed: {
    isOnline() {
      const h = new Date().getHours()
      const day = new Date().getDay()
      return day >= 1 && day <= 5 && h >= 9 && h < 18
    },
  },
  methods: {
    async submitMessage() {
      if (!this.message.trim()) return
      this.submitting = true
      // 模拟提交（实际项目可接入工单系统）
      await new Promise(r => setTimeout(r, 1000))
      this.submitting = false
      uni.showModal({
        title: '留言已提交',
        content: '感谢您的反馈！我们将在1个工作日内回复您。',
        showCancel: false,
        confirmText: '好的',
        success: () => {
          this.message = ''
          this.phone = ''
          uni.navigateBack()
        }
      })
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

.avatar-section { display: flex; flex-direction: column; align-items: center; padding: 32rpx 0; }
.cs-avatar { width: 120rpx; height: 120rpx; border-radius: 50%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); display: flex; align-items: center; justify-content: center; margin-bottom: 16rpx; box-shadow: 0 4rpx 16rpx rgba(59,130,246,0.3); }
.cs-avatar .ph { font-size: 56rpx; color: #FFFFFF; }
.cs-name { font-size: 30rpx; font-weight: 700; color: #2D3748; margin-bottom: 8rpx; }
.cs-status { display: flex; align-items: center; gap: 8rpx; font-size: 22rpx; color: #718096; }
.status-dot { width: 12rpx; height: 12rpx; border-radius: 50%; }
.status-dot.online { background: #22C55E; }
.status-dot.offline { background: #A0AEC0; }

.form-card { background: #FFFFFF; border-radius: 24rpx; padding: 28rpx; margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); }
.form-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 24rpx; }
.form-group { margin-bottom: 24rpx; }
.form-label { font-size: 24rpx; font-weight: 700; color: #718096; margin-bottom: 12rpx; }
.type-grid { display: flex; flex-wrap: wrap; gap: 12rpx; }
.type-option { padding: 12rpx 24rpx; background: #F5F5F5; border-radius: 14rpx; font-size: 22rpx; color: #718096; font-weight: 600; transition: all 0.2s; }
.type-option.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); color: #4F9EF8; }
.form-textarea { width: 100%; background: #F8FAFF; border: 2rpx solid #E5E7EB; border-radius: 16rpx; padding: 20rpx; font-size: 26rpx; color: #2D3748; min-height: 160rpx; box-sizing: border-box; }
.char-count { font-size: 20rpx; color: #A0AEC0; text-align: right; margin-top: 8rpx; }
.form-input-wrap { background: #F8FAFF; border: 2rpx solid #E5E7EB; border-radius: 16rpx; padding: 20rpx; }
.form-input { width: 100%; font-size: 26rpx; color: #2D3748; background: transparent; }
.submit-btn { width: 100%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10rpx; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2); }
.submit-btn .ph { font-size: 28rpx; }
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; }
.contact-list { background: #FFFFFF; border-radius: 24rpx; overflow: hidden; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); }
.contact-item { display: flex; align-items: center; gap: 16rpx; padding: 24rpx 28rpx; border-bottom: 1rpx solid #F5F5F5; }
.contact-item.last { border-bottom: none; }
.contact-icon { width: 56rpx; height: 56rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.contact-icon .ph { font-size: 26rpx; }
.contact-icon.blue { background: rgba(79,158,248,0.1); }
.contact-icon.blue .ph { color: #4F9EF8; }
.contact-icon.green { background: rgba(34,197,94,0.1); }
.contact-icon.green .ph { color: #22C55E; }
.contact-icon.orange { background: rgba(245,127,23,0.1); }
.contact-icon.orange .ph { color: #F57F17; }
.contact-info { flex: 1; }
.contact-label { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }
.contact-val { font-size: 26rpx; font-weight: 700; color: #2D3748; margin-top: 4rpx; }
</style>
