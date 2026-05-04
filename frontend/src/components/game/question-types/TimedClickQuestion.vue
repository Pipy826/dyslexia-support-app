<template>
  <view class="tc-card">
    <!-- 目标描述 + 倒计时 -->
    <view class="tc-header">
      <view class="tc-target-desc">{{ question.target_description }}</view>
      <view class="tc-countdown" :class="{ urgent: timeLeft <= 3 }">{{ timeLeft }}s</view>
    </view>

    <!-- 倒计时进度条 -->
    <view class="tc-timer-bar">
      <view class="tc-timer-fill" :style="{ width: timerPercent + '%', background: timerBarColor }"></view>
    </view>

    <!-- 项目网格 -->
    <view class="tc-grid" :style="gridStyle">
      <view
        v-for="item in question.items" :key="item.id"
        class="tc-item"
        :class="{
          'tc-clicked':     clickedIds.has(item.id),
          'tc-wrong-flash': wrongFlashId === item.id,
        }"
        :style="itemStyle(item)"
        @click="handleItemClick(item)"
      >
        <text class="tc-shape-icon">{{ shapeIcon(item.shape) }}</text>
      </view>
    </view>
  </view>
</template>

<script>
import { scoreTimedClick } from '@/utils/levelScoring'

export default {
  name: 'TimedClickQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted', 'skip-question'],
  data() {
    return {
      clickedIds: new Set(),
      timeLeft: 0,
      timer: null,
      submitted: false,
      wrongFlashId: null,
    }
  },
  computed: {
    gridCols() {
      const n = this.question.items?.length || 0
      return n <= 4 ? 2 : n <= 9 ? 3 : 4
    },
    gridStyle() {
      return {
        display: 'grid',
        gridTemplateColumns: `repeat(${this.gridCols}, 1fr)`,
        gap: '16rpx',
      }
    },
    timerPercent() {
      const total = this.question.time_limit || 10
      return Math.max(0, (this.timeLeft / total) * 100)
    },
    timerBarColor() {
      if (this.timeLeft <= 3) return '#FF6B6B'
      if (this.timeLeft <= 5) return '#F97316'
      return '#EAB308'
    },
  },
  watch: {
    question: { immediate: true, handler(q) { this.reset(q) } },
  },
  beforeUnmount() { this.clearTimer() },
  methods: {
    reset(q) {
      this.clearTimer()
      this.clickedIds = new Set()
      this.submitted = false
      this.wrongFlashId = null
      if (!q?.items?.length) {
        this.$emit('skip-question')
        return
      }
      this.timeLeft = q.time_limit || 10
      this.startTimer()
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this.clearTimer(); this.submitAnswer() }
      }, 1000)
    },
    clearTimer() {
      if (this.timer) { clearInterval(this.timer); this.timer = null }
    },
    shapeIcon(shape) {
      return { circle: '●', square: '■', triangle: '▲' }[shape] || '●'
    },
    itemStyle(item) {
      const colorMap = {
        red: '#EF4444', blue: '#3B82F6', green: '#22C55E',
        yellow: '#EAB308', purple: '#A855F7', orange: '#F97316',
      }
      const bg = colorMap[item.color] || item.color || '#9CA3AF'
      return { background: bg }
    },
    handleItemClick(item) {
      if (this.submitted) return
      if (this.clickedIds.has(item.id)) return
      if (item.is_target) {
        const s = new Set(this.clickedIds)
        s.add(item.id)
        this.clickedIds = s
      } else {
        this.wrongFlashId = item.id
        setTimeout(() => { this.wrongFlashId = null }, 250)
      }
    },
    submitAnswer() {
      if (this.submitted) return
      this.submitted = true
      this.clearTimer()
      const score = scoreTimedClick(this.clickedIds, this.question.items)
      const targets = this.question.items.filter(i => i.is_target)
      const isCorrect = targets.length > 0 && targets.every(t => this.clickedIds.has(t.id))
      this.$emit('answer-submitted', {
        score,
        clickedIds: Array.from(this.clickedIds),
        isCorrect,
      })
    },
  },
}
</script>

<style scoped>
.tc-card {
  margin: 16rpx 32rpx 0;
  background: #FFFFFF; border-radius: 28rpx; padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  display: flex; flex-direction: column; gap: 24rpx;
}

/* 头部 */
.tc-header { display: flex; justify-content: space-between; align-items: center; }
.tc-target-desc {
  font-size: 30rpx; font-weight: 800; color: #2D3748;
  background: #FEF9C3; padding: 10rpx 20rpx; border-radius: 12rpx;
  border: 2rpx solid #FDE047;
}
.tc-countdown {
  font-size: 44rpx; font-weight: 900; color: #EAB308;
  min-width: 80rpx; text-align: right;
}
.tc-countdown.urgent { color: #FF6B6B; animation: blink 0.5s infinite; }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

/* 倒计时条 */
.tc-timer-bar {
  height: 16rpx; background: #F3F4F6; border-radius: 8rpx; overflow: hidden;
}
.tc-timer-fill { height: 100%; border-radius: 8rpx; transition: width 1s linear, background 0.3s; }

/* 项目网格 */
.tc-grid { padding: 8rpx; }
.tc-item {
  height: 120rpx; border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; position: relative; overflow: hidden;
}
.tc-item:active { transform: scale(0.9); }
.tc-shape-icon { font-size: 56rpx; color: rgba(255,255,255,0.9); }
.tc-item.tc-clicked {
  opacity: 0.35;
}
.tc-item.tc-clicked::after {
  content: '✓';
  position: absolute; font-size: 48rpx; color: #FFFFFF; font-weight: 900;
}
.tc-item.tc-wrong-flash {
  animation: wrongFlash 0.25s ease;
}
@keyframes wrongFlash {
  0%,100% { filter: brightness(1); }
  50% { filter: brightness(0.4) sepia(1) hue-rotate(-30deg); }
}
</style>
