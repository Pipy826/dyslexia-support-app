<template>
  <view class="page-container">
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
        <view class="stars-right">
          <text class="ph ph-star stars-icon"></text>
        </view>
      </view>

      <!-- 关键里程碑 -->
      <view class="milestone-row" v-if="firstScreeningDate || continuousDays > 0">
        <view class="milestone-item" v-if="firstScreeningDate">
          <text class="ph ph-calendar-check milestone-icon"></text>
          <view class="milestone-val">{{ firstScreeningDate }}</view>
          <view class="milestone-label">首次筛查</view>
        </view>
        <view class="milestone-divider" v-if="firstScreeningDate && continuousDays > 0"></view>
        <view class="milestone-item" v-if="continuousDays > 0">
          <text class="ph ph-fire milestone-icon fire"></text>
          <view class="milestone-val">{{ continuousDays }}天</view>
          <view class="milestone-label">连续训练</view>
        </view>
        <view class="milestone-divider" v-if="completedTasks.length > 0"></view>
        <view class="milestone-item" v-if="completedTasks.length > 0">
          <text class="ph ph-check-circle milestone-icon green"></text>
          <view class="milestone-val">{{ completedTasks.length }}次</view>
          <view class="milestone-label">累计训练</view>
        </view>
      </view>

      <!-- 能力趋势图 -->
      <view class="section-title">能力评估趋势</view>
      <view class="trend-chart-card" v-if="chartReports.length > 0">
        <!-- SVG 折线图 -->
        <view class="chart-legend">
          <view class="legend-item low"><view class="legend-dot"></view>低风险</view>
          <view class="legend-item medium"><view class="legend-dot"></view>中风险</view>
          <view class="legend-item high"><view class="legend-dot"></view>高风险</view>
        </view>
        <view class="chart-wrap">
          <!-- Y轴标签 -->
          <view class="y-axis">
            <view class="y-label">100</view>
            <view class="y-label">75</view>
            <view class="y-label">50</view>
            <view class="y-label">25</view>
            <view class="y-label">0</view>
          </view>
          <!-- 图表主体 -->
          <view class="chart-body">
            <!-- 网格线 -->
            <view class="grid-line" v-for="i in 4" :key="i" :style="{ bottom: (i * 25) + '%' }"></view>
            <!-- 折线和点 -->
            <view class="chart-points">
              <view
                v-for="(r, idx) in chartReports"
                :key="r.id"
                class="chart-point-wrap"
                :style="{ left: pointLeft(idx) + '%' }"
              >
                <!-- 连接线（到下一个点） -->
                <view
                  v-if="idx < chartReports.length - 1"
                  class="chart-line"
                  :style="lineStyle(idx)"
                ></view>
                <!-- 数据点 -->
                <view
                  :class="['chart-dot', r.risk_level]"
                  :style="{ bottom: (r.overall_score || 0) + '%' }"
                  @click="viewReport(r.id)"
                >
                  <view class="dot-tooltip">{{ r.overall_score }}分</view>
                </view>
              </view>
            </view>
            <!-- X轴日期 -->
            <view class="x-axis">
              <view
                v-for="(r, idx) in chartReports"
                :key="r.id"
                class="x-label"
                :style="{ left: pointLeft(idx) + '%' }"
              >{{ formatShortDate(r.created_at) }}</view>
            </view>
          </view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="ph ph-chart-line-up"></text>
        <view class="empty-text">完成筛查后将显示能力趋势</view>
      </view>

      <!-- 趋势分析文字 -->
      <view class="trend-analysis" v-if="chartReports.length > 0">
        <text class="ph ph-trend-up trend-analysis-icon"></text>
        <view class="trend-analysis-text">{{ trendAnalysisText }}</view>
      </view>

      <!-- 历史评估列表 -->
      <view class="section-title" v-if="reports.length > 0">历史评估记录</view>
      <view class="trend-card" v-if="reports.length > 0">
        <view class="trend-item" v-for="(r, i) in reports" :key="r.id" @click="viewReport(r.id)">
          <view class="trend-dot" :class="r.risk_level"></view>
          <view class="trend-info">
            <view class="trend-title">第 {{ reports.length - i }} 次评估</view>
            <view class="trend-date">{{ formatDate(r.created_at) }}</view>
          </view>
          <view class="trend-score" :class="r.risk_level">{{ r.overall_score ?? '--' }}分</view>
          <view class="trend-badge" :class="r.risk_level">{{ riskLabel(r.risk_level) }}</view>
        </view>
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
      totalStars: 0,
      continuousDays: 0,
      firstScreeningDate: ''
    }
  },
  computed: {
    // 最多取最近 6 次用于图表
    chartReports() {
      return [...this.reports].reverse().slice(0, 6)
    },
    trendAnalysisText() {
      const r = this.chartReports
      if (r.length === 0) return ''
      if (r.length === 1) return '首次评估，继续坚持训练后可查看趋势变化'
      const latest = r[r.length - 1].overall_score || 0
      const prev = r[r.length - 2].overall_score || 0
      const diff = latest - prev
      if (diff >= 10) return '稳定改善中 📈 继续保持！'
      if (diff > 0) return '缓慢改善中，坚持训练效果会更明显'
      if (Math.abs(diff) <= 5) return '基本稳定，建议调整训练重点'
      return '近期有所波动，建议关注训练质量'
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

        // 首次筛查时间
        if (reports.length > 0) {
          const oldest = [...reports].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))[0]
          this.firstScreeningDate = this.formatDate(oldest.created_at)
        }

        // 连续训练天数
        this.continuousDays = this._calcContinuousDays(tasks)
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    _calcContinuousDays(completedTasks) {
      if (!completedTasks || completedTasks.length === 0) return 0
      const days = new Set(completedTasks.map(t => {
        const d = t.completed_at || t.created_at
        return d ? d.split('T')[0] : null
      }).filter(Boolean))
      const sorted = [...days].sort().reverse()
      let count = 0
      let prev = null
      for (const day of sorted) {
        if (!prev) { count = 1; prev = day; continue }
        const diff = (new Date(prev) - new Date(day)) / 86400000
        if (diff === 1) { count++; prev = day }
        else break
      }
      return count
    },

    // 图表辅助
    pointLeft(idx) {
      const n = this.chartReports.length
      if (n <= 1) return 50
      return 5 + (idx / (n - 1)) * 90
    },
    lineStyle(idx) {
      const curr = this.chartReports[idx]
      const next = this.chartReports[idx + 1]
      const n = this.chartReports.length
      const x1 = this.pointLeft(idx)
      const x2 = this.pointLeft(idx + 1)
      const y1 = curr.overall_score || 0
      const y2 = next.overall_score || 0
      const dx = x2 - x1  // % 单位
      const dy = y2 - y1  // % 单位（bottom）
      const len = Math.sqrt(dx * dx + dy * dy)
      const angle = Math.atan2(-dy, dx) * (180 / Math.PI)
      return {
        width: len + '%',
        transform: `rotate(${angle}deg)`,
        transformOrigin: '0 50%',
        bottom: y1 + '%',
        left: x1 + '%'
      }
    },

    riskLabel(level) {
      return { low: '低风险', medium: '中风险', high: '高风险' }[level] || level
    },
    taskTypeName(type) {
      return { visual: '视觉训练', spelling: '拼字训练', reading: '阅读训练', comprehension: '阅读训练' }[type] || type
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    },
    formatShortDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },
    viewReport(id) {
      uni.navigateTo({ url: `/pages/parent/report/detail?id=${id}` })
    },
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F9FAFB; }

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
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-btn .ph { font-size: 40rpx; color: #6B7280; }
.header-title { font-size: 36rpx; font-weight: 700; color: #1F2937; }

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
.stars-count { font-size: 80rpx; font-weight: 800; color: #FFFFFF; }
.stars-label { font-size: 26rpx; color: rgba(255,255,255,0.8); margin-top: 8rpx; }
.stars-icon { font-size: 120rpx; color: rgba(255,255,255,0.25); }

.section-title { font-size: 36rpx; font-weight: 700; color: #1F2937; margin-bottom: 24rpx; }

/* 关键里程碑 */
.milestone-row {
  display: flex;
  align-items: center;
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 32rpx 40rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}
.milestone-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}
.milestone-icon { font-size: 40rpx; color: #F59E0B; }
.milestone-icon.fire { color: #EF4444; }
.milestone-icon.green { color: #10B981; }
.milestone-val { font-size: 36rpx; font-weight: 800; color: #1F2937; }
.milestone-label { font-size: 20rpx; color: #9CA3AF; }
.milestone-divider {
  width: 1rpx;
  height: 64rpx;
  background: #F3F4F6;
  flex-shrink: 0;
}

/* 趋势图卡片 */
.trend-chart-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 40rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.chart-legend {
  display: flex;
  gap: 32rpx;
  margin-bottom: 24rpx;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 22rpx;
  color: #6B7280;
}
.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}
.legend-item.low .legend-dot { background: #10B981; }
.legend-item.medium .legend-dot { background: #F59E0B; }
.legend-item.high .legend-dot { background: #EF4444; }

.chart-wrap {
  display: flex;
  gap: 16rpx;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 8rpx 0 40rpx;
  width: 60rpx;
  flex-shrink: 0;
}
.y-label { font-size: 18rpx; color: #D1D5DB; text-align: right; }

.chart-body {
  flex: 1;
  position: relative;
  height: 300rpx;
}

.grid-line {
  position: absolute;
  left: 0; right: 0;
  height: 1rpx;
  background: #F3F4F6;
}

.chart-points {
  position: absolute;
  inset: 0;
  bottom: 40rpx;
}

.chart-point-wrap {
  position: absolute;
  bottom: 0;
  transform: translateX(-50%);
}

.chart-line {
  position: absolute;
  height: 3rpx;
  background: #BFDBFE;
  transform-origin: 0 50%;
}

.chart-dot {
  position: absolute;
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  transform: translate(-50%, 50%);
  border: 4rpx solid #FFFFFF;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.15);
  cursor: pointer;
}
.chart-dot.low { background: #10B981; }
.chart-dot.medium { background: #F59E0B; }
.chart-dot.high { background: #EF4444; }

.dot-tooltip {
  position: absolute;
  bottom: 32rpx;
  left: 50%;
  transform: translateX(-50%);
  background: #374151;
  color: #FFFFFF;
  font-size: 18rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s;
}
.chart-dot:active .dot-tooltip { opacity: 1; }

.x-axis {
  position: absolute;
  bottom: 0;
  left: 0; right: 0;
  height: 40rpx;
}
.x-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 18rpx;
  color: #9CA3AF;
  bottom: 0;
}

/* 趋势分析文字 */
.trend-analysis {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #EFF6FF;
  border-radius: 32rpx;
  padding: 32rpx 40rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DBEAFE;
}
.trend-analysis-icon {
  font-size: 40rpx;
  color: #3B82F6;
  flex-shrink: 0;
}
.trend-analysis-text {
  font-size: 28rpx;
  color: #1D4ED8;
  font-weight: 600;
  line-height: 1.5;
}

/* 历史列表 */
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
.trend-dot { width: 20rpx; height: 20rpx; border-radius: 50%; flex-shrink: 0; }
.trend-dot.low { background: #10B981; }
.trend-dot.medium { background: #F59E0B; }
.trend-dot.high { background: #EF4444; }
.trend-info { flex: 1; }
.trend-title { font-size: 28rpx; font-weight: 700; color: #374151; }
.trend-date { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }
.trend-score { font-size: 32rpx; font-weight: 700; margin-right: 16rpx; }
.trend-score.low { color: #10B981; }
.trend-score.medium { color: #F59E0B; }
.trend-score.high { color: #EF4444; }
.trend-badge { font-size: 20rpx; font-weight: 700; padding: 6rpx 20rpx; border-radius: 16rpx; }
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
.task-icon-wrap .ph { font-size: 48rpx; color: #10B981; }
.task-info { flex: 1; }
.task-name { font-size: 28rpx; font-weight: 700; color: #374151; }
.task-date { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }
.task-star { display: flex; align-items: center; gap: 8rpx; font-size: 24rpx; font-weight: 700; color: #F59E0B; }
.task-star .ph { font-size: 28rpx; }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx;
  margin-bottom: 48rpx;
}
.empty-state .ph { font-size: 80rpx; color: #D1D5DB; margin-bottom: 24rpx; }
.empty-text { font-size: 26rpx; color: #9CA3AF; }
</style>
