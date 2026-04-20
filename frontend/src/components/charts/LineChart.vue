<template>
  <view class="line-container">
    <!-- 纯 SVG 折线图，兼容 H5 / 微信小程序 / App -->
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      :width="W"
      :height="H"
      xmlns="http://www.w3.org/2000/svg"
      class="line-svg"
    >
      <!-- 网格线 + Y 轴标签 -->
      <g v-for="pct in gridLevels" :key="pct">
        <line
          :x1="padL" :y1="yPos(pct)"
          :x2="W - padR" :y2="yPos(pct)"
          stroke="#F3F4F6" stroke-width="1"
        />
        <text
          :x="padL - 5" :y="yPos(pct)"
          text-anchor="end" dominant-baseline="middle"
          :font-size="labelSize" fill="#A0AEC0"
        >{{ pct }}</text>
      </g>

      <!-- 风险参考线 -->
      <line :x1="padL" :y1="yPos(75)" :x2="W - padR" :y2="yPos(75)"
        stroke="#22C55E" stroke-width="1" stroke-dasharray="4,3" opacity="0.4" />
      <line :x1="padL" :y1="yPos(60)" :x2="W - padR" :y2="yPos(60)"
        stroke="#F57F17" stroke-width="1" stroke-dasharray="4,3" opacity="0.4" />

      <!-- 填充区域 -->
      <path v-if="pts.length >= 2" :d="fillPath" fill="rgba(79,158,248,0.08)" />

      <!-- 折线 -->
      <polyline v-if="pts.length >= 2"
        :points="linePoints"
        fill="none" stroke="#4F9EF8" stroke-width="2.5"
        stroke-linejoin="round" stroke-linecap="round"
      />

      <!-- 数据点 + 分数 + 日期 -->
      <g v-for="(p, i) in pts" :key="i">
        <!-- 光晕 -->
        <circle :cx="p.x" :cy="p.y" r="8" :fill="p.color" opacity="0.15" />
        <!-- 点 -->
        <circle :cx="p.x" :cy="p.y" r="4.5" :fill="p.color" stroke="#FFFFFF" stroke-width="2" />
        <!-- 分数标签 -->
        <text
          :x="p.x" :y="p.y - 10"
          text-anchor="middle" dominant-baseline="auto"
          :font-size="scoreSize" :fill="p.color" font-weight="bold"
        >{{ p.score }}</text>
        <!-- 日期标签 -->
        <text
          :x="p.x" :y="H - padB + 12"
          text-anchor="middle" dominant-baseline="hanging"
          :font-size="labelSize" fill="#A0AEC0"
        >{{ p.date }}</text>
      </g>
    </svg>
  </view>
</template>

<script>
/**
 * 折线图组件 - 纯 SVG，兼容 H5 / 微信小程序 / App
 * Props:
 *   scores: [{ score, risk_level, date }]
 *   width:  number (px)
 *   height: number (px)
 */
export default {
  name: 'LineChart',
  props: {
    scores: { type: Array, default: () => [] },
    width:  { type: Number, default: 320 },
    height: { type: Number, default: 180 },
  },
  data() {
    return {
      padL: 38, padR: 12, padT: 22, padB: 22,
      gridLevels: [0, 25, 50, 75, 100],
    }
  },
  computed: {
    W() { return this.width },
    H() { return this.height },
    labelSize() { return Math.max(9, this.W * 0.033) },
    scoreSize() { return Math.max(10, this.W * 0.038) },
    chartW() { return this.W - this.padL - this.padR },
    chartH() { return this.H - this.padT - this.padB },

    pts() {
      const { scores, padL, padT, chartW, chartH } = this
      const n = scores.length
      if (n === 0) return []
      return scores.map((item, i) => {
        const x = padL + (n === 1 ? chartW / 2 : (i / (n - 1)) * chartW)
        const y = padT + chartH - (Math.min(Math.max(item.score, 0), 100) / 100) * chartH
        const color = item.risk_level === 'low' ? '#22C55E'
          : item.risk_level === 'medium' ? '#F57F17' : '#FF6B6B'
        return { x, y, score: item.score, color, date: this._fmtDate(item.date) }
      })
    },

    linePoints() {
      return this.pts.map(p => `${p.x},${p.y}`).join(' ')
    },

    fillPath() {
      if (this.pts.length < 2) return ''
      const { pts, padL, padT, chartH } = this
      const bottom = padT + chartH
      const top = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')
      return `${top} L${pts[pts.length - 1].x},${bottom} L${pts[0].x},${bottom} Z`
    },
  },
  methods: {
    yPos(pct) {
      return this.padT + this.chartH - (pct / 100) * this.chartH
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
.line-svg { display: block; width: 100%; height: auto; }
</style>
