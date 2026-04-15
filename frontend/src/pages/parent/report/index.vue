<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">评估报告</view>
      <button class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text> 问问AI
      </button>
    </view>

    <view class="page-content">
      <!-- 有报告时显示 -->
      <template v-if="latestReport">
        <!-- 总体结论卡片 -->
        <view class="conclusion-card">
          <view class="report-time">生成时间：{{ formatDate(latestReport.created_at) }}</view>
          <view class="conclusion-row">
            <view class="conclusion-indicator" :class="latestReport.risk_level"></view>
            <view class="conclusion-title">{{ riskTitle(latestReport.risk_level) }}</view>
          </view>
          <view class="conclusion-desc">{{ latestReport.summary }}</view>
        </view>

        <!-- 能力多维剖析 -->
        <view class="section-title">能力多维剖析</view>
        <view class="ability-card">
          <!-- SVG 雷达图 -->
          <view class="radar-wrap" v-if="radarPoints.length > 0">
            <svg viewBox="0 0 300 300" class="radar-svg">
              <!-- 背景网格 -->
              <polygon
                v-for="level in [1,2,3,4]"
                :key="level"
                :points="getRadarPolygon(level * 25)"
                fill="none"
                stroke="#F3F4F6"
                stroke-width="1"
              />
              <!-- 轴线 -->
              <line
                v-for="(axis, i) in radarAxes"
                :key="'axis'+i"
                x1="150" y1="150"
                :x2="axis.x" :y2="axis.y"
                stroke="#E5E7EB"
                stroke-width="1"
              />
              <!-- 数据区域 -->
              <polygon
                :points="radarDataPoints"
                fill="rgba(59,130,246,0.15)"
                stroke="#3B82F6"
                stroke-width="2"
              />
              <!-- 数据点 -->
              <circle
                v-for="(pt, i) in radarPoints"
                :key="'pt'+i"
                :cx="pt.x" :cy="pt.y"
                r="5"
                :fill="pt.color"
                stroke="#FFFFFF"
                stroke-width="2"
              />
              <!-- 维度标签 -->
              <text
                v-for="(axis, i) in radarAxes"
                :key="'lbl'+i"
                :x="axis.labelX" :y="axis.labelY"
                text-anchor="middle"
                dominant-baseline="middle"
                font-size="11"
                fill="#6B7280"
              >{{ axis.shortName }}</text>
            </svg>
          </view>

          <view class="ability-item" v-for="(score, dim) in parsedDimensions" :key="dim">
            <view class="ability-header">
              <view class="ability-name">{{ dimName(dim) }}</view>
              <view class="ability-tag" :class="scoreClass(score)">{{ scoreLabel(score) }}</view>
            </view>
            <view class="ability-progress">
              <view class="progress-track">
                <view class="progress-fill" :class="scoreClass(score)" :style="{ width: score + '%' }"></view>
              </view>
            </view>
            <view class="ability-hint">{{ dimHint(dim, score) }}</view>
          </view>
        </view>

        <!-- 历史报告列表 -->
        <view class="section-title" v-if="reports.length > 1">历史记录</view>
        <view class="history-list" v-if="reports.length > 1">
          <view
            class="history-item"
            v-for="r in reports.slice(1)"
            :key="r.id"
            @click="viewDetail(r.id)"
          >
            <view class="history-dot" :class="r.risk_level"></view>
            <view class="history-info">
              <view class="history-date">{{ formatDate(r.created_at) }}</view>
              <view class="history-score">{{ r.overall_score }}分</view>
            </view>
            <view class="history-badge" :class="r.risk_level">{{ riskTitle(r.risk_level) }}</view>
          </view>
        </view>

        <!-- 家长建议 -->
        <view class="section-title">干预建议</view>
        <view class="advice-card">
          <view class="advice-header">
            <text class="ph ph-info"></text>
            <view class="advice-title">专业建议</view>
          </view>
          <view class="advice-desc">{{ latestReport.recommendations }}</view>
          <button class="advice-btn" @click="goToTraining">查看专属干预方案 →</button>
        </view>

        <!-- 复评建议 -->
        <view class="reassess-card">
          <view class="reassess-header">
            <text class="ph ph-calendar-check"></text>
            <view class="reassess-title">复评建议</view>
          </view>
          <view class="reassess-desc">{{ reassessText }}</view>
          <button class="reassess-btn" @click="goToScreening">立即复评</button>
        </view>

        <!-- 高风险专业引导 -->
        <view class="high-risk-card" v-if="latestReport.risk_level === 'high'">
          <view class="high-risk-header">
            <text class="ph ph-warning-circle high-risk-icon"></text>
            <view class="high-risk-title">建议专业评估</view>
          </view>
          <view class="high-risk-desc">根据本次评估结果，建议尽快联系专业机构进行全面评估，以获得更准确的诊断和干预方案。</view>
          <button class="high-risk-btn" @click="goToAiChat">了解更多</button>
        </view>
      </template>

      <!-- 无报告时 -->
      <view class="empty-state" v-else>
        <view class="empty-icon"><text class="ph ph-file-text"></text></view>
        <view class="empty-title">暂无评估报告</view>
        <view class="empty-desc">完成筛查后，系统将自动生成详细的能力评估报告</view>
        <button class="empty-btn" @click="goToScreening">立即发起筛查</button>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/report/index"></tab-bar>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getReports } from '../../../api/report.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      children: [],
      currentChild: null,
      reports: [],
      latestReport: null,
      parsedDimensions: {}
    }
  },
  computed: {
    radarDimOrder() {
      return ['visual_discrimination','phonological','character_order','spelling','reading_comprehension','semantic_integration','information_extraction','attention']
    },
    radarAxes() {
      const dims = this.radarDimOrder
      const n = dims.length
      const cx = 150, cy = 150, r = 100, labelR = 125
      const shortNames = {
        visual_discrimination: '视觉', phonological: '音形',
        character_order: '字序', spelling: '拼写',
        reading_comprehension: '阅读', semantic_integration: '语义',
        information_extraction: '提取', attention: '注意力'
      }
      return dims.map((dim, i) => {
        const angle = (2 * Math.PI * i / n) - Math.PI / 2
        return {
          x: cx + r * Math.cos(angle),
          y: cy + r * Math.sin(angle),
          labelX: cx + labelR * Math.cos(angle),
          labelY: cy + labelR * Math.sin(angle),
          shortName: shortNames[dim] || dim
        }
      })
    },
    radarPoints() {
      if (!this.parsedDimensions || Object.keys(this.parsedDimensions).length === 0) return []
      const dims = this.radarDimOrder
      const n = dims.length
      const cx = 150, cy = 150, r = 100
      return dims.map((dim, i) => {
        const score = this.parsedDimensions[dim] || 0
        const angle = (2 * Math.PI * i / n) - Math.PI / 2
        const dist = (score / 100) * r
        const color = score >= 75 ? '#10B981' : score >= 60 ? '#F59E0B' : '#EF4444'
        return {
          x: cx + dist * Math.cos(angle),
          y: cy + dist * Math.sin(angle),
          color
        }
      })
    },
    radarDataPoints() {
      return this.radarPoints.map(p => `${p.x},${p.y}`).join(' ')
    },
    reassessText() {
      if (!this.latestReport) return ''
      const level = this.latestReport.risk_level
      if (level === 'low') return '建议1个月后复评，持续跟踪能力变化'
      if (level === 'medium') return '建议2周后复评，观察训练效果'
      return '建议尽快复评，密切关注变化'
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
          this.currentChild = saved
            ? (this.children.find(c => c.id === saved.id) || this.children[0])
            : this.children[0]
          setCurrentChild(this.currentChild)
          await this.loadReports()
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadReports() {
      if (!this.currentChild) return
      try {
        this.reports = await getReports(this.currentChild.id)
        this.latestReport = this.reports[0] || null
        if (this.latestReport?.dimensions) {
          try {
            this.parsedDimensions = JSON.parse(this.latestReport.dimensions)
          } catch (e) {
            this.parsedDimensions = {}
          }
        }
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    riskTitle(level) {
      return { low: '低风险 / 正常', medium: '中风险 / 需关注', high: '高风险 / 重点关注' }[level] || level
    },
    dimName(dim) {
      const map = {
        visual_discrimination: '视觉辨识能力', phonological: '音形映射能力',
        character_order: '字序组织能力', spelling: '拼写输出能力',
        reading_comprehension: '阅读理解能力', semantic_integration: '语义整合能力',
        information_extraction: '信息提取能力', attention: '任务注意力'
      }
      return map[dim] || dim
    },
    dimHint(dim, score) {
      const good = {
        visual_discrimination: '形近字辨别能力良好，视觉扫描稳定。',
        phonological:          '音形联结反应正常，拼音识字能力稳定。',
        character_order:       '汉字笔顺记忆良好，字形组织稳定。',
        spelling:              '拼写输出稳定，作答犹豫较少。',
        reading_comprehension: '能准确理解句子和短文的核心意思。',
        semantic_integration:  '句间关系理解正常，语义整合能力良好。',
        information_extraction:'能从文中快速定位关键信息。',
        attention:             '能持续专注完成任务，注意力稳定。'
      }
      const weak = {
        visual_discrimination: '易混淆形近字，视觉扫描时容易漏字或看错。',
        phonological:          '音形联结反应偏慢，拼音与汉字对应存在困难。',
        character_order:       '书写时部件位置偶有颠倒，笔顺记忆不稳定。',
        spelling:              '作答犹豫期较长，部件颠倒或替换发生率偏高。',
        reading_comprehension: '理解句子和短文时存在困难，容易遗漏关键信息。',
        semantic_integration:  '句间关系理解存在偏差，语义整合能力需加强。',
        information_extraction:'从文中提取关键信息时容易遗漏或混淆。',
        attention:             '持续专注能力不足，连续任务中表现有波动。'
      }
      if (score >= 75) return good[dim] || ''
      if (score >= 60) return `${weak[dim] || ''} 建议适当加强练习。`
      return `${weak[dim] || ''} 这是当前需要重点关注的能力维度。`
    },
    scoreClass(score) {
      if (score >= 75) return 'green'
      if (score >= 60) return 'orange'
      return 'red'
    },
    scoreLabel(score) {
      if (score >= 75) return '良好'
      if (score >= 60) return '中等'
      return '偏弱'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    viewDetail(id) {
      uni.navigateTo({ url: `/pages/parent/report/detail?id=${id}` })
    },
    goToAiChat() {
      uni.navigateTo({ url: '/pages/parent/ai-chat/index' })
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/parent/training/index' })
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    getRadarPolygon(pct) {
      const dims = this.radarDimOrder
      const n = dims.length
      const cx = 150, cy = 150, r = 100
      return dims.map((_, i) => {
        const angle = (2 * Math.PI * i / n) - Math.PI / 2
        const dist = (pct / 100) * r
        return `${cx + dist * Math.cos(angle)},${cy + dist * Math.sin(angle)}`
      }).join(' ')
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
  padding-bottom: 196rpx;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid #F3F4F6;
}

.header-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #F3E8FF;
  color: #7C3AED;
  border: 1rpx solid #EDE9FE;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  font-size: 22rpx;
  font-weight: 700;
}

.ai-btn .ph {
  font-size: 28rpx;
}

/* 页面内容 */
.page-content {
  padding: 48rpx 48rpx;
}

/* 结论卡片 */
.conclusion-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.report-time {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 16rpx;
}

.conclusion-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.conclusion-indicator {
  width: 6rpx;
  height: 48rpx;
  border-radius: 3rpx;
}

.conclusion-indicator.orange {
  background: #F59E0B;
}

.conclusion-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #1F2937;
}

.conclusion-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
}

.conclusion-desc .highlight {
  font-weight: 700;
  color: #F59E0B;
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 能力卡片 */
.ability-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.ability-item {
  margin-bottom: 40rpx;
}

.ability-item:last-child {
  margin-bottom: 0;
}

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 12rpx;
}

.ability-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.ability-tag {
  font-size: 20rpx;
  font-weight: 700;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.ability-tag.orange {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.ability-tag.green {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.ability-progress {
  margin-bottom: 12rpx;
}

.progress-track {
  height: 16rpx;
  background: #F3F4F6;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s;
}

.progress-fill.orange {
  background: #F59E0B;
}

.progress-fill.green {
  background: #10B981;
}

.ability-hint {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 建议卡片 */
.advice-card {
  background: #EFF6FF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DBEAFE;
  position: relative;
}

.advice-icon {
  position: absolute;
  top: 32rpx;
  right: 32rpx;
  font-size: 80rpx;
  color: #BFDBFE;
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.advice-header .ph {
  font-size: 28rpx;
  color: #3B82F6;
}

.advice-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.advice-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 32rpx;
}

.advice-desc .highlight {
  font-weight: 700;
  color: #3B82F6;
}

.advice-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #DBEAFE;
  color: #3B82F6;
  border-radius: 32rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

/* 风险颜色 */
.conclusion-indicator.low { background: #10B981; }
.conclusion-indicator.medium { background: #F59E0B; }
.conclusion-indicator.high { background: #EF4444; }

.ability-tag.red { background: rgba(239,68,68,0.1); color: #EF4444; }
.progress-fill.red { background: #EF4444; }

/* 历史列表 */
.history-list {
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 16rpx 32rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
}

.history-item:last-child { border-bottom: none; }

.history-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.history-dot.low { background: #10B981; }
.history-dot.medium { background: #F59E0B; }
.history-dot.high { background: #EF4444; }

.history-info { flex: 1; }
.history-date { font-size: 26rpx; color: #374151; font-weight: 500; }
.history-score { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }

.history-badge {
  font-size: 20rpx;
  font-weight: 700;
  padding: 6rpx 20rpx;
  border-radius: 16rpx;
}

.history-badge.low { background: #ECFDF5; color: #10B981; }
.history-badge.medium { background: #FEF3C7; color: #F59E0B; }
.history-badge.high { background: #FEF2F2; color: #EF4444; }

/* 雷达图 */
.radar-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 40rpx;
}
.radar-svg {
  width: 300rpx;
  height: 300rpx;
}

/* 复评建议卡片 */
.reassess-card {
  background: #F0FDF4;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #BBF7D0;
}
.reassess-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}
.reassess-header .ph {
  font-size: 32rpx;
  color: #10B981;
}
.reassess-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}
.reassess-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 32rpx;
}
.reassess-btn {
  width: 100%;
  background: #10B981;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 高风险专业引导卡片 */
.high-risk-card {
  background: #FEF2F2;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 2rpx solid #FECACA;
}
.high-risk-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
}
.high-risk-icon {
  font-size: 40rpx;
  color: #EF4444;
}
.high-risk-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #DC2626;
}
.high-risk-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 32rpx;
}
.high-risk-btn {
  width: 100%;
  background: #EF4444;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 48rpx;
}

.empty-icon .ph { font-size: 96rpx; color: #D1D5DB; }
.empty-title { font-size: 36rpx; font-weight: 700; color: #374151; margin: 32rpx 0 16rpx; }
.empty-desc { font-size: 26rpx; color: #9CA3AF; text-align: center; line-height: 1.6; margin-bottom: 48rpx; }

.empty-btn {
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 24rpx 64rpx;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
