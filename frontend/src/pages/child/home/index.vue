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
      uni.redirectTo({ url: '/pages/child/training/index' })
    }
  }
}
</script>

<style scoped>
/* 儿童首页 - 固定屏幕高度，禁止上下左右滚动 */
.page-container {
  height: 100vh;
  width: 100%;
  background: linear-gradient(180deg, #F0F7FF 0%, #FFFEF9 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;       /* 禁止任何方向滚动 */
  box-sizing: border-box;
  /* 为底部浮动导航栏留出空间 */
  padding-bottom: calc(100rpx + env(safe-area-inset-bottom));
}

/* ── 顶部信息栏 ── */
.top-bar {
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.user-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.avatar {
  width: 60rpx;
  height: 60rpx;
  min-width: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFE4B5, #FFD93D);
  border: 3rpx solid #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  color: #D97706;
  box-shadow: 0 4rpx 12rpx rgba(255, 217, 61, 0.3);
  flex-shrink: 0;
  margin-right: 14rpx;
}

.user-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.user-text .hello {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-text .welcome {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 2rpx;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
}

.stars-badge {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  padding: 10rpx 18rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.3);
  flex-shrink: 0;
  margin-left: 12rpx;
}

.stars-badge .ph {
  font-size: 26rpx;
  color: #F57F17;
  margin-right: 6rpx;
}

.stars-count {
  font-size: 22rpx;
  font-weight: 700;
  color: #E65100;
}

/* ── 内容区：flex:1 填满剩余高度 ── */
.content-area {
  flex: 1;
  min-height: 0;         /* 关键：允许收缩 */
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 32rpx 16rpx;
  overflow: hidden;      /* 禁止内容区滚动 */
  width: 100%;
  box-sizing: border-box;
}

/* ── 插画：用 flex:1 自适应高度，不用 aspect-ratio ── */
.illustration {
  width: 100%;
  flex: 1;
  min-height: 0;
  margin-bottom: 20rpx;
  position: relative;
  background: linear-gradient(135deg, #FFFFFF 0%, #F0F7FF 100%);
  border-radius: 28rpx;
  box-shadow: 0 4rpx 24rpx rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.illustration-bg {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(79, 158, 248, 0.06) 0%, transparent 70%);
}

.illustration-main {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.illustration-main .ph {
  font-size: 100rpx;
  color: #4F9EF8;
  display: block;
  margin-bottom: 16rpx;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12rpx); }
}

.dots {
  display: flex;
  flex-direction: row;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  margin: 0 6rpx;
  animation: pulse 1.5s ease-in-out infinite;
}

.dot.red { background: #FF6B6B; animation-delay: 0s; }
.dot.green { background: #22C55E; animation-delay: 0.2s; }
.dot.blue { background: #4F9EF8; animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
}

/* ── 标题区 ── */
.title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 6rpx;
  text-align: center;
  flex-shrink: 0;
}

.subtitle {
  font-size: 22rpx;
  color: #A0AEC0;
  text-align: center;
  margin-bottom: 20rpx;
  font-weight: 500;
  flex-shrink: 0;
}

/* ── 游戏类型选择：3个按钮均分，不横向滚动 ── */
.game-types {
  display: flex;
  flex-direction: row;
  width: 100%;
  margin-bottom: 20rpx;
  flex-shrink: 0;
  overflow: hidden;      /* 禁止横向滚动 */
}

.game-type-btn {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 14rpx 8rpx;
  border-radius: 16rpx;
  font-size: 22rpx;
  font-weight: 700;
  color: #A0AEC0;
  background: #FFFFFF;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  white-space: nowrap;
  overflow: hidden;
}

/* 按钮之间的间距用 margin */
.game-type-btn:not(:last-child) {
  margin-right: 12rpx;
}

.game-type-btn .ph {
  font-size: 24rpx;
  margin-right: 6rpx;
}

.game-type-btn.active {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  box-shadow: 0 2rpx 12rpx rgba(79, 158, 248, 0.2);
}

/* ── 开始按钮 ── */
.start-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 34rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-sizing: border-box;
}

.start-btn .ph {
  font-size: 36rpx;
  margin-right: 10rpx;
}

.parent-tip {
  margin-top: 16rpx;
  font-size: 20rpx;
  color: #CBD5E0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  flex-shrink: 0;
}

.parent-tip .ph {
  font-size: 20rpx;
  margin-right: 6rpx;
}

/* bottom-nav 类保留但为空，实际由 tab-bar 组件渲染 */
.bottom-nav { display: none; }
</style>
