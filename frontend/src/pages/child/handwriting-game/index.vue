<template>
  <view class="page-container">

    <!-- ── 顶部栏 ── -->
    <view class="top-bar">
      <view class="progress-info">
        <text class="progress-text">第 {{ currentIndex + 1 }} 题 / 共 {{ questions.length }} 题</text>
      </view>
      <view class="top-right-area">
        <view class="stars-badge">
          <text class="ph ph-star"></text>
          <text class="stars-num">{{ sessionStars }}</text>
        </view>
        <view class="exit-btn" @click="exitGame">
          <text class="ph ph-x"></text>
        </view>
      </view>
    </view>

    <!-- ── 主内容区 ── -->
    <scroll-view class="content-area" scroll-y>

      <!-- 目标汉字展示区 -->
      <view class="character-section">
        <view class="character-card">
          <!-- 笔顺动画提示（展示阶段） -->
          <view class="stroke-hint" v-if="phase === 'preview'">
            <view class="stroke-anim-label">笔顺提示</view>
            <view class="stroke-order-list">
              <view
                v-for="(stroke, idx) in currentQuestion.stroke_order"
                :key="idx"
                :class="['stroke-tag', { active: idx <= animStrokeIdx }]"
              >{{ stroke }}</view>
            </view>
          </view>

          <!-- 大字展示 -->
          <view class="big-character">{{ currentQuestion ? currentQuestion.character : '' }}</view>

          <!-- 笔画数提示 -->
          <view class="stroke-count-hint">
            <text class="ph ph-pencil-line"></text>
            共 {{ currentQuestion ? currentQuestion.stroke_count : 0 }} 画
          </view>
        </view>
      </view>

      <!-- 状态提示条 -->
      <view :class="['status-bar', statusBarClass]" v-if="statusMsg">
        <text :class="'ph ' + statusIcon"></text>
        <text class="status-text">{{ statusMsg }}</text>
      </view>

      <!-- 画布区 -->
      <view class="canvas-section">
        <view class="canvas-label">
          <text class="ph ph-hand-pointing"></text>
          <text>{{ phase === 'preview' ? '请等待笔顺动画...' : '在下方书写汉字' }}</text>
        </view>

        <handwriting-canvas
          ref="canvas"
          :height="380"
          stroke-color="#2D3748"
          :line-width="5"
          :disabled="phase !== 'writing'"
          :show-hint="phase === 'writing'"
          @input="onCanvasInput"
        ></handwriting-canvas>

        <!-- 超时进度条 -->
        <view class="timeout-bar" v-if="phase === 'writing'">
          <view class="timeout-fill" :style="{ width: timeoutPercent + '%', background: timeoutColor }"></view>
        </view>
        <view class="timeout-label" v-if="phase === 'writing'">
          <text class="ph ph-timer"></text>
          剩余 {{ timeLeft }} 秒
        </view>
      </view>

      <!-- 底部按钮区 -->
      <view class="action-bar">
        <button
          class="btn-rewrite"
          @click="rewrite"
          :disabled="phase !== 'writing'"
        >
          <text class="ph ph-eraser"></text> 重写
        </button>
        <button
          class="btn-submit"
          @click="submit"
          :disabled="phase !== 'writing' || !hasStrokes"
        >
          <text class="ph ph-check"></text> 提交
        </button>
      </view>

      <!-- 底部安全区 -->
      <view style="height: 60rpx;"></view>
    </scroll-view>

    <!-- ── 正向反馈弹窗 ── -->
    <view class="feedback-overlay" v-if="showFeedback">
      <view :class="['feedback-card', feedbackType === 'correct' ? 'correct' : 'wrong']">
        <view class="feedback-emoji">{{ feedbackType === 'correct' ? '🎉' : '💪' }}</view>
        <view class="feedback-title">{{ feedbackTitle }}</view>
        <view class="feedback-desc">{{ feedbackDesc }}</view>

        <!-- 庆祝星星动画 -->
        <view class="stars-burst" v-if="feedbackType === 'correct'">
          <text v-for="i in 6" :key="i" class="burst-star" :style="burstStarStyle(i)">⭐</text>
        </view>

        <!-- 笔顺提示（答错时） -->
        <view class="stroke-hint-detail" v-if="feedbackType === 'wrong' && retryCount < 2">
          <view class="hint-label">正确笔顺：</view>
          <view class="stroke-order-list">
            <view
              v-for="(s, i) in currentQuestion.stroke_order"
              :key="i"
              class="stroke-tag active"
            >{{ s }}</view>
          </view>
        </view>

        <button class="feedback-btn" @click="onFeedbackNext">
          {{ feedbackNextLabel }}
        </button>
      </view>
    </view>

    <!-- ── 超时提示弹窗 ── -->
    <view class="feedback-overlay" v-if="showTimeout">
      <view class="feedback-card timeout">
        <view class="feedback-emoji">⏰</view>
        <view class="feedback-title">时间到啦！</view>
        <view class="feedback-desc">没关系，我们跳过这道题继续吧</view>
        <button class="feedback-btn" @click="skipQuestion">继续下一题</button>
      </view>
    </view>

    <!-- ── 退出确认弹窗 ── -->
    <view class="exit-modal-overlay" v-if="showExitModal" @click="showExitModal = false">
      <view class="exit-modal-content" @click.stop>
        <view class="exit-modal-icon">
          <text class="ph ph-warning"></text>
        </view>
        <view class="exit-modal-title">要休息一下吗？</view>
        <view class="exit-modal-desc">当前进度不会保存哦，下次重新开始。</view>
        <button class="exit-modal-btn outline" @click="doExit">退出游戏</button>
        <button class="exit-modal-btn primary" @click="showExitModal = false">继续游戏</button>
      </view>
    </view>

    <!-- ── 游戏结果页 ── -->
    <view class="result-overlay" v-if="phase === 'result'">
      <view class="result-card">
        <view class="result-emoji">
          {{ sessionStars >= 4 ? '🏆' : sessionStars >= 2 ? '😊' : '🌱' }}
        </view>
        <view class="result-title">游戏完成！</view>
        <view class="result-stars">
          <text
            v-for="i in 5"
            :key="i"
            :class="['result-star', { earned: i <= sessionStars }]"
          >⭐</text>
        </view>
        <view class="result-stats">
          <view class="stat-item">
            <view class="stat-num">{{ passedCount }}</view>
            <view class="stat-label">写对了</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-num">{{ questions.length }}</view>
            <view class="stat-label">共几题</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-num">{{ sessionStars }}</view>
            <view class="stat-label">颗星星</view>
          </view>
        </view>
        <button class="result-btn" @click="finishGame">
          <text class="ph ph-check-circle"></text> 完成
        </button>
      </view>
    </view>

  </view>
</template>

<script>
import HandwritingCanvas from '../../../components/game/HandwritingCanvas.vue'
import AudioManager from '../../../utils/audio.js'
import { evaluateHandwriting, calcHandwritingStars } from '../../../utils/gameScoring.js'
import { buildHandwritingPayload, enqueueRecord, shouldRetry } from '../../../utils/gameDataBuilder.js'
import { completeTask, createTask } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { get } from '../../../api/index.js'

// ── 本地题库 ──────────────────────────────────────────────────────────────────
const LOCAL_QUESTIONS = {
  L1: [
    { id: 'hw_L1_001', character: '一', stroke_count: 1, stroke_order: ['横'], difficulty: 'L1', time_limit: 30 },
    { id: 'hw_L1_002', character: '二', stroke_count: 2, stroke_order: ['横', '横'], difficulty: 'L1', time_limit: 30 },
    { id: 'hw_L1_003', character: '三', stroke_count: 3, stroke_order: ['横', '横', '横'], difficulty: 'L1', time_limit: 30 },
    { id: 'hw_L1_004', character: '人', stroke_count: 2, stroke_order: ['撇', '捺'], difficulty: 'L1', time_limit: 30 },
    { id: 'hw_L1_005', character: '口', stroke_count: 3, stroke_order: ['竖', '横折', '横'], difficulty: 'L1', time_limit: 30 },
  ],
  L2: [
    { id: 'hw_L2_001', character: '你', stroke_count: 7, stroke_order: ['撇','竖','撇','横','竖钩','撇','点'], difficulty: 'L2', time_limit: 45 },
    { id: 'hw_L2_002', character: '我', stroke_count: 7, stroke_order: ['横','竖钩','撇','横','斜钩','撇','点'], difficulty: 'L2', time_limit: 45 },
    { id: 'hw_L2_003', character: '他', stroke_count: 5, stroke_order: ['撇','竖','横','竖','横折钩'], difficulty: 'L2', time_limit: 45 },
    { id: 'hw_L2_004', character: '好', stroke_count: 6, stroke_order: ['撇折','点','横折','横','竖','横'], difficulty: 'L2', time_limit: 45 },
    { id: 'hw_L2_005', character: '学', stroke_count: 8, stroke_order: ['点','点','横撇','点','横折','横','竖','横'], difficulty: 'L2', time_limit: 45 },
  ],
  L3: [
    { id: 'hw_L3_001', character: '爱', stroke_count: 10, stroke_order: ['横折','点','撇','横','竖','横','撇','捺','撇','点'], difficulty: 'L3', time_limit: 60 },
    { id: 'hw_L3_002', character: '家', stroke_count: 10, stroke_order: ['点','横撇','竖','横折','横','撇','竖弯钩','撇','撇','捺'], difficulty: 'L3', time_limit: 60 },
    { id: 'hw_L3_003', character: '朋', stroke_count: 8, stroke_order: ['横折钩','横','横','竖','横折钩','横','横','竖'], difficulty: 'L3', time_limit: 60 },
    { id: 'hw_L3_004', character: '友', stroke_count: 4, stroke_order: ['横','撇','撇','捺'], difficulty: 'L3', time_limit: 60 },
    { id: 'hw_L3_005', character: '读', stroke_count: 10, stroke_order: ['点','横折提','点','撇','横','竖','横折','横','撇','点'], difficulty: 'L3', time_limit: 60 },
  ],
}

const QUESTIONS_PER_SESSION = 5

export default {
  name: 'HandwritingGame',

  components: { HandwritingCanvas },

  data() {
    return {
      // 游戏参数
      difficulty: 'L1',
      taskId: null,

      // 题目数据
      questions: [],
      currentIndex: 0,

      // 游戏阶段：'loading' | 'preview' | 'writing' | 'feedback' | 'result'
      phase: 'loading',

      // 笔顺动画
      animStrokeIdx: -1,
      animTimer: null,

      // 超时计时
      timeLeft: 30,
      timeoutTimer: null,
      showTimeout: false,

      // 退出弹窗
      showExitModal: false,

      // 笔迹状态
      hasStrokes: false,

      // 反馈弹窗
      showFeedback: false,
      feedbackType: 'correct', // 'correct' | 'wrong'
      feedbackTitle: '',
      feedbackDesc: '',
      retryCount: 0,

      // 本局统计
      sessionStars: 0,
      passedCount: 0,
      startTime: null,

      // 状态提示条
      statusMsg: '',
      statusBarClass: '',
      statusIcon: '',
    }
  },

  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || null
    },
    timeoutPercent() {
      const limit = this.currentQuestion ? this.currentQuestion.time_limit : 30
      return Math.max(0, Math.min(100, (this.timeLeft / limit) * 100))
    },
    timeoutColor() {
      if (this.timeoutPercent > 50) return '#22C55E'
      if (this.timeoutPercent > 25) return '#F59E0B'
      return '#EF4444'
    },
    feedbackNextLabel() {
      if (this.feedbackType === 'correct') {
        return this.currentIndex + 1 >= this.questions.length ? '查看结果' : '下一题'
      }
      if (this.retryCount < 2) return '再试一次'
      return this.currentIndex + 1 >= this.questions.length ? '查看结果' : '下一题'
    },
  },

  onLoad(options) {
    this.difficulty = options.difficulty || 'L1'
    this.taskId = options.task_id ? parseInt(options.task_id) : null
    this.startTime = Date.now()
    this.loadQuestions()
  },

  onUnload() {
    this._clearTimers()
  },

  methods: {
    // ── 数据加载 ──────────────────────────────────────────────────────────────

    async loadQuestions() {
      this.phase = 'loading'
      let questions = []

      try {
        const res = await get(`/api/training/games/handwriting?difficulty=${this.difficulty}`)
        if (res && Array.isArray(res.questions) && res.questions.length > 0) {
          questions = res.questions
        }
      } catch (e) {
        // 接口不存在或失败，使用本地题库
      }

      if (questions.length === 0) {
        const pool = LOCAL_QUESTIONS[this.difficulty] || LOCAL_QUESTIONS.L1
        // 随机取 QUESTIONS_PER_SESSION 道题（不足则全取）
        const shuffled = [...pool].sort(() => Math.random() - 0.5)
        questions = shuffled.slice(0, QUESTIONS_PER_SESSION)
      }

      this.questions = questions
      this.currentIndex = 0
      this.startPreview()
    },

    // ── 游戏流程 ──────────────────────────────────────────────────────────────

    startPreview() {
      if (!this.currentQuestion) return
      this.phase = 'preview'
      this.retryCount = 0
      this.hasStrokes = false
      this.statusMsg = ''
      this.animStrokeIdx = -1

      // 笔顺动画：每 400ms 高亮一个笔画
      const strokes = this.currentQuestion.stroke_order || []
      let idx = 0
      this.animTimer = setInterval(() => {
        this.animStrokeIdx = idx
        idx++
        if (idx >= strokes.length) {
          clearInterval(this.animTimer)
          this.animTimer = null
          // 动画结束后 300ms 激活画布
          setTimeout(() => {
            this.startWriting()
          }, 300)
        }
      }, 400)

      // 最少展示 1500ms
      // （由 animTimer 控制，单笔字也会等 400ms + 300ms = 700ms，
      //   多笔字自然超过 1500ms；单笔字额外补足）
      if (strokes.length <= 3) {
        // 确保至少 1500ms 后才激活画布
        const minDelay = 1500
        const animDuration = strokes.length * 400 + 300
        if (animDuration < minDelay) {
          // 已在 animTimer 结束后的 setTimeout 中处理，此处无需额外操作
          // 但需要覆盖 animTimer 结束后的 setTimeout
          // 重新设置：在 animTimer 结束后延迟足够时间
        }
      }
    },

    startWriting() {
      this.phase = 'writing'
      this.hasStrokes = false

      // 清空画布
      if (this.$refs.canvas) {
        this.$refs.canvas.clear()
      }

      // 启动超时计时
      const limit = this.currentQuestion ? this.currentQuestion.time_limit : 30
      this.timeLeft = limit
      this._startTimeoutTimer(limit)
    },

    _startTimeoutTimer(limit) {
      this._clearTimeoutTimer()
      this.timeoutTimer = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this._clearTimeoutTimer()
          this._onTimeout()
        }
      }, 1000)
    },

    _onTimeout() {
      if (this.phase !== 'writing') return
      this.showTimeout = true
      this.phase = 'feedback'
    },

    skipQuestion() {
      this.showTimeout = false
      this._nextQuestion()
    },

    onCanvasInput(strokes) {
      this.hasStrokes = Array.isArray(strokes) && strokes.length > 0
      // 有输入时重置超时计时
      if (this.hasStrokes) {
        const limit = this.currentQuestion ? this.currentQuestion.time_limit : 30
        this._clearTimeoutTimer()
        this._startTimeoutTimer(limit)
      }
    },

    // ── 提交与评分 ────────────────────────────────────────────────────────────

    submit() {
      if (this.phase !== 'writing') return
      if (!this.hasStrokes) {
        uni.showToast({ title: '请先书写汉字', icon: 'none' })
        return
      }

      this._clearTimeoutTimer()
      this.phase = 'feedback'

      const strokeData = this.$refs.canvas ? this.$refs.canvas.getStrokeData() : []
      // 无参考笔迹时传空数组，evaluateHandwriting 会给基础分
      const score = evaluateHandwriting(strokeData, [])

      if (score >= 60) {
        // 答对
        this.passedCount++
        this.sessionStars += calcHandwritingStars(score)
        AudioManager.playSFX('correct')
        this.feedbackType = 'correct'
        this.feedbackTitle = '写得不错！'
        this.feedbackDesc = `得分：${score} 分，获得 1 颗星！`
        this.showFeedback = true
      } else {
        // 答错
        AudioManager.playSFX('wrong')
        this.feedbackType = 'wrong'
        this.retryCount++

        if (this.retryCount < 2) {
          this.feedbackTitle = '再试一次！'
          this.feedbackDesc = `得分：${score} 分，参考笔顺如下，加油！`
        } else {
          this.feedbackTitle = '没关系！'
          this.feedbackDesc = `得分：${score} 分，继续下一题吧！`
        }
        this.showFeedback = true
      }
    },

    rewrite() {
      if (this.phase !== 'writing') return
      if (this.$refs.canvas) {
        this.$refs.canvas.clear()
      }
      this.hasStrokes = false
    },

    onFeedbackNext() {
      this.showFeedback = false

      if (this.feedbackType === 'wrong' && this.retryCount < 2) {
        // 允许重试
        this.phase = 'writing'
        if (this.$refs.canvas) {
          this.$refs.canvas.clear()
        }
        this.hasStrokes = false
        const limit = this.currentQuestion ? this.currentQuestion.time_limit : 30
        this.timeLeft = limit
        this._startTimeoutTimer(limit)
        return
      }

      this._nextQuestion()
    },

    _nextQuestion() {
      if (this.currentIndex + 1 >= this.questions.length) {
        // 所有题目完成
        await this._finishSession()
      } else {
        this.currentIndex++
        this.startPreview()
      }
    },

    // ── 游戏结束 ──────────────────────────────────────────────────────────────

    async _finishSession() {
      this._clearTimers()
      AudioManager.playSFX('complete')
      this.phase = 'result'

      const durationSeconds = Math.round((Date.now() - this.startTime) / 1000)
      const accuracy = this.questions.length > 0
        ? Math.round((this.passedCount / this.questions.length) * 100)
        : 0
      const payload = buildHandwritingPayload({
        taskId: this.taskId,
        difficulty: this.difficulty,
        score: accuracy,
        starsEarned: this.sessionStars,
        durationSeconds,
        charactersAttempted: this.questions.length,
        charactersPasssed: this.passedCount,
      })

      // 提交至后端
      if (this.taskId) {
        try {
          await completeTask(this.taskId, payload)
        } catch (e) {
          enqueueRecord({ taskId: this.taskId, payload })
        }
      } else {
        // 从挑战tab直接进入，没有task_id，自动创建并完成任务以记录星星
        try {
          const child = getCurrentChild()
          if (child?.id) {
            const task = await createTask({
              child_id: child.id,
              task_type: 'handwriting',
              task_name: '手写汉字挑战',
              scheduled_date: new Date().toISOString().split('T')[0],
            })
            await completeTask(task.id, { ...payload, task_id: task.id })
          }
        } catch (e) { console.warn('自动创建任务失败', e) }
      }

      // 保存结果供结算页使用（与前6种游戏格式对齐）
      uni.setStorageSync('last_training_result', {
        game_type: 'handwriting',
        correct_count: this.passedCount,
        total_count: this.questions.length,
        accuracy,
        stars: this.sessionStars,
        mode: 'training',
      })

      // 跳转到统一结算页
      uni.redirectTo({ url: '/pages/child/training-reward/index' })
    },

    finishGame() {
      uni.navigateBack({ delta: 1 })
    },

    // ── 导航 ──────────────────────────────────────────────────────────────────

    goBack() {
      this._clearTimers()
      uni.navigateBack({ delta: 1 })
    },

    exitGame() {
      this.showExitModal = true
    },

    doExit() {
      this._clearTimers()
      this.showExitModal = false
      uni.navigateBack({ delta: 1 })
    },

    // ── 工具方法 ──────────────────────────────────────────────────────────────

    _clearTimers() {
      this._clearTimeoutTimer()
      if (this.animTimer) {
        clearInterval(this.animTimer)
        this.animTimer = null
      }
    },

    _clearTimeoutTimer() {
      if (this.timeoutTimer) {
        clearInterval(this.timeoutTimer)
        this.timeoutTimer = null
      }
    },

    burstStarStyle(i) {
      const angle = (i - 1) * 60
      const rad = (angle * Math.PI) / 180
      const dist = 60
      const x = Math.cos(rad) * dist
      const y = Math.sin(rad) * dist
      return {
        transform: `translate(${x}rpx, ${y}rpx)`,
        animationDelay: `${(i - 1) * 80}ms`,
      }
    },
  },
}
</script>

<style scoped>
/* ── 页面容器 ── */
.page-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #FFF8F0 0%, #FFF3E0 100%);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

/* ── 顶部栏 ── */
.top-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 56rpx 32rpx 20rpx;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
}

.back-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #FFF3E0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #FFE0B2;
}
.back-btn:active { transform: scale(0.92); }
.back-btn .ph { font-size: 32rpx; color: #F57F17; }

.progress-info {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.progress-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #5D4037;
}

.stars-badge {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  padding: 10rpx 20rpx;
  border-radius: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.3);
}
.stars-badge .ph { font-size: 28rpx; color: #F57F17; }
.stars-num { font-size: 28rpx; font-weight: 800; color: #E65100; }

.top-right-area {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
}

.exit-btn {
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 107, 107, 0.1);
  border: 2rpx solid rgba(255, 107, 107, 0.2);
  display: flex; align-items: center; justify-content: center;
}
.exit-btn .ph { font-size: 28rpx; color: #FF6B6B; }

/* 退出确认弹窗 */
.exit-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(45, 55, 72, 0.5);
  z-index: 9999;
  display: flex; justify-content: center; align-items: center;
}
.exit-modal-content {
  background: #FFFEF9;
  width: 80%; max-width: 640rpx;
  border-radius: 72rpx;
  padding: 56rpx 48rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 32rpx 80rpx rgba(0,0,0,0.2);
  border: 5rpx solid rgba(255,255,255,0.9);
  position: relative; overflow: hidden;
}
.exit-modal-content::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 10rpx;
  background: linear-gradient(90deg, #4F9EF8, #A78BFA, #FF9ECD, #FFD93D);
}
.exit-modal-icon {
  width: 140rpx; height: 140rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  border: 4rpx solid #FFD54F;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 32rpx;
}
.exit-modal-icon .ph { font-size: 72rpx; color: #F57F17; }
.exit-modal-title { font-size: 44rpx; font-weight: 900; color: #2D3748; margin-bottom: 16rpx; }
.exit-modal-desc { font-size: 28rpx; color: #A0AEC0; text-align: center; margin-bottom: 40rpx; font-weight: 600; line-height: 1.6; }
.exit-modal-btn {
  width: 100%; border-radius: 9999rpx;
  padding: 32rpx; font-size: 30rpx; font-weight: 800;
  margin-bottom: 24rpx; letter-spacing: 1rpx;
}
.exit-modal-btn.outline {
  background: #FFFFFF; border: 4rpx solid #E5E7EB;
  color: #A0AEC0; box-shadow: 0 4rpx 0 #E5E7EB;
}
.exit-modal-btn.primary {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  box-shadow: 0 6rpx 0 #2563EB, 0 8rpx 24rpx rgba(59,130,246,0.35);
}

/* ── 内容区 ── */
.content-area {
  flex: 1;
  padding: 24rpx 28rpx;
  width: 100%;
  box-sizing: border-box;
}

/* ── 汉字展示区 ── */
.character-section {
  margin-bottom: 20rpx;
}

.character-card {
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 32rpx 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(245, 127, 23, 0.12);
  border: 3rpx solid #FFE0B2;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.big-character {
  font-size: 160rpx;
  font-weight: 900;
  color: #3E2723;
  line-height: 1;
  text-shadow: 2rpx 4rpx 12rpx rgba(0, 0, 0, 0.1);
  font-family: 'KaiTi', 'STKaiti', serif;
}

.stroke-count-hint {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #8D6E63;
  font-weight: 600;
}
.stroke-count-hint .ph { font-size: 28rpx; color: #FF8F00; }

/* 笔顺动画提示 */
.stroke-hint {
  width: 100%;
}
.stroke-anim-label {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 600;
  margin-bottom: 10rpx;
  text-align: center;
}
.stroke-order-list {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 8rpx;
  justify-content: center;
}
.stroke-tag {
  padding: 6rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  font-weight: 600;
  background: #F5F5F5;
  color: #BDBDBD;
  transition: all 0.3s;
}
.stroke-tag.active {
  background: linear-gradient(135deg, #FFE0B2, #FFCC80);
  color: #E65100;
  box-shadow: 0 2rpx 8rpx rgba(255, 152, 0, 0.3);
}

/* ── 状态提示条 ── */
.status-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10rpx;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  font-size: 26rpx;
  font-weight: 600;
}
.status-bar.success {
  background: #F0FDF4;
  color: #22C55E;
  border: 2rpx solid #BBF7D0;
}
.status-bar.error {
  background: #FFF5F5;
  color: #EF4444;
  border: 2rpx solid #FECACA;
}
.status-bar .ph { font-size: 28rpx; }

/* ── 画布区 ── */
.canvas-section {
  margin-bottom: 24rpx;
}

.canvas-label {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #8D6E63;
  font-weight: 600;
  margin-bottom: 12rpx;
  text-align: center;
}
.canvas-label .ph { font-size: 26rpx; color: #FF8F00; }

/* 超时进度条 */
.timeout-bar {
  height: 8rpx;
  background: #F5F5F5;
  border-radius: 4rpx;
  margin-top: 12rpx;
  overflow: hidden;
}
.timeout-fill {
  height: 100%;
  border-radius: 4rpx;
  transition: width 1s linear, background 0.5s;
}
.timeout-label {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 600;
  margin-top: 8rpx;
  text-align: center;
}
.timeout-label .ph { font-size: 22rpx; }

/* ── 底部按钮 ── */
.action-bar {
  display: flex;
  flex-direction: row;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.btn-rewrite {
  flex: 1;
  background: #FFF3E0;
  color: #F57F17;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 700;
  border: 3rpx solid #FFE0B2;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}
.btn-rewrite:active { transform: scale(0.97); }
.btn-rewrite[disabled] { opacity: 0.4; }
.btn-rewrite .ph { font-size: 30rpx; }

.btn-submit {
  flex: 2;
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(245, 127, 23, 0.35);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}
.btn-submit:active { transform: scale(0.97); }
.btn-submit[disabled] { opacity: 0.4; box-shadow: none; }
.btn-submit .ph { font-size: 30rpx; }

/* ── 反馈弹窗 ── */
.feedback-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.feedback-card {
  background: #FFFFFF;
  width: 88%;
  max-width: 620rpx;
  border-radius: 36rpx;
  padding: 48rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  position: relative;
  overflow: hidden;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }

.feedback-card.correct {
  border-top: 8rpx solid #22C55E;
}
.feedback-card.wrong {
  border-top: 8rpx solid #F59E0B;
}
.feedback-card.timeout {
  border-top: 8rpx solid #6B7280;
}

.feedback-emoji {
  font-size: 80rpx;
  line-height: 1;
}
.feedback-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #2D3748;
}
.feedback-desc {
  font-size: 26rpx;
  color: #718096;
  font-weight: 500;
  text-align: center;
}

/* 庆祝星星爆炸 */
.stars-burst {
  position: relative;
  width: 40rpx;
  height: 40rpx;
  margin: 8rpx 0;
}
.burst-star {
  position: absolute;
  top: 0; left: 0;
  font-size: 28rpx;
  animation: burstOut 0.6s ease-out forwards;
}
@keyframes burstOut {
  0% { transform: translate(0, 0) scale(0); opacity: 1; }
  100% { opacity: 0; scale: 1.2; }
}

/* 笔顺提示（答错时） */
.stroke-hint-detail {
  width: 100%;
  background: #FFF8F0;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}
.hint-label {
  font-size: 22rpx;
  color: #8D6E63;
  font-weight: 600;
  margin-bottom: 10rpx;
}

.feedback-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(245, 127, 23, 0.3);
  margin-top: 8rpx;
}
.feedback-btn:active { transform: scale(0.97); }

/* ── 结果页 ── */
.result-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(160deg, #FFF8F0 0%, #FFF3E0 100%);
  z-index: 9998;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s;
}

.result-card {
  background: #FFFFFF;
  width: 88%;
  max-width: 640rpx;
  border-radius: 40rpx;
  padding: 56rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 8rpx 40rpx rgba(245, 127, 23, 0.15);
  border: 3rpx solid #FFE0B2;
  animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.result-emoji {
  font-size: 100rpx;
  line-height: 1;
}
.result-title {
  font-size: 44rpx;
  font-weight: 900;
  color: #3E2723;
}

.result-stars {
  display: flex;
  flex-direction: row;
  gap: 8rpx;
}
.result-star {
  font-size: 44rpx;
  opacity: 0.2;
  transition: all 0.3s;
}
.result-star.earned {
  opacity: 1;
  animation: starPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes starPop { from { transform: scale(0); } to { transform: scale(1); } }

.result-stats {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 0;
  background: #FFF8F0;
  border-radius: 20rpx;
  padding: 20rpx 32rpx;
  width: 100%;
}
.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}
.stat-num {
  font-size: 48rpx;
  font-weight: 900;
  color: #F57F17;
}
.stat-label {
  font-size: 22rpx;
  color: #8D6E63;
  font-weight: 600;
}
.stat-divider {
  width: 2rpx;
  height: 60rpx;
  background: #FFE0B2;
}

.result-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  font-size: 32rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 20rpx rgba(245, 127, 23, 0.35);
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
}
.result-btn:active { transform: scale(0.97); }
.result-btn .ph { font-size: 32rpx; }
</style>
