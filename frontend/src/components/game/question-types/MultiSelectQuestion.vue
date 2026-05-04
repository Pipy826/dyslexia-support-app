<template>
  <view class="ms-card">
    <view class="ms-passage" :class="{ 'show-feedback': confirmed }">
      <view
        v-for="(char, index) in textChars"
        :key="index"
        class="ms-char"
        :class="{
          selected:  !confirmed && selectedPositions.has(index),
          correct:   confirmed && errorPositions.includes(index),
          wrong:     confirmed && selectedPositions.has(index) && !errorPositions.includes(index),
          missed:    confirmed && !selectedPositions.has(index) && errorPositions.includes(index),
        }"
        @click="handleCharClick(index)"
      >{{ char }}</view>
    </view>
    <view class="ms-timer-bar" v-if="!confirmed">
      <view class="ms-timer-fill" :style="{ width: timerPercent + '%', background: timerColor }"></view>
      <text class="ms-timer-text">{{ timeLeft }}s</text>
    </view>
    <view class="ms-feedback" v-if="confirmed">
      <text v-if="isAllCorrect" class="fb-correct">全部找对了！</text>
      <text v-else class="fb-partial">{{ feedbackText }}</text>
    </view>
    <button class="ms-confirm-btn" :class="{ disabled: !canSubmit || confirmed }" :disabled="!canSubmit || confirmed" @click="handleSubmit">确认</button>
  </view>
</template>

<script>
import { scoreMultiSelect } from '@/utils/levelScoring'
export default {
  name: 'MultiSelectQuestion',
  props: { question: { type: Object, required: true } },
  emits: ['answer-submitted'],
  data() {
    return { selectedPositions: new Set(), confirmed: false, timeLeft: 0, timer: null }
  },
  computed: {
    textChars() { return this.question.text ? this.question.text.split('') : [] },
    errorPositions() { return this.question.error_positions || [] },
    canSubmit() { return this.selectedPositions.size > 0 },
    timerPercent() { return Math.max(0, (this.timeLeft / (this.question.time_limit || 30)) * 100) },
    timerColor() {
      if (this.timeLeft <= 5) return '#FF6B6B'
      if (this.timeLeft <= 10) return '#F97316'
      return '#4F9EF8'
    },
    isAllCorrect() {
      if (this.selectedPositions.size !== this.errorPositions.length) return false
      return this.errorPositions.every(p => this.selectedPositions.has(p))
    },
    feedbackText() {
      const correct = this.errorPositions.filter(p => this.selectedPositions.has(p)).length
      const wrong = [...this.selectedPositions].filter(p => !this.errorPositions.includes(p)).length
      const missed = this.errorPositions.length - correct
      const parts = []
      if (correct > 0) parts.push('找对 ' + correct + ' 个')
      if (wrong > 0) parts.push('误选 ' + wrong + ' 个')
      if (missed > 0) parts.push('漏选 ' + missed + ' 个')
      return parts.join('，') || '继续加油！'
    },
  },
  watch: { question: { immediate: true, handler() { this.reset() } } },
  beforeUnmount() { this.clearTimer() },
  methods: {
    reset() {
      this.selectedPositions = new Set()
      this.confirmed = false
      this.clearTimer()
      this.timeLeft = this.question.time_limit || 30
      this.startTimer()
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this.clearTimer(); this.submitAnswer() }
      }, 1000)
    },
    clearTimer() { if (this.timer) { clearInterval(this.timer); this.timer = null } },
    handleCharClick(index) {
      if (this.confirmed) return
      const s = new Set(this.selectedPositions)
      s.has(index) ? s.delete(index) : s.add(index)
      this.selectedPositions = s
    },
    handleSubmit() {
      if (!this.canSubmit) { uni.showToast({ title: '请先点击错别字', icon: 'none' }); return }
      if (this.confirmed) return
      this.clearTimer(); this.submitAnswer()
    },
    submitAnswer() {
      if (this.confirmed) return
      this.confirmed = true
      const score = scoreMultiSelect(Array.from(this.selectedPositions), this.errorPositions)
      this.$emit('answer-submitted', { score, selectedPositions: Array.from(this.selectedPositions), isCorrect: score >= 1.0 })
    },
  },
}
</script>

<style scoped>
.ms-card { margin: 16rpx 32rpx 0; background: #FFFFFF; border-radius: 28rpx; padding: 32rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 24rpx; }
.ms-passage { display: flex; flex-wrap: wrap; gap: 4rpx; background: #F9FAFB; border-radius: 16rpx; padding: 24rpx; line-height: 1.8; }
.ms-char { font-size: 36rpx; color: #2D3748; padding: 4rpx 6rpx; border-radius: 8rpx; transition: all 0.15s; }
.ms-char.selected { background: #DBEAFE; color: #2563EB; transform: scale(1.1); }
.ms-char.correct { background: #DCFCE7; color: #16A34A; }
.ms-char.wrong { background: #FFE4E4; color: #DC2626; }
.ms-char.missed { border-bottom: 4rpx solid #F97316; }
.ms-timer-bar { height: 16rpx; background: #F3F4F6; border-radius: 8rpx; overflow: hidden; position: relative; }
.ms-timer-fill { height: 100%; border-radius: 8rpx; transition: width 1s linear, background 0.3s; }
.ms-timer-text { position: absolute; right: 8rpx; top: 50%; transform: translateY(-50%); font-size: 18rpx; font-weight: 700; color: #6B7280; }
.ms-feedback { text-align: center; }
.fb-correct { font-size: 28rpx; font-weight: 700; color: #16A34A; }
.fb-partial { font-size: 26rpx; color: #F97316; }
.ms-confirm-btn { width: 100%; padding: 28rpx; border-radius: 20rpx; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; font-size: 30rpx; font-weight: 700; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25); border: none; }
.ms-confirm-btn.disabled { background: #E5E7EB; color: #9CA3AF; box-shadow: none; }
</style>