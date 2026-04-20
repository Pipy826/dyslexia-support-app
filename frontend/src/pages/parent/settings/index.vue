<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">设置</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 账号与安全 -->
      <view class="section-title">账号与安全</view>
      <view class="menu-card">
        <view class="menu-item" @click="goToAccountEdit">
          <view class="menu-icon blue">
            <text class="ph ph-user-gear"></text>
          </view>
          <view class="menu-label">账号设置</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last">
          <view class="menu-icon green">
            <text class="ph ph-shield-check"></text>
          </view>
          <view class="menu-label">隐私与安全</view>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 通知设置 -->
      <view class="section-title">通知设置</view>
      <view class="menu-card">
        <view class="menu-item" @click="goToReminder">
          <view class="menu-icon orange">
            <text class="ph ph-bell"></text>
          </view>
          <view class="menu-label">任务与提醒设置</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last">
          <view class="menu-left">
            <view class="menu-icon purple">
              <text class="ph ph-chat-circle"></text>
            </view>
            <view class="menu-label">消息通知</view>
          </view>
          <view class="toggle" :class="{ on: notificationEnabled }" @click="toggleNotification">
            <view class="toggle-thumb"></view>
          </view>
        </view>
      </view>

      <!-- 显示设置 -->
      <view class="section-title">显示设置</view>
      <view class="menu-card">
        <view class="menu-item">
          <view class="menu-left">
            <view class="menu-icon yellow">
              <text class="ph ph-sun"></text>
            </view>
            <view class="menu-label">深色模式</view>
          </view>
          <view class="toggle" :class="{ on: darkMode }" @click="toggleDarkMode">
            <view class="toggle-thumb"></view>
          </view>
        </view>
        <view class="menu-item last">
          <view class="menu-icon pink">
            <text class="ph ph-text-aa"></text>
          </view>
          <view class="menu-label">字体大小</view>
          <view class="font-size-picker">
            <view
              v-for="size in ['小', '中', '大']"
              :key="size"
              :class="['size-option', { active: fontSize === size }]"
              @click="fontSize = size; saveSettings()"
            >{{ size }}</view>
          </view>
        </view>
      </view>

      <!-- 帮助与反馈 -->
      <view class="section-title">帮助与反馈</view>
      <view class="menu-card">
        <view class="menu-item" @click="goToHelp">
          <view class="menu-icon blue">
            <text class="ph ph-question"></text>
          </view>
          <view class="menu-label">帮助中心</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToContact">
          <view class="menu-icon green">
            <text class="ph ph-headset"></text>
          </view>
          <view class="menu-label">联系客服</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last" @click="goToFeedback">
          <view class="menu-icon orange">
            <text class="ph ph-chat-text"></text>
          </view>
          <view class="menu-label">意见反馈</view>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 关于 -->
      <view class="section-title">关于</view>
      <view class="menu-card">
        <view class="menu-item" @click="goToAbout">
          <view class="menu-icon gray">
            <text class="ph ph-info"></text>
          </view>
          <view class="menu-label">关于系统</view>
          <view class="version-badge">v1.0.0</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="checkUpdate">
          <view class="menu-icon purple">
            <text class="ph ph-download"></text>
          </view>
          <view class="menu-label">检查更新</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last" @click="clearCache">
          <view class="menu-icon red">
            <text class="ph ph-trash"></text>
          </view>
          <view class="menu-label">清除缓存</view>
          <view class="cache-size">约 12.5 MB</view>
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
      notificationEnabled: true,
      darkMode: false,
      fontSize: '中',
    }
  },
  onLoad() {
    this.loadSettings()
  },
  methods: {
    loadSettings() {
      const settings = uni.getStorageSync('app_settings') || {}
      this.notificationEnabled = settings.notificationEnabled ?? true
      this.darkMode = settings.darkMode ?? false
      this.fontSize = settings.fontSize ?? '中'
    },
    saveSettings() {
      uni.setStorageSync('app_settings', {
        notificationEnabled: this.notificationEnabled,
        darkMode: this.darkMode,
        fontSize: this.fontSize,
      })
      uni.showToast({ title: '设置已保存', icon: 'success', duration: 1000 })
    },
    toggleNotification() {
      this.notificationEnabled = !this.notificationEnabled
      this.saveSettings()
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode
      this.saveSettings()
      uni.showToast({ title: '深色模式开发中', icon: 'none' })
    },
    checkUpdate() {
      uni.showLoading({ title: '检查中...' })
      setTimeout(() => {
        uni.hideLoading()
        uni.showToast({ title: '已是最新版本', icon: 'success' })
      }, 1000)
    },
    clearCache() {
      uni.showModal({
        title: '清除缓存',
        content: '确定要清除缓存吗？这不会删除您的账号数据。',
        success: (res) => {
          if (res.confirm) {
            uni.showLoading({ title: '清除中...' })
            setTimeout(() => {
              uni.hideLoading()
              uni.showToast({ title: '缓存已清除', icon: 'success' })
            }, 800)
          }
        }
      })
    },
    goToAccountEdit() {
      uni.navigateTo({ url: '/pages/parent/account/edit' })
    },
    goToReminder() {
      uni.navigateTo({ url: '/pages/parent/reminder/index' })
    },
    goToHelp() {
      uni.navigateTo({ url: '/pages/parent/help/index' })
    },
    goToContact() {
      uni.navigateTo({ url: '/pages/parent/help/contact' })
    },
    goToFeedback() {
      uni.showToast({ title: '功能开发中', icon: 'none' })
    },
    goToAbout() {
      uni.navigateTo({ url: '/pages/parent/about/index' })
    },
    goBack() {
      uni.navigateBack()
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  overflow-x: hidden;
}
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.back-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.back-btn .ph {
  font-size: 28rpx;
  color: #718096;
}

.header-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
}

.page-content {
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
}

.menu-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx 28rpx;
  border-bottom: 1rpx solid #F5F5F5;
  transition: all 0.2s;
}

.menu-item:active {
  background: #F8FAFF;
}

.menu-item.last {
  border-bottom: none;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
}

.menu-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon .ph {
  font-size: 26rpx;
}

.menu-icon.blue {
  background: rgba(79, 158, 248, 0.1);
}

.menu-icon.blue .ph {
  color: #4F9EF8;
}

.menu-icon.green {
  background: rgba(34, 197, 94, 0.1);
}

.menu-icon.green .ph {
  color: #22C55E;
}

.menu-icon.orange {
  background: rgba(245, 127, 23, 0.1);
}

.menu-icon.orange .ph {
  color: #F57F17;
}

.menu-icon.purple {
  background: rgba(167, 139, 250, 0.1);
}

.menu-icon.purple .ph {
  color: #A78BFA;
}

.menu-icon.yellow {
  background: rgba(251, 191, 36, 0.1);
}

.menu-icon.yellow .ph {
  color: #FBBF24;
}

.menu-icon.pink {
  background: rgba(236, 72, 153, 0.1);
}

.menu-icon.pink .ph {
  color: #EC4899;
}

.menu-icon.gray {
  background: #F5F5F5;
}

.menu-icon.gray .ph {
  color: #A0AEC0;
}

.menu-icon.red {
  background: rgba(239, 68, 68, 0.1);
}

.menu-icon.red .ph {
  color: #EF4444;
}

.menu-label {
  flex: 1;
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.menu-arrow {
  font-size: 28rpx;
  color: #D1D5DB;
}

.version-badge {
  font-size: 18rpx;
  font-weight: 700;
  color: #A0AEC0;
  background: #F5F5F5;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.cache-size {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 600;
}

/* 开关 */
.toggle {
  width: 80rpx;
  height: 44rpx;
  border-radius: 22rpx;
  background: #E5E7EB;
  position: relative;
  transition: all 0.3s;
  flex-shrink: 0;
}

.toggle.on {
  background: #22C55E;
}

.toggle-thumb {
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  background: #FFFFFF;
  box-shadow: 0 2rpx 6rpx rgba(0, 0, 0, 0.15);
  transition: all 0.3s;
}

.toggle.on .toggle-thumb {
  left: 40rpx;
}

/* 字体大小选择 */
.font-size-picker {
  display: flex;
  gap: 8rpx;
}

.size-option {
  font-size: 20rpx;
  font-weight: 700;
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  background: #F5F5F5;
  color: #718096;
  transition: all 0.2s;
}

.size-option.active {
  background: rgba(79, 158, 248, 0.1);
  color: #4F9EF8;
}
</style>
