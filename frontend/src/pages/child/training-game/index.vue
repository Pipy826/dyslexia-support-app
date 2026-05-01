<template>
  <view class="page-container" :style="{ '--game-primary': gameTheme.primary, '--game-gradient': gameTheme.gradient }">
    <!-- 顶部：渐变主题色背景 + 进度 + 退出 -->
    <view class="game-header" :style="{ background: gameTheme.gradient }">
      <button class="exit-btn" @click="exitGame">
        <text class="ph ph-x"></text>
      </button>
      <view class="progress-section">
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
        <view class="progress-text">{{ currentIndex + 1 }}/{{ questions.length }}</view>
      </view>
      <circle-timer
        :time-left="timeLeft"
        :total-time="currentQuestion?.time_limit || 10"
      ></circle-timer>
    </view>

    <!-- 训练模式标签 -->
    <view class="mode-badge" v-if="!loading && currentQuestion && !showResult">
      <text class="ph ph-barbell"></text> 训练模式 · {{ gameTypeName }}
    </view>

    <!-- 加载中 -->
    <view class="loading-area" v-if="loading">
      <view class="loading-icon"><text class="ph ph-circle-notch spin"></text></view>
      <view class="loading-text">题目加载中...</view>
    </view>

    <!-- 游戏区域 -->
    <view class="game-content" v-else-if="currentQuestion && !showResult">
      <view class="question-card">
        <view class="question-area">
          <view class="question-header">
            <button class="audio-btn" @click="playAudio">
              <text class="ph ph-speaker-high"></text>
            </button>
            <view class="question-title">{{ currentQuestion.title }}</view>
          </view>
          <view class="question-instruction">{{ currentQuestion.instruction }}</view>

          <!-- 视觉辨识：2x2 大字格 -->
          <view :class="['options-grid', { shake: shakeOptions }]" v-if="currentQuestion.type === 'visual_discrimination'">
            <view
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              :class="['option-char', getOptionClass(index)]"
              @click="selectAnswer(index)"
            >{{ option }}</view>
          </view>

          <!-- 其他题型：竖向列表 -->
          <view :class="['options-list', { shake: shakeOptions }]" v-else>
            <view
              v-for="(option, index) in currentQuestion.options"
              :key="index"
              :class="['option-item', getOptionClass(index)]"
              @click="selectAnswer(index)"
            >
              <view class="option-label">{{ ['A','B','C','D'][index] }}</view>
              <view class="option-text">{{ option }}</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 答题反馈遮罩 -->
    <view class="feedback-overlay" v-if="showFeedback">
      <view :class="['feedback-icon', lastCorrect === true ? 'correct' : lastCorrect === false ? 'wrong' : 'neutral']">
        <text :class="lastCorrect === true ? 'ph ph-check-circle' : lastCorrect === false ? 'ph ph-x-circle' : 'ph ph-arrow-right'"></text>
      </view>
      <view class="feedback-text">
        {{ lastCorrect === true ? '答对了！🎉' : lastCorrect === false ? '加油，继续！' : '下一题' }}
      </view>
      <view class="feedback-correct" v-if="lastCorrect === false && currentCorrectAnswer">
        正确答案：<text class="feedback-answer">{{ currentCorrectAnswer }}</text>
      </view>
    </view>

    <!-- 粒子动画（答对时） -->
    <view class="particles-overlay" v-if="showParticles">
      <view class="particle" v-for="(p, i) in particles" :key="i" :style="p.style">{{ p.emoji }}</view>
    </view>

    <!-- 退出确认弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click="hideModal">
      <view class="modal-content" @click.stop>
        <view class="modal-icon warning"><text class="ph ph-warning"></text></view>
        <view class="modal-title">要休息一下吗？</view>
        <view class="modal-desc">训练进度会保存，下次继续加油！</view>
        <button class="modal-btn outline" @click="confirmExit">退出训练</button>
        <button class="modal-btn primary" @click="hideModal">继续训练</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getQuestions } from '../../../api/screening.js'
import { completeTask, updateTaskProgress } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { getGameTheme } from '../../../utils/gameThemes.js'
import CircleTimer from '../../../components/game/CircleTimer.vue'

export default {
  components: { CircleTimer },
  data() {
    return {
      taskId: null,
      gameType: 'visual',
      grade: '',
      questions: [],
      currentIndex: 0,
      answers: [],
      child: null,
      showExitModal: false,
      showFeedback: false,
      lastCorrect: null,
      currentCorrectAnswer: '',
      questionStartTime: null,
      firstClickTime: null,
      timeLeft: 10,
      timerInterval: null,
      loading: true,
      showResult: false,
      correctAnswerMap: {},
      selectedAnswer: null,
      shakeOptions: false,
      showParticles: false,
    }
  },
  computed: {
    currentQuestion() { return this.questions[this.currentIndex] || null },
    progressPercent() {
      if (!this.questions.length) return 0
      return (this.currentIndex / this.questions.length) * 100
    },
    gameTypeName() {
      const map = {
        visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
        working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
      }
      return map[this.gameType] || this.gameType
    },
    gameTheme() {
      return getGameTheme(this.gameType)
    },
    particles() {
      const emojis = ['⭐', '✨', '🎉', '💫', '🌟', '🎊']
      return Array.from({ length: 6 }, (_, i) => ({
        emoji: emojis[i % emojis.length],
        style: {
          left: (10 + i * 15) + '%',
          top: (20 + (i % 3) * 20) + '%',
          animationDelay: (i * 0.08) + 's',
        },
      }))
    },
  },
  onLoad(options) {
    this.child = getCurrentChild()
    if (options.task_id) this.taskId = parseInt(options.task_id)
    if (options.game_type) this.gameType = options.game_type
    if (options.grade) this.grade = options.grade
    else if (this.child?.grade) this.grade = this.child.grade
    this.loadQuestions()
  },
  onUnload() { this.clearTimer() },
  onBackPress() {
    this.showExitModal = true
    return true
  },
  methods: {
    async loadQuestions() {
      this.loading = true
      try {
        const VALID_TYPES = ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']
        if (!VALID_TYPES.includes(this.gameType)) {
          this.gameType = 'visual'
        }
        const res = await getQuestions(this.gameType, { grade: this.grade, count: 8 })
        this.questions = res.questions || []
        this.correctAnswerMap = {}
        this.questions.forEach(q => {
          if (q.correct_index !== undefined) this.correctAnswerMap[q.id] = q.correct_index
        })
        if (!this.questions.length) {
          uni.showToast({ title: '暂无题目', icon: 'none' })
          return
        }
        this.loading = false
        this.resetQuestionState()
        this.startTimer()
        if (this.taskId) {
          updateTaskProgress(this.taskId, { status: 'in_progress', progress: 0 }).catch(() => {})
        }
      } catch (e) {
        uni.showToast({ title: '加载失败，请重试', icon: 'none' })
        this.loading = false
      }
    },
    resetQuestionState() {
      this.questionStartTime = Date.now()
      this.firstClickTime = null
      this.selectedAnswer = null
    },
    startTimer() {
      this.clearTimer()
      const q = this.currentQuestion
      this.timeLeft = q?.time_limit || 10
      this.timerInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.clearTimer()
          this.autoSubmitCurrent()
        }
      }, 1000)
    },
    clearTimer() {
      if (this.timerInterval) { clearInterval(this.timerInterval); this.timerInterval = null }
    },
    autoSubmitCurrent() {
      const timeSpent = Math.round(this.currentQuestion?.time_limit || 10)
      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: -1, time_spent: timeSpent,
        reaction_time: null, change_count: 0, is_timeout: true,
      })
      this.showFeedbackAnim(false)
      this.nextQuestion()
    },
    selectAnswer(index) {
      if (this.showFeedback) return
      if (this.firstClickTime === null) this.firstClickTime = Date.now()
      this.selectedAnswer = index
      this.confirmAnswer()
    },
    getOptionClass(index) {
      if (this.showFeedback) {
        const correctIndex = this.correctAnswerMap[this.currentQuestion?.id]
        if (correctIndex !== undefined) {
          if (index === correctIndex) return 'correct'
          if (index === this.selectedAnswer) return 'wrong'
        }
        return ''
      }
      return this.selectedAnswer === index ? 'selected' : ''
    },
    confirmAnswer() {
      if (this.selectedAnswer === null || this.showFeedback) return
      this.clearTimer()
      const timeSpent = Math.round((this.currentQuestion?.time_limit || 10) - this.timeLeft)
      const correctIndex = this.correctAnswerMap[this.currentQuestion.id]
      const isCorrect = correctIndex !== undefined ? this.selectedAnswer === correctIndex : null
      const reactionTime = this.firstClickTime ? this.firstClickTime - this.questionStartTime : null
      if (isCorrect === false && correctIndex !== undefined) {
        this.currentCorrectAnswer = this.currentQuestion.options[correctIndex] || ''
      } else {
        this.currentCorrectAnswer = ''
      }
      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: this.selectedAnswer,
        time_spent: timeSpent,
        reaction_time: reactionTime,
        change_count: 0,
        is_timeout: false,
        is_correct: isCorrect,
      })
      this.showFeedbackAnim(isCorrect)
    },
    showFeedbackAnim(correct) {
      this.lastCorrect = correct
      this.showFeedback = true
      // 答对：粒子动画
      if (correct === true) {
        this.showParticles = true
        setTimeout(() => { this.showParticles = false }, 800)
      }
      // 答错：震动动画
      if (correct === false) {
        this.shakeOptions = true
        setTimeout(() => { this.shakeOptions = false }, 400)
      }
      const delay = correct === true ? 600 : 1200
      setTimeout(() => {
        this.showFeedback = false
        this.nextQuestion()
      }, delay)
    },
    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.resetQuestionState()
        this.startTimer()
        if (this.taskId) {
          const pct = Math.round((this.currentIndex / this.questions.length) * 100)
          updateTaskProgress(this.taskId, { progress: pct }).catch(() => {})
        }
      } else {
        this.finishTraining()
      }
    },
    async finishTraining() {
      this.showResult = true
      this.clearTimer()
      const correctCount = this.answers.filter(a => a.is_correct === true).length
      const totalCount = this.answers.length
      const accuracy = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0
      if (this.taskId) {
        try {
          await completeTask(this.taskId, {
            correct_count: correctCount,
            total_count: totalCount,
            accuracy,
          })
        } catch (e) { console.warn('完成任务失败', e) }
      }
      uni.setStorageSync('last_training_result', {
        game_type: this.gameType,
        correct_count: correctCount,
        total_count: totalCount,
        accuracy,
        stars: 1,
        mode: 'training',
      })
      uni.redirectTo({ url: '/pages/child/training-reward/index' })
    },
    playAudio() {
      const text = this.currentQuestion?.instruction || this.currentQuestion?.title
      if (!text) return
      // #ifdef MP-WEIXIN
      if (uni.textToSpeech) {
        uni.textToSpeech({ lang: 'zh_CN', tts: true, content: text, fail: () => {} })
      } else {
        uni.showToast({ title: text, icon: 'none', duration: 2000 })
      }
      // #endif
      // #ifndef MP-WEIXIN
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
        const utter = new window.SpeechSynthesisUtterance(text)
        utter.lang = 'zh-CN'; utter.rate = 0.85
        window.speechSynthesis.speak(utter)
        return
      }
      uni.showToast({ title: text, icon: 'none', duration: 2000 })
      // #endif
    },
    exitGame() {
      this.clearTimer()
      this.showFeedback = false
      this.showExitModal = true
    },
    hideModal() { this.showExitModal = false },
    confirmExit() {
      this.clearTimer()
      this.showExitModal = false
      uni.redirectTo({ url: '/pages/child/training/index' })
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* 顶部渐变头部 */
.game-header {
  padding: 56rpx 32rpx 24rpx;
  min-height: 200rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.15);
}

.exit-btn {
  width: 72rpx; height: 72rpx;
  display: flex; align-items: center; justify-content: center;
  padding: 0; background: rgba(255,255,255,0.25);
  border-radius: 50%; flex-shrink: 0;
  border: 2rpx solid rgba(255,255,255,0.4);
  transition: all 0.2s;
}
.exit-btn:active { transform: translateY(3rpx); background: rgba(255,255,255,0.4); }
.exit-btn .ph { font-size: 36rpx; color: #FFFFFF; }

.progress-section { flex: 1; }
.progress-track {
  height: 12rpx; background: rgba(255,255,255,0.3);
  border-radius: 6rpx; overflow: hidden; margin-bottom: 8rpx;
}
.progress-fill {
  height: 100%; background: rgba(255,255,255,0.9);
  border-radius: 6rpx; transition: width 0.4s;
}
.progress-text {
  font-size: 22rpx; font-weight: 700; color: rgba(255,255,255,0.85); text-align: center;
}

/* 训练模式标签 */
.mode-badge {
  display: inline-flex; align-items: center; gap: 8rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8; font-size: 22rpx; font-weight: 700;
  padding: 10rpx 24rpx; border-radius: 20rpx;
  margin: 20rpx 32rpx 0;
  border: 1rpx solid #BFDBFE;
  align-self: flex-start;
}
.mode-badge .ph { font-size: 22rpx; }

/* 加载 */
.loading-area {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 20rpx;
}
.loading-icon .ph { font-size: 64rpx; color: var(--game-primary, #4F9EF8); }
.loading-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 游戏内容区 */
.game-content {
  flex: 1; padding: 20rpx 32rpx 0;
  display: flex; flex-direction: column;
}

.question-card {
  background: #FFFFFF; border-radius: 28rpx;
  padding: 32rpx; flex: 1;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
}

.question-area { display: flex; flex-direction: column; align-items: center; }

.question-header {
  display: flex; align-items: center; gap: 12rpx;
  margin-bottom: 12rpx; width: 100%;
}
.audio-btn {
  width: 64rpx; height: 64rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  padding: 0; flex-shrink: 0; border: 2rpx solid #BFDBFE;
}
.audio-btn .ph { font-size: 32rpx; color: #4F9EF8; }
.question-title { font-size: 40rpx; font-weight: 800; color: #2D3748; flex: 1; }
.question-instruction {
  font-size: 26rpx; color: #718096; text-align: center;
  margin-bottom: 36rpx; line-height: 1.6; font-weight: 500; width: 100%;
}

/* 视觉辨识 2x2 */
.options-grid { display: flex; flex-wrap: wrap; gap: 20rpx; width: 100%; }
.option-char {
  width: calc(50% - 10rpx);
  height: calc(50vw - 60rpx);
  background: #FFFFFF; border: 3rpx solid #E5E7EB; border-radius: 24rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 96rpx; font-weight: 800; color: #2D3748; transition: all 0.2s;
}
.option-char.selected { border-color: var(--game-primary, #4F9EF8); background: linear-gradient(135deg, #EFF6FF, #DBEAFE); color: var(--game-primary, #4F9EF8); }
.option-char.correct { border-color: #22C55E; background: linear-gradient(135deg, #F0FDF4, #DCFCE7); color: #22C55E; }
.option-char.wrong { border-color: #FF6B6B; background: linear-gradient(135deg, #FFF5F5, #FFE4E4); color: #FF6B6B; }

/* 竖向列表 */
.options-list { display: flex; flex-direction: column; gap: 16rpx; width: 100%; }
.option-item {
  background: #FFFFFF; border: 3rpx solid #E5E7EB; border-radius: 20rpx;
  padding: 24rpx 28rpx; display: flex; align-items: center; gap: 24rpx; transition: all 0.2s;
}
.option-item.selected { border-color: var(--game-primary, #4F9EF8); background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.option-item.correct { border-color: #22C55E; background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.option-item.wrong { border-color: #FF6B6B; background: linear-gradient(135deg, #FFF5F5, #FFE4E4); }
.option-label {
  width: 48rpx; height: 48rpx; border-radius: 12rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center;
  font-size: 24rpx; font-weight: 700; color: #A0AEC0; flex-shrink: 0;
}
.option-item.selected .option-label { background: #DBEAFE; color: var(--game-primary, #4F9EF8); }
.option-item.correct .option-label { background: #DCFCE7; color: #22C55E; }
.option-item.wrong .option-label { background: #FFE4E4; color: #FF6B6B; }
.option-text { font-size: 32rpx; font-weight: 700; color: #2D3748; flex: 1; }
.option-item.selected .option-text { color: var(--game-primary, #4F9EF8); }
.option-item.correct .option-text { color: #22C55E; }
.option-item.wrong .option-text { color: #FF6B6B; }

/* 震动动画 */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8rpx); }
  40% { transform: translateX(8rpx); }
  60% { transform: translateX(-6rpx); }
  80% { transform: translateX(6rpx); }
}
.shake { animation: shake 0.4s ease; }

/* 答题反馈遮罩 */
.feedback-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.96); z-index: 500;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20rpx;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.feedback-icon .ph { font-size: 160rpx; animation: popIn 0.3s cubic-bezier(0.4,0,0.2,1); }
.feedback-icon.correct .ph { color: #22C55E; }
.feedback-icon.wrong .ph { color: #FF6B6B; }
.feedback-icon.neutral .ph { color: var(--game-primary, #4F9EF8); }
@keyframes popIn { 0% { transform: scale(0.4); opacity: 0; } 70% { transform: scale(1.1); } 100% { transform: scale(1); opacity: 1; } }
.feedback-text { font-size: 44rpx; font-weight: 800; color: #2D3748; }
.feedback-correct { font-size: 26rpx; color: #718096; }
.feedback-answer { font-size: 30rpx; font-weight: 700; color: #22C55E; }

/* 粒子动画 */
.particles-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  pointer-events: none; z-index: 600;
}
.particle {
  position: absolute; font-size: 48rpx;
  animation: particleFly 0.8s ease-out forwards;
}
@keyframes particleFly {
  0% { transform: translateY(0) scale(0); opacity: 1; }
  100% { transform: translateY(-200rpx) scale(1.2); opacity: 0; }
}

/* 退出弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 10000;
  display: flex; justify-content: center; align-items: center;
}
.modal-content {
  background: #FFFFFF; width: 85%; border-radius: 32rpx; padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center;
}
.modal-icon { width: 112rpx; height: 112rpx; border-radius: 28rpx; display: flex; align-items: center; justify-content: center; margin-bottom: 28rpx; }
.modal-icon.warning { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.modal-icon.warning .ph { font-size: 56rpx; color: #F57F17; }
.modal-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; }
.modal-desc { font-size: 26rpx; color: #718096; text-align: center; line-height: 1.6; margin-bottom: 36rpx; font-weight: 500; }
.modal-btn { width: 100%; border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700; margin-bottom: 16rpx; transition: all 0.2s; }
.modal-btn.outline { background: #F5F5F5; color: #718096; }
.modal-btn.primary { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25); }
</style>
