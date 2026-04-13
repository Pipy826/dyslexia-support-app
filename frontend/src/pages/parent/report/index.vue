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
            <view class="ability-hint">{{ dimHint(dim) }}</view>
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
    dimHint(dim) {
      const map = {
        visual_discrimination: '区分形近字的能力。', phonological: '音义联结能力。',
        character_order: '笔画顺序记忆能力。', spelling: '拼写输出稳定性。',
        reading_comprehension: '理解文字内容的能力。', semantic_integration: '句间关系理解能力。',
        information_extraction: '从文本提取关键信息的能力。', attention: '持续专注完成任务的能力。'
      }
      return map[dim] || ''
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
