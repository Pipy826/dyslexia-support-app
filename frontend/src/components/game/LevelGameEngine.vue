<template>
  <view class="level-engine" :style="{ '--primary': gameColor }">

    <!-- 加载中 -->
    <view class="loading-area" v-if="loading">
      <!-- 顶部栏（加载状态也显示返回按钮） -->
      <view class="level-header loading-header">
        <view class="level-info-row">
          <view class="back-btn" @click="handleBackToLevels">
            <text class="ph ph-caret-left"></text>
          </view>
          <view class="level-tag">加载中...</view>
          <view class="header-placeholder"></view>
        </view>
      </view>
      <view class="loading-body">
        <text class="ph ph-circle-notch spin loading-icon"></text>
        <view class="loading-text">关卡加载中...</view>
      </view>
    </view>

    <!-- 错误 -->
    <view class="error-area" v-else-if="error">
      <!-- 顶部栏（错误状态也显示返回按钮） -->
      <view class="level-header error-header">
        <view class="level-info-row">
          <view class="back-btn" @click="handleBackToLevels">
            <text class="ph ph-caret-left"></text>
          </view>
          <view class="level-tag">加载失败</view>
          <view class="header-placeholder"></view>
        </view>
      </view>
      <view class="error-body">
        <text class="ph ph-warning-circle error-icon"></text>
        <view class="error-text">{{ error }}</view>
        <view class="retry-btn" @click="loadLevelData">重试</view>
      </view>
    </view>

    <!-- 游戏进行中 -->
    <view class="game-area" v-else-if="levelData && !showResult">

      <!-- 顶部进度条 -->
      <view class="level-header" :style="{ background: gameGradient }">
        <view class="level-info-row">
          <view class="back-btn" @click="handleBackClick">
            <text class="ph ph-caret-left"></text>
          </view>
          <view class="level-title-area">
            <text :class="'ph ' + gameIcon + ' level-game-icon'"></text>
            <view class="level-tag">{{ levelData.title }}</view>
          </view>
          <view class="progress-text">第 {{ currentIndex + 1 }} 题 / 共 {{ effectiveTotal }} 题</view>
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
      </view>

      <!-- 题目区域 -->
      <view class="question-wrapper" v-if="currentQuestion">

        <!-- 题型标签 -->
        <view class="type-badge-row">
          <view class="question-type-badge">{{ questionTypeName }}</view>
        </view>

        <!-- ① 选择题：visual_discrimination / spelling_recognition / reading_comprehension
                      working_memory_sequence / rapid_naming_choice / spatial_judgment -->
        <view class="question-card" v-if="isChoiceType">
          <view class="question-header-row">
            <view class="question-title">{{ currentQuestion.title }}</view>
          </view>
          <view class="question-instruction">{{ currentQuestion.instruction }}</view>

          <!-- 视觉辨识：2×2 大字格 -->
          <view :class="['options-grid', { shake: shaking }]"
                v-if="currentQuestion.type === 'visual_discrimination'">
            <view
              v-for="(opt, i) in currentQuestion.options" :key="i"
              :class="['option-char', getChoiceClass(i)]"
              @click="handleChoiceAnswer(i)"
            >{{ opt }}</view>
          </view>

          <!-- 其他选择题：竖向列表 -->
          <view :class="['options-list', { shake: shaking }]" v-else>
            <view
              v-for="(opt, i) in currentQuestion.options" :key="i"
              :class="['option-item', getChoiceClass(i)]"
              @click="handleChoiceAnswer(i)"
            >
              <view class="option-label">{{ ['A','B','C','D'][i] }}</view>
              <view class="option-text">{{ opt }}</view>
            </view>
          </view>
        </view>

        <!-- ② 拖拽排序：sort_order -->
        <view class="question-card" v-else-if="currentQuestion.type === 'sort_order'">
          <view class="question-header-row">
            <view class="question-title">{{ currentQuestion.title }}</view>
          </view>
          <view class="question-instruction">{{ currentQuestion.instruction }}</view>
          <DragSort
            :key="'sort_' + currentIndex"
            :items="sortItems"
            @confirm="handleSortAnswer"
          />
        </view>

        <!-- ③ 圈出错字：multi_select_error -->
        <MultiSelectQuestion
          v-else-if="currentQuestion.type === 'multi_select_error'"
          :key="'ms_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ④ 拼音拼写：pinyin_spelling -->
        <PinyinSpellingQuestion
          v-else-if="currentQuestion.type === 'pinyin_spelling'"
          :key="'ps_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑤ 判断对错：true_false -->
        <TrueFalseQuestion
          v-else-if="currentQuestion.type === 'true_false'"
          :key="'tf_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑥ 点击序列复现：sequence_click -->
        <SequenceClickQuestion
          v-else-if="currentQuestion.type === 'sequence_click'"
          :key="'sc_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑦ 计时点击：timed_click -->
        <TimedClickQuestion
          v-else-if="currentQuestion.type === 'timed_click'"
          :key="'tc_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
          @skip-question="handleSkipQuestion"
        />

        <!-- ⑧ 路径描绘：path_draw -->
        <PathDrawQuestion
          v-else-if="currentQuestion.type === 'path_draw'"
          :key="'pd_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑨ 翻牌配对：flip_card_match -->
        <FlipCardQuestion
          v-else-if="currentQuestion.type === 'flip_card_match'"
          :key="'fc_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑩ 连线配对：connect_pairs -->
        <ConnectPairsQuestion
          v-else-if="currentQuestion.type === 'connect_pairs'"
          :key="'cp_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- ⑪ 手写描摹：handwriting_trace -->
        <HandwritingQuestion
          v-else-if="currentQuestion.type === 'handwriting_trace'"
          :key="'hw_' + currentIndex"
          :question="currentQuestion"
          @answer-submitted="handleComponentAnswer"
        />

        <!-- 未知题型兜底 -->
        <view class="question-card unknown-type" v-else>
          <view class="question-title">{{ currentQuestion.title }}</view>
          <view class="question-instruction">{{ currentQuestion.instruction }}</view>
          <view class="unknown-hint">暂不支持该题型，已自动跳过</view>
          <view class="skip-btn" @click="handleSkipQuestion">跳过</view>
        </view>

      </view>
    </view>

    <!-- 选择题答题反馈遮罩（仅选择题使用，其他题型组件内部处理） -->
    <view class="feedback-overlay" v-if="showChoiceFeedback">
      <view :class="['feedback-icon', lastCorrect ? 'correct' : 'wrong']">
        <text :class="lastCorrect ? 'ph ph-check-circle' : 'ph ph-x-circle'"></text>
      </view>
      <view class="feedback-text">{{ lastCorrect ? '答对了！🎉' : '加油，继续！' }}</view>
      <view class="feedback-correct" v-if="!lastCorrect && correctAnswerText">
        正确答案：<text class="feedback-answer">{{ correctAnswerText }}</text>
      </view>
    </view>

    <!-- 结果页 -->
    <view class="result-area" v-if="showResult && result">
      <view class="result-card">
        <view :class="['result-icon', result.passed ? 'passed' : 'failed']">
          <text :class="result.passed ? 'ph ph-trophy' : 'ph ph-smiley-sad'"></text>
        </view>
        <view class="result-title">{{ result.passed ? '关卡通过！🎉' : '再试一次吧！' }}</view>

        <!-- 星星展示 -->
        <view class="stars-row" v-if="result.passed">
          <text
            v-for="n in 3" :key="n"
            :class="['star-icon', n <= result.stars_earned ? 'star-filled' : 'star-empty']"
          >★</text>
        </view>

        <view class="result-stats">
          <view class="stat-item">
            <view class="stat-value">{{ result.correct_count }}</view>
            <view class="stat-label">答对</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-value">{{ result.total_count }}</view>
            <view class="stat-label">总题数</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-value">{{ Math.round(result.accuracy * 100) }}%</view>
            <view class="stat-label">正确率</view>
          </view>
        </view>

        <view class="result-pass-hint" v-if="!result.passed">
          需要 {{ Math.round((levelData.pass_condition?.min_accuracy || 0.7) * 100) }}% 正确率才能通关
        </view>

        <view class="result-btns">
          <view class="result-btn retry" @click="handleRetry">再来一次</view>
          <view class="result-btn back" @click="handleBackToLevels">返回关卡</view>
        </view>
      </view>
    </view>

    <!-- 退出确认弹窗（游戏进行中点返回时显示） -->
    <view class="exit-overlay" v-if="showExitConfirm" @click="showExitConfirm = false">
      <view class="exit-card" @click.stop>
        <view class="exit-icon-wrap">
          <text class="ph ph-warning exit-icon"></text>
        </view>
        <view class="exit-title">要休息一下吗？</view>
        <view class="exit-desc">当前关卡进度不会保存，下次重新开始。</view>
        <view class="exit-btns">
          <view class="exit-btn-item outline" @click="showExitConfirm = false">继续游戏</view>
          <view class="exit-btn-item danger" @click="confirmExit">退出关卡</view>
        </view>
      </view>
    </view>

  </view>
</template>

<script>
import { get } from '@/api'
import { getGameTheme } from '@/utils/gameThemes.js'
import { buildLevelExtraData } from '@/utils/levelScoring.js'
import { GAME_TASK_ICONS } from '@/utils/constants.js'
import DragSort from '@/components/game/DragSort.vue'
import MultiSelectQuestion from '@/components/game/question-types/MultiSelectQuestion.vue'
import PinyinSpellingQuestion from '@/components/game/question-types/PinyinSpellingQuestion.vue'
import TrueFalseQuestion from '@/components/game/question-types/TrueFalseQuestion.vue'
import SequenceClickQuestion from '@/components/game/question-types/SequenceClickQuestion.vue'
import TimedClickQuestion from '@/components/game/question-types/TimedClickQuestion.vue'
import PathDrawQuestion from '@/components/game/question-types/PathDrawQuestion.vue'
import FlipCardQuestion from '@/components/game/question-types/FlipCardQuestion.vue'
import ConnectPairsQuestion from '@/components/game/question-types/ConnectPairsQuestion.vue'
import HandwritingQuestion from '@/components/game/question-types/HandwritingQuestion.vue'

// 使用选择题逻辑的题型
const CHOICE_TYPES = new Set([
  'visual_discrimination',
  'spelling_recognition',
  'reading_comprehension',
  'working_memory_sequence',
  'rapid_naming_choice',
  'spatial_judgment',
])

// 题型中文名
const TYPE_NAMES = {
  visual_discrimination:   '找不同',
  multi_select_error:      '圈出错字',
  spelling_recognition:    '拼音选字',
  pinyin_spelling:         '拼音拼写',
  reading_comprehension:   '选词填空',
  sort_order:              '拖拽排序',
  true_false:              '判断对错',
  working_memory_sequence: '序列选择',
  sequence_click:          '点击复现',
  rapid_naming_choice:     '快速命名',
  timed_click:             '计时点击',
  spatial_judgment:        '空间判断',
  path_draw:               '路径描绘',
  flip_card_match:         '翻牌配对',
  connect_pairs:           '连线配对',
  handwriting_trace:       '手写描摹',
}

export default {
  name: 'LevelGameEngine',
  components: {
    DragSort,
    MultiSelectQuestion,
    PinyinSpellingQuestion,
    TrueFalseQuestion,
    SequenceClickQuestion,
    TimedClickQuestion,
    PathDrawQuestion,
    FlipCardQuestion,
    ConnectPairsQuestion,
    HandwritingQuestion,
  },
  props: {
    levelId: { type: String, required: true },
  },
  emits: ['level-complete', 'retry', 'back-to-levels'],
  data() {
    return {
      levelData: null,
      // currentIndex 指向 questions 数组，跳过的题不计入 answers
      currentIndex: 0,
      answers: [],          // { question_id, type, correct, score }
      skippedCount: 0,      // 被跳过的题数
      startTime: null,
      loading: true,
      error: null,
      showResult: false,
      result: null,
      // 选择题专用反馈状态
      showChoiceFeedback: false,
      lastCorrect: null,
      correctAnswerText: '',
      shaking: false,
      selectedAnswer: null,
      // 退出确认
      showExitConfirm: false,
    }
  },
  computed: {
    currentQuestion() {
      if (!this.levelData?.questions) return null
      return this.levelData.questions[this.currentIndex] || null
    },
    // 实际计入评分的题目总数（排除跳过的）
    effectiveTotal() {
      return (this.levelData?.questions?.length || 0) - this.skippedCount
    },
    progressPercent() {
      const total = this.levelData?.questions?.length || 0
      if (!total) return 0
      return (this.currentIndex / total) * 100
    },
    isChoiceType() {
      return this.currentQuestion && CHOICE_TYPES.has(this.currentQuestion.type)
    },
    gameColor() {
      const theme = getGameTheme(this.levelData?.game_type || 'visual')
      return theme.primary || '#4F9EF8'
    },
    gameGradient() {
      const theme = getGameTheme(this.levelData?.game_type || 'visual')
      return theme.gradient || 'linear-gradient(135deg, #4F9EF8, #3B82F6)'
    },
    gameIcon() {
      const gameType = this.levelData?.game_type || 'visual'
      return GAME_TASK_ICONS[gameType] || 'ph-game-controller'
    },
    questionTypeName() {
      return TYPE_NAMES[this.currentQuestion?.type] || ''
    },
    // sort_order 题目的 options 转成 DragSort 需要的 items 格式
    sortItems() {
      const q = this.currentQuestion
      if (!q || q.type !== 'sort_order') return []
      return (q.options || []).map((content, i) => ({ id: i, content }))
    },
  },
  watch: {
    levelId: {
      immediate: true,
      handler(val) { if (val) this.loadLevelData() },
    },
  },
  methods: {
    // ─── 数据加载 ───────────────────────────────────────────────
    async loadLevelData() {
      this.loading = true
      this.error = null
      this.currentIndex = 0
      this.answers = []
      this.skippedCount = 0
      this.showResult = false
      this.result = null
      this.showChoiceFeedback = false

      // 先尝试本地缓存（离线支持）
      try {
        const cached = uni.getStorageSync(`level_cache_${this.levelId}`)
        if (cached) this.levelData = JSON.parse(cached)
      } catch (e) { /* 忽略 */ }

      try {
        const res = await get(`/api/training/levels/${this.levelId}`)
        this.levelData = res
        uni.setStorageSync(`level_cache_${this.levelId}`, JSON.stringify(res))
        this.startTime = Date.now()
        this.loading = false
      } catch (e) {
        if (this.levelData) {
          // 有缓存，降级使用
          this.startTime = Date.now()
          this.loading = false
        } else {
          this.error = '关卡加载失败，请重试'
          this.loading = false
        }
      }
    },

    // ─── 选择题逻辑 ─────────────────────────────────────────────
    getChoiceClass(index) {
      if (this.showChoiceFeedback) {
        const correctIdx = this.currentQuestion?.correct_index
        if (correctIdx !== undefined) {
          if (index === correctIdx) return 'correct'
          if (index === this.selectedAnswer) return 'wrong'
        }
        return ''
      }
      return this.selectedAnswer === index ? 'selected' : ''
    },

    handleChoiceAnswer(index) {
      if (this.showChoiceFeedback) return
      this.selectedAnswer = index

      const q = this.currentQuestion
      const correctIdx = q?.correct_index
      const isCorrect = correctIdx !== undefined ? index === correctIdx : true

      if (!isCorrect && correctIdx !== undefined) {
        this.correctAnswerText = q.options?.[correctIdx] || ''
        this.shaking = true
        setTimeout(() => { this.shaking = false }, 400)
      } else {
        this.correctAnswerText = ''
      }

      this.recordAnswer(q.id, q.type, isCorrect, isCorrect ? 1.0 : 0.0)

      this.lastCorrect = isCorrect
      this.showChoiceFeedback = true

      const delay = isCorrect ? 600 : 1200
      setTimeout(() => {
        this.showChoiceFeedback = false
        this.selectedAnswer = null
        this.advanceQuestion()
      }, delay)
    },

    // ─── 拖拽排序逻辑 ────────────────────────────────────────────
    // DragSort 的 @confirm 传回的是 id 数组（即 options 的原始索引）
    // correct_order 是正确排列的原始索引数组，如 [2,0,3,1]
    handleSortAnswer(orderedIds) {
      const q = this.currentQuestion
      const correctOrder = q.correct_order || []
      // orderedIds 是用户排列后的 id 数组，直接与 correct_order 比较
      const isCorrect = JSON.stringify(orderedIds) === JSON.stringify(correctOrder)
      this.recordAnswer(q.id, q.type, isCorrect, isCorrect ? 1.0 : 0.0)
      this.advanceQuestion()
    },

    // ─── 新题型组件统一回调 ──────────────────────────────────────
    // 所有新题型组件 emit 'answer-submitted'，payload: { score, isCorrect, ... }
    handleComponentAnswer({ score, isCorrect }) {
      const q = this.currentQuestion
      this.recordAnswer(q.id, q.type, isCorrect, score)
      // 短暂延迟让组件的反馈动画播完再切题
      setTimeout(() => {
        this.advanceQuestion()
      }, 1000)
    },

    // ─── 跳过题目（TimedClick items为空 / 未知题型） ─────────────
    handleSkipQuestion() {
      this.skippedCount++
      this.advanceQuestion()
    },

    // ─── 通用记录 ────────────────────────────────────────────────
    recordAnswer(questionId, type, isCorrect, score) {
      this.answers.push({
        question_id: questionId,
        type,
        correct: isCorrect === true,
        score: typeof score === 'number' ? score : (isCorrect ? 1.0 : 0.0),
      })
    },

    // ─── 推进题目 ────────────────────────────────────────────────
    advanceQuestion() {
      if (this.currentIndex < this.levelData.questions.length - 1) {
        this.currentIndex++
      } else {
        this.completeLevel()
      }
    },

    // ─── 关卡完成 ────────────────────────────────────────────────
    completeLevel() {
      const total = this.answers.length   // 实际答题数（不含跳过）
      const correct = this.answers.filter(a => a.correct).length
      const accuracy = total > 0 ? correct / total : 0
      const duration = Math.round((Date.now() - this.startTime) / 1000)

      const extraData = buildLevelExtraData({
        gameType: this.levelData.game_type,
        difficulty: this.levelData.difficulty,
        levelId: this.levelData.level_id,
        levelNum: this.levelData.level_num,
        accuracy,
        correctCount: correct,
        totalCount: total,
        durationSeconds: duration,
        passCondition: this.levelData.pass_condition || { min_accuracy: 0.7 },
      })

      this.result = {
        ...extraData,
        correct_count: correct,
        total_count: total,
      }
      this.showResult = true
      this.$emit('level-complete', this.result)
    },

    // ─── 重试 / 返回 ─────────────────────────────────────────────
    handleRetry() {
      this.currentIndex = 0
      this.answers = []
      this.skippedCount = 0
      this.startTime = Date.now()
      this.showResult = false
      this.result = null
      this.selectedAnswer = null
      this.showChoiceFeedback = false
      this.$emit('retry')
    },

    handleBackToLevels() {
      this.$emit('back-to-levels')
    },

    // 游戏进行中点返回：弹确认框
    handleBackClick() {
      this.showExitConfirm = true
    },

    confirmExit() {
      this.showExitConfirm = false
      this.$emit('back-to-levels')
    },
  },
}
</script>

<style scoped>
.level-engine {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

/* ── 加载 / 错误 ── */
.loading-area, .error-area {
  flex: 1; display: flex; flex-direction: column;
  min-height: 100vh;
}
.loading-header, .error-header {
  padding: 56rpx 32rpx 24rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.12);
}
.loading-body, .error-body {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 20rpx; padding: 80rpx 0;
}
.loading-icon { font-size: 64rpx; color: var(--primary, #4F9EF8); }
.loading-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
.error-icon { font-size: 80rpx; color: #FF6B6B; }
.error-text { font-size: 26rpx; color: #718096; }
.retry-btn {
  padding: 16rpx 48rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF; border-radius: 20rpx; font-size: 26rpx; font-weight: 700;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* ── 顶部进度 ── */
.level-header {
  padding: 56rpx 32rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.12);
}
.level-info-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16rpx;
}
.back-btn {
  width: 72rpx; height: 72rpx; border-radius: 50%;
  background: rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; border: 2rpx solid rgba(255,255,255,0.4);
}
.back-btn:active { background: rgba(255,255,255,0.4); transform: scale(0.95); }
.back-btn .ph { font-size: 36rpx; color: #FFFFFF; }
.level-title-area {
  display: flex; align-items: center; gap: 10rpx;
  flex: 1; justify-content: center;
}
.level-game-icon { font-size: 28rpx; color: rgba(255,255,255,0.9); }
.level-tag { font-size: 28rpx; font-weight: 800; color: #FFFFFF; text-align: center; }
.header-placeholder { width: 72rpx; flex-shrink: 0; }
.progress-text { font-size: 22rpx; font-weight: 700; color: rgba(255,255,255,0.85); flex-shrink: 0; }
.progress-track {
  height: 10rpx; background: rgba(255,255,255,0.3);
  border-radius: 5rpx; overflow: hidden;
}
.progress-fill {
  height: 100%; background: rgba(255,255,255,0.9);
  border-radius: 5rpx; transition: width 0.4s;
}

/* ── 题型标签 ── */
.type-badge-row {
  padding: 16rpx 32rpx 0;
  display: flex; justify-content: flex-end;
}
.question-type-badge {
  font-size: 20rpx; font-weight: 700; color: var(--primary, #4F9EF8);
  background: #EFF6FF; padding: 6rpx 16rpx; border-radius: 12rpx;
  border: 1rpx solid #BFDBFE;
}

/* ── 题目卡片（选择题 / 排序题） ── */
.question-wrapper {
  flex: 1; display: flex; flex-direction: column;
  padding-bottom: 40rpx;
}
.question-card {
  margin: 16rpx 32rpx 0;
  background: #FFFFFF; border-radius: 28rpx; padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06);
}
.question-header-row {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 12rpx;
}
.question-title { font-size: 36rpx; font-weight: 800; color: #2D3748; flex: 1; }
.question-instruction {
  font-size: 26rpx; color: #718096; line-height: 1.6;
  margin-bottom: 32rpx; font-weight: 500;
}

/* ── 视觉辨识 2×2 ── */
.options-grid { display: flex; flex-wrap: wrap; gap: 20rpx; }
.option-char {
  width: calc(50% - 10rpx); aspect-ratio: 1;
  background: #FFFFFF; border: 3rpx solid #E5E7EB; border-radius: 24rpx;
  display: flex; align-items: center; justify-content: center;
  font-size: 96rpx; font-weight: 800; color: #2D3748; transition: all 0.2s;
}
.option-char:active { transform: scale(0.95); }
.option-char.selected { border-color: var(--primary, #4F9EF8); background: #EFF6FF; color: var(--primary, #4F9EF8); }
.option-char.correct  { border-color: #22C55E; background: #F0FDF4; color: #22C55E; }
.option-char.wrong    { border-color: #FF6B6B; background: #FFF5F5; color: #FF6B6B; }

/* ── 通用选项列表 ── */
.options-list { display: flex; flex-direction: column; gap: 16rpx; }
.option-item {
  background: #FFFFFF; border: 3rpx solid #E5E7EB; border-radius: 20rpx;
  padding: 24rpx 28rpx; display: flex; align-items: center; gap: 20rpx; transition: all 0.2s;
}
.option-item:active { transform: scale(0.98); }
.option-item.selected { border-color: var(--primary, #4F9EF8); background: #EFF6FF; }
.option-item.correct  { border-color: #22C55E; background: #F0FDF4; }
.option-item.wrong    { border-color: #FF6B6B; background: #FFF5F5; }
.option-label {
  width: 48rpx; height: 48rpx; border-radius: 12rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center;
  font-size: 22rpx; font-weight: 700; color: #A0AEC0; flex-shrink: 0;
}
.option-item.selected .option-label { background: #DBEAFE; color: var(--primary, #4F9EF8); }
.option-item.correct  .option-label { background: #DCFCE7; color: #22C55E; }
.option-item.wrong    .option-label { background: #FFE4E4; color: #FF6B6B; }
.option-text { font-size: 30rpx; font-weight: 700; color: #2D3748; flex: 1; }
.option-item.selected .option-text { color: var(--primary, #4F9EF8); }
.option-item.correct  .option-text { color: #22C55E; }
.option-item.wrong    .option-text { color: #FF6B6B; }

/* ── 未知题型兜底 ── */
.unknown-type { text-align: center; }
.unknown-hint { font-size: 24rpx; color: #A0AEC0; margin: 24rpx 0; }
.skip-btn {
  display: inline-block; padding: 16rpx 48rpx;
  background: #F5F5F5; color: #718096; border-radius: 20rpx;
  font-size: 26rpx; font-weight: 700;
}

/* ── 震动 ── */
@keyframes shake {
  0%,100% { transform: translateX(0); }
  20% { transform: translateX(-8rpx); }
  40% { transform: translateX(8rpx); }
  60% { transform: translateX(-6rpx); }
  80% { transform: translateX(6rpx); }
}
.shake { animation: shake 0.4s ease; }

/* ── 选择题反馈遮罩 ── */
.feedback-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.96); z-index: 500;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 20rpx;
  animation: fadeIn 0.15s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.feedback-icon .ph { font-size: 160rpx; animation: popIn 0.3s cubic-bezier(0.4,0,0.2,1); }
.feedback-icon.correct .ph { color: #22C55E; }
.feedback-icon.wrong   .ph { color: #FF6B6B; }
@keyframes popIn { 0% { transform: scale(0.4); opacity: 0; } 70% { transform: scale(1.1); } 100% { transform: scale(1); opacity: 1; } }
.feedback-text { font-size: 44rpx; font-weight: 800; color: #2D3748; }
.feedback-correct { font-size: 26rpx; color: #718096; }
.feedback-answer { font-size: 30rpx; font-weight: 700; color: #22C55E; }

/* ── 结果页 ── */
.result-area {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 600;
  display: flex; align-items: center; justify-content: center; padding: 32rpx;
}
.result-card {
  background: #FFFFFF; border-radius: 32rpx; padding: 48rpx 40rpx;
  width: 100%; max-width: 640rpx;
  display: flex; flex-direction: column; align-items: center;
  animation: popIn 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.result-icon {
  width: 120rpx; height: 120rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; margin-bottom: 24rpx;
}
.result-icon.passed { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.result-icon.passed .ph { font-size: 60rpx; color: #F57F17; }
.result-icon.failed { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); }
.result-icon.failed .ph { font-size: 60rpx; color: #FF6B6B; }
.result-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 20rpx; }

/* 星星 */
.stars-row { display: flex; gap: 12rpx; margin-bottom: 24rpx; }
.star-icon { font-size: 56rpx; transition: all 0.3s; }
.star-filled { color: #F59E0B; }
.star-empty  { color: #E5E7EB; }

.result-stats {
  display: flex; align-items: center;
  background: #F9FAFB; border-radius: 20rpx; padding: 24rpx 32rpx;
  margin-bottom: 20rpx; width: 100%;
}
.stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.stat-value { font-size: 44rpx; font-weight: 900; color: #2D3748; }
.stat-label { font-size: 20rpx; color: #A0AEC0; font-weight: 600; }
.stat-divider { width: 2rpx; height: 60rpx; background: #E5E7EB; }
.result-pass-hint { font-size: 22rpx; color: #A0AEC0; margin-bottom: 28rpx; text-align: center; }
.result-btns { display: flex; gap: 16rpx; width: 100%; }
.result-btn {
  flex: 1; padding: 28rpx; border-radius: 16rpx;
  font-size: 28rpx; font-weight: 700; text-align: center; transition: all 0.2s;
}
.result-btn:active { transform: scale(0.97); }
.result-btn.retry { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25); }
.result-btn.back  { background: #F5F5F5; color: #718096; }

/* ── 退出确认弹窗 ── */
.exit-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.45); z-index: 700;
  display: flex; align-items: center; justify-content: center; padding: 32rpx;
}
.exit-card {
  background: #FFFFFF; border-radius: 32rpx; padding: 48rpx 40rpx;
  width: 100%; max-width: 600rpx;
  display: flex; flex-direction: column; align-items: center;
  animation: popIn 0.25s cubic-bezier(0.34,1.56,0.64,1);
}
.exit-icon-wrap {
  width: 112rpx; height: 112rpx; border-radius: 28rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 28rpx;
}
.exit-icon { font-size: 56rpx; color: #F57F17; }
.exit-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; }
.exit-desc { font-size: 26rpx; color: #718096; text-align: center; line-height: 1.6; margin-bottom: 36rpx; font-weight: 500; }
.exit-btns { display: flex; gap: 16rpx; width: 100%; }
.exit-btn-item {
  flex: 1; padding: 28rpx; border-radius: 16rpx;
  font-size: 28rpx; font-weight: 700; text-align: center; transition: all 0.2s;
}
.exit-btn-item:active { transform: scale(0.97); }
.exit-btn-item.outline { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25); }
.exit-btn-item.danger  { background: #F5F5F5; color: #718096; }
</style>
