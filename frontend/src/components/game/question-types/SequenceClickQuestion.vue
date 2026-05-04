<template>
  <view class="sc-card">
    <!-- 阶段提示 -->
    <view class="sc-phase-banner" :class="displayPhase ? 'phase-watch' : 'phase-click'">
      <text class="ph" :class="displayPhase ? 'ph-eye' : 'ph-cursor-click'"></text>
      <text class="sc-phase-text">{{ displayPhase ? '记住格子亮起的顺序' : '请按顺序点击格子' }}</text>
    </view>

    <!-- 格子网格 -->
    <view class="sc-grid" :style="gridStyle">
      <view
        v-for="idx in totalCells" :key="idx"
        class="sc-cell"
        :class="{
          highlighted: displayPhase && (idx - 1) === currentHighlight,
          clicked:     !displayPhase && clickedSet.has(idx - 1),
          disabled:    displayPhase,
        }"
        @click="handleCellClick(idx - 1)"
      ></view>
    </view>

    <!-- 输入阶段倒计时条 -->
    <view class="sc-timer-bar" v-if="!displayPhase && !submitted">
      <view class="sc-timer-fill" :style="{ width: timerPercent + '%' }"></view>
    </view>

    <!-- 进度提示（输入阶段） -->
    <view class="sc-progress-hint" v-if="!displayPhase && !submitted">
      已点击 {{ clickedSequence.length }} / {{ sequence.length }}
    </view>
  </view>
</template>

<script>
import { scoreSequenceClick } from '@/utils/levelScoring'

export default {
  name: 'SequenceClickQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      displayPhase: true,
      currentHighlight: -1,
      clickedSequence: [],
      clickedSet: new Set(),
      submitted: false,
      displayTimer: null,
      inputTimer: null,
      timeLeft: 0,
    }
  },
  computed: {
    gridSize() { return this.question.grid_size || 3 },
    totalCells() { return this.gridSize * this.gridSize },
    sequence() { return this.question.sequence || [] },
    displayInterval() { return this.question.display_interval || 800 },
    gridStyle() {
      const size = this.gridSize
      const cellPx = Math.min(160, Math.floor(560 / size))
      return {
        display: 'grid',
        gridTemplateColumns: `repeat(${size}, ${cellPx}rpx)`,
        gridTemplateRows: `repeat(${size}, ${cellPx}rpx)`,
        gap: '16rpx',
      }
    },
    timerPercent() {
      const total = this.question.time_limit || 15
      return Math.max(0, (this.timeLeft / total) * 100)
    },
  },
  watch: {
    question: { immediate: true, handler() { this.reset() } },
  },
  beforeUnmount() { this.clearAllTimers() },
  methods: {
    reset() {
      this.clearAllTimers()
      this.displayPhase = true
      this.currentHighlight = -1
      this.clickedSequence = []
      this.clickedSet = new Set()
      this.submitted = false
      this.startDisplayPhase()
    },
    startDisplayPhase() {
      let idx = 0
      // 短暂延迟后开始展示
      setTimeout(() => {
        this.displayTimer = setInterval(() => {
          if (idx < this.sequence.length) {
            this.currentHighlight = this.sequence[idx]
            idx++
          } else {
            clearInterval(this.displayTimer)
            this.displayTimer = null
            // 展示完毕，切换到输入阶段
            setTimeout(() => {
              this.currentHighlight = -1
              this.displayPhase = false
              this.startInputTimer()
            }, 400)
          }
        }, this.displayInterval)
      }, 500)
    },
    startInputTimer() {
      this.timeLeft = this.question.time_limit || 15
      this.inputTimer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this.clearAllTimers(); this.submitAnswer() }
      }, 1000)
    },
    clearAllTimers() {
      if (this.displayTimer) { clearInterval(this.displayTimer); this.displayTimer = null }
      if (this.inputTimer)   { clearInterval(this.inputTimer);   this.inputTimer = null }
    },
    handleCellClick(index) {
      if (this.displayPhase || this.submitted) return
      if (this.clickedSet.has(index)) return
      const s = new Set(this.clickedSet)
      s.add(index)
      this.clickedSet = s
      this.clickedSequence.push(index)
      if (this.clickedSequence.length === this.sequence.length) {
        this.clearAllTimers()
        this.submitAnswer()
      }
    },
    submitAnswer() {
      if (this.submitted) return
      this.submitted = true
      const score = scoreSequenceClick(this.clickedSequence, this.sequence)
      this.$emit('answer-submitted', {
        score,
        clickedSequence: this.clickedSequence,
        isCorrect: score >= 1.0,
      })
    },
  },
}
</script>

<style scoped>
.sc-card {
  margin: 16rpx 32rpx 0;
  background: #FFFFFF; border-radius: 28rpx; padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  display: flex; flex-direction: column; align-items: center; gap: 28rpx;
}

/* 阶段横幅 */
.sc-phase-banner {
  width: 100%; padding: 16rpx 24rpx; border-radius: 16rpx;
  display: flex; align-items: center; gap: 12rpx;
}
.phase-watch { background: linear-gradient(135deg, #FFF9C4, #FEF3C7); }
.phase-watch .ph { color: #D97706; font-size: 32rpx; }
.phase-click { background: linear-gradient(135deg, #DBEAFE, #EFF6FF); }
.phase-click .ph { color: #2563EB; font-size: 32rpx; }
.sc-phase-text { font-size: 26rpx; font-weight: 700; color: #374151; }

/* 格子网格 */
.sc-grid { padding: 8rpx; }
.sc-cell {
  background: #F3F4F6; border-radius: 16rpx;
  border: 3rpx solid #E5E7EB; transition: all 0.2s;
}
.sc-cell.highlighted {
  background: linear-gradient(135deg, #FCD34D, #F59E0B);
  border-color: #F59E0B;
  box-shadow: 0 0 20rpx rgba(245,158,11,0.5);
  transform: scale(1.05);
}
.sc-cell.clicked {
  background: linear-gradient(135deg, #6EE7B7, #34D399);
  border-color: #10B981;
}
.sc-cell.disabled { pointer-events: none; }
.sc-cell:active:not(.disabled) { transform: scale(0.92); }

/* 倒计时条 */
.sc-timer-bar {
  width: 100%; height: 12rpx; background: #F3F4F6; border-radius: 6rpx; overflow: hidden;
}
.sc-timer-fill {
  height: 100%; background: linear-gradient(90deg, #34D399, #F59E0B, #FF6B6B);
  border-radius: 6rpx; transition: width 1s linear;
}

/* 进度提示 */
.sc-progress-hint { font-size: 24rpx; color: #9CA3AF; font-weight: 600; }
</style>
