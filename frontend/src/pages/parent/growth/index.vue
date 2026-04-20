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
          <!-- SVG 折线图，宽度自适应 -->
          <line-chart :scores="scores" :width="chartWidth" :height="180"></line-chart>
        </view>

        <!-- 图例 -->
        <view class="chart-legend">
          <view class="legend-item"><view class="legend-dot green"></view>低风险</view>
          <view class="legend-item"><view class="legend-dot orange"></view>中风险</view>
          <view class="legend-item"><view class="legend-dot red"></view>高风险</view>
        </view>
      </view>

      <!-- AI 趋势分析 -->
      <view class="section-title">AI 趋势分析</view>
      <!-- 结构化趋势标签 -->
      <view class="trend-badge-row" v-if="trendLabel">
        <view class="trend-badge" :class="trendBadgeClass">
          <text :class="'ph ' + trendBadgeIcon"></text>
          {{ trendLabel }}
        </view>
      </view>
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
      <view class="dimension-history-card" v-if="dimensionHistory.length > 0">        <view
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
              :class="s >= 75 ? 'green' : s >= 60 ? 'orange' : 'red'"
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

      <!-- 干预阶段记录 -->
      <view class="section-title" v-if="milestoneRecords.length > 0">干预阶段记录</view>
      <view class="milestone-list" v-if="milestoneRecords.length > 0">
        <view class="milestone-item" v-for="r in milestoneRecords" :key="r.id">
          <view class="milestone-dot" :class="r.record_type === 'screening' ? 'blue' : 'green'"></view>
          <view class="milestone-content">
            <view class="milestone-title">{{ r.title }}</view>
            <view class="milestone-desc" v-if="r.content">{{ r.content }}</view>
            <view class="milestone-date">{{ formatShortDate(r.created_at) }}</view>
          </view>
        </view>
      </view>

      <!-- 家长备注 -->
      <view class="section-title">成长备注</view>
      <view class="notes-card">
        <view class="notes-list" v-if="growthNotes.length > 0">
          <view class="note-item" v-for="note in growthNotes" :key="note.id">
            <view class="note-date">{{ formatShortDate(note.created_at) }}</view>
            <view class="note-content">{{ note.content }}</view>
          </view>
        </view>
        <view class="notes-empty" v-else>
          <text class="ph ph-note-pencil"></text>
          <view>记录孩子的成长点滴</view>
        </view>
        <!-- 添加备注 -->
        <view class="note-input-wrap" v-if="showNoteInput">
          <textarea
            class="note-input"
            v-model="noteText"
            placeholder="记录今天的观察或感受..."
            maxlength="200"
          />
          <view class="note-input-actions">
            <view class="note-cancel" @click="showNoteInput = false; noteText = ''">取消</view>
            <button class="note-submit" @click="submitNote" :disabled="!noteText.trim()">保存</button>
          </view>
        </view>
        <button class="add-note-btn" @click="showNoteInput = true" v-else>
          <text class="ph ph-plus"></text> 添加备注
        </button>
      </view>

      <!-- 底部占位 -->
      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getGrowthAnalysis } from '../../../api/ai.js'
import { getReports } from '../../../api/report.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { getGrowthRecords, createGrowthRecord } from '../../../api/training.js'
import LineChart from '../../../components/charts/LineChart.vue'

export default {
  components: { LineChart },
  data() {
    return {
      childId: null,
      childName: '',
      reportCount: 0,
      scores: [],
      analysis: '',
      analysisLoading: false,
      dimensionHistory: [],
      trendLabel: '',  // 结构化趋势标签
      chartWidth: 300,
      // 备注
      growthNotes: [],
      milestoneRecords: [],
      showNoteInput: false,
      noteText: '',
    }
  },

  onLoad(options) {
    // 计算图表宽度：屏幕宽度 - 页面左右 padding(28*2) - 卡片 padding(20*2)，单位 px
    try {
      const info = uni.getSystemInfoSync()
      const rpxRatio = info.windowWidth / 750
      this.chartWidth = Math.floor(info.windowWidth - (28 + 20) * 2 * rpxRatio)
    } catch (e) {
      this.chartWidth = 300
    }
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

  computed: {
    trendBadgeClass() {
      const map = { '稳定改善': 'green', '波动改善': 'blue', '基本稳定': 'gray', '持续无改善': 'orange', '可能恶化': 'red' }
      return map[this.trendLabel] || 'gray'
    },
    trendBadgeIcon() {
      const map = { '稳定改善': 'ph-trend-up', '波动改善': 'ph-trend-up', '基本稳定': 'ph-minus', '持续无改善': 'ph-warning', '可能恶化': 'ph-trend-down' }
      return map[this.trendLabel] || 'ph-minus'
    },
  },

  methods: {
    async loadAnalysis() {
      if (!this.childId || this.analysisLoading) return
      this.analysisLoading = true
      this.analysis = ''

      // 第一步：先从报告接口快速拿到基础数据（不依赖 AI，不会超时）
      try {
        const reports = await getReports(this.childId)
        if (reports && reports.length > 0) {
          this.reportCount = reports.length
          // 取最新报告的孩子名（报告里没有，用已有的 childName）
          this.scores = reports.map(r => ({
            date: r.created_at ? r.created_at.slice(0, 10) : '',
            score: r.overall_score || 0,
            risk_level: r.risk_level || 'medium',
            dimensions: (() => {
              try { return typeof r.dimensions === 'string' ? JSON.parse(r.dimensions) : (r.dimensions || {}) }
              catch (e) { return {} }
            })(),
          })).reverse() // 升序（旧→新）
          this.buildDimensionHistory(this.scores)
          this.trendLabel = this._calcTrendLabel(this.scores)
        }
      } catch (e) {
        console.warn('加载报告数据失败', e)
      }

      // 第二步：调 AI 接口获取智能分析（可能较慢，失败时降级）
      try {
        const res = await getGrowthAnalysis(this.childId)
        if (res.child_name) this.childName = res.child_name
        if (res.report_count) this.reportCount = res.report_count
        if (res.scores && res.scores.length > 0) {
          this.scores = res.scores
          this.buildDimensionHistory(res.scores)
          this.trendLabel = this._calcTrendLabel(res.scores)
        }
        this.analysis = res.analysis || this._localFallbackAnalysis()
      } catch (e) {
        console.warn('AI 分析获取失败，使用本地降级', e)
        // 降级：用本地数据生成分析文字，不报错
        this.analysis = this._localFallbackAnalysis()
      } finally {
        this.analysisLoading = false
      }

      this.loadNotes()
    },

    _localFallbackAnalysis() {
      if (!this.scores || this.scores.length === 0) return ''
      const label = this.trendLabel
      const count = this.scores.length
      const latest = this.scores[this.scores.length - 1]?.score || 0
      const first = this.scores[0]?.score || 0
      const delta = latest - first
      if (label === '稳定改善') return `经过 ${count} 次筛查，${this.childName || '孩子'}的综合得分从 ${first} 分提升到 ${latest} 分，整体呈稳定上升趋势，训练效果良好，请继续保持。`
      if (label === '波动改善') return `经过 ${count} 次筛查，${this.childName || '孩子'}的综合得分整体有所提升（${first}→${latest}分），过程中有一定波动，属于正常现象，建议保持规律训练。`
      if (label === '可能恶化') return `近期筛查显示得分有所下降（${first}→${latest}分），建议检查训练频率是否规律，并关注孩子的状态，必要时调整训练方案。`
      if (label === '持续无改善') return `经过 ${count} 次筛查，得分基本维持在 ${latest} 分左右，建议尝试调整训练方式或增加训练频率，也可咨询专业人士获取建议。`
      return `已完成 ${count} 次筛查，当前综合得分 ${latest} 分，整体表现基本稳定，建议继续坚持每日训练。`
    },

    async loadNotes() {
      if (!this.childId) return
      try {
        const records = await getGrowthRecords(this.childId)
        // 家长手动备注
        this.growthNotes = records.filter(r => r.record_type === 'note').slice(0, 10)
        // 系统自动生成的里程碑记录（筛查/训练）
        this.milestoneRecords = records.filter(r => r.record_type !== 'note').slice(0, 5)
      } catch (e) { console.warn('加载备注失败', e) }
    },

    async submitNote() {
      if (!this.noteText.trim() || !this.childId) return
      try {
        await createGrowthRecord({
          child_id: this.childId,
          record_type: 'note',
          title: '家长备注',
          content: this.noteText.trim(),
        })
        this.noteText = ''
        this.showNoteInput = false
        uni.showToast({ title: '备注已保存', icon: 'success' })
        await this.loadNotes()
      } catch (e) {
        uni.showToast({ title: '保存失败', icon: 'none' })
      }
    },

    buildDimensionHistory(scores) {
      if (!scores || scores.length < 2) {
        this.dimensionHistory = []
        return
      }
      const dimNames = {
        visual_discrimination:    '视觉辨识',
        phonological:             '音形映射',
        character_order:          '字序组织',
        spelling:                 '拼写输出',
        reading_comprehension:    '阅读理解',
        semantic_integration:     '语义整合',
        information_extraction:   '信息提取',
        attention:                '注意力',
        working_memory_capacity:  '工作记忆',
        short_term_memory:        '短时记忆',
        rapid_naming_speed:       '快速命名',
        phonological_awareness:   '音韵意识',
        fine_motor_control:       '精细动作',
        visual_motor_integration: '视动整合',
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

    _calcTrendLabel(scores) {
      if (!scores || scores.length < 2) return ''
      const vals = scores.map(s => s.score || 0)
      const first = vals[0], last = vals[vals.length - 1]
      const delta = last - first
      // 检查是否有波动
      const diffs = vals.slice(1).map((v, i) => v - vals[i])
      const hasUp = diffs.some(d => d > 3)
      const hasDown = diffs.some(d => d < -3)
      if (delta > 8) return hasDown ? '波动改善' : '稳定改善'
      if (delta < -8) return '可能恶化'
      if (Math.abs(delta) <= 5 && !hasUp && !hasDown) return '基本稳定'
      if (delta > 0 && hasDown) return '波动改善'
      if (delta <= 0 && scores.length >= 3) return '持续无改善'
      return '基本稳定'
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

/* ── 趋势标签 ── */
.trend-badge-row { margin-bottom: 16rpx; }
.trend-badge {
  display: inline-flex; align-items: center; gap: 8rpx;
  padding: 10rpx 24rpx; border-radius: 20rpx;
  font-size: 24rpx; font-weight: 700;
}
.trend-badge .ph { font-size: 24rpx; }
.trend-badge.green { background: rgba(34,197,94,0.1); color: #22C55E; }
.trend-badge.blue { background: rgba(79,158,248,0.1); color: #4F9EF8; }
.trend-badge.gray { background: #F5F5F5; color: #718096; }
.trend-badge.orange { background: rgba(245,127,23,0.1); color: #F57F17; }
.trend-badge.red { background: rgba(255,107,107,0.1); color: #FF6B6B; }

/* ── 区域标题 ── */
.section-title {  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
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
  overflow: hidden;
}

.chart-empty {
  text-align: center;
  padding: 48rpx 0;
  color: #A0AEC0;
  font-size: 24rpx;
}
.chart-empty .ph { font-size: 64rpx; color: #D1D5DB; display: block; margin-bottom: 12rpx; }

/* SVG 折线图 */
.chart-area { width: 100%; overflow: hidden; margin-bottom: 12rpx; }
.line-chart-svg { width: 100%; height: 200rpx; display: block; }

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

/* ── 里程碑记录 ── */
.milestone-list { background: #FFFFFF; border-radius: 24rpx; padding: 20rpx 28rpx; margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); display: flex; flex-direction: column; gap: 0; }
.milestone-item { display: flex; align-items: flex-start; gap: 16rpx; padding: 16rpx 0; border-bottom: 1rpx solid #F5F5F5; position: relative; }
.milestone-item:last-child { border-bottom: none; }
.milestone-dot { width: 14rpx; height: 14rpx; border-radius: 50%; flex-shrink: 0; margin-top: 8rpx; }
.milestone-dot.blue { background: #4F9EF8; }
.milestone-dot.green { background: #22C55E; }
.milestone-content { flex: 1; }
.milestone-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.milestone-desc { font-size: 22rpx; color: #718096; margin-top: 4rpx; line-height: 1.5; }
.milestone-date { font-size: 18rpx; color: #A0AEC0; margin-top: 4rpx; }

/* ── 备注模块 ── */.notes-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 24rpx;
  margin-bottom: 20rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.notes-list { display: flex; flex-direction: column; gap: 16rpx; margin-bottom: 20rpx; }
.note-item { background: #F8FAFF; border-radius: 16rpx; padding: 16rpx 20rpx; }
.note-date { font-size: 18rpx; color: #A0AEC0; font-weight: 600; margin-bottom: 6rpx; }
.note-content { font-size: 24rpx; color: #2D3748; line-height: 1.6; font-weight: 500; }
.notes-empty { display: flex; flex-direction: column; align-items: center; gap: 10rpx; padding: 24rpx 0; color: #A0AEC0; font-size: 24rpx; margin-bottom: 16rpx; }
.notes-empty .ph { font-size: 48rpx; color: #D1D5DB; }
.note-input-wrap { margin-bottom: 16rpx; }
.note-input { width: 100%; background: #F8FAFF; border: 2rpx solid #E5E7EB; border-radius: 16rpx; padding: 16rpx 20rpx; font-size: 26rpx; color: #2D3748; min-height: 120rpx; box-sizing: border-box; }
.note-input-actions { display: flex; justify-content: flex-end; gap: 16rpx; margin-top: 12rpx; }
.note-cancel { font-size: 24rpx; color: #A0AEC0; font-weight: 600; padding: 10rpx 20rpx; }
.note-submit { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; border-radius: 12rpx; padding: 10rpx 28rpx; font-size: 24rpx; font-weight: 700; }
.add-note-btn { width: 100%; background: #F8FAFF; border: 2rpx dashed #BFDBFE; color: #4F9EF8; border-radius: 16rpx; padding: 20rpx; font-size: 24rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 8rpx; }
.add-note-btn .ph { font-size: 24rpx; }
</style>
