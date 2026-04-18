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
/* 创意报告页面 - 数据可视化 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 160rpx;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.header-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: linear-gradient(135deg, #F5F3FF, #EDE9FE);
  color: #7C3AED;
  border: 1rpx solid #DDD6FE;
  padding: 10rpx 20rpx;
  border-radius: 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  transition: all 0.2s;
}
.ai-btn:active { transform: scale(0.95); }
.ai-btn .ph { font-size: 24rpx; }

.page-content { padding: 24rpx 32rpx; }

.conclusion-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.report-time { font-size: 20rpx; color: #A0AEC0; margin-bottom: 12rpx; font-weight: 500; }

.conclusion-row { display: flex; align-items: center; gap: 12rpx; margin-bottom: 16rpx; }

.conclusion-indicator { width: 5rpx; height: 40rpx; border-radius: 3rpx; }
.conclusion-indicator.low { background: linear-gradient(180deg, #22C55E, #4ADE80); }
.conclusion-indicator.medium { background: linear-gradient(180deg, #F57F17, #FFB74D); }
.conclusion-indicator.high { background: linear-gradient(180deg, #FF6B6B, #FF8E8E); }
.conclusion-indicator.orange { background: linear-gradient(180deg, #F57F17, #FFB74D); }

.conclusion-title { font-size: 40rpx; font-weight: 800; color: #2D3748; }
.conclusion-desc { font-size: 24rpx; color: #718096; line-height: 1.7; font-weight: 500; }
.conclusion-desc .highlight { font-weight: 700; color: #F57F17; }

.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
  display: flex; align-items: center; gap: 8rpx;
}
.section-title::before {
  content: ''; display: inline-block; width: 4rpx; height: 22rpx;
  background: linear-gradient(180deg, #4F9EF8, #A78BFA); border-radius: 2rpx;
}

.ability-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 32rpx;
  margin-bottom: 20rpx; box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.ability-item { margin-bottom: 28rpx; }
.ability-item:last-child { margin-bottom: 0; }

.ability-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10rpx; }
.ability-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }

.ability-tag { font-size: 20rpx; font-weight: 700; padding: 4rpx 14rpx; border-radius: 10rpx; }
.ability-tag.orange { background: rgba(245, 127, 23, 0.1); color: #F57F17; }
.ability-tag.green { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.ability-tag.red { background: rgba(255, 107, 107, 0.1); color: #FF6B6B; }

.ability-progress { margin-bottom: 8rpx; }
.progress-track { height: 10rpx; background: #F0F0F0; border-radius: 5rpx; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 5rpx; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.progress-fill.orange { background: linear-gradient(90deg, #F57F17, #FFB74D); }
.progress-fill.green { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.progress-fill.red { background: linear-gradient(90deg, #FF6B6B, #FF8E8E); }

.ability-hint { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

.advice-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx; padding: 32rpx; margin-bottom: 20rpx; border: 1rpx solid #BFDBFE;
}
.advice-header { display: flex; align-items: center; gap: 8rpx; margin-bottom: 12rpx; }
.advice-header .ph { font-size: 24rpx; color: #4F9EF8; }
.advice-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.advice-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 24rpx; font-weight: 500; }
.advice-desc .highlight { font-weight: 700; color: #4F9EF8; }
.advice-btn {
  width: 100%; background: #FFFFFF; border: 2rpx solid #BFDBFE; color: #4F9EF8;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; gap: 6rpx; transition: all 0.2s;
}
.advice-btn:active { transform: scale(0.97); background: #EFF6FF; }

.history-list {
  background: #FFFFFF; border-radius: 20rpx; padding: 8rpx 24rpx;
  margin-bottom: 20rpx; box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
.history-item {
  display: flex; align-items: center; gap: 20rpx; padding: 20rpx 0;
  border-bottom: 1rpx solid #F5F5F5; transition: all 0.2s;
}
.history-item:last-child { border-bottom: none; }
.history-item:active { opacity: 0.7; }
.history-dot { width: 12rpx; height: 12rpx; border-radius: 50%; flex-shrink: 0; }
.history-dot.low { background: #22C55E; }
.history-dot.medium { background: #F57F17; }
.history-dot.high { background: #FF6B6B; }
.history-info { flex: 1; }
.history-date { font-size: 24rpx; color: #2D3748; font-weight: 600; }
.history-score { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.history-badge { font-size: 20rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 10rpx; }
.history-badge.low { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.history-badge.medium { background: rgba(245, 127, 23, 0.1); color: #F57F17; }
.history-badge.high { background: rgba(255, 107, 107, 0.1); color: #FF6B6B; }

.radar-wrap { display: flex; justify-content: center; margin-bottom: 32rpx; }
.radar-svg { width: 280rpx; height: 280rpx; }

.reassess-card {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border-radius: 24rpx; padding: 32rpx; margin-bottom: 20rpx; border: 1rpx solid #BBF7D0;
}
.reassess-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 12rpx; }
.reassess-header .ph { font-size: 28rpx; color: #22C55E; }
.reassess-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.reassess-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 24rpx; font-weight: 500; }
.reassess-btn {
  width: 100%; background: linear-gradient(135deg, #22C55E, #16A34A); color: #FFFFFF;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(34, 197, 94, 0.2); transition: all 0.2s;
}
.reassess-btn:active { transform: scale(0.97); }

.high-risk-card {
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  border-radius: 24rpx; padding: 32rpx; margin-bottom: 20rpx; border: 2rpx solid #FECACA;
}
.high-risk-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 12rpx; }
.high-risk-icon { font-size: 32rpx; color: #FF6B6B; }
.high-risk-title { font-size: 28rpx; font-weight: 700; color: #DC2626; }
.high-risk-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 24rpx; font-weight: 500; }
.high-risk-btn {
  width: 100%; background: linear-gradient(135deg, #FF6B6B, #EF4444); color: #FFFFFF;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.2); transition: all 0.2s;
}
.high-risk-btn:active { transform: scale(0.97); }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 100rpx 40rpx; }
.empty-icon .ph { font-size: 80rpx; color: #D1D5DB; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #2D3748; margin: 24rpx 0 12rpx; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; text-align: center; line-height: 1.6; margin-bottom: 40rpx; font-weight: 500; }
.empty-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; padding: 22rpx 56rpx; font-size: 26rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2); transition: all 0.2s;
}
.empty-btn:active { transform: scale(0.97); }
</style>
