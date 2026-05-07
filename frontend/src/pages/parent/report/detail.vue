<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">报告详情</view>
      <view class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text>
      </view>
    </view>

    <scroll-view class="page-content" scroll-y v-if="report">
      <!-- 基本信息 -->
      <view class="summary-card">
        <view class="summary-top">
          <attention-badge :level="report.risk_level"></attention-badge>
          <view class="summary-date">{{ formatDate(report.created_at) }}</view>
        </view>
        <view class="summary-score">{{ report.overall_score }}<text class="score-unit">分</text></view>
        <view class="summary-game">{{ gameTypeName(report.game_type) }} 能力探索</view>
        <view class="summary-text">{{ report.summary }}</view>
      </view>

      <!-- 维度得分 -->
      <view class="section-title">各维度得分</view>
      <view class="dimensions-card" v-if="dimensions && Object.keys(dimensions).length > 0">
        <view class="dim-item" v-for="(score, dim) in dimensions" :key="dim">
          <view class="dim-header">
            <view class="dim-name">{{ dimName(dim) }}</view>
            <view class="dim-score" :class="score >= 75 ? 'green' : score >= 60 ? 'orange' : 'red'">{{ score }}分</view>
          </view>
          <view class="dim-bar">
            <view class="dim-fill" :class="score >= 75 ? 'green' : score >= 60 ? 'orange' : 'red'" :style="{ width: score + '%' }"></view>
          </view>
          <view class="dim-hint">{{ dimHint(dim, score) }}</view>
        </view>
      </view>
      <view class="empty-dims" v-else>
        <text class="ph ph-chart-bar"></text>
        <view>暂无维度数据</view>
      </view>

      <!-- 成长建议 -->
      <view class="section-title">成长建议</view>
      <view class="advice-card">
        <view class="advice-text">{{ report.recommendations }}</view>
        <button class="advice-btn" @click="goToTraining">查看训练计划 →</button>
      </view>

      <!-- 操作按钮 -->
      <view class="action-row">
        <button class="action-btn primary" @click="goToScreening">发起复评</button>
        <button class="action-btn" :class="report.risk_level === 'high' ? 'ai-highlight' : 'outline'" @click="goToAiChat">
          <text class="ph ph-robot"></text> AI 解读
        </button>
      </view>

      <!-- 导出报告 -->
      <view class="export-row">
        <button class="export-btn" @click="exportReport" :class="{ loading: exporting }">
          <text class="ph" :class="exporting ? 'ph-circle-notch spin' : 'ph-download-simple'"></text>
          {{ exporting ? '生成中...' : '导出报告' }}
        </button>
        <view class="export-hint">生成文字版报告，可截图保存或分享</view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <!-- 加载中 -->
    <view class="loading-state" v-else-if="loading">
      <text class="ph ph-circle-notch spin"></text>
      <view>加载中...</view>
    </view>

    <!-- 加载失败 -->
    <view class="error-state" v-else>
      <text class="ph ph-warning-circle"></text>
      <view>报告加载失败</view>
      <button class="retry-btn" @click="loadReport">重试</button>
    </view>
  </view>
</template>

<script>
import { getReport, getReportDimensions, exportReportText } from '../../../api/report.js'
import AttentionBadge from '../../../components/common/AttentionBadge.vue'
import { friendlyRiskLevel } from '../../../utils/terminology.js'

const GAME_TYPE_NAMES = {
  visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
  working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
}

const DIM_NAMES = {
  visual_discrimination: '视觉辨识能力', phonological: '音形映射能力',
  character_order: '字序组织能力', spelling: '拼写输出能力',
  reading_comprehension: '阅读理解能力', semantic_integration: '语义整合能力',
  information_extraction: '信息提取能力', attention: '任务注意力',
  working_memory_capacity: '工作记忆容量', short_term_memory: '短时记忆能力',
  rapid_naming_speed: '快速命名速度', phonological_awareness: '音韵意识',
  fine_motor_control: '精细动作控制', visual_motor_integration: '视动整合能力',
}

export default {
  components: { AttentionBadge },
  data() {
    return {
      reportId: null,
      report: null,
      dimensions: {},
      loading: true,
      exporting: false,
    }
  },
  onLoad(options) {
    if (options.id) {
      this.reportId = parseInt(options.id)
      this.loadReport()
    } else {
      this.loading = false
    }
  },
  methods: {
    async loadReport() {
      if (!this.reportId) return
      this.loading = true
      try {
        const [report, dimRes] = await Promise.all([
          getReport(this.reportId),
          getReportDimensions(this.reportId),
        ])
        this.report = report
        this.dimensions = dimRes.dimensions || {}
      } catch (e) {
        console.error('加载报告失败', e)
        this.report = null
      } finally {
        this.loading = false
      }
    },
    riskLabel(level) {
      return friendlyRiskLevel(level)
    },
    gameTypeName(type) {
      return GAME_TYPE_NAMES[type] || type || '综合'
    },
    dimName(dim) {
      return DIM_NAMES[dim] || dim
    },
    dimHint(dim, score) {
      if (score >= 75) return '表现良好'
      if (score >= 60) return '需适当关注'
      return '重点关注维度'
    },
    scoreClass(score) {
      if (score >= 75) return 'green'
      if (score >= 60) return 'orange'
      return 'red'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    goBack() { uni.navigateBack() },
    goToAiChat() { uni.navigateTo({ url: '/pages/parent/ai-chat/index' }) },
    goToTraining() { uni.navigateTo({ url: '/pages/parent/training/index' }) },
    goToScreening() { uni.navigateTo({ url: '/pages/parent/screening/index' }) },

    async exportReport() {
      if (!this.report || this.exporting) return
      this.exporting = true
      try {
        // 优先使用服务端生成的报告文字（更准确）
        const res = await exportReportText(this.reportId)
        const content = res.content
        uni.setClipboardData({
          data: content,
          success: () => {
            uni.showModal({
              title: '报告已复制',
              content: '报告文字内容已复制到剪贴板，可粘贴到备忘录或微信中保存分享。',
              showCancel: false,
              confirmText: '好的',
            })
          },
          fail: () => {
            uni.showToast({ title: '复制失败，请重试', icon: 'none' })
          }
        })
      } catch (e) {
        // 降级：本地生成
        this._exportLocal()
      } finally {
        this.exporting = false
      }
    },

    _exportLocal() {
      const lines = []
      lines.push('═══════════════════════════════')
      lines.push('  悦读灯塔 · 成长评估报告')
      lines.push('═══════════════════════════════')
      lines.push(`游戏类型：${this.gameTypeName(this.report.game_type)}`)
      lines.push(`评估日期：${this.formatDate(this.report.created_at)}`)
      lines.push(`综合得分：${this.report.overall_score} 分`)
      lines.push(`关注等级：${this.riskLabel(this.report.risk_level)}`)
      lines.push('───────────────────────────────')
      lines.push('【评估总结】')
      lines.push(this.report.summary || '暂无')
      lines.push('───────────────────────────────')
      lines.push('【各维度得分】')
      if (this.dimensions && Object.keys(this.dimensions).length > 0) {
        for (const [dim, score] of Object.entries(this.dimensions)) {
          const bar = '█'.repeat(Math.round(score / 10)) + '░'.repeat(10 - Math.round(score / 10))
          lines.push(`${this.dimName(dim)}  ${bar}  ${score}分`)
        }
      } else {
        lines.push('暂无维度数据')
      }
      lines.push('───────────────────────────────')
      lines.push('【成长建议】')
      lines.push(this.report.recommendations || '暂无')
      lines.push('───────────────────────────────')
      lines.push('⚠️ 本报告仅供参考，不构成专业观察结论')
      lines.push('═══════════════════════════════')
      uni.setClipboardData({
        data: lines.join('\n'),
        success: () => uni.showToast({ title: '报告已复制', icon: 'success' }),
        fail: () => uni.showToast({ title: '复制失败', icon: 'none' }),
      })
    },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center; box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { flex: 1; font-size: 30rpx; font-weight: 700; color: #2D3748; }
.ai-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
}
.ai-btn .ph { font-size: 28rpx; color: #4F9EF8; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

.summary-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 32rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}
.summary-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20rpx; }
.risk-badge { font-size: 22rpx; font-weight: 700; padding: 6rpx 20rpx; border-radius: 12rpx; }
.risk-badge.low { background: rgba(34,197,94,0.1); color: #22C55E; }
.risk-badge.medium { background: rgba(245,127,23,0.1); color: #F57F17; }
.risk-badge.high { background: rgba(255,107,107,0.1); color: #FF6B6B; }
.summary-date { font-size: 20rpx; color: #A0AEC0; }
.summary-score { font-size: 80rpx; font-weight: 800; color: #2D3748; line-height: 1; }
.score-unit { font-size: 28rpx; font-weight: 600; color: #A0AEC0; }
.summary-game { font-size: 22rpx; color: #A0AEC0; margin-bottom: 16rpx; font-weight: 500; }
.summary-text { font-size: 26rpx; color: #718096; line-height: 1.7; font-weight: 500; }

.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
}

.dimensions-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 28rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}
.dim-item { margin-bottom: 24rpx; }
.dim-item:last-child { margin-bottom: 0; }
.dim-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8rpx; }
.dim-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.dim-score { font-size: 24rpx; font-weight: 700; }
.dim-score.green { color: #22C55E; }
.dim-score.orange { color: #F57F17; }
.dim-score.red { color: #FF6B6B; }
.dim-bar { height: 10rpx; background: #F0F0F0; border-radius: 5rpx; overflow: hidden; margin-bottom: 6rpx; }
.dim-fill { height: 100%; border-radius: 5rpx; transition: width 0.5s; }
.dim-fill.green { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.dim-fill.orange { background: linear-gradient(90deg, #F57F17, #FFB74D); }
.dim-fill.red { background: linear-gradient(90deg, #FF6B6B, #FF8E8E); }
.dim-hint { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

.empty-dims {
  display: flex; flex-direction: column; align-items: center; gap: 12rpx;
  padding: 48rpx 0; color: #A0AEC0; font-size: 24rpx; margin-bottom: 24rpx;
}
.empty-dims .ph { font-size: 64rpx; color: #D1D5DB; }

.advice-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx; padding: 28rpx; margin-bottom: 24rpx; border: 1rpx solid #BFDBFE;
}
.advice-text { font-size: 26rpx; color: #718096; line-height: 1.7; margin-bottom: 20rpx; font-weight: 500; }
.advice-btn {
  width: 100%; background: #FFFFFF; border: 2rpx solid #BFDBFE; color: #4F9EF8;
  border-radius: 14rpx; padding: 22rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

.action-row { display: flex; gap: 16rpx; margin-bottom: 16rpx; }
.action-btn { flex: 1; border-radius: 16rpx; padding: 24rpx; font-size: 26rpx; font-weight: 700; transition: all 0.2s; }
.action-btn:active { transform: scale(0.97); }
.action-btn.primary { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2); }
.action-btn.outline { background: #FFFFFF; border: 2rpx solid #E5E7EB; color: #718096; }
.action-btn.ai-highlight {
  background: linear-gradient(135deg, #F5F3FF, #EDE9FE);
  border: 2rpx solid #DDD6FE;
  color: #7C3AED;
  font-weight: 700;
}
.action-btn.ai-highlight .ph { margin-right: 6rpx; }

/* 高风险 AI 引导卡片 */
.ai-guide-card {
  background: linear-gradient(135deg, #7C3AED, #A78BFA);
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 6rpx 20rpx rgba(124, 58, 237, 0.3);
  transition: all 0.2s;
}
.ai-guide-card:active { transform: scale(0.98); }

.ai-guide-left {
  display: flex;
  align-items: center;
  gap: 16rpx;
  flex: 1;
}

.ai-guide-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ai-guide-icon .ph { font-size: 36rpx; color: #FFFFFF; }

.ai-guide-text { flex: 1; }
.ai-guide-title { font-size: 28rpx; font-weight: 800; color: #FFFFFF; margin-bottom: 6rpx; }
.ai-guide-desc { font-size: 22rpx; color: rgba(255,255,255,0.85); line-height: 1.4; font-weight: 500; }

.ai-guide-arrow {
  font-size: 28rpx;
  color: rgba(255,255,255,0.8);
  flex-shrink: 0;
}

.export-row { display: flex; flex-direction: column; align-items: center; gap: 10rpx; margin-bottom: 24rpx; }
.export-btn {
  width: 100%; border-radius: 16rpx; padding: 24rpx; font-size: 26rpx; font-weight: 700;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7); color: #22C55E;
  border: 2rpx solid #86EFAC;
  display: flex; align-items: center; justify-content: center; gap: 10rpx;
  transition: all 0.2s;
}
.export-btn:active { transform: scale(0.97); }
.export-btn.loading { opacity: 0.7; }
.export-btn .ph { font-size: 26rpx; }
.export-hint { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

.loading-state, .error-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 60vh; gap: 20rpx; color: #A0AEC0; font-size: 26rpx;
}
.loading-state .ph { font-size: 64rpx; color: #4F9EF8; }
.error-state .ph { font-size: 64rpx; color: #FF6B6B; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }
.retry-btn { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; border-radius: 14rpx; padding: 16rpx 40rpx; font-size: 26rpx; font-weight: 700; margin-top: 8rpx; }
</style>
