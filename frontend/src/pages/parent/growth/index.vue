<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">成长记录</view>
    </view>

    <view class="page-content">
      <!-- 星星统计 -->
      <view class="stars-card">
        <view class="stars-left">
          <view class="stars-count">{{ totalStars }}</view>
          <view class="stars-label">累计获得星星</view>
        </view>
        <view class="stars-icon">
          <text class="ph ph-star"></text>
        </view>
      </view>

      <!-- 筛查历史趋势 -->
      <view class="section-title">能力评估趋势</view>
      <view class="trend-card" v-if="reports.length > 0">
        <view class="trend-item" v-for="(r, i) in reports" :key="r.id">
          <view class="trend-dot" :class="r.risk_level"></view>
          <view class="trend-info">
            <view class="trend-title">第{{ reports.length - i }}次评估</view>
            <view class="trend-date">{{ formatDate(r.created_at) }}</view>
          </view>
          <view class="trend-score" :class="r.risk_level">{{ r.overall_score || '--' }}分</view>
          <view class="trend-badge" :class="r.risk_level">{{ riskLabel(r.risk_level) }}</view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="ph ph-chart-line"></text>
        <view class="empty-text">完成筛查后将显示能力趋势</view>
      </view>

      <!-- 训练完成记录 -->
      <view class="section-title">训练完成记录</view>
      <view class="task-history" v-if="completedTasks.length > 0">
        <view class="task-item" v-for="t in completedTasks" :key="t.id">
          <view class="task-icon-wrap">
            <text class="ph ph-check-circle"></text>
          </view>
          <view class="task-info">
            <view class="task-name">{{ t.task_name || taskTypeName(t.task_type) }}</view>
            <view class="task-date">{{ formatDate(t.completed_at || t.created_at) }}</view>
          </view>
          <view class="task-star">
            <text class="ph ph-star"></text> +1
          </view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="ph ph-trophy"></text>
        <view class="empty-text">完成训练任务后将在这里记录</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'
import { getReports } from '../../../api/report.js'
import { getTasks, getTotalStars } from '../../../api/training.js'

export default {
  data() {
    return {
      currentChild: null,
      reports: [],
      completedTasks: [],
      totalStars: 0
    }
  },
  onShow() {
    this.currentChild = getCurrentChild()
    if (this.currentChild) this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [reports, tasks, starRes] = await Promise.all([
          getReports(this.currentChild.id),
          getTasks(this.currentChild.id, 'completed'),
          getTotalStars(this.currentChild.id)
        ])
        this.reports = reports
        this.completedTasks = tasks
        this.totalStars = starRes.total_stars || 0
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    riskLabel(level) {
      return { low: '低风险', medium: '中风险', high: '高风险' }[level] || level
    },
    taskTypeName(type) {
      return { visual: '视觉训练', spelling: '拼字训练', reading: '阅读训练' }[type] || type
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    },
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn .ph { font-size: 40rpx; color: #6B7280; }

.header-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.page-content { padding: 48rpx; }

/* 星星卡片 */
.stars-card {
  background: linear-gradient(135deg, #F59E0B, #FBBF24);
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stars-count {
  font-size: 80rpx;
  font-weight: 800;
  color: #FFFFFF;
}

.stars-label {
  font-size: 26rpx;
  color: rgba(255,255,255,0.8);
  margin-top: 8rpx;
}

.stars-icon .ph {
  font-size: 120rpx;
  color: rgba(255,255,255,0.3);
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 趋势卡片 */
.trend-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 32rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
}

.trend-item:last-child { border-bottom: none; }

.trend-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.trend-dot.low { background: #10B981; }
.trend-dot.medium { background: #F59E0B; }
.trend-dot.high { background: #EF4444; }

.trend-info { flex: 1; }

.trend-title { font-size: 28rpx; font-weight: 700; color: #374151; }
.trend-date { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }

.trend-score {
  font-size: 32rpx;
  font-weight: 700;
  margin-right: 16rpx;
}

.trend-score.low { color: #10B981; }
.trend-score.medium { color: #F59E0B; }
.trend-score.high { color: #EF4444; }

.trend-badge {
  font-size: 20rpx;
  font-weight: 700;
  padding: 6rpx 20rpx;
  border-radius: 16rpx;
}

.trend-badge.low { background: #ECFDF5; color: #10B981; }
.trend-badge.medium { background: #FEF3C7; color: #F59E0B; }
.trend-badge.high { background: #FEF2F2; color: #EF4444; }

/* 训练记录 */
.task-history {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 32rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
}

.task-item:last-child { border-bottom: none; }

.task-icon-wrap .ph {
  font-size: 48rpx;
  color: #10B981;
}

.task-info { flex: 1; }
.task-name { font-size: 28rpx; font-weight: 700; color: #374151; }
.task-date { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }

.task-star {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #F59E0B;
}

.task-star .ph { font-size: 28rpx; }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx;
  margin-bottom: 48rpx;
}

.empty-state .ph {
  font-size: 80rpx;
  color: #D1D5DB;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 26rpx;
  color: #9CA3AF;
}
</style>
