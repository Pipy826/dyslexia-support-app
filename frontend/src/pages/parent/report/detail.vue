<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">报告详情</view>
      <button class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text> 问问AI
      </button>
    </view>

    <view class="page-content" v-if="report">
      <!-- 概览卡片 -->
      <view class="overview-card">
        <view class="report-time">生成时间：{{ formatDateTime(report.created_at) }}</view>
        <view class="conclusion-row">
          <view class="conclusion-indicator" :class="report.risk_level === 'high' ? 'red' : (report.risk_level === 'medium' ? 'orange' : 'green')"></view>
          <view class="conclusion-title">{{ getRiskTitle(report.risk_level) }}</view>
        </view>
        <view class="overview-desc">{{ report.summary }}</view>
      </view>

      <!-- 能力维度评分 -->
      <view class="section-title">能力多维剖析</view>
      <view class="ability-card">
        <view class="ability-item" v-for="(score, dim) in dimensions" :key="dim">
          <view class="ability-header">
            <view class="ability-name">{{ getDimName(dim) }}</view>
            <view class="ability-tag" :class="getScoreClass(score)">{{ getScoreLabel(score) }}</view>
          </view>
          <view class="progress-track">
            <view class="progress-fill" :class="getScoreClass(score)" :style="{ width: score + '%' }"></view>
          </view>
          <view class="ability-hint">{{ getDimHint(dim, score) }}</view>
        </view>
      </view>

      <!-- AI 个性化解读 -->
      <view class="section-title">AI 个性化解读</view>
      <view class="ai-interpretation-card">
        <view class="ai-card-header">
          <view class="ai-avatar">
            <text class="ph-fill ph-robot"></text>
          </view>
          <view class="ai-card-title">AI 助手解读</view>
          <view class="ai-refresh-btn" @click="loadAiInterpretation" v-if="!aiLoading">
            <text class="ph ph-arrows-clockwise"></text>
          </view>
        </view>

        <!-- 加载中 -->
        <view class="ai-loading" v-if="aiLoading">
          <view class="dot-flashing"></view>
          <view class="ai-loading-text">AI 正在分析报告...</view>
        </view>

        <!-- 解读内容 -->
        <view class="ai-content" v-else-if="aiInterpretation">
          {{ aiInterpretation }}
        </view>

        <!-- 未加载 -->
        <view class="ai-placeholder" v-else>
          <button class="ai-load-btn" @click="loadAiInterpretation">
            <text class="ph ph-sparkle"></text> 获取 AI 解读
          </button>
        </view>

        <button class="ai-chat-btn" @click="goToAiChat" v-if="aiInterpretation">
          <text class="ph ph-chat-circle-dots"></text> 继续追问 AI
        </button>
      </view>

      <!-- 干预建议 -->
      <view class="section-title">干预建议</view>
      <view class="advice-card">
        <view class="advice-header">
          <text class="ph ph-info"></text>
          <view class="advice-title">专业建议</view>
        </view>
        <view class="advice-desc">{{ report.recommendations }}</view>
        <button class="advice-btn" @click="goToTraining">查看专属干预方案 →</button>
      </view>

      <!-- 高风险专业引导 -->
      <view class="high-risk-card" v-if="report.risk_level === 'high'">
        <view class="high-risk-header">
          <text class="ph ph-warning-circle high-risk-icon"></text>
          <view class="high-risk-title">建议专业评估</view>
        </view>
        <view class="high-risk-desc">根据本次评估结果，建议尽快联系专业机构进行全面评估，以获得更准确的诊断和干预方案。</view>
        <button class="high-risk-btn" @click="goToAiChat">了解更多</button>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-state" v-else>
      <text class="ph ph-circle-notch"></text>
      <view class="loading-text">加载中...</view>
    </view>

    <!-- 情绪支持弹窗（高风险时自动弹出） -->
    <view class="modal-overlay" v-if="showEmotionalModal" @click="showEmotionalModal = false">
      <view class="emotional-modal" @click.stop>
        <view class="emotional-header">
          <view class="emotional-avatar">
            <text class="ph-fill ph-heart"></text>
          </view>
          <view class="emotional-title">给家长的话</view>
          <view class="emotional-close" @click="showEmotionalModal = false">
            <text class="ph ph-x"></text>
          </view>
        </view>

        <view class="emotional-loading" v-if="emotionalLoading">
          <view class="loading-spinner-sm"></view>
          <view>AI 正在准备...</view>
        </view>

        <view class="emotional-content" v-else>
          {{ emotionalSupport }}
        </view>

        <view class="emotional-actions">
          <button class="emotional-chat-btn" @click="goToAiChatFromModal">
            <text class="ph ph-chat-circle-dots"></text> 继续和 AI 聊聊
          </button>
          <button class="emotional-close-btn" @click="showEmotionalModal = false">
            我知道了
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getReport, getReportDimensions } from '../../../api/report.js'
import { getReportInterpretation, getEmotionalSupport } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      reportId: null,
      report: null,
      dimensions: null,
      currentChild: null,
      aiInterpretation: '',
      aiLoading: false,
      emotionalSupport: '',
      emotionalLoading: false,
      showEmotionalModal: false,
    }
  },
  onLoad(options) {
    this.reportId = options.id
    this.currentChild = getCurrentChild()
    this.loadReport()
  },
  methods: {
    async loadReport() {
      try {
        this.report = await getReport(this.reportId)
        const dimRes = await getReportDimensions(this.reportId)
        const raw = dimRes.dimensions
        this.dimensions = (typeof raw === 'string') ? JSON.parse(raw) : (raw || {})
        // 报告加载完后自动获取AI解读
        this.loadAiInterpretation()
        // 高风险时自动触发情绪支持
        if (this.report?.risk_level === 'high') {
          this.loadEmotionalSupport()
        }
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    async loadAiInterpretation() {
      if (this.aiLoading) return
      this.aiLoading = true
      this.aiInterpretation = ''
      try {
        const res = await getReportInterpretation(this.reportId)
        this.aiInterpretation = res.interpretation
      } catch (e) {
        console.error('AI解读失败', e)
        uni.showToast({ title: 'AI解读暂时不可用', icon: 'none' })
      } finally {
        this.aiLoading = false
      }
    },
    async loadEmotionalSupport() {
      this.emotionalLoading = true
      try {
        const res = await getEmotionalSupport(this.reportId)
        this.emotionalSupport = res.support
        // 延迟弹出，让用户先看到报告
        setTimeout(() => {
          this.showEmotionalModal = true
        }, 1500)
      } catch (e) {
        console.error('情绪支持加载失败', e)
      } finally {
        this.emotionalLoading = false
      }
    },
    getRiskTitle(level) {
      const titles = {
        low: '低风险 / 正常',
        medium: '中风险 / 需关注',
        high: '高风险 / 重点关注'
      }
      return titles[level] || level
    },
    getDimName(dim) {
      const names = {
        visual_discrimination: '视觉辨识能力',
        phonological: '音形映射能力',
        character_order: '字序组织能力',
        spelling: '拼写输出能力',
        reading_comprehension: '阅读理解能力',
        semantic_integration: '语义整合能力',
        information_extraction: '信息提取能力',
        attention: '任务注意力'
      }
      return names[dim] || dim
    },
    getDimHint(dim, score) {
      // 根据分数高低返回不同的描述
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
    getScoreClass(score) {
      if (score >= 75) return 'green'
      if (score >= 60) return 'orange'
      return 'red'
    },
    getScoreLabel(score) {
      if (score >= 75) return '良好'
      if (score >= 60) return '中等'
      return '偏弱'
    },
    formatDateTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
    },
    goBack() {
      uni.navigateBack()
    },
    goToAiChat() {
      uni.navigateTo({
        url: `/pages/parent/ai-chat/index?child_id=${this.currentChild?.id}`
      })
    },
    goToAiChatFromModal() {
      this.showEmotionalModal = false
      this.goToAiChat()
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/parent/training/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
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

.back-btn .ph {
  font-size: 40rpx;
  color: #6B7280;
}

.header-title {
  flex: 1;
  font-size: 36rpx;
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

/* 概览卡片 */
.overview-card {
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

.conclusion-indicator.green { background: #10B981; }
.conclusion-indicator.orange { background: #F59E0B; }
.conclusion-indicator.red { background: #EF4444; }

.conclusion-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
}

.overview-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
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

.ability-tag.green {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.ability-tag.orange {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.ability-tag.red {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.progress-track {
  height: 16rpx;
  background: #F3F4F6;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s;
}

.progress-fill.green { background: #10B981; }
.progress-fill.orange { background: #F59E0B; }
.progress-fill.red { background: #EF4444; }

.ability-hint {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 建议卡片 */
.advice-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
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
}

/* AI 解读卡片 */
.ai-interpretation-card {
  background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DDD6FE;
}

.ai-card-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 28rpx;
}

.ai-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #7C3AED;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-avatar .ph {
  font-size: 32rpx;
  color: #FFFFFF;
}

.ai-card-title {
  flex: 1;
  font-size: 28rpx;
  font-weight: 700;
  color: #5B21B6;
}

.ai-refresh-btn .ph {
  font-size: 32rpx;
  color: #7C3AED;
}

.ai-loading {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 16rpx 0;
}

.ai-loading-text {
  font-size: 26rpx;
  color: #7C3AED;
}

.ai-content {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
  margin-bottom: 32rpx;
}

.ai-placeholder {
  display: flex;
  justify-content: center;
  padding: 16rpx 0;
}

.ai-load-btn {
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

.ai-load-btn .ph {
  font-size: 28rpx;
}

.ai-chat-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #DDD6FE;
  color: #7C3AED;
  border-radius: 32rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.ai-chat-btn .ph {
  font-size: 28rpx;
}

/* 思考动画 */
.dot-flashing {
  position: relative;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background-color: #7C3AED;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0.5s;
}

.dot-flashing::before,
.dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background-color: #7C3AED;
}

.dot-flashing::before {
  left: -28rpx;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 28rpx;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 1s;
}

@keyframes dot-flashing {
  0% { background-color: #7C3AED; }
  100% { background-color: #DDD6FE; }
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

/* 情绪支持弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
}

.emotional-modal {
  background: #FFFFFF;
  width: 100%;
  border-radius: 64rpx 64rpx 0 0;
  padding: 48rpx;
  padding-bottom: calc(48rpx + env(safe-area-inset-bottom));
}

.emotional-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.emotional-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #FEF2F2;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.emotional-avatar .ph {
  font-size: 36rpx;
  color: #EF4444;
}

.emotional-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
}

.emotional-close .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

.emotional-loading {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 32rpx 0;
  color: #9CA3AF;
  font-size: 26rpx;
}

.loading-spinner-sm {
  width: 40rpx;
  height: 40rpx;
  border: 4rpx solid #F3F4F6;
  border-top-color: #EF4444;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.emotional-content {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.8;
  margin-bottom: 40rpx;
  background: #FFF5F5;
  border-radius: 24rpx;
  padding: 32rpx;
}

.emotional-actions {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.emotional-chat-btn {
  width: 100%;
  background: #EF4444;
  color: #FFFFFF;
  border-radius: 40rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.emotional-chat-btn .ph { font-size: 30rpx; }

.emotional-close-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #E5E7EB;
  color: #6B7280;
  border-radius: 40rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx;
}

.loading-state .ph {
  font-size: 64rpx;
  color: #D1D5DB;
  animation: rotate 1s linear infinite;
}

.loading-text {
  font-size: 28rpx;
  color: #9CA3AF;
  margin-top: 16rpx;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
