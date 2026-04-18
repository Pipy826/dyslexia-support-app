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
      if (!scores || scores.length < 2) {
        this.dimensionHistory = []
        return
      }
      const dimNames = {
        visual_discrimination: '视觉辨识',
        phonological: '音形映射',
        character_order: '字序组织',
        spelling: '拼写输出',
        reading_comprehension: '阅读理解',
        semantic_integration: '语义整合',
        information_extraction: '信息提取',
        attention: '注意力',
      }
      // 收集所有出现过的维度
      const allDims = new Set()
      scores.forEach(s => {
        const dims = s.dimensions || {}
        Object.keys(dims).forEach(d => allDims.add(d))
      })
      this.dimensionHistory = [...allDims].map(key => {
        const dimScores = scores.map(s => {
          const dims = s.dimensions || {}
          return dims[key] !== undefined ? dims[key] : null
        }).filter(v => v !== null)
        const first = dimScores[0] ?? 0
        const last = dimScores[dimScores.length - 1] ?? 0
        return {
          key,
          name: dimNames[key] || key,
          scores: dimScores,
          trend: last - first,
        }
      })
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
/* 成长分析 - 禁止横向滚动，纯竖向布局 */

/* 最外层锁死宽度，禁止横向溢出 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

/* ── 头部 ── */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255,255,255,0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.06);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.back-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }

.header-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
  min-width: 0;
  overflow: hidden;
}

.ai-badge {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  padding: 8rpx 18rpx;
  border-radius: 14rpx;
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-shrink: 0;
}
.ai-badge .ph { font-size: 22rpx; margin-right: 6rpx; }

/* ── 内容区：锁死宽度 ── */
.page-content {
  padding: 24rpx 28rpx;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* ── 孩子信息栏 ── */
.child-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 24rpx;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.child-avatar-sm {
  width: 52rpx;
  height: 52rpx;
  min-width: 52rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 700;
  color: #4F9EF8;
  flex-shrink: 0;
  margin-right: 12rpx;
}

.child-bar-name {
  flex: 1;
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.report-count-badge {
  font-size: 18rpx;
  color: #A0AEC0;
  background: #F0F0F0;
  padding: 5rpx 14rpx;
  border-radius: 10rpx;
  font-weight: 600;
  flex-shrink: 0;
  margin-left: 8rpx;
  white-space: nowrap;
}

/* ── 区域标题 ── */
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
  padding-left: 14rpx;
  border-left: 4rpx solid #4F9EF8;
  line-height: 1.4;
  box-sizing: border-box;
  width: 100%;
}

/* ── 图表卡片 ── */
.chart-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;   /* 关键：截断超出内容 */
}

.chart-empty {
  text-align: center;
  padding: 48rpx 0;
  color: #A0AEC0;
  font-size: 24rpx;
}
.chart-empty .ph { font-size: 64rpx; color: #D1D5DB; display: block; margin-bottom: 12rpx; }

/* 图表区域：y轴固定 + 柱体区自适应，不超出 */
.chart-area {
  display: flex;
  flex-direction: row;
  height: 240rpx;
  margin-bottom: 24rpx;
  width: 100%;
  overflow: hidden;   /* 关键 */
}

.chart-y-labels {
  width: 44rpx;
  min-width: 44rpx;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-bottom: 36rpx;
  margin-right: 4rpx;
}
.y-label { font-size: 16rpx; color: #A0AEC0; text-align: right; }

.chart-body {
  flex: 1;
  min-width: 0;       /* 关键：允许收缩 */
  max-width: 100%;    /* 关键：不超出父容器 */
  position: relative;
  overflow: hidden;   /* 关键 */
}

.chart-grid {
  position: absolute;
  top: 0; left: 0; right: 0;
  bottom: 36rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.grid-line { height: 1rpx; background: #F0F0F0; }

.chart-bars {
  position: absolute;
  top: 0; left: 0; right: 0;
  bottom: 36rpx;
  display: flex;
  flex-direction: row;
  align-items: flex-end;
  overflow: hidden;   /* 关键：超出的柱子直接截断 */
}

.chart-bar-wrap {
  flex: 1;
  min-width: 0;       /* 关键：允许收缩到0 */
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  position: relative;
  padding: 0 2rpx;
  box-sizing: border-box;
  overflow: hidden;
}

.chart-bar-label {
  font-size: 16rpx;
  color: #718096;
  font-weight: 700;
  margin-bottom: 3rpx;
  line-height: 1;
  white-space: nowrap;
  overflow: hidden;
}

.chart-bar {
  width: 100%;
  border-radius: 4rpx 4rpx 0 0;
  min-height: 6rpx;
}
.chart-bar.green { background: linear-gradient(180deg, #4ADE80, #22C55E); }
.chart-bar.orange { background: linear-gradient(180deg, #FFB74D, #F57F17); }
.chart-bar.red { background: linear-gradient(180deg, #FF8E8E, #FF6B6B); }
.chart-bar.blue { background: linear-gradient(180deg, #93C5FD, #4F9EF8); }

/* 日期标签：隐藏超出部分，不撑宽 */
.chart-bar-date {
  position: absolute;
  bottom: -32rpx;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 16rpx;
  color: #A0AEC0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

/* 图例 */
.chart-legend {
  display: flex;
  flex-direction: row;
  justify-content: center;
  margin-top: 4rpx;
  width: 100%;
  overflow: hidden;
}
.legend-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-size: 20rpx;
  color: #718096;
  margin: 0 12rpx;
  flex-shrink: 0;
}
.legend-dot {
  width: 12rpx;
  height: 12rpx;
  min-width: 12rpx;
  border-radius: 50%;
  margin-right: 6rpx;
}
.legend-dot.green { background: #22C55E; }
.legend-dot.orange { background: #F57F17; }
.legend-dot.red { background: #FF6B6B; }

/* ── AI 分析卡片 ── */
.analysis-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  border: 1rpx solid #BFDBFE;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.analysis-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  margin-bottom: 16rpx;
  width: 100%;
  overflow: hidden;
}

.analysis-avatar {
  width: 52rpx;
  height: 52rpx;
  min-width: 52rpx;
  border-radius: 14rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 12rpx;
}
.analysis-avatar .ph { font-size: 26rpx; color: #FFFFFF; }

.analysis-title {
  flex: 1;
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  min-width: 0;
  overflow: hidden;
}

.refresh-btn {
  width: 48rpx;
  height: 48rpx;
  min-width: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.refresh-btn .ph { font-size: 26rpx; color: #4F9EF8; }

.analysis-loading {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 12rpx 0;
  overflow: hidden;
}
.loading-spinner {
  width: 36rpx;
  height: 36rpx;
  min-width: 36rpx;
  border: 4rpx solid #BFDBFE;
  border-top-color: #4F9EF8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  flex-shrink: 0;
  margin-right: 12rpx;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: #4F9EF8; font-weight: 600; min-width: 0; overflow: hidden; }

.analysis-content {
  font-size: 26rpx;
  color: #2D3748;
  line-height: 1.8;
  word-break: break-all;
  word-wrap: break-word;
}

.analysis-empty { text-align: center; padding: 16rpx 0; }
.analysis-empty-text { font-size: 24rpx; color: #718096; line-height: 1.6; margin-bottom: 20rpx; }

.go-screen-btn {
  display: inline-flex;
  flex-direction: row;
  align-items: center;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 14rpx;
  padding: 16rpx 36rpx;
  font-size: 24rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2);
}
.go-screen-btn .ph { font-size: 24rpx; margin-right: 8rpx; }

/* ── 维度历史 ── */
.dimension-history-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;   /* 关键：截断超出的分数点 */
}

.dim-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #F5F5F5;
  width: 100%;
  overflow: hidden;   /* 关键 */
}
.dim-row:last-child { border-bottom: none; }

.dim-name {
  width: 112rpx;
  min-width: 112rpx;
  font-size: 22rpx;
  color: #2D3748;
  font-weight: 600;
  flex-shrink: 0;
  line-height: 1.3;
}

/* 分数点区域：flex-wrap + overflow:hidden，超出的点不显示 */
.dim-scores {
  flex: 1;
  min-width: 0;
  max-width: 100%;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  overflow: hidden;   /* 关键：超出的分数点直接截断 */
  align-content: flex-start;
}

.dim-score-dot {
  width: 44rpx;
  height: 44rpx;
  min-width: 44rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 2rpx;
  flex-shrink: 0;
}
.dim-score-dot.green { background: rgba(34,197,94,0.12); }
.dim-score-dot.orange { background: rgba(245,127,23,0.12); }
.dim-score-dot.red { background: rgba(255,107,107,0.12); }

.dim-score-val { font-size: 17rpx; font-weight: 700; }
.dim-score-dot.green .dim-score-val { color: #22C55E; }
.dim-score-dot.orange .dim-score-val { color: #F57F17; }
.dim-score-dot.red .dim-score-val { color: #FF6B6B; }

.dim-trend {
  width: 68rpx;
  min-width: 68rpx;
  font-size: 20rpx;
  font-weight: 700;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  flex-shrink: 0;
  margin-left: 4rpx;
  overflow: hidden;
}
.dim-trend .ph { font-size: 20rpx; margin-right: 3rpx; }
.dim-trend.up { color: #22C55E; }
.dim-trend.down { color: #FF6B6B; }
.dim-trend.flat { color: #A0AEC0; }
</style>
