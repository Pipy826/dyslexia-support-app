<template>
  <view class="tf-card" @touchstart="onTouchStart" @touchend="onTouchEnd">
    <!-- 题目标题 -->
    <view class="tf-header">
      <view class="tf-title">{{ question.title }}</view>
      <view class="tf-instruction">{{ question.instruction }}</view>
    </view>

    <!-- 陈述句 -->
    <view class="tf-statement">
      <text class="tf-statement-text">{{ question.statement }}</text>
    </view>

    <!-- 倒计时条 -->
    <view class="tf-timer-bar" v-if="!submitted">
      <view class="tf-timer-fill" :style="{ width: timerPercent + '%', background: timerColor }"></view>
    </view>

    <!-- 答题按钮 -->
    <view class="tf-buttons" v-if="!submitted">
      <view class="tf-btn tf-true" @click="handleAnswer(true)">
        <text class="tf-btn-icon">✓</text>
        <text class="tf-btn-text">对</text>
      </view>
      <view class="tf-btn tf-false" @click="handleAnswer(false)">
        <text class="tf-btn-icon">✗</text>
        <text class="tf-btn-text">错</text>
      </view>
    </view>

    <!-- 答题后反馈 -->
    <view class="tf-result" v-if="submitted">
      <view :class="['tf-result-icon', isAnswerCorrect ? 'correct' : 'wrong']">
        {{ isAnswerCorrect ? '✓' : '✗' }}
      </view>
      <view class="tf-explanation">{{ question.explanation }}</view>
    </view>

    <!-- 滑动提示 -->
    <view class="tf-swipe-hint" v-if="!submitted">
      <text class="ph ph-arrows-left-right"></text> 左右滑动也可作答
    </view>
  </view>
</template>

<script>
export default {
  name: 'TrueFalseQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      submitted: false,
      userAnswer: null,
      timeLeft: 0,
      timer: null,
      touchStartX: 0,
    }
  },
  computed: {
    isAnswerCorrect() { return this.userAnswer === this.question.is_correct },
    timerPercent() {
      const total = this.question.time_limit || 8
      return Math.max(0, (this.timeLeft / total) * 100)
    },
    timerColor() {
      if (this.timeLeft <= 2) return '#FF6B6B'
      if (this.timeLeft <= 4) return '#F97316'
      return '#22C55E'
    },
  },
  watch: {
    question: { immediate: true, handler() { this.reset() } },
  },
  beforeUnmount() { this.clearTimer() },
  methods: {
    reset() {
      this.submitted = false
      this.userAnswer = null
      this.clearTimer()
      this.timeLeft = this.question.time_limit || 8
      this.startTimer()
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this.clearTimer(); this.handleAnswer(false) }
      }, 1000)
    },
    clearTimer() {
      if (this.timer) { clearInterval(this.timer); this.timer = null }
    },
    handleAnswer(answer) {
      if (this.submitted) return
      this.clearTimer()
      this.submitted = true
      this.userAnswer = answer
      const isCorrect = answer === this.question.is_correct
      this.$emit('answer-submitted', {
        score: isCorrect ? 1.0 : 0.0,
        userAnswer: answer,
        isCorrect,
      })
    },
    onTouchStart(e) {
      this.touchStartX = e.touches[0].clientX
    },
    onTouchEnd(e) {
      if (this.submitted) return
      const delta = e.changedTouches[0].clientX - this.touchStartX
      if (Math.abs(delta) > 60) this.handleAnswer(delta > 0)
    },
  },
}
</script>

<style scoped>
.tf-card {
  margin: 16rpx 32rpx 0;
  background: #FFFFFF; border-radius: 28rpx; padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  display: flex; flex-direction: column; gap: 28rpx;
}
.tf-header { text-align: center; }
.tf-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 8rpx; }
.tf-instruction { font-size: 24rpx; color: #9CA3AF; }

.tf-statement {
  background: #F9FAFB; border-radius: 20rpx; padding: 32rpx;
  text-align: center;
}
.tf-statement-text { font-size: 36rpx; line-height: 1.7; color: #2D3748; font-weight: 600; }

/* 倒计时条 */
.tf-timer-bar {
  height: 12rpx; background: #F3F4F6; border-radius: 6rpx; overflow: hidden;
}
.tf-timer-fill { height: 100%; border-radius: 6rpx; transition: width 1s linear, background 0.3s; }

/* 按钮 */
.tf-buttons { display: flex; gap: 24rpx; }
.tf-btn {
  flex: 1; height: 160rpx; border-radius: 24rpx;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8rpx;
  transition: transform 0.15s;
}
.tf-btn:active { transform: scale(0.95); }
.tf-true  { background: linear-gradient(135deg, #22C55E, #16A34A); }
.tf-false { background: linear-gradient(135deg, #FF6B6B, #DC2626); }
.tf-btn-icon { font-size: 56rpx; color: #FFFFFF; line-height: 1; }
.tf-btn-text  { font-size: 32rpx; font-weight: 800; color: #FFFFFF; }

/* 结果 */
.tf-result { display: flex; flex-direction: column; align-items: center; gap: 20rpx; }
.tf-result-icon {
  width: 96rpx; height: 96rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 48rpx; font-weight: 800; color: #FFFFFF;
}
.tf-result-icon.correct { background: #22C55E; }
.tf-result-icon.wrong   { background: #FF6B6B; }
.tf-explanation { font-size: 28rpx; color: #6B7280; text-align: center; line-height: 1.6; }

/* 滑动提示 */
.tf-swipe-hint {
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
  font-size: 22rpx; color: #D1D5DB;
}
.tf-swipe-hint .ph { font-size: 22rpx; }
</style>
