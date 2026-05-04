<template>
  <view class="flip-card-question">
    <!-- 指引文字 -->
    <view class="question-card">
      <view class="question-title">{{ question.title }}</view>
      <view class="question-instruction">{{ question.instruction }}</view>
    </view>

    <!-- 预览倒计时提示 -->
    <view class="preview-banner" v-if="phase === 'preview'">
      <text class="ph ph-eye"></text>
      <text class="preview-text">记住卡片位置！{{ previewCountdown }}s</text>
    </view>

    <!-- 配对进度 -->
    <view class="match-progress" v-if="phase === 'playing'">
      <text class="ph ph-check-circle"></text>
      <text class="progress-text">已配对 {{ matchedCount }} / {{ totalPairs }} 对</text>
    </view>

    <!-- 卡片网格 -->
    <view :class="['cards-grid', gridClass]">
      <view
        v-for="card in cards"
        :key="card.id"
        :class="['card-wrap', { matched: card.isMatched }]"
        @click="onCardClick(card)"
      >
        <view :class="['card-inner', { flipped: card.isFlipped || card.isMatched }]">
          <!-- 背面 -->
          <view class="card-back">
            <text class="back-icon">🌟</text>
          </view>
          <!-- 正面 -->
          <view class="card-front">
            <text class="card-text">{{ card.content }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 完成提示 -->
    <view class="complete-banner" v-if="phase === 'complete'">
      <text class="ph ph-trophy"></text>
      <text class="complete-text">全部配对完成！🎉</text>
    </view>
  </view>
</template>

<script>
export default {
  name: 'FlipCardQuestion',
  props: {
    question: { type: Object, required: true },
  },
  emits: ['answer-submitted'],
  data() {
    return {
      cards: [],
      phase: 'preview',   // 'preview' | 'playing' | 'complete'
      flippedCards: [],
      isAnimating: false,
      matchedCount: 0,
      startTime: null,
      previewCountdown: 0,
      previewTimer: null,
      submitted: false,
      timeoutTimer: null,
    }
  },
  computed: {
    totalPairs() {
      return (this.question.pairs || []).length
    },
    gridClass() {
      const n = this.cards.length
      if (n <= 6) return 'grid-3col'
      if (n <= 8) return 'grid-4col'
      return 'grid-4col'
    },
  },
  mounted() {
    this.initGame()
  },
  beforeUnmount() {
    this._clearTimers()
  },
  methods: {
    initGame() {
      const pairs = this.question.pairs || []
      const rawCards = []
      let idx = 1
      for (const pair of pairs) {
        rawCards.push({ id: `card_a_${idx}`, pairId: pair.pair_id, content: pair.card_a.content, isFlipped: false, isMatched: false })
        rawCards.push({ id: `card_b_${idx}`, pairId: pair.pair_id, content: pair.card_b.content, isFlipped: false, isMatched: false })
        idx++
      }
      // 随机打乱
      for (let i = rawCards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [rawCards[i], rawCards[j]] = [rawCards[j], rawCards[i]]
      }
      this.cards = rawCards
      this.matchedCount = 0
      this.flippedCards = []
      this.isAnimating = false
      this.submitted = false

      // 预览阶段：翻开所有卡片
      this.cards = this.cards.map(c => ({ ...c, isFlipped: true }))
      this.phase = 'preview'

      const previewMs = this.question.preview_duration || 2000
      this.previewCountdown = Math.ceil(previewMs / 1000)

      // 倒计时
      this.previewTimer = setInterval(() => {
        this.previewCountdown--
        if (this.previewCountdown <= 0) {
          clearInterval(this.previewTimer)
          this.previewTimer = null
        }
      }, 1000)

      // 预览结束后翻回背面
      setTimeout(() => {
        this.cards = this.cards.map(c => ({ ...c, isFlipped: false }))
        this.phase = 'playing'
        this.startTime = Date.now()

        // 超时处理
        const timeLimit = (this.question.time_limit || 60) * 1000
        this.timeoutTimer = setTimeout(() => {
          if (!this.submitted) this._submit()
        }, timeLimit)
      }, previewMs)
    },

    onCardClick(card) {
      if (this.phase !== 'playing') return
      if (card.isFlipped || card.isMatched || this.isAnimating) return
      if (this.flippedCards.length >= 2) return

      this._setFlipped(card.id, true)
      this.flippedCards = [...this.flippedCards, card]

      if (this.flippedCards.length === 2) {
        this.isAnimating = true
        const [a, b] = this.flippedCards
        if (a.pairId === b.pairId) {
          // 配对成功
          setTimeout(() => {
            this._setMatched(a.id)
            this._setMatched(b.id)
            this.matchedCount++
            this.flippedCards = []
            this.isAnimating = false
            if (this.matchedCount >= this.totalPairs) {
              this.phase = 'complete'
              setTimeout(() => this._submit(), 600)
            }
          }, 300)
        } else {
          // 配对失败，翻回
          setTimeout(() => {
            this._setFlipped(a.id, false)
            this._setFlipped(b.id, false)
            this.flippedCards = []
            setTimeout(() => { this.isAnimating = false }, 300)
          }, 800)
        }
      }
    },

    _setFlipped(id, val) {
      this.cards = this.cards.map(c => c.id === id ? { ...c, isFlipped: val } : c)
    },
    _setMatched(id) {
      this.cards = this.cards.map(c => c.id === id ? { ...c, isFlipped: true, isMatched: true } : c)
    },

    _submit() {
      if (this.submitted) return
      this.submitted = true
      this._clearTimers()
      const score = this.totalPairs > 0 ? this.matchedCount / this.totalPairs : 0
      const isCorrect = score >= 0.7
      this.$emit('answer-submitted', {
        score,
        matchedPairs: this.matchedCount,
        totalPairs: this.totalPairs,
        isCorrect,
      })
    },

    _clearTimers() {
      if (this.previewTimer) { clearInterval(this.previewTimer); this.previewTimer = null }
      if (this.timeoutTimer) { clearTimeout(this.timeoutTimer); this.timeoutTimer = null }
    },
  },
}
</script>

<style scoped>
.flip-card-question {
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

.preview-banner {
  display: flex; align-items: center; gap: 12rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  border-radius: 20rpx; padding: 16rpx 24rpx;
}
.preview-banner .ph { font-size: 32rpx; color: #F57F17; }
.preview-text { font-size: 26rpx; font-weight: 700; color: #F57F17; }

.match-progress {
  display: flex; align-items: center; gap: 10rpx;
  padding: 8rpx 0;
}
.match-progress .ph { font-size: 28rpx; color: #22C55E; }
.progress-text { font-size: 24rpx; font-weight: 700; color: #22C55E; }

/* 卡片网格 */
.cards-grid {
  display: grid;
  gap: 16rpx;
}
.grid-3col { grid-template-columns: repeat(3, 1fr); }
.grid-4col { grid-template-columns: repeat(4, 1fr); }

/* 单张卡片 */
.card-wrap {
  aspect-ratio: 1 / 1.1;
  perspective: 800rpx;
  cursor: pointer;
  border-radius: 20rpx;
  transition: box-shadow 0.3s;
}
.card-wrap.matched {
  box-shadow: 0 0 0 4rpx #22C55E, 0 4rpx 16rpx rgba(34,197,94,0.3);
}

.card-inner {
  position: relative;
  width: 100%; height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
  border-radius: 20rpx;
}
.card-inner.flipped { transform: rotateY(180deg); }

.card-back, .card-front {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  border-radius: 20rpx;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  display: flex; align-items: center; justify-content: center;
}

.card-back {
  background: linear-gradient(135deg, #A78BFA, #7C3AED);
  box-shadow: 0 4rpx 16rpx rgba(124,58,237,0.25);
}
.back-icon { font-size: 48rpx; opacity: 0.85; }

.card-front {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 3rpx solid #FDE68A;
  transform: rotateY(180deg);
  padding: 8rpx;
}
.card-text {
  font-size: 40rpx;
  font-weight: 900;
  color: #92400E;
  text-align: center;
  line-height: 1.2;
  word-break: break-all;
}

.complete-banner {
  display: flex; align-items: center; justify-content: center; gap: 12rpx;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border-radius: 20rpx; padding: 20rpx;
  border: 2rpx solid #22C55E;
}
.complete-banner .ph { font-size: 36rpx; color: #22C55E; }
.complete-text { font-size: 28rpx; font-weight: 800; color: #22C55E; }
</style>
