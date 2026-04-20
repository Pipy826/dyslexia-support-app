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
      <view class="question-area">
        <view class="question-header">
          <button class="audio-btn" @click="playAudio">
            <text class="ph ph-speaker-high"></text>
          </button>
          <view class="question-title">{{ currentQuestion.title }}</view>
        </view>
        <view class="question-instruction">{{ currentQuestion.instruction }}</view>

        <!-- 文字理解题：支持重复阅读（记录次数） -->
        <view class="reread-bar" v-if="currentQuestion.type === 'reading_comprehension' && rereadCount > 0">
          <text class="ph ph-eye"></text> 已重读 {{ rereadCount }} 次
        </view>

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

        <!-- 工作记忆序列：突出显示序列内容 -->
        <view class="options-list" v-else-if="currentQuestion.type === 'working_memory_sequence'">
          <view
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            :class="['option-item', 'option-sequence', getOptionClass(index)]"
            @click="selectAnswer(index)"
          >
            <view class="option-label">{{ ['A','B','C','D'][index] }}</view>
            <view class="option-text">{{ option }}</view>
          </view>
        </view>

        <!-- 排序题型：点击上移/下移调整顺序 -->
        <view class="sort-container" v-else-if="currentQuestion.type === 'sort_order'">
          <view class="sort-item" v-for="(item, idx) in sortItems" :key="item.originalIndex">
            <view class="sort-num">{{ idx + 1 }}</view>
            <view class="sort-text">{{ item.text }}</view>
            <view class="sort-btns">
              <view class="sort-btn" :class="{ disabled: idx === 0 }" @click="moveUp(idx)">↑</view>
              <view class="sort-btn" :class="{ disabled: idx === sortItems.length - 1 }" @click="moveDown(idx)">↓</view>
            </view>
          </view>
          <button class="confirm-sort-btn" @click="confirmSortAnswer">确认顺序 ✓</button>
        </view>

        <!-- 其他题型：竖向列表 -->
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
        {{ lastCorrect === true ? '答对了！🎉' : lastCorrect === false ? '加油，继续！' : '下一题' }}
      </view>
      <!-- 答错时显示正确答案 -->
      <view class="feedback-correct" v-if="lastCorrect === false && currentCorrectAnswer">
        正确答案：<text class="feedback-answer">{{ currentCorrectAnswer }}</text>
      </view>
    </view>

    <!-- 难度调整提示 -->
    <view class="difficulty-toast" v-if="showDifficultyToast">
      <text class="ph ph-sparkle"></text>
      {{ difficultyToastText }}
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
import { evaluateAdaptiveDifficulty } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      gameType: 'visual',
      difficulty: 'L1',
      grade: '',          // 孩子年级，用于后端难度映射
      questions: [],
      currentIndex: 0,
      selectedAnswer: null,
      answers: [],
      child: null,
      screeningId: null,
      showExitModal: false,
      showFeedback: false,
      lastCorrect: false,
      currentCorrectAnswer: '',
      // 行为数据采集
      questionStartTime: null,
      firstClickTime: null,
      changeCount: 0,
      rereadCount: 0,   // 文字理解题：重复阅读次数
      timeLeft: 10,
      timerInterval: null,
      loading: true,
      showResult: false,
      correctAnswerMap: {},
      // 自适应难度
      adaptiveCheckInterval: 5,  // 每5题检查一次
      difficultyLevels: ['L1', 'L2', 'L3'],
      showDifficultyToast: false,
      difficultyToastText: '',
      difficultyOverridden: false,  // true 表示自适应已手动覆盖 grade 映射
      currentTimeLimit: null,       // 动态时限（null 时回退到题目自带的 time_limit）
      sortItems: [],                // 排序题：当前排列的选项数组，每项含 {text, originalIndex}
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
    if (options.grade) {
      this.grade = options.grade
    } else if (this.child?.grade) {
      this.grade = this.child.grade
    }
    this.initScreening()
  },
  onUnload() {
    this.clearTimer()
  },
  // 拦截手势返回，弹出退出确认
  onBackPress() {
    this.showExitModal = true
    return true
  },
  methods: {
    async initScreening() {
      this.loading = true
      try {
        const saved = uni.getStorageSync('current_screening')
        if (saved && saved.game_type === this.gameType) {
          this.screeningId = saved.id
          this.gameType = saved.game_type
          this.difficulty = saved.difficulty || 'L1'
          await this.loadQuestions()
          // 断点续传：恢复已答进度
          if (saved.currentIndex > 0 && saved.answers && saved.answers.length > 0) {
            this.currentIndex = Math.min(saved.currentIndex, this.questions.length - 1)
            this.answers = saved.answers
            uni.showToast({ title: '已恢复上次进度', icon: 'none', duration: 1500 })
          }
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
        // 首次加载：传 grade 让后端自动映射难度；自适应调难时 difficulty 已更新，直接传
        const options = this.difficultyOverridden
          ? { difficulty: this.difficulty, count: 10 }
          : { grade: this.grade || this.child?.grade, count: 10 }

        const res = await getQuestions(this.gameType, options)
        // 后端返回实际使用的 difficulty，同步到本地（首次加载时尤其重要）
        if (res.difficulty) this.difficulty = res.difficulty

        this.questions = res.questions || []
        // 首次加载：用第一题的 time_limit 初始化动态时限
        if (!this.difficultyOverridden && this.questions.length > 0) {
          this.currentTimeLimit = this.questions[0].time_limit ?? null
        }
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
        this.resetQuestionState()
        this.startTimer()
      } catch (e) {
        console.error('加载题目失败', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
        this.loading = false
      }
    },

    resetQuestionState() {
      this.questionStartTime = Date.now()
      this.firstClickTime = null
      this.changeCount = 0
      this.rereadCount = 0
      // 排序题：随机打乱选项初始化 sortItems
      if (this.currentQuestion?.type === 'sort_order') {
        const items = (this.currentQuestion.options || []).map((text, i) => ({ text, originalIndex: i }))
        // Fisher-Yates 洗牌
        for (let i = items.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [items[i], items[j]] = [items[j], items[i]]
        }
        this.sortItems = items
      } else {
        this.sortItems = []
      }
    },

    startTimer() {
      this.clearTimer()
      const q = this.currentQuestion
      // 优先用动态时限，回退到题目自带的 time_limit；用 || 而非 ?? 以过滤 0 值
      this.timeLeft = q?.type === 'sort_order' ? 30 : (this.currentTimeLimit || q?.time_limit || 10)
      this.timerInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this.clearTimer()
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
      // 超时时 time_spent = 实际动态时限，Math.round 保证传 int（pydantic 要求）
      const timeSpent = Math.round(this.currentTimeLimit || this.currentQuestion?.time_limit || 10)
      // 排序题超时：提交当前顺序
      if (this.currentQuestion?.type === 'sort_order') {
        const currentOrder = this.sortItems.map(item => item.originalIndex)
        const correctOrder = this.currentQuestion.correct_order || []
        const isCorrect = JSON.stringify(currentOrder) === JSON.stringify(correctOrder)
        this.answers.push({
          question_id: this.currentQuestion.id,
          answer: currentOrder,
          time_spent: 30,
          reaction_time: null,
          change_count: this.changeCount,
          is_timeout: true
        })
        this.showFeedbackAnim(isCorrect)
        return
      }
      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: -1,
        time_spent: timeSpent,
        reaction_time: null,
        change_count: this.changeCount,
        is_timeout: true
      })
      this.showFeedbackAnim(false)
      this.nextQuestion()
    },

    moveUp(index) {
      if (index === 0) return
      const items = [...this.sortItems];
      [items[index - 1], items[index]] = [items[index], items[index - 1]]
      this.sortItems = items
    },

    moveDown(index) {
      if (index === this.sortItems.length - 1) return
      const items = [...this.sortItems];
      [items[index], items[index + 1]] = [items[index + 1], items[index]]
      this.sortItems = items
    },

    confirmSortAnswer() {
      if (this.showFeedback) return
      this.clearTimer()
      const currentOrder = this.sortItems.map(item => item.originalIndex)
      const correctOrder = this.currentQuestion.correct_order || []
      const isCorrect = JSON.stringify(currentOrder) === JSON.stringify(correctOrder)
      const timeSpent = Math.round(30 - this.timeLeft)
      const reactionTime = this.firstClickTime ? this.firstClickTime - this.questionStartTime : null
      if (!isCorrect && correctOrder.length > 0) {
        this.currentCorrectAnswer = correctOrder.map(i => this.currentQuestion.options[i]).join(' → ')
      } else {
        this.currentCorrectAnswer = ''
      }
      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: currentOrder,
        time_spent: timeSpent,
        reaction_time: reactionTime,
        change_count: this.changeCount,
        is_timeout: false
      })
      this.showFeedbackAnim(isCorrect)
    },

    selectAnswer(index) {
      // 反馈动画期间不响应点击
      if (this.showFeedback) return

      // 记录首次点击时间（reaction_time）
      if (this.firstClickTime === null) {
        this.firstClickTime = Date.now()
      }

      this.selectedAnswer = index
      // 选中即立刻提交
      this.confirmAnswer()
    },

    getOptionClass(index) {
      if (this.showFeedback) {
        const correctIndex = this.correctAnswerMap[this.currentQuestion?.id]
        if (correctIndex !== undefined) {
          if (index === correctIndex) return 'correct'
          if (index === this.selectedAnswer) return 'wrong'
        } else {
          if (index === this.selectedAnswer) return this.lastCorrect ? 'correct' : 'wrong'
        }
        return ''
      }
      return this.selectedAnswer === index ? 'selected' : ''
    },

    confirmAnswer() {
      if (this.selectedAnswer === null || this.showFeedback) return
      this.clearTimer()  // 倒计时作废

      const timeSpent = Math.round((this.currentTimeLimit ?? this.currentQuestion?.time_limit ?? 10) - this.timeLeft)
      const correctIndex = this.correctAnswerMap[this.currentQuestion.id]
      const isCorrect = correctIndex !== undefined ? this.selectedAnswer === correctIndex : null
      const reactionTime = this.firstClickTime ? this.firstClickTime - this.questionStartTime : null

      // 答错时记录正确答案文本，用于反馈展示
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
        change_count: this.changeCount,
        is_timeout: false,
        reread_count: this.rereadCount,
      })

      this.showFeedbackAnim(isCorrect)
    },

    showFeedbackAnim(correct) {
      this.lastCorrect = correct
      this.showFeedback = true
      // 答对600ms，答错1200ms（让孩子看清正确答案）
      const delay = correct === true ? 600 : 1200
      setTimeout(() => {
        this.showFeedback = false
        this.nextQuestion()
      }, delay)
    },

    nextQuestion() {
      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.selectedAnswer = null
        this.resetQuestionState()
        this.startTimer()
        // 保存断点进度
        const saved = uni.getStorageSync('current_screening') || {}
        uni.setStorageSync('current_screening', {
          ...saved,
          currentIndex: this.currentIndex,
          answers: this.answers,
        })
        // 每 adaptiveCheckInterval 题检查一次难度
        if (this.currentIndex % this.adaptiveCheckInterval === 0 && this.currentIndex > 0) {
          this.checkAdaptiveDifficulty()
        }
      } else {
        this.submitResults()
      }
    },

    async checkAdaptiveDifficulty() {
      // 取最近 adaptiveCheckInterval 条答题记录
      const recent = this.answers.slice(-this.adaptiveCheckInterval)
      if (recent.length < 3) return

      try {
        const result = await evaluateAdaptiveDifficulty({
          game_type: this.gameType,
          current_difficulty: this.difficulty,
          recent_answers: recent,
          current_time_limit: this.currentTimeLimit,
          grade: this.grade || this.child?.grade || null,
        })

        if (!result.should_adjust) return

        // 更新动态时限（无论是否换难度都要更新）
        if (result.new_time_limit != null) {
          this.currentTimeLimit = result.new_time_limit
        }

        if (result.difficulty_changed) {
          this.difficulty = result.new_difficulty
          this.difficultyOverridden = true
          if (result.direction === 'up') {
            this.showDifficultyHint('难度提升了！你真棒 🚀')
          } else {
            this.showDifficultyHint('换个简单一点的试试 💪')
          }
          await this.appendQuestions()
        } else {
          // 只调时限，不换题
          if (result.direction === 'up') {
            this.showDifficultyHint('节奏加快啦，继续冲！⚡')
          }
          // 放宽时限不提示，避免打击孩子信心
        }
      } catch (e) {
        // 静默失败，不影响游戏
      }
    },

    async appendQuestions() {
      try {
        // 自适应调难追加题目：明确传 difficulty，标记已手动覆盖
        this.difficultyOverridden = true
        const res = await getQuestions(this.gameType, { difficulty: this.difficulty, count: 5 })
        const newQs = (res.questions || []).filter(
          q => !this.questions.find(existing => existing.id === q.id)
        )
        newQs.forEach(q => {
          if (q.correct_index !== undefined) {
            this.correctAnswerMap[q.id] = q.correct_index
          }
        })
        this.questions = [...this.questions, ...newQs]
      } catch (e) {
        // 静默失败
      }
    },

    showDifficultyHint(text) {
      this.difficultyToastText = text
      this.showDifficultyToast = true
      setTimeout(() => {
        this.showDifficultyToast = false
      }, 2000)
    },

    async submitResults() {
      this.showResult = true
      this.clearTimer()
      try {
        const res = await submitScreening({
          screening_id: this.screeningId,
          answers: this.answers
        })

        // 筛查完成后也给一颗星星（通过创建并立即完成一个临时任务）
        const pendingTaskId = uni.getStorageSync('pending_task_id')
        if (pendingTaskId) {
          try { await completeTask(pendingTaskId) } catch (e) { console.warn('标记任务完成失败', e) }
          uni.removeStorageSync('pending_task_id')
        } else if (this.child?.id) {
          // 筛查本身也奖励一颗星
          try {
            const { createTask, completeTask: ct } = await import('../../../api/training.js')
            const today = new Date().toISOString().split('T')[0]
            const task = await createTask({
              child_id: this.child.id,
              task_type: this.gameType,
              task_name: '完成筛查挑战',
              scheduled_date: today,
            })
            await ct(task.id)
          } catch (e) { /* 静默失败，不影响主流程 */ }
        }

        // 保存游戏结果供奖励页面使用（AI鼓励话语）
        const correctCount = this.answers.filter(a => {
          const correctIdx = this.correctAnswerMap[a.question_id]
          return correctIdx !== undefined && a.answer === correctIdx
        }).length
        uni.setStorageSync('last_game_result', {
          game_type: this.gameType,
          score: res.score || 0,
          correct_count: correctCount,
          total_count: this.answers.length,
          stars: 1,
        })

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
      // 文字理解题：记录重复阅读次数（首次不算，从第2次开始计）
      if (this.currentQuestion?.type === 'reading_comprehension') {
        this.rereadCount++
      }
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
        utter.lang = 'zh-CN'
        utter.rate = 0.85
        window.speechSynthesis.speak(utter)
        return
      }
      uni.showToast({ title: text, icon: 'none', duration: 2000 })
      // #endif
    },

    exitGame() { this.showExitModal = true },
    hideModal() { this.showExitModal = false },
    confirmExit() {
      this.clearTimer()
      uni.redirectTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>

<style scoped>
/* 创意游戏页面 - 沉浸式设计 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

/* 游戏顶部 - 统一风格 */
.game-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.exit-btn {
  width: 72rpx; height: 72rpx;
  display: flex; align-items: center; justify-content: center;
  padding: 0; background: #FFF0F0;
  border-radius: 50%;
  flex-shrink: 0;
  border: 3rpx solid #FFD0D0;
  box-shadow: 0 3rpx 0 #FFB3B3;
  transition: all 0.2s;
}
.exit-btn:active { transform: translateY(3rpx); box-shadow: none; }
.exit-btn .ph { font-size: 36rpx; color: #FF6B6B; }

.progress-section { flex: 1; }
.progress-track {
  height: 24rpx;
  background: #F0F0F0;
  border-radius: 9999rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
  box-shadow: inset 0 2rpx 6rpx rgba(0,0,0,0.08);
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4F9EF8, #A78BFA, #FF9ECD);
  border-radius: 9999rpx;
  transition: width 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}
.progress-fill::after {
  content: '';
  position: absolute;
  top: 0; left: -100%;
  width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);
  animation: shimmer 2s infinite;
}
@keyframes shimmer { 0% { left: -100%; } 100% { left: 100%; } }
.progress-text { font-size: 24rpx; font-weight: 800; color: #A0AEC0; text-align: center; }

.timer-badge {
  display: flex; align-items: center; gap: 6rpx;
  background: linear-gradient(135deg, #F0F7FF, #DBEAFE);
  padding: 14rpx 24rpx;
  border-radius: 9999rpx;
  font-size: 28rpx; font-weight: 800; color: #4F9EF8;
  flex-shrink: 0;
  border: 3rpx solid #BFDBFE;
  box-shadow: 0 3rpx 0 #93C5FD;
  transition: all 0.3s;
}
.timer-badge .ph { font-size: 30rpx; }
.timer-badge.warning {
  background: linear-gradient(135deg, #FFF0F0, #FFE4E4);
  color: #FF6B6B;
  border-color: #FFB3B3;
  box-shadow: 0 3rpx 0 #FF8080;
  animation: pulse 0.5s infinite;
}
@keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.08); } }

/* 加载中 */
.loading-area { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24rpx; }
.loading-icon .ph { font-size: 80rpx; color: #4F9EF8; }
.loading-text { font-size: 30rpx; color: #A0AEC0; font-weight: 700; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 游戏内容区 */
.game-content { flex: 1; padding: 48rpx 48rpx 0; display: flex; flex-direction: column; }
.question-area { display: flex; flex-direction: column; align-items: center; }
.question-header { display: flex; align-items: center; gap: 16rpx; margin-bottom: 16rpx; }

.audio-btn {
  width: 80rpx; height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  padding: 0; flex-shrink: 0;
  border: 3rpx solid #BFDBFE;
  box-shadow: 0 4rpx 0 #93C5FD;
  transition: all 0.2s;
}
.audio-btn:active { transform: translateY(4rpx); box-shadow: none; }
.audio-btn .ph { font-size: 40rpx; color: #4F9EF8; }

.question-title { font-size: 44rpx; font-weight: 900; color: #2D3748; letter-spacing: 1rpx; }
.question-instruction {
  font-size: 30rpx; color: #718096;
  text-align: center; margin-bottom: 56rpx;
  line-height: 1.7; padding: 0 16rpx;
  font-weight: 600;
}

/* 视觉辨识选项 - 2x2 紧凑网格 */
.options-grid { display: flex; flex-wrap: wrap; gap: 16rpx; width: 100%; }
.option-char {
  width: calc(50% - 8rpx);
  height: 160rpx;
  background: #FFFFFF;
  border: 3rpx solid #E5E7EB;
  border-radius: 24rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 64rpx; font-weight: 800; color: #2D3748;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  box-sizing: border-box;
}
.option-char:active { transform: scale(0.95); }
.option-char.selected {
  border-color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  box-shadow: 0 4rpx 16rpx rgba(79, 158, 248, 0.2);
}
.option-char.correct {
  border-color: #22C55E;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  color: #22C55E;
}
.option-char.wrong {
  border-color: #FF6B6B;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  color: #FF6B6B;
}

/* 列表选项 - 圆润卡片 */
.options-list { display: flex; flex-direction: column; gap: 24rpx; width: 100%; }
.option-item {
  background: #FFFFFF;
  border: 5rpx solid #E5E7EB;
  border-radius: 48rpx;
  padding: 32rpx 40rpx;
  display: flex; align-items: center; gap: 32rpx;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 5rpx 0 #E5E7EB, 0 8rpx 20rpx rgba(0,0,0,0.05);
}
.option-item:active { transform: scale(0.97) translateY(5rpx); box-shadow: 0 1rpx 0 #E5E7EB; }
.option-item.selected {
  border-color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  box-shadow: 0 5rpx 0 #93C5FD, 0 8rpx 20rpx rgba(79, 158, 248, 0.2);
}
.option-item.correct {
  border-color: #22C55E;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  box-shadow: 0 5rpx 0 #86EFAC, 0 8rpx 20rpx rgba(34, 197, 94, 0.2);
}
.option-item.wrong {
  border-color: #FF6B6B;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  box-shadow: 0 5rpx 0 #FCA5A5, 0 8rpx 20rpx rgba(255, 107, 107, 0.2);
}
.option-label {
  width: 60rpx; height: 60rpx;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex; align-items: center; justify-content: center;
  font-size: 28rpx; font-weight: 800; color: #A0AEC0;
  flex-shrink: 0;
}
.option-item.selected .option-label { background: #DBEAFE; color: #4F9EF8; }
.option-item.correct .option-label { background: #DCFCE7; color: #22C55E; }
.option-item.wrong .option-label { background: #FFE4E4; color: #FF6B6B; }
.option-text { font-size: 36rpx; font-weight: 700; color: #2D3748; flex: 1; }
.option-item.selected .option-text { color: #4F9EF8; }
.option-item.correct .option-text { color: #22C55E; }
.option-item.wrong .option-text { color: #FF6B6B; }

/* 答题反馈遮罩 - 大号可爱 */
.feedback-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 254, 249, 0.95);
  z-index: 500;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 24rpx;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.feedback-icon .ph { font-size: 180rpx; animation: popIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.feedback-icon.correct .ph { color: #22C55E; filter: drop-shadow(0 8rpx 16rpx rgba(34, 197, 94, 0.4)); }
.feedback-icon.wrong .ph { color: #FF6B6B; filter: drop-shadow(0 8rpx 16rpx rgba(255, 107, 107, 0.4)); }
.feedback-icon.neutral .ph { color: #4F9EF8; filter: drop-shadow(0 8rpx 16rpx rgba(79, 158, 248, 0.4)); }
@keyframes popIn {
  0% { transform: scale(0.3) rotate(-10deg); opacity: 0; }
  70% { transform: scale(1.15) rotate(5deg); opacity: 1; }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
.feedback-text { font-size: 52rpx; font-weight: 900; color: #2D3748; letter-spacing: 2rpx; }
.feedback-correct { font-size: 28rpx; color: #718096; margin-top: 8rpx; font-weight: 600; }
.feedback-answer { font-size: 36rpx; font-weight: 800; color: #22C55E; }

/* 弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(45, 55, 72, 0.5);
  z-index: 9999;
  display: flex; justify-content: center; align-items: center;
}
.modal-content {
  background: #FFFEF9;
  width: 80%; max-width: 640rpx;
  border-radius: 72rpx;
  padding: 56rpx 48rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 32rpx 80rpx rgba(0,0,0,0.2);
  border: 5rpx solid rgba(255, 255, 255, 0.9);
  position: relative; overflow: hidden;
}
.modal-content::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 10rpx;
  background: linear-gradient(90deg, #4F9EF8, #A78BFA, #FF9ECD, #FFD93D);
}
.modal-icon {
  width: 140rpx; height: 140rpx;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 32rpx;
}
.modal-icon.warning { background: linear-gradient(135deg, #FFF9C4, #FFE082); border: 4rpx solid #FFD54F; }
.modal-icon.warning .ph { font-size: 72rpx; color: #F57F17; }
.modal-title { font-size: 44rpx; font-weight: 900; color: #2D3748; margin-bottom: 16rpx; }
.modal-desc { font-size: 28rpx; color: #A0AEC0; text-align: center; margin-bottom: 40rpx; font-weight: 600; line-height: 1.6; }
.modal-btn {
  width: 100%; border-radius: 9999rpx;
  padding: 32rpx; font-size: 30rpx; font-weight: 800;
  margin-bottom: 24rpx; letter-spacing: 1rpx;
}
.modal-btn.outline {
  background: #FFFFFF;
  border: 4rpx solid #E5E7EB;
  color: #A0AEC0;
  box-shadow: 0 4rpx 0 #E5E7EB;
}
.modal-btn.primary {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  box-shadow: 0 6rpx 0 #2563EB, 0 8rpx 24rpx rgba(59, 130, 246, 0.35);
}

/* 难度调整提示 - 可爱气泡 */
.difficulty-toast {
  position: fixed;
  top: 200rpx; left: 50%;
  transform: translateX(-50%);
  background: linear-gradient(135deg, #2D3748, #4A5568);
  color: #FFFFFF;
  padding: 24rpx 48rpx;
  border-radius: 9999rpx;
  font-size: 30rpx; font-weight: 800;
  display: flex; align-items: center; gap: 12rpx;
  z-index: 1000;
  animation: toastIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  white-space: nowrap;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.2);
}
.difficulty-toast .ph { font-size: 32rpx; color: #FFD93D; }
@keyframes toastIn {
  from { opacity: 0; transform: translateX(-50%) translateY(-30rpx) scale(0.8); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}

/* 重复阅读提示 */
.reread-bar {
  display: flex; align-items: center; gap: 8rpx;
  background: rgba(79, 158, 248, 0.08);
  border: 1rpx solid #BFDBFE;
  border-radius: 12rpx;
  padding: 8rpx 20rpx;
  font-size: 22rpx; color: #4F9EF8; font-weight: 600;
  margin-bottom: 16rpx;
}
.reread-bar .ph { font-size: 22rpx; }

/* 排序题型 */
.sort-container { width: 100%; display: flex; flex-direction: column; gap: 16rpx; }
.sort-item { background: #FFFFFF; border: 3rpx solid #E5E7EB; border-radius: 20rpx; padding: 24rpx 20rpx; display: flex; align-items: center; gap: 16rpx; transition: all 0.2s; }
.sort-num { width: 48rpx; height: 48rpx; border-radius: 50%; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); display: flex; align-items: center; justify-content: center; font-size: 24rpx; font-weight: 800; color: #4F9EF8; flex-shrink: 0; }
.sort-text { flex: 1; font-size: 30rpx; font-weight: 700; color: #2D3748; line-height: 1.5; }
.sort-btns { display: flex; flex-direction: column; gap: 8rpx; flex-shrink: 0; }
.sort-btn { width: 52rpx; height: 52rpx; border-radius: 12rpx; background: #F5F7FA; border: 2rpx solid #E5E7EB; display: flex; align-items: center; justify-content: center; font-size: 24rpx; color: #4F9EF8; font-weight: 800; transition: all 0.2s; }
.sort-btn:active { background: #DBEAFE; transform: scale(0.92); }
.sort-btn.disabled { color: #D1D5DB; background: #F9FAFB; }
.confirm-sort-btn { width: 100%; background: linear-gradient(135deg, #22C55E, #16A34A); color: #FFFFFF; border-radius: 20rpx; padding: 28rpx; font-size: 30rpx; font-weight: 800; margin-top: 8rpx; box-shadow: 0 4rpx 12rpx rgba(34,197,94,0.3); }
</style>
