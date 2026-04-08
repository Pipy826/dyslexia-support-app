<template>
  <view class="page-container">
    <!-- 顶部信息 -->
    <view class="top-bar">
      <view class="user-info">
        <view class="avatar">
          <text class="ph ph-user"></text>
        </view>
        <view class="user-text">
          <view class="hello">你好，小明</view>
          <view class="welcome">准备好今天的挑战了吗？</view>
        </view>
      </view>
      <view class="notification">
        <text class="ph ph-bell"></text>
      </view>
    </view>

    <!-- 核心内容区 -->
    <view class="content-area">
      <!-- 占位插画 -->
      <view class="illustration bounce">
        <view class="illustration-bg"></view>
        <view class="illustration-main">
          <text class="ph ph-rocket"></text>
          <view class="dots">
            <view class="dot red"></view>
            <view class="dot green"></view>
            <view class="dot blue"></view>
          </view>
        </view>
      </view>

      <view class="title">语言探险之旅</view>
      <view class="subtitle">完成挑战，收集小星星，看看你的超能力！</view>

      <!-- 开始筛查按钮 -->
      <button class="start-btn" @click="startChallenge">
        <text class="ph ph-play"></text> 开始挑战
      </button>

      <view class="parent-tip">
        <text class="ph ph-info"></text> 家长辅助提示：请让孩子在安静环境下独立完成
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item active">
        <text class="ph ph-game-controller"></text>
        <view class="nav-label">挑战</view>
      </view>
      <view class="nav-item" @click="goToTraining">
        <text class="ph ph-tree"></text>
        <view class="nav-label">训练乐园</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      child: null
    }
  },
  onLoad() {
    this.child = getCurrentChild()
    if (!this.child) {
      uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
    }
  },
  methods: {
    startChallenge() {
      uni.navigateTo({ url: '/pages/child/prep/index' })
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/child/training/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  padding-bottom: 168rpx;
}

/* 顶部信息 */
.top-bar {
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFFFFF;
  z-index: 10;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar .ph {
  font-size: 48rpx;
  color: #3B82F6;
}

.user-text .hello {
  font-size: 40rpx;
  font-weight: 700;
  color: #374151;
}

.user-text .welcome {
  font-size: 26rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.notification {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #F9FAFB;
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

/* 核心内容区 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 48rpx;
}

/* 占位插画 */
.illustration {
  width: 384rpx;
  height: 384rpx;
  margin-bottom: 64rpx;
  position: relative;
}

.illustration-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #EFF6FF;
  border-radius: 80rpx;
  transform: rotate(6deg);
}

.illustration-main {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #FFFFFF;
  border-radius: 80rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid #F3F4F6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.illustration-main .ph {
  font-size: 120rpx;
  color: #60A5FA;
  margin-bottom: 16rpx;
}

.dots {
  display: flex;
  gap: 16rpx;
}

.dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.dot.red { background: #F87171; }
.dot.green { background: #34D399; }
.dot.blue { background: #60A5FA; }

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 16rpx;
  text-align: center;
}

.subtitle {
  font-size: 28rpx;
  color: #9CA3AF;
  text-align: center;
  padding: 0 32rpx;
  margin-bottom: 80rpx;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  max-width: 640rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}

.start-btn .ph {
  font-size: 48rpx;
}

/* 家长提示 */
.parent-tip {
  margin-top: 32rpx;
  font-size: 22rpx;
  color: #D1D5DB;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.parent-tip .ph {
  font-size: 24rpx;
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 168rpx;
  background: #FFFFFF;
  border-top: 1rpx solid #F3F4F6;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 16rpx 96rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  gap: 160rpx;
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  color: #9CA3AF;
}

.nav-item.active {
  color: #3B82F6;
}

.nav-item .ph {
  font-size: 48rpx;
}

.nav-label {
  font-size: 22rpx;
  font-weight: 500;
}

.nav-item.active .nav-label {
  font-weight: 700;
}

/* 动画 */
@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-30rpx); }
  60% { transform: translateY(-14rpx); }
}

.bounce {
  animation: bounce 2s infinite;
}
</style>
