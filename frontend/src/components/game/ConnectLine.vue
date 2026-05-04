<template>
  <!--
    ConnectLine.vue
    连一连游戏连线渲染组件
    由于 UniApp 对 SVG 支持有限，使用绝对定位 <view> + CSS transform 模拟连线。
    每条线由一个细长矩形 + rotate 实现，端点用圆形 view 标记。
  -->
  <view class="connect-line-layer" :style="{ width: width + 'px', height: height + 'px' }">

    <!-- 已建立的连线 -->
    <block v-for="conn in connections" :key="conn.id">
      <template v-if="getPos(conn)">
        <!-- 线段 -->
        <view
          class="line-segment"
          :style="lineStyle(conn)"
          @click="$emit('line-click', conn.id)"
        ></view>
        <!-- 左端点圆 -->
        <view class="line-dot" :style="dotStyle(getPos(conn).x1, getPos(conn).y1, lineColor(conn))"></view>
        <!-- 右端点圆 -->
        <view class="line-dot" :style="dotStyle(getPos(conn).x2, getPos(conn).y2, lineColor(conn))"></view>
      </template>
    </block>

    <!-- 拖动中的临时连线（虚线效果用短线段模拟） -->
    <template v-if="tempLine">
      <!-- 临时线段 -->
      <view class="line-segment line-temp" :style="tempLineStyle"></view>
      <!-- 临时起点圆 -->
      <view class="line-dot" :style="dotStyle(tempLine.fromX, tempLine.fromY, '#3B82F6')"></view>
    </template>

  </view>
</template>

<script>
export default {
  name: 'ConnectLine',

  props: {
    /** 已建立的连线列表，每项 { id, leftId, rightId, color, isCorrect } */
    connections: {
      type: Array,
      default: () => [],
    },
    /** 左侧项中心坐标映射 { [itemId]: { x, y } } */
    leftPositions: {
      type: Object,
      default: () => ({}),
    },
    /** 右侧项中心坐标映射 { [itemId]: { x, y } } */
    rightPositions: {
      type: Object,
      default: () => ({}),
    },
    /** 拖动中的临时连线 { fromX, fromY, toX, toY } 或 null */
    tempLine: {
      type: Object,
      default: null,
    },
    /** SVG/层宽度（px） */
    width: {
      type: Number,
      default: 375,
    },
    /** SVG/层高度（px） */
    height: {
      type: Number,
      default: 600,
    },
  },

  emits: ['line-click'],

  methods: {
    /**
     * 获取连线的起止坐标，若坐标不存在则返回 null
     */
    getPos(conn) {
      const lp = this.leftPositions[conn.leftId]
      const rp = this.rightPositions[conn.rightId]
      if (!lp || !rp) return null
      return { x1: lp.x, y1: lp.y, x2: rp.x, y2: rp.y }
    },

    /**
     * 根据 isCorrect 字段返回连线颜色
     * isCorrect === true  → 绿色
     * isCorrect === false → 红色
     * isCorrect === null/undefined → 蓝色（未判断）
     */
    lineColor(conn) {
      if (conn.isCorrect === true) return '#22C55E'
      if (conn.isCorrect === false) return '#EF4444'
      return '#3B82F6'
    },

    /**
     * 计算线段的 CSS transform 样式（绝对定位矩形旋转）
     */
    lineStyle(conn) {
      const pos = this.getPos(conn)
      if (!pos) return {}
      return this._buildLineStyle(pos.x1, pos.y1, pos.x2, pos.y2, this.lineColor(conn), false)
    },

    /**
     * 构建线段样式对象
     * 原理：以 (x1, y1) 为左端，计算长度和角度，用 transform-origin 旋转
     */
    _buildLineStyle(x1, y1, x2, y2, color, isDashed) {
      const dx = x2 - x1
      const dy = y2 - y1
      const length = Math.sqrt(dx * dx + dy * dy)
      const angle = Math.atan2(dy, dx) * (180 / Math.PI)

      return {
        position: 'absolute',
        left: x1 + 'px',
        top: (y1 - 2) + 'px',          // 垂直居中（线宽 4px，偏移 2px）
        width: length + 'px',
        height: '4px',
        backgroundColor: isDashed ? 'transparent' : color,
        backgroundImage: isDashed
          ? `repeating-linear-gradient(90deg, ${color} 0, ${color} 10px, transparent 10px, transparent 18px)`
          : 'none',
        borderRadius: '2px',
        transformOrigin: '0 50%',
        transform: `rotate(${angle}deg)`,
        zIndex: 10,
        pointerEvents: isDashed ? 'none' : 'auto',
      }
    },

    /**
     * 端点圆样式
     */
    dotStyle(x, y, color) {
      return {
        position: 'absolute',
        left: (x - 6) + 'px',
        top: (y - 6) + 'px',
        width: '12px',
        height: '12px',
        borderRadius: '50%',
        backgroundColor: color,
        zIndex: 11,
        pointerEvents: 'none',
      }
    },
  },

  computed: {
    tempLineStyle() {
      if (!this.tempLine) return {}
      return this._buildLineStyle(
        this.tempLine.fromX, this.tempLine.fromY,
        this.tempLine.toX, this.tempLine.toY,
        '#3B82F6', true
      )
    },
  },
}
</script>

<style scoped>
.connect-line-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
  overflow: visible;
  z-index: 10;
}

.line-segment {
  pointer-events: auto;
  cursor: pointer;
}

.line-temp {
  pointer-events: none !important;
}

.line-dot {
  pointer-events: none;
}
</style>
