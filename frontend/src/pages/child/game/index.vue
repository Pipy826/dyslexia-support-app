<template>
  <view class="page-container">
    <!-- 游戏顶部：进度条与退出 -->
    <view class="game-header">
      <button class="exit-btn" @click="exitGame">
        <text class="ph ph-x"></text>
      </button>
      <view class="progress-section">
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
        <view class="progress-text">{{ currentIndex + 1 }}/{{ questions.length }}</view>
      </view>
      <view class="timer-badge" :class="{ warning: timeLeft <= 3 }">
        <text class="ph ph-timer"></text>
        {{ timeLeft }}s
      </view>
    </view>

    <!-- 加载中 -->
    <view class="loading-area" v-if="loading">
      <view class="loading-icon">
        <text class="ph ph-circle-notch spin"></text>
      </view>
      <view class="loading-text">题目加载中...</view>
    </view>

    <!-- 游戏核心区域 -->
    <view class="game-content" v-else-if="currentQuestion && !showResult">
      <!-- 题目区域 -->
      <view class="question-area">
        <view class="question-header">
          <button class="audio-btn" @click="playAudio">
            <text class="ph ph-speaker-high"></text>
          </button>
          <view class="question-title">{{ currentQuestion.title }}</view>
        </view>
        <view class="question-instruction">{{ currentQuestion.instruction }}</view>

        <!-- 视觉辨识：2x2 大字格 -->
        <view class="options-grid" v-if="currentQuestion.type === 'visual_discrimination'">
          <view
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            :class="['option-char', getOptionClass(index)]"
            @click="selectAnswer(index)"
          >
            {{ option }}
          </view>
        </view>

        <!-- 拼字/理解：竖向列表 -->
        <view class="options-list" v-else>
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

    <!-- 答题反馈遮罩 -->
    <view class="feedback-overlay" v-if="showFeedback">
      <view :class="['feedback-icon', lastCorrect === true ? 'correct' : lastCorrect === false ? 'wrong' : 'neutral']">
        <text :class="lastCorrect === true ? 'ph ph-check-circle' : lastCorrect === false ? 'ph ph-x-circle' : 'ph ph-arrow-right'"></text>
      </view>
      <view class="feedback-text">
        {{ lastCorrect === true ? '答对了！🎉' : lastCorrect === false ? '再想想哦~' : '下一题' }}
      </view>
    </view>

    <!-- 底部操作区 -->
    <view class="bottom-area" v-if="!loading && currentQuestion && !showResult">
      <button
        :class="['next-btn', { active: selectedAnswer !== null }]"
        @click="confirmAnswer"
        :disabled="selectedAnswer === null"
      >
        选好了 ✓
      </button>
    </view>

    <!-- 退出确认弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click="hideModal">
      <view class="modal-content" @click.stop>
        <view class="modal-icon warning">
          <text class="ph ph-warning"></text>
        </view>
        <view class="modal-title">要休息一下吗？</view>
        <view class="modal-desc">现在的进度会保存哦，下次可以继续挑战。</view>
        <button class="modal-btn outline" @click="confirmExit">退出挑战</button>
        <button class="modal-btn primary" @click="hideModal">继续挑战</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getQuestions, startScreening, submitScreening } from '../../../api/screening.js'
import { completeTask } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      gameType: 'visual',
      difficulty: 'L1',
      questions: [],
      currentIndex: 0,
      selectedAnswer: null,
      answers: [],
      child: null,
      screeningId: null,
      showExitModal: false,
      showFeedback: false,
      lastCorrect: false,
      questionStartTime: null,
      timeLeft: 10,
      timerInterval: null,
      loading: true,
      showResult: false,
      correctAnswerMap: {}
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex] || null
    },
    progressPercent() {
      if (this.questions.length === 0) return 0
      return (this.currentIndex / this.questions.length) * 100
    }
  },
  onLoad(options) {
    this.child = getCurrentChild()
    if (options.game_type) this.gameType = options.game_type
    if (options.difficulty) this.difficulty = options.difficulty
    this.initScreening()
  },
  onUnload() {
    this.clearTimer()
  },
  methods: {
    async initScreening() {
      this.loading = true
      try {
        // 检查是否有已存在的筛查会话
        const saved = uni.getStorageSync('current_screening')
        if (saved && saved.game_type === this.gameType) {
          this.screeningId = saved.id
          this.gameType = saved.game_type
          this.difficulty = saved.difficulty || 'L1'
          await this.loadQuestions()
          return
        }

        if (!this.child) {
          uni.showToast({ title: '请先在家长端选择孩子', icon: 'none' })
          setTimeout(() => uni.redirectTo({ url: '/pages/child/home/index' }), 1500)
          return
        }

        const res = await startScreening({
          child_id: this.child.id,
          game_type: this.gameType
        })
        this.screeningId = res.id
        uni.setStorageSync('current_screening', {
          id: res.id,
          game_type: this.gameType,
          difficulty: this.difficulty
        })
        await this.loadQuestions()
      } catch (e) {
        console.error('初始化筛查失败', e)
        // 401: token 失效，提示重新登录
        if (e?._statusCode === 401 || e?.message === '未授权') {
          uni.showToast({ title: '登录已过期，请家长重新登录', icon: 'none' })
          setTimeout(() => uni.reLaunch({ url: '/pages/parent/auth/login' }), 1500)
        } else {
          uni.showToast({ title: '加载失败，请返回重试', icon: 'none' })
        }
        this.loading = false
      }
    },

    async loadQuestions() {
      try {
        const res = await getQuestions(this.gameType, this.difficulty, 10)
        this.questions = res.questions || []
        // 缓存正确答案用于即时反馈
        this.correctAnswerMap = {}
        this.questions.forEach(q => {
          if (q.correct_index !== undefined) {
            this.correctAnswerMap[q.id] = q.correct_index
          }
        })
        if (this.questions.length === 0) {
          uni.showToast({ title: '暂无题目', icon: 'none' })
          return
        }
        this.loading = false
        this.startTimer()
      } catch (e) {
        console.error('加载题目失败', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
        this.loading = false
      }
    },

    startTimer() {
      this.clearTimer()
      const q = this.currentQuestion
      this.timeLeft = q?.time_limit || 10
      this.timerInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.clearTimer()
          // 超时自动提交当前题（记为未答）
          this.autoSubmitCurrent()
        }
      }, 1000)
    },

    clearTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    },

    autoSubmitCurrent() {
      // 超时：记录为未答（answer = -1）
      const timeSpent = (this.currentQuestion?.time_limit || 10)
      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: -1,
        time_spent: timeSpent
      })
      this.showFeedbackAnim(false)
      this.nextQuestion()
    },

    selectAnswer(index) {
      if (this.showFeedback) return
      this.selectedAnswer = index
    },

    getOptionClass(index) {
      if (this.showFeedback) {
        const correctIndex = this.correctAnswerMap[this.currentQuestion?.id]
        if (correctIndex !== undefined) {
          if (index === correctIndex) return 'correct'
          if (index === this.selectedAnswer) return 'wrong'
        } else {
          // 没有答案信息时只高亮选中项
          if (index === this.selectedAnswer) return this.lastCorrect ? 'correct' : 'wrong'
        }
        return ''
      }
      return this.selectedAnswer === index ? 'selected' : ''
    },

    confirmAnswer() {
      if (this.selectedAnswer === null || this.showFeedback) return
      this.clearTimer()

      const timeSpent = Math.round(
        ((this.currentQuestion?.time_limit || 10) - this.timeLeft)
      )

      // 本地判断是否正确
      const correctIndex = this.correctAnswerMap[this.currentQuestion.id]
      const isCorrect = correctIndex !== undefined
        ? this.selectedAnswer === correctIndex
        : null  // 无答案信息时不判断

      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: this.selectedAnswer,
        time_spent: timeSpent
      })

      this.showFeedbackAnim(isCorrect)
    },

    showFeedbackAnim(correct) {
      // correct: true=答对, false=答错, null=无法判断(中性)
      this.lastCorrect = correct
      this.showFeedback = true
      setTimeout(() => {
        this.showFeedback = false
        this.nextQuestion()
      }, 800)
    },

    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.selectedAnswer = null
        this.startTimer()
      } else {
        this.submitResults()
      }
    },

    async submitResults() {
      this.showResult = true
      this.clearTimer()
      try {
        await submitScreening({
          screening_id: this.screeningId,
          answers: this.answers
        })

        // 如果有待完成的训练任务，自动标记完成
        const pendingTaskId = uni.getStorageSync('pending_task_id')
        if (pendingTaskId) {
          try {
            await completeTask(pendingTaskId)
          } catch (e) {
            console.warn('标记任务完成失败', e)
          }
          uni.removeStorageSync('pending_task_id')
        }

        uni.removeStorageSync('current_screening')
        uni.redirectTo({ url: '/pages/child/reward/index' })
      } catch (e) {
        console.error('提交失败', e)
        uni.showToast({ title: '提交失败，请重试', icon: 'none' })
        this.showResult = false
      }
    },

    playAudio() {
      const text = this.currentQuestion?.instruction || this.currentQuestion?.title
      if (!text) return
      // H5 环境
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        window.speechSynthesis.cancel()
        const utter = new window.SpeechSynthesisUtterance(text)
        utter.lang = 'zh-CN'
        utter.rate = 0.85
        window.speechSynthesis.speak(utter)
        return
      }
      // 微信小程序
      if (uni.textToSpeech) {
        uni.textToSpeech({
          lang: 'zh_CN',
          tts: true,
          content: text,
          fail: () => uni.showToast({ title: text, icon: 'none', duration: 2000 })
        })
      } else {
        uni.showToast({ title: text, icon: 'none', duration: 2000 })
      }
    },

    exitGame() {
      this.showExitModal = true
    },
    hideModal() {
      this.showExitModal = false
    },
    confirmExit() {
      this.clearTimer()
      uni.redirectTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
  display: flex;
  flex-direction: column;
}

/* 游戏顶部 */
.game-header {
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  border-radius: 0 0 48rpx 48rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.exit-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  flex-shrink: 0;
}
.exit-btn .ph { font-size: 40rpx; color: #9CA3AF; }

.progress-section { flex: 1; }

.progress-track {
  height: 20rpx;
  background: #F3F4F6;
  border-radius: 10rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6, #10B981);
  border-radius: 10rpx;
  transition: width 0.4s ease;
}

.progress-text {
  font-size: 24rpx;
  font-weight: 700;
  color: #6B7280;
  text-align: center;
}

.timer-badge {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #F3F4F6;
  padding: 12rpx 20rpx;
  border-radius: 50rpx;
  font-size: 26rpx;
  font-weight: 700;
  color: #6B7280;
  flex-shrink: 0;
  transition: all 0.3s;
}
.timer-badge .ph { font-size: 28rpx; }
.timer-badge.warning {
  background: #FEF2F2;
  color: #EF4444;
  animation: pulse 0.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

/* 加载 */
.loading-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
}
.loading-icon .ph { font-size: 80rpx; color: #3B82F6; }
.loading-text { font-size: 28rpx; color: #9CA3AF; }

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 游戏内容 */
.game-content {
  flex: 1;
  padding: 48rpx 48rpx 0;
  display: flex;
  flex-direction: column;
}

.question-area {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.question-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.audio-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}
.audio-btn .ph { font-size: 36rpx; color: #3B82F6; }

.question-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #374151;
}

.question-instruction {
  font-size: 30rpx;
  color: #6B7280;
  text-align: center;
  margin-bottom: 56rpx;
  line-height: 1.6;
  padding: 0 16rpx;
}

/* 视觉辨识：2x2 大字格 */
.options-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32rpx;
  width: 100%;
  max-width: 560rpx;
}

.option-char {
  aspect-ratio: 1;
  background: #FFFFFF;
  border: 4rpx solid #E5E7EB;
  border-radius: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 96rpx;
  font-weight: 700;
  color: #374151;
  transition: all 0.2s;
}
.option-char:active { transform: scale(0.95); }
.option-char.selected { border-color: #3B82F6; background: #EFF6FF; color: #3B82F6; }
.option-char.correct { border-color: #10B981; background: #ECFDF5; color: #10B981; }
.option-char.wrong { border-color: #EF4444; background: #FEF2F2; color: #EF4444; }

/* 拼字/理解：竖向列表 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  width: 100%;
}

.option-item {
  background: #FFFFFF;
  border: 4rpx solid #E5E7EB;
  border-radius: 40rpx;
  padding: 32rpx 40rpx;
  display: flex;
  align-items: center;
  gap: 32rpx;
  transition: all 0.2s;
}
.option-item:active { transform: scale(0.98); }
.option-item.selected { border-color: #3B82F6; background: #EFF6FF; }
.option-item.correct { border-color: #10B981; background: #ECFDF5; }
.option-item.wrong { border-color: #EF4444; background: #FEF2F2; }

.option-label {
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 700;
  color: #9CA3AF;
  flex-shrink: 0;
}
.option-item.selected .option-label { background: #DBEAFE; color: #3B82F6; }
.option-item.correct .option-label { background: #D1FAE5; color: #10B981; }
.option-item.wrong .option-label { background: #FEE2E2; color: #EF4444; }

.option-text {
  font-size: 36rpx;
  font-weight: 600;
  color: #374151;
  flex: 1;
}
.option-item.selected .option-text { color: #3B82F6; }
.option-item.correct .option-text { color: #10B981; }
.option-item.wrong .option-text { color: #EF4444; }

/* 答题反馈遮罩 */
.feedback-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.85);
  z-index: 500;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  animation: fadeIn 0.15s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.feedback-icon .ph {
  font-size: 160rpx;
  animation: popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.feedback-icon.correct .ph { color: #10B981; }
.feedback-icon.wrong .ph { color: #EF4444; }
.feedback-icon.neutral .ph { color: #3B82F6; }

@keyframes popIn {
  0% { transform: scale(0.3); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.feedback-text {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
}

/* 底部操作区 */
.bottom-area {
  padding: 32rpx 48rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
}

.next-btn {
  width: 100%;
  background: #E5E7EB;
  color: #9CA3AF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 36rpx;
  font-weight: 700;
  transition: all 0.2s;
}
.next-btn.active {
  background: #3B82F6;
  color: #FFFFFF;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}
.next-btn.active:active { transform: scale(0.97); }

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: #FFFFFF;
  width: 80%;
  max-width: 640rpx;
  border-radius: 64rpx;
  padding: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-icon {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}
.modal-icon.warning { background: #FEF3C7; }
.modal-icon.warning .ph { font-size: 64rpx; color: #F59E0B; }

.modal-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 16rpx;
}

.modal-desc {
  font-size: 26rpx;
  color: #9CA3AF;
  text-align: center;
  margin-bottom: 40rpx;
}

.modal-btn {
  width: 100%;
  border-radius: 48rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  margin-bottom: 24rpx;
}
.modal-btn.outline { background: #FFFFFF; border: 4rpx solid #E5E7EB; color: #6B7280; }
.modal-btn.primary { background: #3B82F6; color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2); }
</style>
