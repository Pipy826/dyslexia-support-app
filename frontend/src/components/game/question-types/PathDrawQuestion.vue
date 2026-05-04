<template>
  <view class="pd-card">
    <!-- 标题 -->
    <view class="pd-header">
      <view class="pd-title">{{ question.title }}</view>
      <view class="pd-instruction">{{ question.instruction }}</view>
    </view>

    <!-- 倒计时条 -->
    <view class="pd-timer-bar" v-if="!submitted">
      <view class="pd-timer-fill" :style="{ width: timerPercent + '%' }"></view>
      <text class="pd-timer-text">{{ timeLeft }}s</text>
    </view>

    <!-- 画布区域 -->
    <view class="pd-canvas-wrap">
      <canvas
        canvas-id="pathCanvas"
        id="pathCanvas"
        class="pd-canvas"
        @touchstart="onTouchStart"
        @touchmove="onTouchMove"
        @touchend="onTouchEnd"
      ></canvas>
    </view>

    <!-- 重试提示 -->
    <view class="pd-retry-hint" v-if="showRetryHint">
      请沿虚线描绘，还可重试 {{ 3 - retryCount }} 次
    </view>

    <!-- 重试按钮 -->
    <view class="pd-retry-btn" v-if="showRetryHint && retryCount < 3" @click="handleRetry">
      重试
    </view>
  </view>
</template>

<script>
import { scorePathDraw } from '@/utils/levelScoring'

const CANVAS_W = 600  // rpx 逻辑宽度，实际像素在 mounted 时获取
const CANVAS_H = 400

export default {
  name: 'PathDrawQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      userPath: [],
      isDrawing: false,
      submitted: false,
      retryCount: 0,
      showRetryHint: false,
      timeLeft: 0,
      timer: null,
      canvasW: 300,   // 实际像素宽
      canvasH: 200,   // 实际像素高
    }
  },
  computed: {
    timerPercent() {
      const total = this.question.time_limit || 15
      return Math.max(0, (this.timeLeft / total) * 100)
    },
  },
  watch: {
    question: { immediate: false, handler() { this.reset() } },
  },
  mounted() {
    this.$nextTick(() => {
      this.measureCanvas()
    })
  },
  beforeUnmount() { this.clearTimer() },
  methods: {
    measureCanvas() {
      const query = uni.createSelectorQuery().in(this)
      query.select('#pathCanvas').boundingClientRect(rect => {
        if (rect) {
          this.canvasW = rect.width
          this.canvasH = rect.height
        }
        this.reset()
      }).exec()
    },
    reset() {
      this.clearTimer()
      this.userPath = []
      this.isDrawing = false
      this.showRetryHint = false
      this.submitted = false
      this.timeLeft = this.question.time_limit || 15
      this.$nextTick(() => {
        this.drawReferencePath()
        this.startTimer()
      })
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
    drawReferencePath() {
      const ctx = uni.createCanvasContext('pathCanvas', this)
      if (!ctx) return
      ctx.clearRect(0, 0, this.canvasW, this.canvasH)
      const pts = this.question.path_points
      if (!pts || pts.length < 2) return
      ctx.setStrokeStyle('#CBD5E1')
      ctx.setLineWidth(6)
      ctx.setLineDash([14, 10])
      ctx.beginPath()
      ctx.moveTo(pts[0].x * this.canvasW, pts[0].y * this.canvasH)
      for (let i = 1; i < pts.length; i++) {
        ctx.lineTo(pts[i].x * this.canvasW, pts[i].y * this.canvasH)
      }
      ctx.stroke()
      ctx.draw()
    },
    drawUserPath() {
      const ctx = uni.createCanvasContext('pathCanvas', this)
      if (!ctx || this.userPath.length < 2) return
      // 重绘参考路径
      const pts = this.question.path_points
      ctx.clearRect(0, 0, this.canvasW, this.canvasH)
      if (pts && pts.length >= 2) {
        ctx.setStrokeStyle('#CBD5E1')
        ctx.setLineWidth(6)
        ctx.setLineDash([14, 10])
        ctx.beginPath()
        ctx.moveTo(pts[0].x * this.canvasW, pts[0].y * this.canvasH)
        for (let i = 1; i < pts.length; i++) {
          ctx.lineTo(pts[i].x * this.canvasW, pts[i].y * this.canvasH)
        }
        ctx.stroke()
      }
      // 绘制用户轨迹
      ctx.setStrokeStyle('#4F9EF8')
      ctx.setLineWidth(8)
      ctx.setLineDash([])
      ctx.setLineCap('round')
      ctx.setLineJoin('round')
      ctx.beginPath()
      ctx.moveTo(this.userPath[0].x * this.canvasW, this.userPath[0].y * this.canvasH)
      for (let i = 1; i < this.userPath.length; i++) {
        ctx.lineTo(this.userPath[i].x * this.canvasW, this.userPath[i].y * this.canvasH)
      }
      ctx.stroke()
      ctx.draw()
    },
    getTouchPos(touch) {
      // touch 坐标已是页面坐标，需减去 canvas 的 offsetTop/Left
      // UniApp 中 canvas 事件的 touches 坐标是相对于 canvas 的
      return {
        x: touch.x / this.canvasW,
        y: touch.y / this.canvasH,
      }
    },
    onTouchStart(e) {
      if (this.submitted) return
      this.isDrawing = true
      this.userPath = []
      const t = e.touches[0]
      this.userPath.push({ x: t.x / this.canvasW, y: t.y / this.canvasH })
    },
    onTouchMove(e) {
      if (!this.isDrawing || this.submitted) return
      const t = e.touches[0]
      this.userPath.push({ x: t.x / this.canvasW, y: t.y / this.canvasH })
      this.drawUserPath()
    },
    onTouchEnd() {
      if (!this.isDrawing || this.submitted) return
      this.isDrawing = false
      if (this.userPath.length < 3) {
        this.showRetryHint = true
        this.retryCount++
        if (this.retryCount >= 3) this.submitAnswer()
        return
      }
      this.submitAnswer()
    },
    submitAnswer() {
      if (this.submitted) return
      this.submitted = true
      this.clearTimer()
      const score = scorePathDraw(
        this.userPath,
        this.question.path_points,
        this.question.tolerance || 0.08,
        this.question.min_coverage || 0.8,
      )
      this.$emit('answer-submitted', {
        score,
        userPath: this.userPath,
        isCorrect: score >= 0.7,
      })
    },
    handleRetry() {
      this.userPath = []
      this.showRetryHint = false
      this.drawReferencePath()
    },
  },
}
</script>

<style scoped>
.pd-card {
  margin: 16rpx 32rpx 0;
  background: #FFFFFF; border-radius: 28rpx; padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  display: flex; flex-direction: column; gap: 20rpx;
}
.pd-header { text-align: center; }
.pd-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 8rpx; }
.pd-instruction { font-size: 24rpx; color: #9CA3AF; }

/* 倒计时条 */
.pd-timer-bar {
  height: 16rpx; background: #F3F4F6; border-radius: 8rpx;
  overflow: hidden; position: relative;
}
.pd-timer-fill {
  height: 100%; background: linear-gradient(90deg, #34D399, #F59E0B, #FF6B6B);
  border-radius: 8rpx; transition: width 1s linear;
}
.pd-timer-text {
  position: absolute; right: 8rpx; top: 50%; transform: translateY(-50%);
  font-size: 18rpx; font-weight: 700; color: #6B7280;
}

/* 画布 */
.pd-canvas-wrap {
  background: #F8FAFF; border-radius: 20rpx; overflow: hidden;
  border: 2rpx solid #E5E7EB;
}
.pd-canvas {
  width: 100%; height: 400rpx; display: block;
}

/* 重试 */
.pd-retry-hint {
  background: #FEF3C7; border-radius: 12rpx; padding: 16rpx 20rpx;
  font-size: 24rpx; color: #92400E; text-align: center;
}
.pd-retry-btn {
  text-align: center; padding: 20rpx;
  background: #FEF9C3; border-radius: 16rpx;
  font-size: 28rpx; font-weight: 700; color: #D97706;
  border: 2rpx solid #FDE047;
}
</style>
