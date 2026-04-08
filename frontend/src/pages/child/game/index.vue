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
    </view>

    <!-- 游戏核心区域 -->
    <view class="game-content">
      <view class="question-area" v-if="currentQuestion">
        <view class="question-header">
          <button class="audio-btn" @click="playAudio">
            <text class="ph ph-speaker-high"></text>
          </button>
          <view class="question-title">{{ currentQuestion.title }}</view>
        </view>
        <view class="question-instruction">{{ currentQuestion.instruction }}</view>

        <!-- 选项区域 -->
        <view class="options-area" :class="currentQuestion.type === 'visual' ? 'grid' : 'list'">
          <view
            v-for="(option, index) in currentQuestion.options"
            :key="index"
            :class="['option-card', { selected: selectedAnswer === index }]"
            @click="selectAnswer(index)"
          >
            {{ option }}
          </view>
        </view>
      </view>
    </view>

    <!-- 底部操作区 -->
    <view class="bottom-area">
      <button
        :class="['next-btn', { active: selectedAnswer !== null }]"
        @click="confirmAnswer"
        :disabled="selectedAnswer === null"
      >
        选好了
      </button>
    </view>

    <!-- 退出确认弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click="hideModal">
      <view class="modal-content" @click.stop>
        <view class="modal-icon">
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
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      gameType: 'visual',
      questions: [],
      currentIndex: 0,
      selectedAnswer: null,
      answers: [],
      child: null,
      screeningId: null,
      showExitModal: false,
      questionStartTime: null
    }
  },
  computed: {
    currentQuestion() {
      return this.questions[this.currentIndex]
    },
    progressPercent() {
      if (this.questions.length === 0) return 0
      return ((this.currentIndex) / this.questions.length) * 100
    }
  },
  onLoad() {
    this.child = getCurrentChild()
    this.loadScreening()
  },
  methods: {
    async loadScreening() {
      const screeningInfo = uni.getStorageSync('current_screening')
      if (screeningInfo) {
        this.screeningId = screeningInfo.id
        this.gameType = screeningInfo.game_type
      } else {
        try {
          const child = getCurrentChild()
          if (!child) {
            uni.showToast({ title: '请先选择孩子', icon: 'none' })
            return
          }
          const res = await startScreening({
            child_id: child.id,
            game_type: 'visual'
          })
          this.screeningId = res.id
          this.gameType = 'visual'
        } catch (e) {
          console.error('启动筛查失败', e)
          return
        }
      }
      this.loadQuestions()
    },
    async loadQuestions() {
      try {
        const res = await getQuestions(this.gameType, 'L1', 10)
        this.questions = res.questions
        this.questionStartTime = Date.now()
      } catch (e) {
        console.error('加载题目失败', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    selectAnswer(index) {
      this.selectedAnswer = index
    },
    playAudio() {
      // 实际开发中调用 audio.play()
      uni.showToast({ title: '播放音频', icon: 'none' })
    },
    confirmAnswer() {
      if (this.selectedAnswer === null) return

      const timeSpent = Math.round((Date.now() - this.questionStartTime) / 1000)

      this.answers.push({
        question_id: this.currentQuestion.id,
        answer: this.selectedAnswer,
        time_spent: timeSpent
      })

      if (this.currentIndex < this.questions.length - 1) {
        this.currentIndex++
        this.selectedAnswer = null
        this.questionStartTime = Date.now()
      } else {
        this.submitResults()
      }
    },
    async submitResults() {
      try {
        await submitScreening({
          screening_id: this.screeningId,
          answers: this.answers
        })

        uni.showToast({ title: '完成啦！', icon: 'success' })
        setTimeout(() => {
          uni.redirectTo({ url: '/pages/child/reward/index' })
        }, 1000)
      } catch (e) {
        console.error('提交失败', e)
        uni.showToast({ title: '提交失败', icon: 'none' })
      }
    },
    exitGame() {
      this.showExitModal = true
    },
    hideModal() {
      this.showExitModal = false
    },
    confirmExit() {
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
  gap: 32rpx;
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
}

.exit-btn .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

.progress-section {
  flex: 1;
}

.progress-track {
  height: 24rpx;
  background: #F3F4F6;
  border-radius: 12rpx;
  overflow: hidden;
  margin-bottom: 8rpx;
}

.progress-fill {
  height: 100%;
  background: #10B981;
  border-radius: 12rpx;
  transition: width 0.5s;
}

.progress-text {
  font-size: 26rpx;
  font-weight: 700;
  color: #3B82F6;
  text-align: center;
}

/* 游戏核心区域 */
.game-content {
  flex: 1;
  padding: 64rpx 48rpx;
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
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.audio-btn .ph {
  font-size: 32rpx;
  color: #3B82F6;
}

.question-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
}

.question-instruction {
  font-size: 28rpx;
  color: #9CA3AF;
  text-align: center;
  margin-bottom: 64rpx;
}

/* 选项区域 */
.options-area {
  width: 100%;
  max-width: 560rpx;
}

.options-area.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32rpx;
}

.options-area.list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.option-card {
  background: #FFFFFF;
  border: 4rpx solid #E5E7EB;
  border-radius: 48rpx;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.options-area.grid .option-card {
  aspect-ratio: 1;
  font-size: 100rpx;
  font-weight: 700;
}

.options-area.list .option-card {
  padding: 40rpx;
  font-size: 48rpx;
  font-weight: 700;
}

.option-card.selected {
  border-color: #3B82F6;
  background: #EFF6FF;
  color: #3B82F6;
}

/* 底部操作区 */
.bottom-area {
  padding: 32rpx 48rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  background: #F9FAFB;
}

.next-btn {
  width: 100%;
  background: #E5E7EB;
  color: #9CA3AF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
}

.next-btn.active {
  background: #3B82F6;
  color: #FFFFFF;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
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
  background: #FEF2F2;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.modal-icon .ph {
  font-size: 64rpx;
  color: #EF4444;
}

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

.modal-btn.outline {
  background: #FFFFFF;
  border: 4rpx solid #E5E7EB;
  color: #6B7280;
}

.modal-btn.primary {
  background: #3B82F6;
  color: #FFFFFF;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}
</style>
