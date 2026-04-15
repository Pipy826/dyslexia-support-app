<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">成长分析</view>
      <view class="ai-badge">
        <text class="ph-fill ph-robot"></text> AI
      </view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 孩子信息 -->
      <view class="child-bar" v-if="childName">
        <view class="child-avatar-sm">{{ childName.charAt(0) }}</view>
        <view class="child-bar-name">{{ childName }} 的成长轨迹</view>
        <view class="report-count-badge">{{ reportCount }} 次筛查</view>
      </view>

      <!-- 得分趋势图 -->
      <view class="section-title">综合得分趋势</view>
      <view class="chart-card">
        <view class="chart-empty" v-if="scores.length === 0">
          <text class="ph ph-chart-line"></text>
          <view>暂无筛查数据</view>
        </view>
        <view class="chart-area" v-else>
          <!-- 简易折线图（用 flex 模拟） -->
          <view class="chart-y-labels">
            <view class="y-label">100</view>
            <view class="y-label">75</view>
            <view class="y-label">50</view>
            <view class="y-label">25</view>
            <view class="y-label">0</view>
          </view>
          <view class="chart-body">
            <view class="chart-grid">
              <view class="grid-line" v-for="i in 4" :key="i"></view>
            </view>
            <view class="chart-bars">
              <view
                class="chart-bar-wrap"
                v-for="(item, i) in scores"
                :key="i"
              >
                <view class="chart-bar-label">{{ item.score }}</view>
                <view
                  class="chart-bar"
                  :class="getRiskClass(item.risk_level)"
                  :style="{ height: item.score + '%' }"
                ></view>
                <view class="chart-bar-date">{{ formatShortDate(item.date) }}</view>
              </view>
            </view>
          </view>
        </view>

        <!-- 图例 -->
        <view class="chart-legend">
          <view class="legend-item">
            <view class="legend-dot green"></view>低风险
          </view>
          <view class="legend-item">
            <view class="legend-dot orange"></view>中风险
          </view>
          <view class="legend-item">
            <view class="legend-dot red"></view>高风险
          </view>
        </view>
      </view>

      <!-- AI 趋势分析 -->
      <view class="section-title">AI 趋势分析</view>
      <view class="analysis-card">
        <view class="analysis-header">
          <view class="analysis-avatar">
            <text class="ph-fill ph-robot"></text>
          </view>
          <view class="analysis-title">智能分析报告</view>
          <view class="refresh-btn" @click="loadAnalysis" v-if="!analysisLoading">
            <text class="ph ph-arrows-clockwise"></text>
          </view>
        </view>

        <!-- 加载中 -->
        <view class="analysis-loading" v-if="analysisLoading">
          <view class="loading-spinner"></view>
          <view class="loading-text">AI 正在分析成长数据...</view>
        </view>

        <!-- 分析内容 -->
        <view class="analysis-content" v-else-if="analysis">
          {{ analysis }}
        </view>

        <!-- 无数据 -->
        <view class="analysis-empty" v-else>
          <view class="analysis-empty-text">完成至少一次筛查后，AI 将为您生成专属成长分析。</view>
          <button class="go-screen-btn" @click="goToScreening">
            <text class="ph ph-play"></text> 去筛查
          </button>
        </view>
      </view>

      <!-- 各维度历史对比 -->
      <view class="section-title" v-if="dimensionHistory.length > 0">各维度变化</view>
      <view class="dimension-history-card" v-if="dimensionHistory.length > 0">
        <view
          class="dim-row"
          v-for="dim in dimensionHistory"
          :key="dim.key"
        >
          <view class="dim-name">{{ dim.name }}</view>
          <view class="dim-scores">
            <view
              class="dim-score-dot"
              v-for="(s, i) in dim.scores"
              :key="i"
              :class="getScoreClass(s)"
              :title="s + '分'"
            >
              <view class="dim-score-val">{{ s }}</view>
            </view>
          </view>
          <view class="dim-trend" :class="dim.trend > 0 ? 'up' : dim.trend < 0 ? 'down' : 'flat'">
            <text :class="dim.trend > 0 ? 'ph ph-trend-up' : dim.trend < 0 ? 'ph ph-trend-down' : 'ph ph-minus'"></text>
            {{ dim.trend > 0 ? '+' : '' }}{{ dim.trend !== 0 ? dim.trend : '—' }}
          </view>
        </view>
      </view>

      <!-- 底部占位 -->
      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getGrowthAnalysis } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      childId: null,
      childName: '',
      reportCount: 0,
      scores: [],
      analysis: '',
      analysisLoading: false,
      dimensionHistory: [],
    }
  },

  onLoad(options) {
    if (options.child_id) {
      this.childId = parseInt(options.child_id)
    } else {
      const child = getCurrentChild()
      this.childId = child?.id
      this.childName = child?.name || ''
    }
    if (this.childId) {
      this.loadAnalysis()
    }
  },

  methods: {
    async loadAnalysis() {
      if (!this.childId || this.analysisLoading) return
      this.analysisLoading = true
      this.analysis = ''
      try {
        const res = await getGrowthAnalysis(this.childId)
        this.childName = res.child_name || this.childName
        this.reportCount = res.report_count || 0
        this.scores = res.scores || []
        this.analysis = res.analysis || ''
        this.buildDimensionHistory(res.scores || [])
      } catch (e) {
        console.error('加载成长分析失败', e)
        uni.showToast({ title: '加载失败，请重试', icon: 'none' })
      } finally {
        this.analysisLoading = false
      }
    },

    buildDimensionHistory(scores) {
      // 从 scores 中提取维度历史（需要后端返回 dimensions 字段）
      // 这里做简化处理，实际可扩展
      this.dimensionHistory = []
    },

    getRiskClass(level) {
      return { low: 'green', medium: 'orange', high: 'red' }[level] || 'blue'
    },

    getScoreClass(score) {
      if (score >= 75) return 'green'
      if (score >= 60) return 'orange'
      return 'red'
    },

    formatShortDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },

    goBack() {
      uni.navigateBack()
    },

    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
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
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.ai-badge {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #F3E8FF;
  color: #7C3AED;
  padding: 8rpx 20rpx;
  border-radius: 50rpx;
  font-size: 22rpx;
  font-weight: 700;
}

.ai-badge .ph { font-size: 24rpx; }

/* 内容区 */
.page-content {
  flex: 1;
  padding: 40rpx 48rpx;
}

/* 孩子信息栏 */
.child-bar {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.child-avatar-sm {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
  font-weight: 700;
  color: #3B82F6;
  flex-shrink: 0;
}

.child-bar-name {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #1F2937;
}

.report-count-badge {
  font-size: 20rpx;
  color: #6B7280;
  background: #F3F4F6;
  padding: 6rpx 20rpx;
  border-radius: 50rpx;
}

/* 区域标题 */
.section-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 20rpx;
}

/* 图表卡片 */
.chart-card {
  background: #FFFFFF;
  border-radius: 40rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  border: 1rpx solid #F3F4F6;
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 60rpx 0;
  color: #9CA3AF;
  font-size: 26rpx;
}

.chart-empty .ph { font-size: 80rpx; color: #D1D5DB; }

.chart-area {
  display: flex;
  gap: 16rpx;
  height: 280rpx;
  margin-bottom: 24rpx;
}

.chart-y-labels {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 40rpx;
}

.y-label {
  font-size: 18rpx;
  color: #9CA3AF;
  text-align: right;
  width: 48rpx;
}

.chart-body {
  flex: 1;
  position: relative;
}

.chart-grid {
  position: absolute;
  inset: 0;
  bottom: 40rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.grid-line {
  height: 1rpx;
  background: #F3F4F6;
  width: 100%;
}

.chart-bars {
  position: absolute;
  inset: 0;
  bottom: 40rpx;
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  padding: 0 8rpx;
}

.chart-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  position: relative;
}

.chart-bar-label {
  font-size: 18rpx;
  color: #6B7280;
  font-weight: 700;
  margin-bottom: 6rpx;
}

.chart-bar {
  width: 100%;
  border-radius: 8rpx 8rpx 0 0;
  min-height: 8rpx;
  transition: height 0.6s ease;
}

.chart-bar.green { background: linear-gradient(180deg, #34D399, #10B981); }
.chart-bar.orange { background: linear-gradient(180deg, #FCD34D, #F59E0B); }
.chart-bar.red { background: linear-gradient(180deg, #F87171, #EF4444); }
.chart-bar.blue { background: linear-gradient(180deg, #60A5FA, #3B82F6); }

.chart-bar-date {
  position: absolute;
  bottom: -36rpx;
  font-size: 18rpx;
  color: #9CA3AF;
  white-space: nowrap;
}

.chart-legend {
  display: flex;
  gap: 32rpx;
  justify-content: center;
  margin-top: 8rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: #6B7280;
}

.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.legend-dot.green { background: #10B981; }
.legend-dot.orange { background: #F59E0B; }
.legend-dot.red { background: #EF4444; }

/* AI 分析卡片 */
.analysis-card {
  background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
  border-radius: 40rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  border: 1rpx solid #DDD6FE;
}

.analysis-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 28rpx;
}

.analysis-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #7C3AED;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.analysis-avatar .ph { font-size: 32rpx; color: #FFFFFF; }

.analysis-title {
  flex: 1;
  font-size: 28rpx;
  font-weight: 700;
  color: #5B21B6;
}

.refresh-btn .ph { font-size: 32rpx; color: #7C3AED; }

.analysis-loading {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 0;
}

.loading-spinner {
  width: 48rpx;
  height: 48rpx;
  border: 4rpx solid #EDE9FE;
  border-top-color: #7C3AED;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text { font-size: 26rpx; color: #7C3AED; }

.analysis-content {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
}

.analysis-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28rpx;
  padding: 16rpx 0;
}

.analysis-empty-text {
  font-size: 26rpx;
  color: #6B7280;
  text-align: center;
  line-height: 1.6;
}

.go-screen-btn {
  background: #7C3AED;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 20rpx 48rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.go-screen-btn .ph { font-size: 28rpx; }

/* 维度历史 */
.dimension-history-card {
  background: #FFFFFF;
  border-radius: 40rpx;
  padding: 40rpx;
  margin-bottom: 40rpx;
  border: 1rpx solid #F3F4F6;
}

.dim-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
}

.dim-row:last-child { border-bottom: none; }

.dim-name {
  width: 140rpx;
  font-size: 24rpx;
  color: #374151;
  font-weight: 600;
  flex-shrink: 0;
}

.dim-scores {
  flex: 1;
  display: flex;
  gap: 12rpx;
  flex-wrap: wrap;
}

.dim-score-dot {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dim-score-dot.green { background: #ECFDF5; }
.dim-score-dot.orange { background: #FEF3C7; }
.dim-score-dot.red { background: #FEF2F2; }

.dim-score-val {
  font-size: 18rpx;
  font-weight: 700;
}

.dim-score-dot.green .dim-score-val { color: #10B981; }
.dim-score-dot.orange .dim-score-val { color: #F59E0B; }
.dim-score-dot.red .dim-score-val { color: #EF4444; }

.dim-trend {
  font-size: 22rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 4rpx;
  width: 80rpx;
  flex-shrink: 0;
}

.dim-trend .ph { font-size: 24rpx; }
.dim-trend.up { color: #10B981; }
.dim-trend.down { color: #EF4444; }
.dim-trend.flat { color: #9CA3AF; }
</style>
