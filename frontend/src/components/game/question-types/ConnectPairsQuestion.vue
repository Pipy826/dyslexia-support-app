<template>
  <view
    class="connect-pairs-question"
    @touchmove.stop.prevent="onTouchMove"
    @touchend.stop="onTouchEnd"
    @touchcancel.stop="onTouchEnd"
  >
    <!-- 题目说明 -->
    <view class="question-card">
      <view class="question-title">{{ question.title }}</view>
      <view class="question-instruction">{{ question.instruction }}</view>
    </view>

    <!-- 进度 -->
    <view class="match-progress">
      <text class="ph ph-link"></text>
      <text class="progress-text">已连 {{ correctCount }} / {{ totalPairs }} 对</text>
    </view>

    <!-- 连线区域 -->
    <view class="columns-wrapper" id="cq-columns-wrapper">

      <!-- 左侧 -->
      <view class="items-col items-left">
        <view
          v-for="item in leftItems"
          :key="item.id"
          :id="'cq_left_' + item.id"
          :class="['item-card', 'item-left', {
            'item-correct':   isLeftCorrect(item.id),
            'item-wrong':     isLeftWrong(item.id),
            'item-connected': isLeftConnected(item.id) && !isLeftCorrect(item.id) && !isLeftWrong(item.id),
            'item-dragging':  draggingLeftId === item.id,
          }]"
          @touchstart.stop.prevent="onTouchStart($event, item)"
        >
          <text class="item-text">{{ item.content }}</text>
        </view>
      </view>

      <!-- 连线层（绝对定位，覆盖中间区域） -->
      <view class="line-layer" id="cq-line-layer">

        <!-- 已建立的连线 -->
        <block v-for="conn in connections" :key="conn.id">
          <view
            v-if="lineStyle(conn)"
            class="line-seg"
            :class="{
              'line-correct': conn.isCorrect === true,
              'line-wrong':   conn.isCorrect === false,
              'line-pending': conn.isCorrect === null,
            }"
            :style="lineStyle(conn)"
          ></view>
          <!-- 左端点 -->
          <view
            v-if="dotStyle(conn, 'left')"
            class="line-dot"
            :class="{
              'dot-correct': conn.isCorrect === true,
              'dot-wrong':   conn.isCorrect === false,
            }"
            :style="dotStyle(conn, 'left')"
          ></view>
          <!-- 右端点 -->
          <view
            v-if="dotStyle(conn, 'right')"
            class="line-dot"
            :class="{
              'dot-correct': conn.isCorrect === true,
              'dot-wrong':   conn.isCorrect === false,
            }"
            :style="dotStyle(conn, 'right')"
          ></view>
        </block>

        <!-- 拖动中的临时连线 -->
        <view
          v-if="tempLine && tempLineStyle"
          class="line-seg line-temp"
          :style="tempLineStyle"
        ></view>
        <view
          v-if="tempLine"
          class="line-dot dot-temp"
          :style="tempDotStyle"
        ></view>

      </view>

      <!-- 右侧 -->
      <view class="items-col items-right">
        <view
          v-for="item in rightItems"
          :key="item.id"
          :id="'cq_right_' + item.id"
          :class="['item-card', 'item-right', {
            'item-correct':   isRightCorrect(item.id),
            'item-wrong':     isRightWrong(item.id),
            'item-connected': isRightConnected(item.id) && !isRightCorrect(item.id) && !isRightWrong(item.id),
          }]"
        >
          <text class="item-text">{{ item.content }}</text>
        </view>
      </view>

    </view>

    <!-- 提交按钮 -->
    <view
      class="submit-btn"
      v-if="connections.length > 0 && !submitted"
      @click="onSubmit"
    >
      <text class="ph ph-check-circle"></text>
      <text>提交答案</text>
    </view>
  </view>
</template>

<script>
let _uid = 0
function uid() { return 'conn_' + (++_uid) + '_' + Date.now() }

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/** 根据两点计算线段的 CSS transform 样式（绝对定位矩形旋转） */
function buildLineStyle(x1, y1, x2, y2) {
  const dx = x2 - x1
  const dy = y2 - y1
  const length = Math.sqrt(dx * dx + dy * dy)
  if (length < 1) return null
  const angle = Math.atan2(dy, dx) * (180 / Math.PI)
  return {
    position: 'absolute',
    left: x1 + 'px',
    top: (y1 - 3) + 'px',   // 线宽 6px，垂直居中偏移 3px
    width: length + 'px',
    height: '6px',
    borderRadius: '3px',
    transformOrigin: '0 50%',
    transform: `rotate(${angle}deg)`,
    zIndex: 5,
    pointerEvents: 'none',
  }
}

export default {
  name: 'ConnectPairsQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      leftItems: [],
      rightItems: [],
      connections: [],
      draggingLeftId: null,
      tempLine: null,       // { fromX, fromY, toX, toY }
      leftPositions: {},    // { [id]: { x, y } } 相对于 line-layer
      rightPositions: {},
      rightRects: {},       // { [id]: { left, top, right, bottom } } 页面绝对坐标
      layerLeft: 0,
      layerTop: 0,
      submitted: false,
      timeoutTimer: null,
    }
  },
  computed: {
    totalPairs() { return this.leftItems.length },
    correctCount() { return this.connections.filter(c => c.isCorrect === true).length },

    tempLineStyle() {
      if (!this.tempLine) return null
      return buildLineStyle(
        this.tempLine.fromX, this.tempLine.fromY,
        this.tempLine.toX,   this.tempLine.toY,
      )
    },
    tempDotStyle() {
      if (!this.tempLine) return null
      return {
        position: 'absolute',
        left: (this.tempLine.fromX - 6) + 'px',
        top:  (this.tempLine.fromY - 6) + 'px',
        width: '12px', height: '12px',
        borderRadius: '50%',
        background: '#3B82F6',
        zIndex: 6,
        pointerEvents: 'none',
      }
    },
  },
  mounted() {
    this.initGame()
    const timeLimit = (this.question.time_limit || 60) * 1000
    this.timeoutTimer = setTimeout(() => {
      if (!this.submitted) this._submit()
    }, timeLimit)
  },
  beforeUnmount() {
    if (this.timeoutTimer) { clearTimeout(this.timeoutTimer); this.timeoutTimer = null }
  },
  methods: {
    initGame() {
      const pairs = this.question.pairs || []
      this.leftItems = pairs.map((p, idx) => ({
        id: 'left_' + idx,
        content: p.left.content,
        pairIndex: idx,
      }))
      this.rightItems = shuffle(pairs.map((p, idx) => ({
        id: 'right_' + idx,
        content: p.right.content,
        pairIndex: idx,
      })))
      this.connections = []
      this.draggingLeftId = null
      this.tempLine = null
      setTimeout(() => this._queryPositions(), 400)
    },

    _queryPositions() {
      const query = uni.createSelectorQuery().in(this)
      query.select('#cq-line-layer').boundingClientRect((layerRect) => {
        if (!layerRect) return
        this.layerLeft = layerRect.left
        this.layerTop  = layerRect.top

        // 查询左侧项坐标（右边缘中心，作为连线起点）
        const lq = uni.createSelectorQuery().in(this)
        this.leftItems.forEach(item => lq.select('#cq_left_' + item.id).boundingClientRect())
        lq.exec((results) => {
          const newLeft = {}
          results.forEach((rect, idx) => {
            if (rect) {
              const item = this.leftItems[idx]
              newLeft[item.id] = {
                x: rect.right - this.layerLeft,
                y: rect.top + rect.height / 2 - this.layerTop,
              }
            }
          })
          this.leftPositions = newLeft

          // 查询右侧项坐标（左边缘中心，作为连线终点）
          const rq = uni.createSelectorQuery().in(this)
          this.rightItems.forEach(item => rq.select('#cq_right_' + item.id).boundingClientRect())
          rq.exec((rResults) => {
            const newRight = {}
            const newRects = {}
            rResults.forEach((rect, idx) => {
              if (rect) {
                const item = this.rightItems[idx]
                newRight[item.id] = {
                  x: rect.left - this.layerLeft,
                  y: rect.top + rect.height / 2 - this.layerTop,
                }
                newRects[item.id] = {
                  left: rect.left, top: rect.top,
                  right: rect.left + rect.width, bottom: rect.top + rect.height,
                }
              }
            })
            this.rightPositions = newRight
            this.rightRects = newRects
          })
        })
      }).exec()
    },

    // ── 计算连线样式（供模板使用） ──────────────────────────────
    lineStyle(conn) {
      const lp = this.leftPositions[conn.leftId]
      const rp = this.rightPositions[conn.rightId]
      if (!lp || !rp) return null
      return buildLineStyle(lp.x, lp.y, rp.x, rp.y)
    },

    dotStyle(conn, side) {
      const pos = side === 'left'
        ? this.leftPositions[conn.leftId]
        : this.rightPositions[conn.rightId]
      if (!pos) return null
      return {
        position: 'absolute',
        left: (pos.x - 7) + 'px',
        top:  (pos.y - 7) + 'px',
        width: '14px', height: '14px',
        borderRadius: '50%',
        zIndex: 6,
        pointerEvents: 'none',
      }
    },

    // ── 触摸事件 ────────────────────────────────────────────────
    onTouchStart(event, leftItem) {
      const touch = event.touches[0]
      if (!touch) return
      this.draggingLeftId = leftItem.id
      const lp = this.leftPositions[leftItem.id]
      this.tempLine = {
        fromX: lp ? lp.x : (touch.clientX - this.layerLeft),
        fromY: lp ? lp.y : (touch.clientY - this.layerTop),
        toX: touch.clientX - this.layerLeft,
        toY: touch.clientY - this.layerTop,
      }
    },

    onTouchMove(event) {
      if (!this.draggingLeftId || !this.tempLine) return
      const touch = event.touches[0]
      if (!touch) return
      this.tempLine = {
        ...this.tempLine,
        toX: touch.clientX - this.layerLeft,
        toY: touch.clientY - this.layerTop,
      }
    },

    onTouchEnd(event) {
      if (!this.draggingLeftId) return
      const touch = event.changedTouches[0]
      if (touch) {
        const hitItem = this._findRightItemAt(touch.clientX, touch.clientY)
        if (hitItem) this._handleDrop(this.draggingLeftId, hitItem)
      }
      this.draggingLeftId = null
      this.tempLine = null
    },

    _findRightItemAt(x, y) {
      for (const item of this.rightItems) {
        const rect = this.rightRects[item.id]
        if (rect && x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
          return item
        }
      }
      return null
    },

    _handleDrop(leftId, rightItem) {
      this.connections = this.connections.filter(c => c.leftId !== leftId)
      this.connections = this.connections.filter(c => c.rightId !== rightItem.id)

      const leftItem = this.leftItems.find(i => i.id === leftId)
      const isCorrect = leftItem && leftItem.pairIndex === rightItem.pairIndex

      this.connections = [...this.connections, {
        id: uid(),
        leftId,
        rightId: rightItem.id,
        isCorrect: isCorrect ? true : false,
      }]

      // 全部正确则自动提交
      const allCorrect = this.leftItems.every(item =>
        this.connections.some(c => c.leftId === item.id && c.isCorrect === true)
      )
      if (allCorrect) setTimeout(() => this._submit(), 600)
    },

    onSubmit() {
      if (!this.submitted) this._submit()
    },

    _submit() {
      if (this.submitted) return
      this.submitted = true
      if (this.timeoutTimer) { clearTimeout(this.timeoutTimer); this.timeoutTimer = null }
      const score = this.totalPairs > 0 ? this.correctCount / this.totalPairs : 0
      this.$emit('answer-submitted', {
        score,
        correctPairs: this.correctCount,
        totalPairs: this.totalPairs,
        isCorrect: score >= 0.7,
      })
    },

    isLeftConnected(id)  { return this.connections.some(c => c.leftId === id) },
    isLeftCorrect(id)    { return this.connections.some(c => c.leftId === id && c.isCorrect === true) },
    isLeftWrong(id)      { return this.connections.some(c => c.leftId === id && c.isCorrect === false) },
    isRightConnected(id) { return this.connections.some(c => c.rightId === id) },
    isRightCorrect(id)   { return this.connections.some(c => c.rightId === id && c.isCorrect === true) },
    isRightWrong(id)     { return this.connections.some(c => c.rightId === id && c.isCorrect === false) },
  },
}
</script>

<style scoped>
.connect-pairs-question {
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

.match-progress {
  display: flex; align-items: center; gap: 10rpx;
  padding: 4rpx 0;
}
.match-progress .ph { font-size: 28rpx; color: #22C55E; }
.progress-text { font-size: 24rpx; font-weight: 700; color: #22C55E; }

/* ── 三列布局 ── */
.columns-wrapper {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  position: relative;
  min-height: 300rpx;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 24rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
  overflow: visible;
}

.items-col {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 16rpx;
  z-index: 20;
  flex-shrink: 0;
  width: 160rpx;
  padding: 0 12rpx;
}
.items-left  { align-items: flex-end; }
.items-right { align-items: flex-start; }

/* 连线层：绝对定位覆盖中间区域 */
.line-layer {
  flex: 1;
  position: relative;
  z-index: 10;
  min-width: 0;
  overflow: visible;
}

/* ── 连线线段 ── */
.line-seg {
  background: #3B82F6;
  border-radius: 3px;
}
.line-correct { background: #22C55E; }
.line-wrong   { background: #EF4444; }
.line-pending { background: #3B82F6; }
.line-temp    { background: #93C5FD; opacity: 0.8; }

/* ── 端点圆 ── */
.line-dot {
  background: #3B82F6;
  border: 2px solid #FFFFFF;
  box-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.dot-correct { background: #22C55E; }
.dot-wrong   { background: #EF4444; }
.dot-temp    { background: #93C5FD; }

/* ── 词语卡片 ── */
.item-card {
  width: 136rpx;
  min-height: 88rpx;
  border-radius: 20rpx;
  background: #FFFFFF;
  border: 3rpx solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12rpx 8rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06);
  transition: all 0.2s;
  cursor: pointer;
}
.item-card:active { transform: scale(0.95); }

/* 左侧卡片右边缘有连接点提示 */
.item-left  { border-right: 5rpx solid #4F9EF8; }
/* 右侧卡片左边缘有连接点提示 */
.item-right { border-left:  5rpx solid #4F9EF8; }

.item-connected { border-color: #3B82F6; background: #EFF6FF; }
.item-correct   { border-color: #22C55E !important; background: #F0FDF4 !important; }
.item-wrong     { border-color: #EF4444 !important; background: #FEF2F2 !important; }
.item-dragging  { transform: scale(1.05); box-shadow: 0 8rpx 24rpx rgba(79,158,248,0.35) !important; }

.item-text {
  font-size: 34rpx;
  font-weight: 800;
  color: #2D3748;
  text-align: center;
  line-height: 1.2;
}
.item-correct .item-text { color: #22C55E; }
.item-wrong   .item-text { color: #EF4444; }

/* ── 提交按钮 ── */
.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(59,130,246,0.35);
}
.submit-btn:active { transform: scale(0.97); }
.submit-btn .ph { font-size: 32rpx; }
</style>
