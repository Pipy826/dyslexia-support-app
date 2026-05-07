<template>
  <view class="handwriting-canvas-wrap" :style="{ height: height + 'rpx' }">
    <canvas
      :id="canvasId"
      :canvas-id="canvasId"
      class="handwriting-canvas"
      :style="{ width: '100%', height: height + 'rpx' }"
      @touchstart="onTouchStart"
      @touchmove="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
    ></canvas>
    <!-- 空白提示 -->
    <view class="canvas-hint" v-if="isEmpty && showHint">
      <text class="ph ph-pencil-simple"></text>
      <text class="hint-text">在这里书写</text>
    </view>
  </view>
</template>

<script>
/**
 * HandwritingCanvas.vue
 * 手写画布组件，封装 touch 事件，收集笔迹点序列
 *
 * Props:
 *   height      {Number}  画布高度（rpx），默认 400
 *   strokeColor {String}  笔迹颜色，默认 '#2D3748'
 *   lineWidth   {Number}  线宽（px），默认 4
 *   showHint    {Boolean} 是否显示空白提示，默认 true
 *   disabled    {Boolean} 是否禁用输入，默认 false
 *
 * Methods:
 *   clear()          清空画布与笔迹数据
 *   getStrokeData()  返回当前所有笔迹数据 [[{x,y,t}, ...], ...]
 *
 * Events:
 *   stroke-start  开始一笔
 *   stroke-end    结束一笔，payload: 当前笔迹点数组
 *   input         任意笔迹变化时触发
 */
export default {
  name: 'HandwritingCanvas',

  props: {
    height: {
      type: Number,
      default: 400,
    },
    strokeColor: {
      type: String,
      default: '#2D3748',
    },
    lineWidth: {
      type: Number,
      default: 4,
    },
    showHint: {
      type: Boolean,
      default: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },

  data() {
    return {
      // 唯一 canvas id，避免多实例冲突
      canvasId: 'hw-canvas-' + Math.random().toString(36).slice(2, 8),
      // 所有笔迹：[[{x, y, t}, ...], ...]
      strokes: [],
      // 当前正在书写的笔迹
      currentStroke: [],
      // 是否正在书写
      isDrawing: false,
      // 画布上下文（uni canvas context）
      ctx: null,
      // 画布实际像素尺寸（px）
      canvasWidth: 0,
      canvasHeight: 0,
      // 画布在页面中的位置（用于坐标转换）
      canvasRect: null,
      // 是否为空（无笔迹）
      isEmpty: true,
    }
  },

  mounted() {
    this.$nextTick(() => {
      this._initCanvas()
    })
  },

  methods: {
    // ── 初始化 ──────────────────────────────────────────────────────────────

    _initCanvas() {
      // 获取画布上下文
      this.ctx = uni.createCanvasContext(this.canvasId, this)

      // 获取画布尺寸与位置
      const query = uni.createSelectorQuery().in(this)
      query
        .select('#' + this.canvasId)
        .boundingClientRect((rect) => {
          if (rect) {
            this.canvasWidth = rect.width
            this.canvasHeight = rect.height
            this.canvasRect = rect
          }
        })
        .exec()

      // 初始化画布样式
      this._setupCtx()
      this._drawBackground()
    },

    _setupCtx() {
      if (!this.ctx) return
      this.ctx.setLineWidth(this.lineWidth)
      this.ctx.setStrokeStyle(this.strokeColor)
      this.ctx.setLineCap('round')
      this.ctx.setLineJoin('round')
    },

    _drawBackground() {
      if (!this.ctx) return
      // 白色背景
      this.ctx.setFillStyle('#FFFFFF')
      this.ctx.fillRect(0, 0, this.canvasWidth || 9999, this.canvasHeight || 9999)
      // 浅色网格辅助线（可选）
      this._drawGrid()
      this.ctx.draw(false)
    },

    _drawGrid() {
      if (!this.ctx || !this.canvasWidth || !this.canvasHeight) return
      const w = this.canvasWidth
      const h = this.canvasHeight
      this.ctx.setStrokeStyle('rgba(200, 200, 200, 0.3)')
      this.ctx.setLineWidth(1)
      this.ctx.setLineDash([4, 4], 0)

      // 横中线
      this.ctx.beginPath()
      this.ctx.moveTo(0, h / 2)
      this.ctx.lineTo(w, h / 2)
      this.ctx.stroke()

      // 竖中线
      this.ctx.beginPath()
      this.ctx.moveTo(w / 2, 0)
      this.ctx.lineTo(w / 2, h)
      this.ctx.stroke()

      // 对角线
      this.ctx.setStrokeStyle('rgba(200, 200, 200, 0.15)')
      this.ctx.beginPath()
      this.ctx.moveTo(0, 0)
      this.ctx.lineTo(w, h)
      this.ctx.stroke()

      this.ctx.beginPath()
      this.ctx.moveTo(w, 0)
      this.ctx.lineTo(0, h)
      this.ctx.stroke()

      // 恢复笔迹样式
      this.ctx.setLineDash([], 0)
      this.ctx.setStrokeStyle(this.strokeColor)
      this.ctx.setLineWidth(this.lineWidth)
    },

    // ── 坐标转换 ─────────────────────────────────────────────────────────────

    /**
     * 将 touch 事件坐标转换为画布坐标
     * UniApp touch 事件的 clientX/clientY 是相对于视口的坐标
     */
    _toCanvasCoord(touch) {
      if (this.canvasRect) {
        return {
          x: touch.clientX - this.canvasRect.left,
          y: touch.clientY - this.canvasRect.top,
        }
      }
      // 降级：直接使用 x/y（部分平台 touch 事件直接提供画布坐标）
      return { x: touch.x || touch.clientX || 0, y: touch.y || touch.clientY || 0 }
    },

    // ── Touch 事件处理 ────────────────────────────────────────────────────────

    onTouchStart(e) {
      if (this.disabled) return
      e.preventDefault && e.preventDefault()

      // 刷新画布位置（防止页面滚动后坐标偏移）
      const query = uni.createSelectorQuery().in(this)
      query
        .select('#' + this.canvasId)
        .boundingClientRect((rect) => {
          if (rect) {
            this.canvasRect = rect
            this.canvasWidth = rect.width
            this.canvasHeight = rect.height
          }
        })
        .exec()

      const touch = e.touches[0]
      const { x, y } = this._toCanvasCoord(touch)
      const t = Date.now()

      this.isDrawing = true
      this.currentStroke = [{ x, y, t }]
      this.isEmpty = false

      // 开始新路径
      if (this.ctx) {
        this.ctx.setLineWidth(this.lineWidth)
        this.ctx.setStrokeStyle(this.strokeColor)
        this.ctx.setLineCap('round')
        this.ctx.setLineJoin('round')
        this.ctx.beginPath()
        this.ctx.moveTo(x, y)
      }

      this.$emit('stroke-start', { x, y, t })
    },

    onTouchMove(e) {
      if (!this.isDrawing || this.disabled) return
      e.preventDefault && e.preventDefault()

      const touch = e.touches[0]
      const { x, y } = this._toCanvasCoord(touch)
      const t = Date.now()

      this.currentStroke.push({ x, y, t })

      // 实时绘制
      if (this.ctx) {
        this.ctx.lineTo(x, y)
        this.ctx.stroke()
        // draw(true) 表示保留之前的内容（增量绘制）
        this.ctx.draw(true)
        // 继续当前路径（draw 后需要重新 beginPath 或 moveTo）
        this.ctx.beginPath()
        this.ctx.moveTo(x, y)
      }

      this.$emit('input', this.currentStroke)
    },

    onTouchEnd(e) {
      if (!this.isDrawing || this.disabled) return

      this.isDrawing = false

      // 保存当前笔迹（至少有 1 个点才算有效笔迹）
      if (this.currentStroke.length > 0) {
        this.strokes.push([...this.currentStroke])
        this.$emit('stroke-end', [...this.currentStroke])
        this.$emit('input', this.strokes)
      }

      this.currentStroke = []
    },

    // ── 公开方法 ──────────────────────────────────────────────────────────────

    /**
     * 清空画布与笔迹数据
     */
    clear() {
      this.strokes = []
      this.currentStroke = []
      this.isDrawing = false
      this.isEmpty = true

      if (this.ctx) {
        this.ctx.clearRect(0, 0, this.canvasWidth || 9999, this.canvasHeight || 9999)
        this._setupCtx()
        this._drawBackground()
      }

      this.$emit('input', [])
    },

    /**
     * 返回当前所有笔迹数据
     * @returns {Array} [[{x, y, t}, ...], ...]
     */
    getStrokeData() {
      return this.strokes.map((stroke) => stroke.map((pt) => ({ ...pt })))
    },

    /**
     * 将画布导出为 base64 图片（PNG 格式）
     * H5 环境直接用 DOM canvas.toDataURL()
     * 小程序环境使用 uni.canvasToTempFilePath
     * @returns {Promise<string>} base64 字符串（含 data:image/png;base64, 前缀），失败返回空字符串
     */
    toBase64() {
      return new Promise((resolve) => {
        // H5 环境：直接通过 DOM 导出，最可靠
        if (typeof document !== 'undefined') {
          try {
            const canvasEl = document.getElementById(this.canvasId)
            if (canvasEl && typeof canvasEl.toDataURL === 'function') {
              resolve(canvasEl.toDataURL('image/png'))
              return
            }
          } catch (e) {
            // ignore
          }
          resolve('')
          return
        }

        // 小程序环境：canvasToTempFilePath → readFile base64
        try {
          uni.canvasToTempFilePath({
            canvasId: this.canvasId,
            fileType: 'png',
            quality: 0.8,
            success: (res) => {
              try {
                const fs = uni.getFileSystemManager()
                fs.readFile({
                  filePath: res.tempFilePath,
                  encoding: 'base64',
                  success: (fileRes) => resolve('data:image/png;base64,' + fileRes.data),
                  fail: () => resolve(''),
                })
              } catch (e) {
                resolve('')
              }
            },
            fail: () => resolve(''),
          }, this)
        } catch (e) {
          resolve('')
        }
      })
    },
  },
}
</script>

<style scoped>
.handwriting-canvas-wrap {
  position: relative;
  width: 100%;
  background: #FFFFFF;
  border-radius: 20rpx;
  overflow: hidden;
  border: 3rpx solid #E8EDF2;
  box-shadow: inset 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.handwriting-canvas {
  display: block;
  width: 100%;
}

/* 空白提示（居中显示，不阻挡触摸） */
.canvas-hint {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  pointer-events: none;
  opacity: 0.35;
}

.canvas-hint .ph {
  font-size: 56rpx;
  color: #A0AEC0;
}

.hint-text {
  font-size: 26rpx;
  color: #A0AEC0;
  font-weight: 500;
}
</style>
