<template>
  <view class="page-container">
    <view class="stars-area">
      <view class="star star-left pop-in" style="animation-delay:0.1s"><text class="ph ph-star-fill"></text></view>
      <view class="star star-center pop-in" style="animation-delay:0.3s"><text class="ph ph-star-fill"></text></view>
      <view class="star star-right pop-in" style="animation-delay:0.5s"><text class="ph ph-star-fill"></text></view>
    </view>

    <view class="content-area">
      <view class="congrats-title pop-in" style="animation-delay:0.7s">训练完成！🎉</view>

      <!-- 训练成绩卡 -->
      <view class="result-card pop-in" style="animation-delay:0.8s">
        <view class="result-row">
          <view class="result-item">
            <view class="result-val green">{{ result.correct_count }}</view>
            <view class="result-label">答对题数</view>
          </view>
          <view class="result-divider"></view>
          <view class="result-item">
            <view class="result-val">{{ result.total_count }}</view>
            <view class="result-label">总题数</view>
          </view>
          <view class="result-divider"></view>
          <view class="result-item">
            <view class="result-val" :class="accuracyClass">{{ result.accuracy }}%</view>
            <view class="result-label">正确率</view>
          </view>
        </view>
        <view class="accuracy-bar-wrap">
          <view class="accuracy-bar" :class="accuracyClass" :style="{ width: result.accuracy + '%' }"></view>
        </view>
        <view class="accuracy-hint">{{ accuracyHint }}</view>
      </view>

      <!-- AI 鼓励 -->
      <view class="ai-encouragement pop-in" style="animation-delay:1s" v-if="encouragement">
        <view class="ai-enc-avatar"><text class="ph-fill ph-robot"></text></view>
        <view class="ai-enc-bubble">
          <view class="ai-enc-text">{{ encouragement }}</view>
        </view>
      </view>
      <view class="ai-encouragement-loading pop-in" style="animation-delay:1s" v-else-if="encLoading">
        <view class="enc-dots">
          <view class="enc-dot"></view><view class="enc-dot"></view><view class="enc-dot"></view>
        </view>
      </view>

      <!-- 总星星 -->
      <view class="total-stars pop-in" style="animation-delay:1.1s">
        <text class="ph ph-star"></text> 累计 {{ totalStars }} 颗星星
      </view>

      <!-- 动态训练策略建议 -->
      <view class="strategy-card pop-in" style="animation-delay:1.15s" v-if="strategy">
        <view class="strategy-header">
          <text class="ph ph-lightbulb strategy-icon"></text>
          <view class="strategy-title">下次训练建议</view>
        </view>
        <view class="strategy-body">{{ strategy }}</view>
        <view class="strategy-tags">
          <view class="strategy-tag" :class="strategyTag.color" v-for="strategyTag in strategyTags" :key="strategyTag.text">
            {{ strategyTag.text }}
          </view>
        </view>
      </view>

      <button class="return-btn pop-in" style="animation-delay:1.2s" @click="returnHome">
        回到训练乐园
      </button>
      <view class="parent-note pop-in" style="animation-delay:1.3s">（训练结果已同步给爸爸妈妈）</view>
    </view>
  </view>
</template>

<script>
import { getTotalStars } from '../../../api/training.js'
import { getEncouragement } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      result: { correct_count: 0, total_count: 0, accuracy: 0, game_type: 'visual', stars: 1 },
      totalStars: 0,
      encouragement: '',
      encLoading: false,
      strategy: '',
      strategyTags: [],
    }
  },
  computed: {
    accuracyClass() {
      if (this.result.accuracy >= 80) return 'green'
      if (this.result.accuracy >= 60) return 'orange'
      return 'red'
    },
    accuracyHint() {
      if (this.result.accuracy >= 80) return '太棒了，表现非常出色！'
      if (this.result.accuracy >= 60) return '做得不错，继续练习会更好！'
      return '没关系，多练几次就会进步的！'
    },
  },
  onLoad() {
    const r = uni.getStorageSync('last_training_result') || {}
    this.result = { correct_count: r.correct_count || 0, total_count: r.total_count || 0, accuracy: r.accuracy || 0, game_type: r.game_type || 'visual', stars: r.stars || 1 }
    this.loadStars()
    this.loadEncouragement()
  },
  methods: {
    async loadStars() {
      const child = getCurrentChild()
      if (!child) return
      try {
        const res = await getTotalStars(child.id)
        this.totalStars = res.total_stars || 0
      } catch (e) { console.warn('加载星星失败', e) }
    },
    async loadEncouragement() {
      const child = getCurrentChild()
      if (!child) return
      this.encLoading = true
      try {
        const res = await getEncouragement({
          child_id: child.id,
          game_type: this.result.game_type,
          score: this.result.accuracy,
          correct_count: this.result.correct_count,
          total_count: this.result.total_count,
        })
        this.encouragement = res.encouragement
      } catch (e) {
        const a = this.result.accuracy
        this.encouragement = a >= 80 ? `${child.name}太厉害了！🌟 训练效果很棒！` : a >= 60 ? `${child.name}做得很好！💪 继续加油！` : `${child.name}已经很努力了！🌈 下次会更好！`
      } finally {
        this.encLoading = false
      }
      // 生成动态策略建议
      this._buildStrategy(child)
    },

    _buildStrategy(child) {
      const a = this.result.accuracy
      const type = this.result.game_type
      const typeNames = {
        visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
        working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
        handwriting: '汉字书写', flip_card: '翻牌记忆', connect_game: '连一连',
      }
      const typeName = typeNames[type] || '本项训练'

      if (a >= 85) {
        this.strategy = `${typeName}表现优秀！下次可以尝试更高难度的题目，挑战自己的极限。`
        this.strategyTags = [
          { text: '可提升难度', color: 'green' },
          { text: '保持节奏', color: 'blue' },
        ]
      } else if (a >= 70) {
        this.strategy = `${typeName}表现良好，建议保持当前难度，每天坚持练习 10 分钟，巩固已有进步。`
        this.strategyTags = [
          { text: '保持当前难度', color: 'blue' },
          { text: '每日坚持', color: 'orange' },
        ]
      } else if (a >= 50) {
        this.strategy = `${typeName}还有提升空间，建议适当降低难度，先把基础打牢，不要着急。`
        this.strategyTags = [
          { text: '建议降低难度', color: 'orange' },
          { text: '多鼓励孩子', color: 'green' },
        ]
      } else {
        this.strategy = `这次${typeName}有些困难，建议家长陪伴练习，从最简单的题目开始，循序渐进。`
        this.strategyTags = [
          { text: '家长陪伴练习', color: 'red' },
          { text: '从基础开始', color: 'orange' },
        ]
      }
    },
    returnHome() {
      uni.removeStorageSync('last_training_result')
      uni.redirectTo({ url: '/pages/child/child-training/index' })
    },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; display: flex; flex-direction: column; padding-bottom: env(safe-area-inset-bottom); overflow-x: hidden; }
.stars-area { width: 100%; height: 280rpx; position: relative; flex-shrink: 0; margin-top: 60rpx; margin-bottom: 16rpx; }
.star { position: absolute; display: flex; align-items: center; justify-content: center; }
.star-left { left: 50%; bottom: 20rpx; transform: translateX(-160rpx); font-size: 88rpx; color: #4F9EF8; filter: drop-shadow(0 4rpx 8rpx rgba(79,158,248,0.35)); }
.star-center { left: 50%; bottom: 40rpx; transform: translateX(-50%); font-size: 144rpx; color: #4F9EF8; filter: drop-shadow(0 6rpx 20rpx rgba(79,158,248,0.45)); animation: starPulse 2s ease-in-out infinite; }
.star-right { left: 50%; bottom: 20rpx; transform: translateX(72rpx); font-size: 88rpx; color: #4F9EF8; filter: drop-shadow(0 4rpx 8rpx rgba(79,158,248,0.35)); }
@keyframes starPulse { 0%,100% { transform: translateX(-50%) scale(1); } 50% { transform: translateX(-50%) scale(1.08); } }@keyframes starPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.08); } }
.content-area { display: flex; flex-direction: column; align-items: center; padding: 0 32rpx 80rpx; }
.congrats-title { font-size: 52rpx; font-weight: 800; color: #2D3748; margin-bottom: 24rpx; }
.result-card { background: #FFFFFF; border-radius: 24rpx; padding: 28rpx; width: 100%; margin-bottom: 28rpx; box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.06); }
.result-row { display: flex; align-items: center; justify-content: space-around; margin-bottom: 20rpx; }
.result-item { display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.result-val { font-size: 52rpx; font-weight: 800; color: #2D3748; }
.result-val.green { color: #22C55E; }
.result-val.orange { color: #F57F17; }
.result-val.red { color: #FF6B6B; }
.result-label { font-size: 22rpx; color: #A0AEC0; font-weight: 600; }
.result-divider { width: 2rpx; height: 60rpx; background: #F0F0F0; }
.accuracy-bar-wrap { height: 12rpx; background: #F0F0F0; border-radius: 6rpx; overflow: hidden; margin-bottom: 12rpx; }
.accuracy-bar { height: 100%; border-radius: 6rpx; transition: width 0.8s cubic-bezier(0.4,0,0.2,1); }
.accuracy-bar.green { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.accuracy-bar.orange { background: linear-gradient(90deg, #F57F17, #FFB74D); }
.accuracy-bar.red { background: linear-gradient(90deg, #FF6B6B, #FF8E8E); }
.accuracy-hint { font-size: 22rpx; color: #718096; text-align: center; font-weight: 500; }
.ai-encouragement { display: flex; align-items: flex-end; gap: 12rpx; margin-bottom: 28rpx; max-width: 600rpx; width: 100%; }
.ai-enc-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ai-enc-avatar .ph { font-size: 32rpx; color: #FFFFFF; }
.ai-enc-bubble { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 2rpx solid #BFDBFE; border-radius: 24rpx; border-bottom-left-radius: 6rpx; padding: 20rpx 24rpx; flex: 1; }
.ai-enc-text { font-size: 26rpx; color: #2D3748; line-height: 1.6; font-weight: 500; }
.ai-encouragement-loading { display: flex; justify-content: center; margin-bottom: 28rpx; height: 64rpx; align-items: center; }
.enc-dots { display: flex; gap: 12rpx; }
.enc-dot { width: 16rpx; height: 16rpx; border-radius: 50%; background: #4F9EF8; animation: enc-bounce 1.2s infinite; }
.enc-dot:nth-child(2) { animation-delay: 0.2s; }
.enc-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes enc-bounce { 0%,80%,100% { transform: scale(0.6) translateY(0); opacity: 0.4; } 40% { transform: scale(1.1) translateY(-10rpx); opacity: 1; } }
.total-stars { display: flex; align-items: center; gap: 10rpx; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); padding: 16rpx 36rpx; border-radius: 20rpx; font-size: 26rpx; font-weight: 700; color: #2D3748; margin-bottom: 48rpx; }
.total-stars .ph { font-size: 28rpx; color: #4F9EF8; }
.return-btn { width: 100%; max-width: 600rpx; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; border-radius: 20rpx; padding: 32rpx; font-size: 36rpx; font-weight: 800; box-shadow: 0 4rpx 16rpx rgba(59,130,246,0.3); transition: all 0.2s; }
.return-btn:active { transform: scale(0.97); }
.parent-note { font-size: 22rpx; color: #CBD5E0; margin-top: 32rpx; font-weight: 500; }

/* 动态策略建议卡片 */
.strategy-card {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FDE68A;
  border-radius: 24rpx;
  padding: 24rpx 28rpx;
  width: 100%;
  margin-bottom: 28rpx;
}
.strategy-header {
  display: flex; align-items: center; gap: 10rpx; margin-bottom: 12rpx;
}
.strategy-icon { font-size: 28rpx; color: #F59E0B; }
.strategy-title { font-size: 24rpx; font-weight: 700; color: #92400E; }
.strategy-body { font-size: 24rpx; color: #78350F; line-height: 1.7; margin-bottom: 14rpx; font-weight: 500; }
.strategy-tags { display: flex; flex-wrap: wrap; gap: 10rpx; }
.strategy-tag { font-size: 20rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 10rpx; }
.strategy-tag.green { background: rgba(34,197,94,0.12); color: #22C55E; }
.strategy-tag.blue { background: rgba(79,158,248,0.12); color: #4F9EF8; }
.strategy-tag.orange { background: rgba(245,127,23,0.12); color: #F57F17; }
.strategy-tag.red { background: rgba(255,107,107,0.12); color: #FF6B6B; }
@keyframes popIn { 0% { transform: scale(0.5); opacity: 0; } 70% { transform: scale(1.05); } 100% { transform: scale(1); opacity: 1; } }
.pop-in { opacity: 0; animation: popIn 0.4s cubic-bezier(0.4,0,0.2,1) forwards; }
</style>
