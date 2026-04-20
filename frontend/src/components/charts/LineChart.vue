<template>
  <view class="line-container">
    <canvas
      type="2d"
      :id="canvasId"
      :style="{ width: width + 'px', height: height + 'px' }"
    ></canvas>
  </view>
</template>

<script>
/**
 * 折线图组件 - 兼容微信小程序 Canvas 2D API
 * Props:
 *   scores: [{ score, risk_level, date }]
 *   width: number
 *   height: number
 */
export default {
  name: 'LineChart',
  props: {
    scores: { type: Array, default: () => [] },
    width: { type: Number, default: 320 },
    height: { type: Number, default: 180 },
  },
  data() {
    return {
      canvasId: 'line_' + Math.random().toString(36).slice(2, 8),
    }
  },
  watch: {
    scores: {
      deep: true,
      handler() { this.$nextTick(() => this.draw()) },
    },
  },
  mounted() {
    this.$nextTick(() => this.draw())
  },
  methods: {
    draw() {
      if (!this.scores || this.scores.length === 0) return
      const dpr = uni.getSystemInfoSync().pixelRatio || 1
      const W = this.width, H = this.height
      const padL = 36, padR = 12, padT = 18, padB = 22

      const query = uni.createSelectorQuery().in(this)
      query.select('#' + this.canvasId).fields({ node: true, size: true }).exec((res) => {
        if (!res || !res[0] || !res[0].node) {
          this._drawH5(W, H, padL, padR, padT, padB, dpr)
          return
        }
        const canvas = res[0].node
        canvas.width = W * dpr
        canvas.height = H * dpr
        const ctx = canvas.getContext('2d')
        ctx.scale(dpr, dpr)
        this._drawOnCtx(ctx, W, H, padL, padR, padT, padB)
      })
    },

    _drawH5(W, H, padL, padR, padT, padB, dpr) {
      const ctx = uni.createCanvasContext(this.canvasId, this)
      this._drawOnCtx(ctx, W, H, padL, padR, padT, padB)
      ctx.draw()
    },

    _drawOnCtx(ctx, W, H, padL, padR, padT, padB) {
      ctx.clearRect(0, 0, W, H)
      const scores = this.scores
      const n = scores.length
      const chartW = W - padL - padR
      const chartH = H - padT - padB

      // 网格线
      const gridLevels = [0, 25, 50, 75, 100]
      gridLevels.forEach(pct => {
        const y = padT + chartH - (pct / 100) * chartH
        ctx.beginPath()
        ctx.moveTo(padL, y)
        ctx.lineTo(W - padR, y)
        ctx.strokeStyle = '#F3F4F6'
        ctx.lineWidth = 1
        ctx.stroke()
        // Y轴标签
        ctx.fillStyle = '#A0AEC0'
        ctx.font = `${W * 0.035}px sans-serif`
        ctx.textAlign = 'right'
        ctx.textBaseline = 'middle'
        ctx.fillText(String(pct), padL - 4, y)
      })

      // 计算数据点坐标
      const pts = scores.map((item, i) => {
        const x = padL + (n === 1 ? chartW / 2 : (i / (n - 1)) * chartW)
        const y = padT + chartH - (Math.min(item.score, 100) / 100) * chartH
        const color = item.risk_level === 'low' ? '#22C55E' : item.risk_level === 'medium' ? '#F57F17' : '#FF6B6B'
        return { x, y, score: item.score, color, date: this._fmtDate(item.date) }
      })

      // 填充区域
      if (pts.length >= 2) {
        ctx.beginPath()
        pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y))
        ctx.lineTo(pts[pts.length - 1].x, padT + chartH)
        ctx.lineTo(pts[0].x, padT + chartH)
        ctx.closePath()
        ctx.fillStyle = 'rgba(79,158,248,0.08)'
        ctx.fill()
      }

      // 折线
      if (pts.length >= 2) {
        ctx.beginPath()
        pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y))
        ctx.strokeStyle = '#4F9EF8'
        ctx.lineWidth = 2.5
        ctx.lineJoin = 'round'
        ctx.lineCap = 'round'
        ctx.stroke()
      }

      // 数据点 + 分数标签 + 日期标签
      const fontSize = Math.max(9, W * 0.032)
      pts.forEach(p => {
        // 数据点
        ctx.beginPath()
        ctx.arc(p.x, p.y, 4, 0, 2 * Math.PI)
        ctx.fillStyle = p.color
        ctx.fill()
        ctx.strokeStyle = '#FFFFFF'
        ctx.lineWidth = 2
        ctx.stroke()
        // 分数
        ctx.fillStyle = p.color
        ctx.font = `bold ${fontSize}px sans-serif`
        ctx.textAlign = 'center'
        ctx.textBaseline = 'bottom'
        ctx.fillText(String(p.score), p.x, p.y - 6)
        // 日期
        ctx.fillStyle = '#A0AEC0'
        ctx.font = `${fontSize * 0.9}px sans-serif`
        ctx.textBaseline = 'top'
        ctx.fillText(p.date, p.x, padT + chartH + 4)
      })
    },

    _fmtDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },
  },
}
</script>

<style scoped>
.line-container { width: 100%; overflow: hidden; }
</style>
