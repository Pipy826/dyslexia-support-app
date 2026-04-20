<template>
  <view class="radar-container">
    <!-- 纯 SVG 雷达图，无需 Canvas，H5 和小程序均兼容 -->
    <svg
      :width="svgSize"
      :height="svgSize"
      :viewBox="`0 0 ${svgSize} ${svgSize}`"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- 背景网格 -->
      <polygon
        v-for="level in 4"
        :key="'grid' + level"
        :points="getGridPoints(level)"
        fill="none"
        stroke="#F3F4F6"
        stroke-width="1"
      />

      <!-- 轴线 -->
      <line
        v-for="(dim, i) in dims"
        :key="'axis' + i"
        :x1="cx" :y1="cy"
        :x2="getPoint(i, r).x"
        :y2="getPoint(i, r).y"
        stroke="#E5E7EB"
        stroke-width="1"
      />

      <!-- 数据多边形 -->
      <polygon
        :points="getDataPoints()"
        fill="rgba(59,130,246,0.15)"
        stroke="#3B82F6"
        stroke-width="2"
        stroke-linejoin="round"
      />

      <!-- 数据点 -->
      <circle
        v-for="(dim, i) in dims"
        :key="'dot' + i"
        :cx="getDataPoint(i).x"
        :cy="getDataPoint(i).y"
        r="4"
        :fill="getScoreColor(dim[1])"
        stroke="white"
        stroke-width="1.5"
      />

      <!-- 标签 -->
      <text
        v-for="(dim, i) in dims"
        :key="'label' + i"
        :x="getLabelPoint(i).x"
        :y="getLabelPoint(i).y"
        text-anchor="middle"
        dominant-baseline="middle"
        :font-size="fontSize"
        fill="#6B7280"
        font-family="PingFang SC, sans-serif"
      >{{ shortNames[dim[0]] || dim[0] }}</text>
    </svg>
  </view>
</template>

<script>
const SHORT_NAMES = {
  visual_discrimination: '视觉', phonological: '音形', character_order: '字序',
  spelling: '拼写', reading_comprehension: '阅读', semantic_integration: '语义',
  information_extraction: '提取', attention: '注意力', working_memory_capacity: '工作记忆',
  short_term_memory: '短时记忆', rapid_naming_speed: '命名速度', phonological_awareness: '音韵',
  fine_motor_control: '精细动作', visual_motor_integration: '视动整合',
}

export default {
  name: 'RadarChart',
  props: {
    dimensions: { type: Object, default: () => ({}) },
    size: { type: Number, default: 260 },
  },
  data() {
    return { svgSize: 260 }
  },
  computed: {
    dims() {
      return Object.entries(this.dimensions || {})
    },
    n() { return this.dims.length },
    cx() { return this.svgSize / 2 },
    cy() { return this.svgSize / 2 },
    r() { return this.svgSize * 0.33 },
    labelR() { return this.svgSize * 0.46 },
    fontSize() { return Math.max(9, Math.floor(this.svgSize * 0.052)) },
    shortNames() { return SHORT_NAMES },
  },
  mounted() {
    const sysInfo = uni.getSystemInfoSync()
    const screenWidth = sysInfo.windowWidth || 375
    // 画布宽度 = 屏幕宽度 - 左右padding(32*2) - 卡片padding(28*2) - 安全余量
    this.svgSize = Math.min(this.size, screenWidth - 120)
  },
  methods: {
    getAngle(i) {
      return (2 * Math.PI * i / this.n) - Math.PI / 2
    },
    getPoint(i, radius) {
      const angle = this.getAngle(i)
      return {
        x: this.cx + radius * Math.cos(angle),
        y: this.cy + radius * Math.sin(angle),
      }
    },
    getGridPoints(level) {
      const rr = this.r * level / 4
      return Array.from({ length: this.n }, (_, i) => {
        const p = this.getPoint(i, rr)
        return `${p.x},${p.y}`
      }).join(' ')
    },
    getDataPoint(i) {
      const score = Math.min(this.dims[i]?.[1] || 0, 100)
      return this.getPoint(i, (score / 100) * this.r)
    },
    getDataPoints() {
      return this.dims.map((_, i) => {
        const p = this.getDataPoint(i)
        return `${p.x},${p.y}`
      }).join(' ')
    },
    getLabelPoint(i) {
      return this.getPoint(i, this.labelR)
    },
    getScoreColor(score) {
      if (score >= 75) return '#10B981'
      if (score >= 60) return '#F59E0B'
      return '#EF4444'
    },
  },
}
</script>

<style scoped>
.radar-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}
</style>
