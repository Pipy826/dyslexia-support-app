<template>
  <view class="ps-card">
    <view class="ps-char-display">
      <text class="ps-char">{{ question.character }}</text>
    </view>
    <view class="ps-selected-area">
      <view v-if="selectedBlocks.length === 0" class="ps-placeholder">点击下方字母块拼出拼音</view>
      <view v-else class="ps-selected-blocks">
        <view v-for="(block, i) in selectedBlocks" :key="'sel_' + i" class="ps-block ps-block-selected" @click="removeBlock(i)">{{ block }}</view>
      </view>
    </view>
    <view class="ps-timer-bar" v-if="!confirmed">
      <view class="ps-timer-fill" :style="{ width: timerPercent + '%', background: timerColor }"></view>
    </view>
    <view class="ps-available-blocks">
      <view v-for="(block, i) in availableBlocks" :key="'avail_' + i" class="ps-block" @click="addBlock(block, i)">{{ block }}</view>
    </view>
    <button class="ps-confirm-btn" :class="{ disabled: !canSubmit || confirmed }" :disabled="!canSubmit || confirmed" @click="handleSubmit">确认</button>
  </view>
</template>

<script>
import { scorePinyinSpelling } from '@/utils/levelScoring'
export default {
  name: 'PinyinSpellingQuestion',
  props: { question: { type: Object, required: true } },
  emits: ['answer-submitted'],
  data() {
    return { selectedBlocks: [], availableBlocks: [], confirmed: false, timeLeft: 0, timer: null }
  },
  computed: {
    canSubmit() { return this.selectedBlocks.length > 0 },
    timerPercent() { return Math.max(0, (this.timeLeft / (this.question.time_limit || 20)) * 100) },
    timerColor() {
      if (this.timeLeft <= 5) return '#FF6B6B'
      if (this.timeLeft <= 8) return '#F97316'
      return '#A78BFA'
    },
  },
  watch: { question: { immediate: true, handler(q) { this.reset(q) } } },
  beforeUnmount() { this.clearTimer() },
  methods: {
    reset(q) {
      this.selectedBlocks = []
      this.availableBlocks = (q && q.available_blocks) ? [...q.available_blocks] : []
      this.confirmed = false
      this.clearTimer()
      this.timeLeft = (q && q.time_limit) || 20
      this.startTimer()
    },
    startTimer() {
      this.timer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this.clearTimer(); this.submitAnswer() }
      }, 1000)
    },
    clearTimer() { if (this.timer) { clearInterval(this.timer); this.timer = null } },
    addBlock(block, index) {
      if (this.confirmed) return
      this.selectedBlocks.push(block)
      this.availableBlocks.splice(index, 1)
    },
    removeBlock(index) {
      if (this.confirmed) return
      const block = this.selectedBlocks.splice(index, 1)[0]
      this.availableBlocks.push(block)
    },
    handleSubmit() {
      if (!this.canSubmit) { uni.showToast({ title: '请先拼出拼音', icon: 'none' }); return }
      if (this.confirmed) return
      this.clearTimer(); this.submitAnswer()
    },
    submitAnswer() {
      if (this.confirmed) return
      this.confirmed = true
      const score = scorePinyinSpelling(this.selectedBlocks, this.question.correct_pinyin)
      this.$emit('answer-submitted', { score, assembled: this.selectedBlocks.join(''), isCorrect: score >= 1.0 })
    },
  },
}
</script>

<style scoped>
.ps-card { margin: 16rpx 32rpx 0; background: #FFFFFF; border-radius: 28rpx; padding: 32rpx; box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 24rpx; align-items: center; }
.ps-char-display { width: 180rpx; height: 180rpx; border-radius: 24rpx; background: linear-gradient(135deg, #F5F3FF, #EDE9FE); display: flex; align-items: center; justify-content: center; box-shadow: 0 4rpx 16rpx rgba(167,139,250,0.2); }
.ps-char { font-size: 100rpx; font-weight: 800; color: #2D3748; }
.ps-selected-area { width: 100%; min-height: 80rpx; background: #F9FAFB; border-radius: 16rpx; padding: 16rpx 20rpx; display: flex; align-items: center; justify-content: center; border: 2rpx dashed #E5E7EB; }
.ps-placeholder { font-size: 26rpx; color: #D1D5DB; }
.ps-selected-blocks { display: flex; flex-wrap: wrap; gap: 12rpx; justify-content: center; }
.ps-block { min-width: 80rpx; height: 64rpx; padding: 0 20rpx; display: flex; align-items: center; justify-content: center; background: #EDE9FE; color: #5B21B6; font-size: 30rpx; font-weight: 700; border-radius: 12rpx; border: 2rpx solid #C4B5FD; transition: all 0.15s; }
.ps-block:active { transform: scale(0.93); }
.ps-block-selected { background: #7C3AED; color: #FFFFFF; border-color: #7C3AED; }
.ps-available-blocks { display: flex; flex-wrap: wrap; gap: 16rpx; justify-content: center; width: 100%; }
.ps-timer-bar { width: 100%; height: 12rpx; background: #F3F4F6; border-radius: 6rpx; overflow: hidden; }
.ps-timer-fill { height: 100%; border-radius: 6rpx; transition: width 1s linear, background 0.3s; }
.ps-confirm-btn { width: 100%; padding: 28rpx; border-radius: 20rpx; background: linear-gradient(135deg, #7C3AED, #6D28D9); color: #FFFFFF; font-size: 30rpx; font-weight: 700; box-shadow: 0 4rpx 12rpx rgba(124,58,237,0.25); border: none; }
.ps-confirm-btn.disabled { background: #E5E7EB; color: #9CA3AF; box-shadow: none; }
</style>