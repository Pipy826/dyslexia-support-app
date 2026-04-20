<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">复评对比</view>
    </view>

    <scroll-view class="page-content" scroll-y v-if="current && previous">
      <!-- 对比概览 -->
      <view class="compare-overview">
        <view class="compare-col">
          <view class="col-label">上次筛查</view>
          <view class="col-date">{{ formatDate(previous.created_at) }}</view>
          <view class="col-score" :class="previous.overall_score >= 75 ? 'green' : previous.overall_score >= 60 ? 'orange' : 'red'">
            {{ previous.overall_score }}分
          </view>
          <view class="col-badge" :class="previous.risk_level">{{ riskLabel(previous.risk_level) }}</view>
        </view>
        <view class="compare-arrow">
          <text class="ph ph-arrow-right"></text>
          <view class="compare-trend" :class="trendClass">
            <text :class="['ph', trendIcon]"></text>
            {{ trendText }}
          </view>
        </view>
        <view class="compare-col">
          <view class="col-label">本次筛查</view>
          <view class="col-date">{{ formatDate(current.created_at) }}</view>
          <view class="col-score" :class="current.overall_score >= 75 ? 'green' : current.overall_score >= 60 ? 'orange' : 'red'">
            {{ current.overall_score }}分
          </view>
          <view class="col-badge" :class="current.risk_level">{{ riskLabel(current.risk_level) }}</view>
        </view>
      </view>

      <!-- 维度对比 -->
      <view class="section-title">各维度变化</view>
      <view class="dim-compare-card">
        <view
          class="dim-row"
          v-for="dim in dimCompareList"
          :key="dim.key"
        >
          <view class="dim-name">{{ dim.name }}</view>
          <view class="dim-bars">
            <view class="bar-wrap">
              <view class="bar-label">上次</view>
              <view class="bar-track">
                <view
                  class="bar-fill prev"
                  :style="{ width: dim.prev + '%' }"
                ></view>
              </view>
              <view class="bar-val">{{ dim.prev }}</view>
            </view>
            <view class="bar-wrap">
              <view class="bar-label">本次</view>
              <view class="bar-track">
                <view
                  class="bar-fill curr"
                  :class="dim.delta >= 0 ? 'up' : 'down'"
                  :style="{ width: dim.curr + '%' }"
                ></view>
              </view>
              <view class="bar-val">{{ dim.curr }}</view>
            </view>
          </view>
          <view class="dim-delta" :class="dim.delta > 0 ? 'up' : dim.delta < 0 ? 'down' : 'flat'">
            <text :class="['ph', dim.delta > 0 ? 'ph-trend-up' : dim.delta < 0 ? 'ph-trend-down' : 'ph-minus']"></text>
            {{ dim.delta > 0 ? '+' : '' }}{{ dim.delta !== 0 ? dim.delta : '—' }}
          </view>
        </view>
      </view>

      <!-- AI 对比解读 -->
      <view class="section-title">AI 对比解读</view>
      <view class="ai-compare-card">
        <view class="ai-header">
          <view class="ai-avatar"><text class="ph-fill ph-robot"></text></view>
          <view class="ai-title">智能对比分析</view>
        </view>
        <view class="ai-loading" v-if="aiLoading">
          <view class="loading-spinner"></view>
          <view class="loading-text">AI 正在分析变化趋势...</view>
        </view>
        <view class="ai-content" v-else-if="aiAnalysis">{{ aiAnalysis }}</view>
        <view class="ai-empty" v-else>
          <button class="ai-load-btn" @click="loadAiAnalysis">
            <text class="ph ph-sparkle"></text> 获取 AI 解读
          </button>
        </view>
      </view>

      <!-- 建议 -->
      <view class="section-title">下一步建议</view>
      <view class="advice-card">
        <view class="advice-item" v-for="(item, i) in nextStepAdvice" :key="i">
          <view class="advice-dot" :class="item.color"></view>
          <view class="advice-text">{{ item.text }}</view>
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <!-- 加载中 -->
    <view class="loading-state" v-else>
      <text class="ph ph-circle-notch spin"></text>
      <view>加载中...</view>
    </view>
  </view>
</template>

<script>
import { getReport } from '../../../api/report.js'
import { getGrowthAnalysis } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

const DIM_NAMES = {
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
  rapid_naming_speed:       '命名速度',
  phonological_awareness:   '音韵意识',
  fine_motor_control:       '精细动作',
  visual_motor_integration: '视动整合',
}

export default {
  data() {
    return {
      currentId: null,
      previousId: null,
      current: null,
      previous: null,
      aiAnalysis: '',
      aiLoading: false,
    }
  },
  onLoad(options) {
    this.currentId = options.current_id
    this.previousId = options.previous_id
    this.loadReports()
  },
  computed: {
    scoreDelta() {
      if (!this.current || !this.previous) return 0
      return this.current.overall_score - this.previous.overall_score
    },
    trendClass() {
      if (this.scoreDelta > 5) return 'up'
      if (this.scoreDelta < -5) return 'down'
      return 'flat'
    },
    trendIcon() {
      if (this.scoreDelta > 5) return 'ph-trend-up'
      if (this.scoreDelta < -5) return 'ph-trend-down'
      return 'ph-minus'
    },
    trendText() {
      if (this.scoreDelta > 5) return `+${this.scoreDelta}分 改善`
      if (this.scoreDelta < -5) return `${this.scoreDelta}分 下降`
      return '基本稳定'
    },
    dimCompareList() {
      if (!this.current || !this.previous) return []
      const currDims = this._parseDims(this.current.dimensions)
      const prevDims = this._parseDims(this.previous.dimensions)
      const allKeys = new Set([...Object.keys(currDims), ...Object.keys(prevDims)])
      return [...allKeys].map(key => ({
        key,
        name: DIM_NAMES[key] || key,
        prev: prevDims[key] ?? 0,
        curr: currDims[key] ?? 0,
        delta: (currDims[key] ?? 0) - (prevDims[key] ?? 0),
      })).sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
    },
    nextStepAdvice() {
      if (!this.current) return []
      const level = this.current.risk_level
      const delta = this.scoreDelta
      const advice = []
      if (delta > 5) {
        advice.push({ text: '孩子有明显进步，继续保持当前训练节奏', color: 'green' })
      } else if (delta < -5) {
        advice.push({ text: '本次得分有所下降，建议检查训练是否坚持', color: 'orange' })
      } else {
        advice.push({ text: '得分基本稳定，可适当增加训练强度', color: 'blue' })
      }
      if (level === 'high') {
        advice.push({ text: '仍处于高风险，建议尽快联系专业机构评估', color: 'red' })
      } else if (level === 'medium') {
        advice.push({ text: '建议2周后再次复评，持续跟踪变化', color: 'orange' })
      } else {
        advice.push({ text: '已达低风险，建议1个月后复评维持效果', color: 'green' })
      }
      // 找出最弱维度
      const weakest = this.dimCompareList.filter(d => d.curr < 60).slice(0, 2)
      for (const d of weakest) {
        advice.push({ text: `重点加强：${d.name}（当前 ${d.curr} 分）`, color: 'orange' })
      }
      return advice
    },
  },
  methods: {
    async loadReports() {
      try {
        const [curr, prev] = await Promise.all([
          getReport(this.currentId),
          getReport(this.previousId),
        ])
        this.current = curr
        this.previous = prev
        this.loadAiAnalysis()
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    async loadAiAnalysis() {
      const child = getCurrentChild()
      if (!child || this.aiLoading) return
      this.aiLoading = true
      this.aiAnalysis = ''
      try {
        // 构建对比上下文，直接调用 chat 接口获取针对性对比解读
        const { post } = await import('../../../api/index.js')
        const currDims = this._parseDims(this.current.dimensions)
        const prevDims = this._parseDims(this.previous.dimensions)
        const delta = this.scoreDelta
        const dimChanges = this.dimCompareList.slice(0, 5).map(d => `${d.name}: ${d.prev}→${d.curr}(${d.delta > 0 ? '+' : ''}${d.delta})`).join('、')
        const prompt = `请对比分析孩子两次筛查结果：上次${this.previous.overall_score}分(${this.previous.risk_level})，本次${this.current.overall_score}分(${this.current.risk_level})，变化${delta > 0 ? '+' : ''}${delta}分。主要维度变化：${dimChanges}。请给出简洁的对比解读和下一步建议，100字以内。`
        const res = await post('/api/ai/chat', { child_id: child.id, message: prompt })
        this.aiAnalysis = res.reply || ''
      } catch (e) {
        console.error('AI分析失败', e)
      } finally {
        this.aiLoading = false
      }
    },
    _parseDims(raw) {
      try {
        return (typeof raw === 'string' && raw.trim()) ? JSON.parse(raw) : (raw || {})
      } catch { return {} }
    },
    riskLabel(level) {
      return { low: '低风险', medium: '中风险', high: '高风险' }[level] || level
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
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}

.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

/* 对比概览 */
.compare-overview {
  background: #FFFFFF; border-radius: 24rpx; padding: 32rpx;
  display: flex; align-items: center; gap: 16rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}

.compare-col {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8rpx;
}

.col-label { font-size: 20rpx; color: #A0AEC0; font-weight: 600; }
.col-date { font-size: 20rpx; color: #A0AEC0; }
.col-score { font-size: 48rpx; font-weight: 800; }
.col-score.green { color: #22C55E; }
.col-score.orange { color: #F57F17; }
.col-score.red { color: #FF6B6B; }

.col-badge { font-size: 20rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 10rpx; }
.col-badge.low { background: rgba(34,197,94,0.1); color: #22C55E; }
.col-badge.medium { background: rgba(245,127,23,0.1); color: #F57F17; }
.col-badge.high { background: rgba(255,107,107,0.1); color: #FF6B6B; }

.compare-arrow {
  display: flex; flex-direction: column; align-items: center; gap: 8rpx;
}
.compare-arrow .ph { font-size: 32rpx; color: #D1D5DB; }

.compare-trend {
  font-size: 20rpx; font-weight: 700;
  display: flex; align-items: center; gap: 4rpx;
  padding: 6rpx 14rpx; border-radius: 10rpx;
}
.compare-trend .ph { font-size: 20rpx; }
.compare-trend.up { background: rgba(34,197,94,0.1); color: #22C55E; }
.compare-trend.down { background: rgba(255,107,107,0.1); color: #FF6B6B; }
.compare-trend.flat { background: #F5F5F5; color: #A0AEC0; }

/* 区域标题 */
.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
}

/* 维度对比 */
.dim-compare-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 24rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}

.dim-row {
  display: flex; align-items: center; gap: 12rpx;
  padding: 16rpx 0; border-bottom: 1rpx solid #F5F5F5;
}
.dim-row:last-child { border-bottom: none; }

.dim-name { width: 100rpx; min-width: 100rpx; font-size: 22rpx; font-weight: 600; color: #2D3748; }

.dim-bars { flex: 1; display: flex; flex-direction: column; gap: 8rpx; }

.bar-wrap { display: flex; align-items: center; gap: 8rpx; }
.bar-label { width: 40rpx; font-size: 18rpx; color: #A0AEC0; flex-shrink: 0; }
.bar-track { flex: 1; height: 10rpx; background: #F0F0F0; border-radius: 5rpx; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 5rpx; transition: width 0.5s; }
.bar-fill.prev { background: #D1D5DB; }
.bar-fill.curr.up { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.bar-fill.curr.down { background: linear-gradient(90deg, #FF6B6B, #FF8E8E); }
.bar-fill.curr:not(.up):not(.down) { background: linear-gradient(90deg, #4F9EF8, #93C5FD); }
.bar-val { width: 40rpx; font-size: 18rpx; font-weight: 700; color: #718096; text-align: right; }

.dim-delta {
  width: 72rpx; min-width: 72rpx; font-size: 20rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: flex-end; gap: 2rpx;
}
.dim-delta .ph { font-size: 20rpx; }
.dim-delta.up { color: #22C55E; }
.dim-delta.down { color: #FF6B6B; }
.dim-delta.flat { color: #A0AEC0; }

/* AI 对比卡片 */
.ai-compare-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx; padding: 28rpx; margin-bottom: 24rpx; border: 1rpx solid #BFDBFE;
}

.ai-header { display: flex; align-items: center; gap: 14rpx; margin-bottom: 20rpx; }
.ai-avatar {
  width: 52rpx; height: 52rpx; border-radius: 14rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex; align-items: center; justify-content: center;
}
.ai-avatar .ph { font-size: 26rpx; color: #FFFFFF; }
.ai-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }

.ai-loading { display: flex; align-items: center; gap: 16rpx; padding: 12rpx 0; }
.loading-spinner {
  width: 36rpx; height: 36rpx; border: 4rpx solid #BFDBFE; border-top-color: #4F9EF8;
  border-radius: 50%; animation: spin 0.8s linear infinite; flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 24rpx; color: #4F9EF8; font-weight: 600; }

.ai-content { font-size: 26rpx; color: #2D3748; line-height: 1.8; font-weight: 500; }

.ai-empty { display: flex; justify-content: center; padding: 12rpx 0; }
.ai-load-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 14rpx; padding: 18rpx 40rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; gap: 8rpx;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2);
}
.ai-load-btn .ph { font-size: 24rpx; }

/* 建议卡片 */
.advice-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 28rpx;
  box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  display: flex; flex-direction: column; gap: 16rpx;
}

.advice-item { display: flex; align-items: flex-start; gap: 16rpx; }
.advice-dot { width: 12rpx; height: 12rpx; border-radius: 50%; flex-shrink: 0; margin-top: 8rpx; }
.advice-dot.green { background: #22C55E; }
.advice-dot.orange { background: #F57F17; }
.advice-dot.blue { background: #4F9EF8; }
.advice-dot.red { background: #FF6B6B; }
.advice-text { font-size: 26rpx; color: #718096; line-height: 1.6; font-weight: 500; }

/* 加载状态 */
.loading-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 160rpx 0; gap: 20rpx; color: #A0AEC0; font-size: 26rpx;
}
.loading-state .ph { font-size: 56rpx; color: #D1D5DB; }
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }
</style>
