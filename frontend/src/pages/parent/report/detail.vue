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
      <view class="section-title">本次筛查维度</view>
      <view class="tested-hint">
        <text class="ph ph-info"></text>
        本报告仅展示本次「{{ getGameTypeName(report.game_type) }}」筛查的维度。完成全部6项筛查后，可在成长分析中查看综合能力图。
      </view>
      <view class="ability-card" v-for="group in getGroupedDimensions()" :key="group.label">
        <view class="group-header">
          <text :class="['ph', group.icon]"></text>
          <view class="group-label">{{ group.label }}</view>
        </view>
        <view class="ability-item" v-for="item in group.items" :key="item.dim">
          <view class="ability-header">
            <view class="ability-name">{{ getDimName(item.dim) }}</view>
            <view class="ability-tag" :class="getScoreClass(item.score)">{{ getScoreLabel(item.score) }}</view>
          </view>
          <view class="progress-track">
            <view class="progress-fill" :class="getScoreClass(item.score)" :style="{ width: item.score + '%' }"></view>
          </view>
          <view class="ability-hint">{{ getDimHint(item.dim, item.score) }}</view>
        </view>
      </view>

      <!-- 综合能力总览（所有筛查合并） -->
      <template v-if="Object.keys(mergedDimensions).length > 0">
        <view class="section-title">综合能力总览</view>

        <!-- 未完成提示 -->
        <view class="pending-hint" v-if="!isMergedComplete">
          <text class="ph ph-clock"></text>
          <view class="pending-text">
            已完成 {{ completedGameTypes.length }}/6 项筛查。
            尚未完成：{{ pendingGameTypes.map(g => getGameTypeName(g)).join('、') }}
          </view>
        </view>
        <view class="complete-hint" v-else>
          <text class="ph ph-check-circle"></text>
          <view>已完成全部6项筛查，以下为综合能力图谱</view>
        </view>

        <view class="ability-card" v-for="group in getMergedGroupedDimensions()" :key="'merged-' + group.label">
          <view class="group-header">
            <text :class="['ph', group.icon]"></text>
            <view class="group-label">{{ group.label }}</view>
          </view>
          <view class="ability-item" v-for="item in group.items" :key="'m-' + item.dim">
            <view class="ability-header">
              <view class="ability-name">{{ getDimName(item.dim) }}</view>
              <view class="ability-tag" :class="getScoreClass(item.score)">{{ getScoreLabel(item.score) }}</view>
            </view>
            <view class="progress-track">
              <view class="progress-fill" :class="getScoreClass(item.score)" :style="{ width: item.score + '%' }"></view>
            </view>
            <view class="ability-hint">{{ getDimHint(item.dim, item.score) }}</view>
          </view>
        </view>
      </template>
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
import { getReport } from '../../../api/report.js'
import { getMergedDimensions } from '../../../api/report.js'
import { getReportInterpretation, getEmotionalSupport } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

const DIMENSION_GROUPS = [
  {
    label: '视觉与注意力',
    icon: 'ph-eye',
    dims: ['visual_discrimination', 'attention'],
  },
  {
    label: '语音与拼写',
    icon: 'ph-text-aa',
    dims: ['spelling', 'phonological', 'character_order'],
  },
  {
    label: '阅读理解',
    icon: 'ph-book-open',
    dims: ['reading_comprehension', 'semantic_integration', 'information_extraction'],
  },
  {
    label: '记忆与命名',
    icon: 'ph-brain',
    dims: ['working_memory_capacity', 'short_term_memory', 'rapid_naming_speed', 'phonological_awareness'],
  },
  {
    label: '动作协调',
    icon: 'ph-hand',
    dims: ['fine_motor_control', 'visual_motor_integration'],
  },
]

export default {
  data() {
    return {
      reportId: null,
      report: null,
      dimensions: null,
      // 综合能力图谱（所有筛查合并）
      mergedDimensions: {},
      completedGameTypes: [],
      pendingGameTypes: [],
      isMergedComplete: false,
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
  computed: {
    childGrade() {
      return this.currentChild?.grade || ''
    }
  },
  methods: {
    async loadReport() {
      try {
        this.report = await getReport(this.reportId)
        // dimensions 已包含在 report 响应中，直接解析，无需额外请求
        const raw = this.report.dimensions
        this.dimensions = (typeof raw === 'string') ? JSON.parse(raw || '{}') : (raw || {})
        // 同时加载该孩子的综合维度
        if (this.currentChild?.id) {
          this.loadMergedDimensions(this.currentChild.id)
        } else if (this.report?.child_id) {
          this.loadMergedDimensions(this.report.child_id)
        }
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
    async loadMergedDimensions(childId) {
      try {
        const res = await getMergedDimensions(childId)
        this.mergedDimensions = res.merged_dimensions || {}
        this.completedGameTypes = res.completed_game_types || []
        this.pendingGameTypes = res.pending_game_types || []
        this.isMergedComplete = res.is_complete || false
      } catch (e) {
        console.error('加载综合维度失败', e)
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
    getGameTypeName(type) {
      const names = {
        visual: '视觉辨识',
        spelling: '拼字识别',
        comprehension: '文字理解',
        working_memory: '工作记忆',
        rapid_naming: '快速命名',
        motor_coordination: '精细动作',
      }
      return names[type] || type || '综合'
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
        attention: '任务注意力',
        working_memory_capacity: '工作记忆容量',
        short_term_memory: '短时记忆能力',
        rapid_naming_speed: '快速命名速度',
        phonological_awareness: '音韵意识',
        fine_motor_control: '精细动作控制',
        visual_motor_integration: '视动整合能力'
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
        attention:             '能持续专注完成任务，注意力稳定。',
        working_memory_capacity: '工作记忆容量充足，能有效保持和处理多项信息。',
        short_term_memory:     '短时记忆能力良好，能准确复现短序列信息。',
        rapid_naming_speed:    '命名速度流畅，能快速准确地识别并说出名称。',
        phonological_awareness:'音韵意识良好，能准确感知和操作语音单元。',
        fine_motor_control:    '精细动作控制良好，手部动作协调稳定。',
        visual_motor_integration: '视动整合能力良好，眼手协调配合流畅。'
      }
      const weak = {
        visual_discrimination: '易混淆形近字，视觉扫描时容易漏字或看错。',
        phonological:          '音形联结反应偏慢，拼音与汉字对应存在困难。',
        character_order:       '书写时部件位置偶有颠倒，笔顺记忆不稳定。',
        spelling:              '作答犹豫期较长，部件颠倒或替换发生率偏高。',
        reading_comprehension: '理解句子和短文时存在困难，容易遗漏关键信息。',
        semantic_integration:  '句间关系理解存在偏差，语义整合能力需加强。',
        information_extraction:'从文中提取关键信息时容易遗漏或混淆。',
        attention:             '持续专注能力不足，连续任务中表现有波动。',
        working_memory_capacity: '工作记忆容量有限，同时处理多项信息时容易出错。',
        short_term_memory:     '短时记忆保持时间较短，序列信息容易遗忘。',
        rapid_naming_speed:    '命名速度偏慢，快速识别图形或文字时反应时间较长。',
        phonological_awareness:'音韵意识薄弱，对语音的感知和操作存在困难。',
        fine_motor_control:    '精细动作控制有待加强，手部动作协调性需要练习。',
        visual_motor_integration: '视动整合能力有待提升，眼手协调配合需要加强。'
      }
      if (score >= 75) return good[dim] || ''
      if (score >= 60) return `${weak[dim] || ''} 建议适当加强练习。`
      return `${weak[dim] || ''} 这是当前需要重点关注的能力维度。`
    },
    getGroupedDimensions() {
      const preschoolGrades = ['幼儿园', '学前', 'preschool']
      const isPreschool = preschoolGrades.includes(this.childGrade)
      const dims = this.dimensions || {}

      // 如果没有任何维度数据，返回空
      if (!Object.keys(dims).length) return []

      const result = []
      for (const group of DIMENSION_GROUPS) {
        const items = []
        for (const dim of group.dims) {
          // 学龄前排除 phonological 维度
          if (isPreschool && dim === 'phonological') continue
          // 只显示本次筛查实际测到的维度（在 dims 中存在且值为数字）
          if (!(dim in dims)) continue
          const val = dims[dim]
          if (typeof val === 'number') {
            items.push({ dim, score: val, untested: false })
          }
          // 不再显示"未测"条目，直接跳过
        }
        // 只保留有至少一个维度的分组
        if (items.length > 0) {
          result.push({ label: group.label, icon: group.icon, items })
        }
      }
      return result
    },
    // 综合能力图谱：合并所有筛查的维度
    getMergedGroupedDimensions() {
      const preschoolGrades = ['幼儿园', '学前', 'preschool']
      const isPreschool = preschoolGrades.includes(this.childGrade)
      const dims = this.mergedDimensions || {}
      if (!Object.keys(dims).length) return []

      const result = []
      for (const group of DIMENSION_GROUPS) {
        const items = []
        for (const dim of group.dims) {
          if (isPreschool && dim === 'phonological') continue
          if (!(dim in dims)) continue
          const val = dims[dim]
          if (typeof val === 'number') {
            items.push({ dim, score: val })
          }
        }
        if (items.length > 0) {
          result.push({ label: group.label, icon: group.icon, items })
        }
      }
      return result
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
/* 报告详情页 - 统一创意风格 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 48rpx;
}

/* 头部 - 紧凑，与首页一致 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20rpx);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.back-btn {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  background: #F5F5F5;
  flex-shrink: 0;
  margin-right: 16rpx;
  transition: all 0.2s;
}
.back-btn:active { background: #EFF6FF; transform: scale(0.92); }
.back-btn .ph { font-size: 28rpx; color: #718096; }

.header-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
}

.ai-btn {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  border: 1rpx solid #BFDBFE;
  padding: 10rpx 20rpx;
  border-radius: 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  transition: all 0.2s;
}
.ai-btn:active { transform: scale(0.95); }
.ai-btn .ph { font-size: 24rpx; margin-right: 6rpx; }

/* 页面内容 */
.page-content { padding: 24rpx 32rpx; }

/* 本次筛查提示 */
.tested-hint {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A;
  border-radius: 16rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  font-size: 22rpx;
  color: #92400E;
  line-height: 1.6;
  font-weight: 500;
}
.tested-hint .ph {
  font-size: 24rpx;
  color: #F59E0B;
  flex-shrink: 0;
  margin-top: 2rpx;
}

/* 未完成提示 */
.pending-hint {
  display: flex;
  align-items: flex-start;
  gap: 10rpx;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A;
  border-radius: 16rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  font-size: 22rpx;
  color: #92400E;
  line-height: 1.6;
  font-weight: 500;
}
.pending-hint .ph {
  font-size: 24rpx;
  color: #F59E0B;
  flex-shrink: 0;
  margin-top: 2rpx;
}
.pending-text { flex: 1; }

/* 已完成提示 */
.complete-hint {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border: 1rpx solid #BBF7D0;
  border-radius: 16rpx;
  padding: 18rpx 20rpx;
  margin-bottom: 16rpx;
  font-size: 22rpx;
  color: #166534;
  font-weight: 600;
}
.complete-hint .ph {
  font-size: 26rpx;
  color: #22C55E;
  flex-shrink: 0;
}

/* 概览卡片 */
.overview-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.report-time { font-size: 20rpx; color: #A0AEC0; margin-bottom: 12rpx; font-weight: 500; }

.conclusion-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.conclusion-indicator {
  width: 5rpx;
  height: 36rpx;
  border-radius: 3rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
}
.conclusion-indicator.green { background: linear-gradient(180deg, #22C55E, #4ADE80); }
.conclusion-indicator.orange { background: linear-gradient(180deg, #F57F17, #FFB74D); }
.conclusion-indicator.red { background: linear-gradient(180deg, #FF6B6B, #FF8E8E); }

.conclusion-title { font-size: 36rpx; font-weight: 800; color: #2D3748; }
.overview-desc { font-size: 24rpx; color: #718096; line-height: 1.7; font-weight: 500; }

/* 区域标题 */
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
}
.section-title::before {
  content: '';
  display: inline-block;
  width: 4rpx;
  height: 22rpx;
  background: linear-gradient(180deg, #4F9EF8, #A78BFA);
  border-radius: 2rpx;
  margin-right: 10rpx;
  flex-shrink: 0;
}

/* 能力卡片 */
.ability-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.ability-item { margin-bottom: 28rpx; }
.ability-item:last-child { margin-bottom: 0; }

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10rpx;
}

.ability-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }

.ability-tag { font-size: 20rpx; font-weight: 700; padding: 4rpx 14rpx; border-radius: 10rpx; }
.ability-tag.green { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.ability-tag.orange { background: rgba(245, 127, 23, 0.1); color: #F57F17; }
.ability-tag.red { background: rgba(255, 107, 107, 0.1); color: #FF6B6B; }

.progress-track { height: 10rpx; background: #F0F0F0; border-radius: 5rpx; overflow: hidden; margin-bottom: 8rpx; }
.progress-fill { height: 100%; border-radius: 5rpx; transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.progress-fill.green { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.progress-fill.orange { background: linear-gradient(90deg, #F57F17, #FFB74D); }
.progress-fill.red { background: linear-gradient(90deg, #FF6B6B, #FF8E8E); }

.ability-hint { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

.group-header {
  display: flex; align-items: center; gap: 10rpx;
  margin-bottom: 20rpx; padding-bottom: 16rpx;
  border-bottom: 1rpx solid #F0F0F0;
}
.group-header .ph { font-size: 28rpx; color: #4F9EF8; }
.group-label { font-size: 24rpx; font-weight: 700; color: #718096; }

.ability-tag.untested { background: #F5F5F5; color: #A0AEC0; }
.progress-fill.untested { background: #E5E7EB; }
.ability-hint.untested-hint { color: #D1D5DB; font-style: italic; }

/* AI 解读卡片 - 蓝色替代紫色 */
.ai-interpretation-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  border: 1rpx solid #BFDBFE;
}

.ai-card-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.ai-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 14rpx;
}
.ai-avatar .ph { font-size: 28rpx; color: #FFFFFF; }

.ai-card-title { flex: 1; font-size: 26rpx; font-weight: 700; color: #2D3748; }

.ai-refresh-btn .ph { font-size: 28rpx; color: #4F9EF8; }

.ai-loading {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
}
.ai-loading-text { font-size: 24rpx; color: #4F9EF8; font-weight: 600; margin-left: 16rpx; }

.ai-content { font-size: 26rpx; color: #2D3748; line-height: 1.8; margin-bottom: 24rpx; font-weight: 500; }

.ai-placeholder { display: flex; justify-content: center; padding: 16rpx 0; }

.ai-load-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 14rpx;
  padding: 18rpx 40rpx;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}
.ai-load-btn .ph { font-size: 24rpx; margin-right: 8rpx; }

.ai-chat-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #BFDBFE;
  color: #4F9EF8;
  border-radius: 14rpx;
  padding: 20rpx;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.ai-chat-btn:active { background: #EFF6FF; }
.ai-chat-btn .ph { font-size: 24rpx; margin-right: 8rpx; }

/* 思考动画 */
.dot-flashing {
  position: relative;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background-color: #4F9EF8;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0.5s;
  flex-shrink: 0;
}
.dot-flashing::before, .dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background-color: #4F9EF8;
}
.dot-flashing::before { left: -22rpx; animation: dot-flashing 1s infinite alternate; animation-delay: 0s; }
.dot-flashing::after { left: 22rpx; animation: dot-flashing 1s infinite alternate; animation-delay: 1s; }
@keyframes dot-flashing { 0% { background-color: #4F9EF8; } 100% { background-color: #BFDBFE; } }

/* 建议卡片 */
.advice-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  border: 1rpx solid #BFDBFE;
}
.advice-header { display: flex; align-items: center; margin-bottom: 12rpx; }
.advice-header .ph { font-size: 24rpx; color: #4F9EF8; margin-right: 8rpx; }
.advice-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.advice-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 20rpx; font-weight: 500; }
.advice-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #BFDBFE;
  color: #4F9EF8;
  border-radius: 14rpx;
  padding: 20rpx;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.advice-btn:active { background: #EFF6FF; }

/* 高风险卡片 */
.high-risk-card {
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 20rpx;
  border: 2rpx solid #FECACA;
}
.high-risk-header { display: flex; align-items: center; margin-bottom: 12rpx; }
.high-risk-icon { font-size: 28rpx; color: #FF6B6B; margin-right: 10rpx; }
.high-risk-title { font-size: 26rpx; font-weight: 700; color: #DC2626; }
.high-risk-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 20rpx; font-weight: 500; }
.high-risk-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF6B6B, #EF4444);
  color: #FFFFFF;
  border-radius: 14rpx;
  padding: 20rpx;
  font-size: 24rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.2);
  transition: all 0.2s;
}
.high-risk-btn:active { transform: scale(0.97); }

/* 情绪支持弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4rpx);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.emotional-modal {
  background: #FFFFFF;
  width: 100%;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }

.emotional-header { display: flex; align-items: center; margin-bottom: 24rpx; }

.emotional-avatar {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 14rpx;
}
.emotional-avatar .ph { font-size: 28rpx; color: #FF6B6B; }

.emotional-title { flex: 1; font-size: 28rpx; font-weight: 700; color: #2D3748; }
.emotional-close .ph { font-size: 32rpx; color: #A0AEC0; }

.emotional-loading { display: flex; align-items: center; padding: 24rpx 0; color: #A0AEC0; font-size: 24rpx; }

.loading-spinner-sm {
  width: 36rpx;
  height: 36rpx;
  border: 4rpx solid #F0F0F0;
  border-top-color: #FF6B6B;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-right: 16rpx;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

.emotional-content {
  font-size: 26rpx;
  color: #2D3748;
  line-height: 1.8;
  margin-bottom: 28rpx;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  border-radius: 16rpx;
  padding: 24rpx;
  font-weight: 500;
}

.emotional-actions { display: flex; flex-direction: column; }

.emotional-chat-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF6B6B, #EF4444);
  color: #FFFFFF;
  border-radius: 14rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.2);
  margin-bottom: 16rpx;
  transition: all 0.2s;
}
.emotional-chat-btn:active { transform: scale(0.97); }
.emotional-chat-btn .ph { font-size: 26rpx; margin-right: 10rpx; }

.emotional-close-btn {
  width: 100%;
  background: #F5F5F5;
  color: #A0AEC0;
  border-radius: 14rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  transition: all 0.2s;
}
.emotional-close-btn:active { background: #EFF6FF; color: #4F9EF8; }

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 160rpx 0;
}
.loading-state .ph { font-size: 56rpx; color: #D1D5DB; animation: rotate 1s linear infinite; }
.loading-text { font-size: 26rpx; color: #A0AEC0; margin-top: 16rpx; font-weight: 500; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
