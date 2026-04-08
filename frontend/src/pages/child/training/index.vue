<template>
  <view class="page-container">
    <!-- 顶部信息 -->
    <view class="top-bar">
      <view class="page-title">训练乐园</view>
      <view class="stars-badge">
        <text class="ph ph-star"></text>
        <view class="stars-count">12 颗</view>
      </view>
    </view>

    <!-- 核心内容区 -->
    <view class="content-area">
      <!-- 今日进度模块 -->
      <view class="progress-card">
        <view class="progress-header">
          <view class="progress-info">
            <view class="progress-title">今日任务</view>
            <view class="progress-subtitle">完成任务获得小星星哦！</view>
          </view>
          <view class="progress-count">1<text class="count-total">/3</text></view>
        </view>
        <view class="progress-track">
          <view class="progress-fill" style="width: 33%"></view>
        </view>
      </view>

      <!-- 任务列表 -->
      <view class="section-title">我的任务</view>
      <view class="task-list">
        <!-- 任务1 已完成 -->
        <view class="task-card completed">
          <view class="task-icon green">
            <text class="ph ph-check-circle"></text>
          </view>
          <view class="task-info">
            <view class="task-name">火眼金睛</view>
            <view class="task-desc">找出不一样的字</view>
          </view>
          <button class="task-btn disabled" disabled>已完成</button>
        </view>

        <!-- 任务2 待完成 -->
        <view class="task-card">
          <view class="task-tag recommend">推荐</view>
          <view class="task-icon blue">
            <text class="ph ph-puzzle-piece"></text>
          </view>
          <view class="task-info">
            <view class="task-name">拼字小达人</view>
            <view class="task-desc">把字拼完整</view>
          </view>
          <button class="task-btn" @click="startTask">去完成</button>
        </view>

        <!-- 任务3 待完成 -->
        <view class="task-card">
          <view class="task-icon orange">
            <text class="ph ph-book-open"></text>
          </view>
          <view class="task-info">
            <view class="task-name">故事大王</view>
            <view class="task-desc">读句子选图片</view>
          </view>
          <button class="task-btn" @click="startTask">去完成</button>
        </view>
      </view>

      <!-- 成就系统 -->
      <view class="section-title">我的成就</view>
      <view class="achievements-grid">
        <view class="achievement-card">
          <text class="ph ph-medal"></text>
          <view class="achievement-name">连胜3天</view>
        </view>
        <view class="achievement-card active">
          <text class="ph ph-trophy"></text>
          <view class="achievement-name">拼字新手</view>
        </view>
        <view class="achievement-card locked">
          <text class="ph ph-crown"></text>
          <view class="achievement-name">待解锁</view>
        </view>
      </view>
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToChallenge">
        <text class="ph ph-game-controller"></text>
        <view class="nav-label">挑战</view>
      </view>
      <view class="nav-item active">
        <text class="ph ph-tree"></text>
        <view class="nav-label">训练乐园</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getTasks, getTotalStars } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      tasks: [],
      totalStars: 12,
      child: null
    }
  },
  onShow() {
    this.child = getCurrentChild()
    if (this.child) {
      this.loadData()
    }
  },
  methods: {
    async loadData() {
      try {
        this.tasks = await getTasks(this.child.id)
        const starRes = await getTotalStars(this.child.id)
        this.totalStars = starRes.total_stars
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    startTask() {
      uni.navigateTo({ url: '/pages/child/game/index' })
    },
    goToChallenge() {
      uni.redirectTo({ url: '/pages/child/home/index' })
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
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
}

.stars-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FEF3C7;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  border: 1rpx solid #FDE68A;
}

.stars-badge .ph {
  font-size: 32rpx;
  color: #F59E0B;
}

.stars-count {
  font-size: 26rpx;
  font-weight: 700;
  color: #D97706;
}

/* 内容区 */
.content-area {
  flex: 1;
  padding: 32rpx 48rpx;
}

/* 进度卡片 */
.progress-card {
  background: #EFF6FF;
  border-radius: 48rpx;
  padding: 40rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DBEAFE;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32rpx;
}

.progress-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #374151;
}

.progress-subtitle {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.progress-count {
  font-size: 64rpx;
  font-weight: 800;
  color: #3B82F6;
}

.count-total {
  font-size: 32rpx;
  color: #93C5FD;
}

.progress-track {
  height: 28rpx;
  background: #FFFFFF;
  border-radius: 14rpx;
  overflow: hidden;
  border: 1rpx solid #DBEAFE;
}

.progress-fill {
  height: 100%;
  background: #3B82F6;
  border-radius: 14rpx;
  transition: width 0.5s;
}

/* 区域标题 */
.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 24rpx;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 48rpx;
}

.task-card {
  background: #FFFFFF;
  border: 4rpx solid #F3F4F6;
  border-radius: 48rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  position: relative;
  overflow: hidden;
}

.task-card.completed {
  opacity: 0.7;
}

.task-tag {
  position: absolute;
  top: 0;
  right: 0;
  background: #EF4444;
  color: #FFFFFF;
  font-size: 18rpx;
  font-weight: 700;
  padding: 8rpx 24rpx;
  border-radius: 0 44rpx 0 24rpx;
}

.task-tag.recommend {
  background: #EF4444;
}

.task-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-icon .ph {
  font-size: 56rpx;
}

.task-icon.green {
  background: #ECFDF5;
}
.task-icon.green .ph {
  color: #10B981;
}

.task-icon.blue {
  background: #EFF6FF;
}
.task-icon.blue .ph {
  color: #3B82F6;
}

.task-icon.orange {
  background: #FEF3C7;
}
.task-icon.orange .ph {
  color: #F59E0B;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 34rpx;
  font-weight: 700;
  color: #374151;
}

.task-desc {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.task-btn {
  padding: 16rpx 32rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  font-size: 24rpx;
  font-weight: 700;
}

.task-btn.disabled {
  background: #F3F4F6;
  color: #9CA3AF;
}

/* 成就网格 */
.achievements-grid {
  display: flex;
  gap: 24rpx;
}

.achievement-card {
  flex: 1;
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 32rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1rpx solid #F3F4F6;
}

.achievement-card .ph {
  font-size: 64rpx;
  color: #D1D5DB;
  margin-bottom: 12rpx;
}

.achievement-card.active .ph {
  color: #F59E0B;
}

.achievement-name {
  font-size: 20rpx;
  font-weight: 700;
  color: #9CA3AF;
  text-align: center;
}

.achievement-card.active .achievement-name {
  color: #374151;
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
</style>
