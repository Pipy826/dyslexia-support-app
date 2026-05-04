<template>
  <view class="handwriting-question">
    <!-- 题目说明 -->
    <view class="question-card">
      <view class="question-title">{{ question.title }}</view>
      <view class="question-instruction">{{ question.instruction }}</view>
    </view>

    <!-- 目标汉字展示 -->
    <view class="character-display">
      <view class="character-label">目标汉字</view>
      <view class="character-box">
        <text class="target-char">{{ question.character }}</text>
      </view>
      <view class="stroke-info">
        <text class="ph ph-pencil-simple"></text>
        <text class="stroke-text">{{ question.stroke_count }} 画</text>
      </view>
    </view>

    <!-- 手写画布 -->
    <view class="canvas-section">
      <view class="canvas-label">在下方书写</view>
      <HandwritingCanvas
        ref="hwCanvas"
        :height="360"
        :disabled="submitted"
        @stroke-end="onStrokeEnd"
      />
    </view>

    <!-- 操作按钮 -->
    <view class="action-row" v-if="!submitted">
      <view class="clear-btn" @click="onClear">
        <text class="ph ph-eraser"></text>
        <text>清除</text>
      </view>
      <view class="submit-btn" @click="onSubmit" :class="{ disabled: strokeCount === 0 }">
        <text class="ph ph-check-circle"></text>
        <text>提交</text>
      </view>
    </view>

    <!-- 提交后反馈 -->
    <view class="feedback-row" v-if="submitted">
      <text class="ph ph-check-circle feedback-icon"></text>
      <text class="feedback-text">已提交！</text>
    </view>
  </view>
</template>

<script>
import HandwritingCanvas from '@/components/game/HandwritingCanvas.vue'

export default {
  name: 'HandwritingQuestion',
  components: { HandwritingCanvas },
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      strokeCount: 0,
      submitted: false,
      timeoutTimer: null,
    }
  },
  mounted() {
    const timeLimit = (this.question.time_limit || 30) * 1000
    this.timeoutTimer = setTimeout(() => {
      if (!this.submitted) this._submit()
    }, timeLimit)
  },
  beforeUnmount() {
    if (this.timeoutTimer) { clearTimeout(this.timeoutTimer); this.timeoutTimer = null }
  },
  methods: {
    onStrokeEnd() {
      this.strokeCount++
    },
    onClear() {
      if (this.$refs.hwCanvas) {
        this.$refs.hwCanvas.clear()
        this.strokeCount = 0
      }
    },
    onSubmit() {
      if (this.strokeCount === 0) {
        uni.showToast({ title: '请先书写汉字', icon: 'none' })
        return
      }
      this._submit()
    },
    _submit() {
      if (this.submitted) return
      this.submitted = true
      if (this.timeoutTimer) { clearTimeout(this.timeoutTimer); this.timeoutTimer = null }

      // 获取笔迹数据
      const strokes = this.$refs.hwCanvas ? this.$refs.hwCanvas.getStrokeData() : []

      // 评分：基于笔画数量与目标笔画数的比较（简化评分）
      const targetStrokes = this.question.stroke_count || 1
      const writtenStrokes = strokes.length
      let score = 0
      if (writtenStrokes > 0) {
        // 笔画数接近目标则得高分，差距越大分越低
        const ratio = Math.min(writtenStrokes, targetStrokes) / Math.max(writtenStrokes, targetStrokes)
        score = Math.max(0.3, ratio)  // 只要写了就至少给0.3分
      }
      const isCorrect = score >= 0.7

      this.$emit('answer-submitted', { score, isCorrect, strokes })
    },
  },
}
</script>

<style scoped>
.handwriting-question {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  padding: 0 32rpx 32rpx;
}

.question-card {
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 28rpx 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  margin-top: 16rpx;
}
.question-title { font-size: 32rpx; font-weight: 800; color: #2D3748; margin-bottom: 8rpx; }
.question-instruction { font-size: 26rpx; color: #718096; }

/* 目标汉字 */
.character-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
}
.character-label {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 600;
}
.character-box {
  width: 160rpx;
  height: 160rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 3rpx solid #BFDBFE;
  display: flex;
  align-items: center;
  justify-content: center;
}
.target-char {
  font-size: 100rpx;
  font-weight: 900;
  color: #2D3748;
  line-height: 1;
}
.stroke-info {
  display: flex;
  align-items: center;
  gap: 8rpx;
}
.stroke-info .ph { font-size: 26rpx; color: #4F9EF8; }
.stroke-text { font-size: 24rpx; color: #4F9EF8; font-weight: 700; }

/* 画布区域 */
.canvas-section {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.canvas-label {
  font-size: 24rpx;
  color: #718096;
  font-weight: 600;
}

/* 操作按钮 */
.action-row {
  display: flex;
  gap: 16rpx;
}
.clear-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  background: #F5F5F5;
  color: #718096;
  border-radius: 20rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
}
.clear-btn:active { transform: scale(0.97); }
.clear-btn .ph { font-size: 28rpx; }

.submit-btn {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25);
}
.submit-btn:active { transform: scale(0.97); }
.submit-btn.disabled { background: #CBD5E0; box-shadow: none; }
.submit-btn .ph { font-size: 28rpx; }

/* 反馈 */
.feedback-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 20rpx;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border-radius: 20rpx;
  border: 2rpx solid #22C55E;
}
.feedback-icon { font-size: 36rpx; color: #22C55E; }
.feedback-text { font-size: 28rpx; font-weight: 700; color: #22C55E; }
</style>
