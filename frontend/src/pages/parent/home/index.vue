<template>
  <view class="page-container">
    <!-- 顶部信息栏 -->
    <view class="top-bar">
      <view class="user-info">
        <view class="avatar">{{ currentChild?.name?.charAt(0) || '明' }}</view>
        <view class="user-text">
          <view class="greeting">晚上好，小明妈妈</view>
          <view class="current-child">当前档案：小明 (7岁) ▼</view>
        </view>
      </view>
      <view class="notification">
        <text class="ph ph-bell"></text>
        <view class="notification-dot"></view>
      </view>
    </view>

    <view class="page-content">
      <!-- 核心引导卡片：发起首次筛查提示 -->
      <view class="guide-card">
        <view class="guide-decoration"></view>
        <view class="guide-icon">
          <text class="ph ph-star"></text>
        </view>
        <view class="guide-tag">系统建议</view>
        <view class="guide-title">初步能力筛查</view>
        <view class="guide-desc">小明尚未进行全面的读写能力筛查，建议抽出15分钟了解孩子的现状，生成定制专属干预计划。</view>
        <button class="guide-btn" @click="goToScreening">立即发起筛查</button>
      </view>

      <!-- 四宫格快捷入口 -->
      <view class="grid-section">
        <view class="grid-item" @click="goToReport">
          <view class="grid-icon blue">
            <text class="ph ph-file-text"></text>
          </view>
          <view class="grid-label">评估报告</view>
        </view>
        <view class="grid-item" @click="goToTraining">
          <view class="grid-icon green">
            <text class="ph ph-calendar-check"></text>
          </view>
          <view class="grid-label">训练计划</view>
        </view>
        <view class="grid-item">
          <view class="grid-icon orange">
            <text class="ph ph-trend-up"></text>
          </view>
          <view class="grid-label">成长记录</view>
        </view>
        <view class="grid-item" @click="showAiChat">
          <view class="grid-icon purple">
            <text class="ph ph-robot"></text>
          </view>
          <view class="grid-label">AI问答</view>
        </view>
      </view>

      <!-- 近期动态模块 -->
      <view class="section-header">
        <view class="section-title">近期动态</view>
        <view class="more-link">查看全部</view>
      </view>

      <view class="activity-list">
        <!-- 动态卡片 1 -->
        <view class="activity-card">
          <view class="activity-icon blue">
            <text class="ph ph-info"></text>
          </view>
          <view class="activity-content">
            <view class="activity-title">完成档案创建</view>
            <view class="activity-time">今天 09:30</view>
          </view>
          <view class="activity-status">已就绪</view>
        </view>

        <!-- 动态卡片 2 -->
        <view class="activity-card muted">
          <view class="activity-icon gray">
            <text class="ph ph-book-open"></text>
          </view>
          <view class="activity-content">
            <view class="activity-title">了解读写障碍表现</view>
            <view class="activity-time">昨天 20:15</view>
          </view>
          <view class="activity-status-text">阅读文章</view>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/home/index"></tab-bar>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'
import { getChildren } from '../../../api/child.js'
import { getReports } from '../../../api/report.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      children: [],
      recentReport: null
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.children = await getChildren()
        if (this.children.length > 0) {
          const saved = getCurrentChild()
          if (saved) {
            this.currentChild = this.children.find(c => c.id === saved.id) || this.children[0]
          } else {
            this.currentChild = this.children[0]
          }
          this.loadRecentReport()
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadRecentReport() {
      if (!this.currentChild) return
      try {
        const reports = await getReports(this.currentChild.id)
        this.recentReport = reports[0] || null
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    goToReport() {
      uni.navigateTo({ url: '/pages/parent/report/index' })
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/parent/training/index' })
    },
    showAiChat() {
      uni.navigateTo({ url: '/pages/parent/ai-chat/index' })
    }
  }
}
</script>

<style scoped>
@import '@/styles/variables.scss';

.page-container {
  min-height: 100vh;
  background: #F9FAFB;
  padding-bottom: 196rpx;
}

/* 顶部信息栏 */
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

.user-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #EFF6FF;
  border: 1rpx solid #BFDBFE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #3B82F6;
}

.user-text .greeting {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
}

.user-text .current-child {
  font-size: 22rpx;
  color: #6B7280;
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
  position: relative;
}

.notification .ph {
  font-size: 40rpx;
  color: #6B7280;
}

.notification-dot {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #EF4444;
}

/* 页面内容 */
.page-content {
  padding: 32rpx 48rpx;
}

/* 引导卡片 */
.guide-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
  position: relative;
  overflow: hidden;
}

.guide-decoration {
  position: absolute;
  right: -32rpx;
  top: -32rpx;
  width: 192rpx;
  height: 192rpx;
  border-radius: 50%;
  background: #EFF6FF;
  opacity: 0.5;
}

.guide-icon {
  width: 48rpx;
  height: 48rpx;
  background: #EFF6FF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.guide-icon .ph {
  font-size: 24rpx;
  color: #3B82F6;
}

.guide-tag {
  font-size: 20rpx;
  font-weight: 700;
  color: #3B82F6;
  letter-spacing: 2rpx;
  margin-bottom: 8rpx;
}

.guide-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.guide-desc {
  font-size: 26rpx;
  color: #6B7280;
  line-height: 1.6;
  margin-bottom: 40rpx;
}

.guide-btn {
  width: 100%;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

/* 四宫格 */
.grid-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32rpx;
  margin-bottom: 48rpx;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.grid-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 32rpx;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid #F9FAFB;
}

.grid-icon .ph {
  font-size: 48rpx;
}

.grid-icon.blue { color: #3B82F6; }
.grid-icon.green { color: #10B981; }
.grid-icon.orange { color: #F59E0B; }
.grid-icon.purple { color: #8B5CF6; }

.grid-label {
  font-size: 22rpx;
  color: #4B5563;
}

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.more-link {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 动态列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.activity-card {
  background: #FFFFFF;
  padding: 32rpx;
  border-radius: 40rpx;
  border: 1rpx solid #F3F4F6;
  display: flex;
  align-items: center;
  gap: 32rpx;
}

.activity-card.muted {
  opacity: 0.6;
}

.activity-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.blue { background: #EFF6FF; }
.activity-icon.blue .ph { color: #3B82F6; }
.activity-icon.gray { background: #F3F4F6; }
.activity-icon.gray .ph { color: #9CA3AF; }

.activity-icon .ph {
  font-size: 32rpx;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.activity-time {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.activity-status {
  font-size: 22rpx;
  font-weight: 500;
  color: #3B82F6;
  background: #EFF6FF;
  padding: 8rpx 24rpx;
  border-radius: 16rpx;
}

.activity-status-text {
  font-size: 22rpx;
  color: #9CA3AF;
}
</style>
