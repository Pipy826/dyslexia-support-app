<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">成长记录</view>
      <button class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text> 问问AI
      </button>
    </view>

    <view class="page-content">
      <!-- 有报告时显示 -->
      <template v-if="latestReport">
        <!-- 成长日记入口 -->
        <view class="diary-entry-card" @click="goToGrowthDiary">
          <view class="diary-entry-left">
            <text class="diary-entry-emoji">📅</text>
            <view class="diary-entry-info">
              <view class="diary-entry-title">成长日记</view>
              <view class="diary-entry-desc">查看趣味成长报告和能力轨迹</view>
            </view>
          </view>
          <text class="ph ph-arrow-right diary-entry-arrow"></text>
        </view>

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
        <view class="section-title">综合能力剖析</view>

        <!-- 未完成全部探索时的提示 -->
        <view class="pending-hint" v-if="!isMergedComplete && completedGameTypes.length > 0">
          <text class="ph ph-clock"></text>
          已完成 {{ completedGameTypes.length }}/6 项能力探索，尚未完成：{{ pendingGameTypes.map(g => gameTypeName(g)).join('、') }}
        </view>

        <view class="ability-card">
          <!-- SVG 雷达图 -->
          <view class="radar-wrap" v-if="Object.keys(mergedDimensions).length >= 3">
            <radar-chart :dimensions="mergedDimensions"></radar-chart>
          </view>

          <!-- 图例说明 -->
          <view class="radar-legend" v-if="Object.keys(mergedDimensions).length >= 3">
            <view class="legend-item">
              <view class="legend-dot green"></view>
              <view class="legend-text">良好（≥75分）</view>
            </view>
            <view class="legend-item">
              <view class="legend-dot orange"></view>
              <view class="legend-text">中等（60-74分）</view>
            </view>
            <view class="legend-item">
              <view class="legend-dot red"></view>
              <view class="legend-text">偏弱（＜60分）</view>
            </view>
          </view>

          <view class="ability-item" v-for="(score, dim) in mergedDimensions" :key="dim">
            <view class="ability-header">
              <view class="ability-name">{{ dimName(dim) }}</view>
              <view class="ability-tag" :class="score >= 75 ? 'green' : score >= 60 ? 'orange' : 'red'">{{ scoreLabel(score) }}</view>
            </view>
            <view class="ability-progress">
              <view class="progress-track">
                <view class="progress-fill" :class="score >= 75 ? 'green' : score >= 60 ? 'orange' : 'red'" :style="{ width: score + '%' }"></view>
              </view>
            </view>
            <view class="ability-hint">{{ dimHint(dim, score) }}</view>
          </view>
        </view>

        <!-- 历史探索记录（按游戏类型分组，每种取最新） -->
        <view class="section-title">历史探索记录</view>
        <view class="history-list">
          <view
            class="history-item"
            v-for="r in groupedHistory"
            :key="r.id"
            @click="viewDetail(r.id)"
          >
            <view class="history-icon" :class="r.risk_level">
              <text class="ph ph-file-text"></text>
            </view>
            <view class="history-info">
              <view class="history-title">{{ gameTypeName(r.game_type) }}能力探索</view>
              <view class="history-date">{{ formatDate(r.created_at) }}</view>
            </view>
            <view class="history-score-wrap">
              <view class="history-score">{{ r.overall_score }}分</view>
              <view class="history-badge" :class="r.risk_level">{{ riskTitle(r.risk_level) }}</view>
            </view>
          </view>
        </view>

        <!-- 成长建议 -->
        <view class="section-title">成长建议</view>
        <view class="advice-card">
          <view class="advice-header">
            <text class="ph ph-info"></text>
            <view class="advice-title">专业建议</view>
          </view>
          <view class="advice-desc">{{ latestReport.recommendations }}</view>
          <button class="advice-btn" @click="goToTraining">查看专属成长方案 →</button>
        </view>

        <!-- 复评建议 -->
        <view class="reassess-card">
          <view class="reassess-header">
            <text class="ph ph-calendar-check"></text>
            <view class="reassess-title">复评建议</view>
          </view>
          <view class="reassess-desc">{{ reassessText }}</view>
          <view class="reassess-btns">
            <button class="reassess-btn" @click="goToScreening">立即复评</button>
            <button class="compare-btn" v-if="reports.length >= 2" @click="goToCompare">查看对比</button>
          </view>
        </view>

        <!-- 高风险专业引导 -->
        <view class="high-risk-card" v-if="latestReport.risk_level === 'high'">
          <view class="high-risk-header">
            <text class="ph ph-warning-circle high-risk-icon"></text>
            <view class="high-risk-title">建议专业评估</view>
          </view>
          <view class="high-risk-desc">根据本次评估结果，建议尽快联系专业机构进行全面评估，以获得更准确的专业意见和成长支持方案。</view>
          <button class="high-risk-btn" @click="goToAiChat">了解更多</button>
        </view>
      </template>

      <!-- 无报告时 -->
      <view class="empty-state" v-else>
        <view class="empty-icon"><text class="ph ph-file-text"></text></view>
        <view class="empty-title">暂无成长记录</view>
        <view class="empty-desc">完成能力探索后，系统将自动生成详细的能力观察报告</view>
        <button class="empty-btn" @click="goToScreening">开始能力探索</button>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/report/index"></tab-bar>

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
        <view class="emotional-content" v-else>{{ emotionalSupport }}</view>
        <view class="emotional-actions">
          <button class="emotional-chat-btn" @click="goToAiChat(); showEmotionalModal = false">
            <text class="ph ph-chat-circle-dots"></text> 继续和 AI 聊聊
          </button>
          <button class="emotional-close-btn" @click="showEmotionalModal = false">我知道了</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getReports, getMergedDimensions } from '../../../api/report.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import { getEmotionalSupport } from '../../../api/ai.js'
import TabBar from '../../../components/tab-bar/index.vue'
import RadarChart from '../../../components/charts/RadarChart.vue'
import { friendlyRiskLevel } from '../../../utils/terminology.js'

// 游戏类型中文名
const GAME_TYPE_NAMES = {
  visual: '视觉辨识',
  spelling: '拼字识别',
  comprehension: '文字理解',
  working_memory: '工作记忆',
  rapid_naming: '快速命名',
  motor_coordination: '精细动作',
}

export default {
  components: { TabBar, RadarChart },
  data() {
    return {
      children: [],
      currentChild: null,
      reports: [],
      latestReport: null,
      // 综合维度（所有筛查合并）
      mergedDimensions: {},
      completedGameTypes: [],
      pendingGameTypes: [],
      isMergedComplete: false,
      emotionalSupport: '',
      emotionalLoading: false,
      showEmotionalModal: false,
    }
  },
  computed: {
    // 雷达图计算属性已移至 RadarChart 组件内部
    reassessText() {
      if (!this.latestReport) return ''
      const level = this.latestReport.risk_level
      if (level === 'low') return '建议1个月后复评，持续跟踪能力变化'
      if (level === 'medium') return '建议2周后复评，观察训练效果'
      return '建议尽快复评，密切关注变化'
    },
    // 按游戏类型分组的历史记录（每种游戏取最新一条）
    groupedHistory() {
      const map = {}
      for (const r of this.reports) {
        const gt = r.game_type || 'unknown'
        if (!map[gt]) map[gt] = r  // 已按时间降序，第一条就是最新
      }
      return Object.values(map).sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
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
        // 加载综合维度
        await this.loadMergedDimensions()
        // 需要更多关注时自动触发情绪支持弹窗
        if (this.latestReport?.risk_level === 'high') {
          this.loadEmotionalSupport()
        }
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    async loadMergedDimensions() {
      if (!this.currentChild) return
      try {
        const res = await getMergedDimensions(this.currentChild.id)
        this.mergedDimensions = res.merged_dimensions || {}
        this.completedGameTypes = res.completed_game_types || []
        this.pendingGameTypes = res.pending_game_types || []
        this.isMergedComplete = res.is_complete || false
      } catch (e) {
        console.error('加载综合维度失败', e)
      }
    },
    async loadEmotionalSupport() {
      if (!this.latestReport) return
      this.emotionalLoading = true
      try {
        const res = await getEmotionalSupport(this.latestReport.id)
        this.emotionalSupport = res.support
        setTimeout(() => { this.showEmotionalModal = true }, 1500)
      } catch (e) {
        console.error('情绪支持加载失败', e)
      } finally {
        this.emotionalLoading = false
      }
    },
    riskTitle(level) {
      const map = {
        low: '表现良好',
        medium: '有些地方可以加强',
        high: '需要更多关注',
      }
      return map[level] || friendlyRiskLevel(level)
    },
    gameTypeName(type) {
      return GAME_TYPE_NAMES[type] || type || '综合'
    },
    dimName(dim) {
      const map = {
        visual_discrimination:    '视觉辨识能力',
        phonological:             '音形映射能力',
        character_order:          '字序组织能力',
        spelling:                 '拼写输出能力',
        reading_comprehension:    '阅读理解能力',
        semantic_integration:     '语义整合能力',
        information_extraction:   '信息提取能力',
        attention:                '任务注意力',
        working_memory_capacity:  '工作记忆容量',
        short_term_memory:        '短时记忆能力',
        rapid_naming_speed:       '快速命名速度',
        phonological_awareness:   '音韵意识',
        fine_motor_control:       '精细动作控制',
        visual_motor_integration: '视动整合能力',
      }
      return map[dim] || dim
    },
    dimHint(dim, score) {
      const good = {
        visual_discrimination:    '形近字辨别能力良好，视觉扫描稳定。',
        phonological:             '音形联结反应正常，拼音识字能力稳定。',
        character_order:          '汉字笔顺记忆良好，字形组织稳定。',
        spelling:                 '拼写输出稳定，作答犹豫较少。',
        reading_comprehension:    '能准确理解句子和短文的核心意思。',
        semantic_integration:     '句间关系理解正常，语义整合能力良好。',
        information_extraction:   '能从文中快速定位关键信息。',
        attention:                '能持续专注完成任务，注意力稳定。',
        working_memory_capacity:  '工作记忆容量充足，能有效保持和处理多项信息。',
        short_term_memory:        '短时记忆能力良好，能准确复现短序列信息。',
        rapid_naming_speed:       '命名速度流畅，能快速准确地识别并说出名称。',
        phonological_awareness:   '音韵意识良好，能准确感知和操作语音单元。',
        fine_motor_control:       '精细动作控制良好，手部动作协调稳定。',
        visual_motor_integration: '视动整合能力良好，眼手协调配合流畅。',
      }
      const weak = {
        visual_discrimination:    '易混淆形近字，视觉扫描时容易漏字或看错。',
        phonological:             '音形联结反应偏慢，拼音与汉字对应存在困难。',
        character_order:          '书写时部件位置偶有颠倒，笔顺记忆不稳定。',
        spelling:                 '作答犹豫期较长，部件颠倒或替换发生率偏高。',
        reading_comprehension:    '理解句子和短文时存在困难，容易遗漏关键信息。',
        semantic_integration:     '句间关系理解存在偏差，语义整合能力需加强。',
        information_extraction:   '从文中提取关键信息时容易遗漏或混淆。',
        attention:                '持续专注能力不足，连续任务中表现有波动。',
        working_memory_capacity:  '工作记忆容量有限，同时处理多项信息时容易出错。',
        short_term_memory:        '短时记忆保持时间较短，序列信息容易遗忘。',
        rapid_naming_speed:       '命名速度偏慢，快速识别图形或文字时反应时间较长。',
        phonological_awareness:   '音韵意识薄弱，对语音的感知和操作存在困难。',
        fine_motor_control:       '精细动作控制有待加强，手部动作协调性需要练习。',
        visual_motor_integration: '视动整合能力有待提升，眼手协调配合需要加强。',
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
    goToCompare() {
      if (this.reports.length < 2) return
      uni.navigateTo({
        url: `/pages/parent/report/compare?current_id=${this.reports[0].id}&previous_id=${this.reports[1].id}`
      })
    },
    goToGrowthDiary() {
      if (!this.currentChild) return
      uni.navigateTo({ url: `/pages/parent/report/growth-diary?child_id=${this.currentChild.id}` })
    },
  }
}
</script>

<style scoped>
/* 创意报告页面 - 数据可视化 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 160rpx;
  overflow-x: hidden;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
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

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; overflow-x: hidden; }

/* 成长日记入口卡片 */
.diary-entry-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 20rpx;
  transition: all 0.2s;
}
.diary-entry-card:active { transform: scale(0.98); }

.diary-entry-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.diary-entry-emoji {
  font-size: 44rpx;
}

.diary-entry-info {
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.diary-entry-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #92400E;
}

.diary-entry-desc {
  font-size: 20rpx;
  color: #B45309;
  font-weight: 500;
}

.diary-entry-arrow {
  font-size: 28rpx;
  color: #D97706;
}

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
  display: flex; flex-direction: column; gap: 12rpx;
  margin-bottom: 20rpx;
}
.history-item {
  background: #FFFFFF;
  display: flex; align-items: center; gap: 16rpx; padding: 20rpx 24rpx;
  border-radius: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04); transition: all 0.2s;
}
.history-item:active { transform: scale(0.98); }
.history-icon {
  width: 64rpx; height: 64rpx; border-radius: 16rpx;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.history-icon.low { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.history-icon.low .ph { color: #22C55E; }
.history-icon.medium { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.history-icon.medium .ph { color: #F57F17; }
.history-icon.high { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); }
.history-icon.high .ph { color: #FF6B6B; }
.history-icon .ph { font-size: 30rpx; }
.history-info { flex: 1; }
.history-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.history-date { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.history-score-wrap { display: flex; flex-direction: column; align-items: flex-end; gap: 6rpx; }
.history-score { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.history-badge { font-size: 20rpx; font-weight: 700; padding: 4rpx 14rpx; border-radius: 10rpx; }
.history-badge.low { background: rgba(34, 197, 94, 0.1); color: #22C55E; }
.history-badge.medium { background: rgba(245, 127, 23, 0.1); color: #F57F17; }
.history-badge.high { background: rgba(255, 107, 107, 0.1); color: #FF6B6B; }

/* 未完成提示 */
.pending-hint {
  display: flex; align-items: flex-start; gap: 10rpx;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A; border-radius: 16rpx;
  padding: 18rpx 20rpx; margin-bottom: 16rpx;
  font-size: 22rpx; color: #92400E; line-height: 1.6; font-weight: 500;
}
.pending-hint .ph { font-size: 24rpx; color: #F59E0B; flex-shrink: 0; margin-top: 2rpx; }

.radar-wrap { display: flex; justify-content: center; margin-bottom: 16rpx; width: 100%; overflow: hidden; }

/* 雷达图图例 */
.radar-legend {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  margin-bottom: 28rpx;
  flex-wrap: wrap;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}
.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}
.legend-dot.green { background: #10B981; }
.legend-dot.orange { background: #F59E0B; }
.legend-dot.red { background: #EF4444; }
.legend-text {
  font-size: 20rpx;
  color: #718096;
  font-weight: 500;
}

.reassess-card {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border-radius: 24rpx; padding: 32rpx; margin-bottom: 20rpx; border: 1rpx solid #BBF7D0;
}
.reassess-header { display: flex; align-items: center; gap: 10rpx; margin-bottom: 12rpx; }
.reassess-header .ph { font-size: 28rpx; color: #22C55E; }
.reassess-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.reassess-desc { font-size: 24rpx; color: #718096; line-height: 1.7; margin-bottom: 24rpx; font-weight: 500; }
.reassess-btns { display: flex; gap: 16rpx; }
.reassess-btn {
  flex: 1; background: linear-gradient(135deg, #22C55E, #16A34A); color: #FFFFFF;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(34, 197, 94, 0.2); transition: all 0.2s;
}
.reassess-btn:active { transform: scale(0.97); }
.compare-btn {
  flex: 1; background: #FFFFFF; border: 2rpx solid #BBF7D0; color: #22C55E;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s;
}
.compare-btn:active { background: #F0FDF4; }

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

/* 情绪支持弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 9999; display: flex; align-items: flex-end;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.emotional-modal {
  background: #FFFFFF; width: 100%;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx; padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.emotional-header { display: flex; align-items: center; margin-bottom: 24rpx; }
.emotional-avatar {
  width: 56rpx; height: 56rpx; border-radius: 14rpx;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-right: 14rpx;
}
.emotional-avatar .ph { font-size: 28rpx; color: #FF6B6B; }
.emotional-title { flex: 1; font-size: 28rpx; font-weight: 700; color: #2D3748; }
.emotional-close .ph { font-size: 32rpx; color: #A0AEC0; }
.emotional-loading { display: flex; align-items: center; padding: 24rpx 0; color: #A0AEC0; font-size: 24rpx; gap: 16rpx; }
.loading-spinner-sm {
  width: 36rpx; height: 36rpx; flex-shrink: 0;
  border: 4rpx solid #F0F0F0; border-top-color: #FF6B6B;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.emotional-content {
  font-size: 26rpx; color: #2D3748; line-height: 1.8; margin-bottom: 28rpx;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  border-radius: 16rpx; padding: 24rpx; font-weight: 500;
}
.emotional-actions { display: flex; flex-direction: column; gap: 16rpx; }
.emotional-chat-btn {
  width: 100%; background: linear-gradient(135deg, #FF6B6B, #EF4444); color: #FFFFFF;
  border-radius: 14rpx; padding: 24rpx; font-size: 26rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; gap: 10rpx;
  box-shadow: 0 4rpx 12rpx rgba(255,107,107,0.2); transition: all 0.2s;
}
.emotional-chat-btn:active { transform: scale(0.97); }
.emotional-chat-btn .ph { font-size: 26rpx; }
.emotional-close-btn {
  width: 100%; background: #F5F5F5; color: #A0AEC0;
  border-radius: 14rpx; padding: 24rpx; font-size: 26rpx; font-weight: 700; transition: all 0.2s;
}
.emotional-close-btn:active { background: #EFF6FF; color: #4F9EF8; }
</style>
