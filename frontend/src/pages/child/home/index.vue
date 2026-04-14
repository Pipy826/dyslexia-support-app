<template>
  <view class="page-container">
    <!-- 顶部信息 -->
    <view class="top-bar">
      <view class="user-info">
        <view class="avatar">{{ childInitial }}</view>
        <view class="user-text">
          <view class="hello">你好，{{ childName }}！</view>
          <view class="welcome">准备好今天的挑战了吗？</view>
        </view>
      </view>
      <view class="stars-badge">
        <text class="ph ph-star"></text>
        <view class="stars-count">{{ totalStars }}</view>
      </view>
    </view>

    <!-- 核心内容区 -->
    <view class="content-area">
      <!-- 插画 -->
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

      <!-- 游戏类型选择 -->
      <view class="game-types">
        <view
          v-for="g in gameTypes"
          :key="g.type"
          :class="['game-type-btn', { active: selectedGameType === g.type }]"
          @click="selectedGameType = g.type"
        >
          <text :class="'ph ' + g.icon"></text>
          {{ g.name }}
        </view>
      </view>

      <!-- 开始按钮 -->
      <button class="start-btn" @click="startChallenge">
        <text class="ph ph-play"></text> 开始挑战
      </button>

      <view class="parent-tip">
        <text class="ph ph-info"></text> 请在安静环境下独立完成
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item active">
        <text class="ph-fill ph-game-controller"></text>
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
import { getTotalStars } from '../../../api/training.js'

export default {
  data() {
    return {
      child: null,
      totalStars: 0,
      selectedGameType: 'visual',
      gameTypes: [
        { type: 'visual', name: '视觉', icon: 'ph-eye' },
        { type: 'spelling', name: '拼字', icon: 'ph-puzzle-piece' },
        { type: 'comprehension', name: '理解', icon: 'ph-book-open' }
      ]
    }
  },
  computed: {
    childName() {
      return this.child?.name || '小朋友'
    },
    childInitial() {
      return this.child?.name?.charAt(0) || '🌟'
    }
  },
  onShow() {
    this.child = getCurrentChild()
    if (!this.child) {
      uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
      return
    }
    this.loadStars()
  },
  methods: {
    async loadStars() {
      try {
        const res = await getTotalStars(this.child.id)
        this.totalStars = res.total_stars || 0
      } catch (e) {
        console.warn('加载星星失败', e)
      }
    },
    startChallenge() {
      if (!this.child) {
        uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
        return
      }
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${this.selectedGameType}`
      })
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

.top-bar {
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info { display: flex; align-items: center; gap: 24rpx; }

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #EFF6FF;
  border: 2rpx solid #BFDBFE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 700;
  color: #3B82F6;
}

.user-text .hello { font-size: 36rpx; font-weight: 700; color: #374151; }
.user-text .welcome { font-size: 24rpx; color: #9CA3AF; margin-top: 4rpx; }

.stars-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FEF3C7;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  border: 1rpx solid #FDE68A;
}
.stars-badge .ph { font-size: 32rpx; color: #F59E0B; }
.stars-count { font-size: 28rpx; font-weight: 700; color: #D97706; }

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx 32rpx;
}

/* 插画 */
.illustration {
  width: 320rpx;
  height: 320rpx;
  margin-bottom: 48rpx;
  position: relative;
}
.illustration-bg {
  position: absolute;
  inset: 0;
  background: #EFF6FF;
  border-radius: 80rpx;
  transform: rotate(6deg);
}
.illustration-main {
  position: absolute;
  inset: 0;
  background: #FFFFFF;
  border-radius: 80rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.05);
  border: 1rpx solid #F3F4F6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.illustration-main .ph { font-size: 100rpx; color: #60A5FA; margin-bottom: 16rpx; }
.dots { display: flex; gap: 16rpx; }
.dot { width: 16rpx; height: 16rpx; border-radius: 50%; }
.dot.red { background: #F87171; }
.dot.green { background: #34D399; }
.dot.blue { background: #60A5FA; }

.title { font-size: 44rpx; font-weight: 700; color: #374151; margin-bottom: 12rpx; text-align: center; }
.subtitle { font-size: 26rpx; color: #9CA3AF; text-align: center; margin-bottom: 48rpx; }

/* 游戏类型选择 */
.game-types {
  display: flex;
  gap: 20rpx;
  margin-bottom: 48rpx;
}
.game-type-btn {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 16rpx 32rpx;
  border-radius: 50rpx;
  border: 2rpx solid #E5E7EB;
  font-size: 26rpx;
  font-weight: 600;
  color: #6B7280;
  background: #FFFFFF;
  transition: all 0.2s;
}
.game-type-btn .ph { font-size: 28rpx; }
.game-type-btn.active {
  background: #EFF6FF;
  border-color: #3B82F6;
  color: #3B82F6;
}

.start-btn {
  width: 100%;
  max-width: 640rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59,130,246,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
}
.start-btn .ph { font-size: 44rpx; }

.parent-tip {
  margin-top: 32rpx;
  font-size: 22rpx;
  color: #D1D5DB;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
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
.nav-item { display: flex; flex-direction: column; align-items: center; gap: 8rpx; color: #9CA3AF; }
.nav-item.active { color: #3B82F6; }
.nav-item .ph, .nav-item .ph-fill { font-size: 48rpx; }
.nav-label { font-size: 22rpx; font-weight: 500; }
.nav-item.active .nav-label { font-weight: 700; }

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-24rpx); }
  60% { transform: translateY(-12rpx); }
}
.bounce { animation: bounce 2.5s infinite; }
</style>
