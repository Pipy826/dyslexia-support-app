<template>
  <view class="page-container">
    <view class="back-btn" @click="goBack">
      <text class="ph ph-arrow-left"></text>
    </view>

    <view class="content-area">
      <view class="game-badge">
        <text :class="'ph ' + gameIcon"></text>
        {{ gameName }}
      </view>

      <view class="title">挑战前的小准备</view>

      <view class="tips-list">
        <view class="tip-card blue">
          <view class="tip-icon"><text class="ph ph-headphones"></text></view>
          <view class="tip-text">找一个安静的地方</view>
        </view>
        <view class="tip-card green">
          <view class="tip-icon"><text class="ph ph-eye"></text></view>
          <view class="tip-text">仔细看，认真听</view>
        </view>
        <view class="tip-card orange">
          <view class="tip-icon"><text class="ph ph-hand"></text></view>
          <view class="tip-text">不用害怕答错哦</view>
        </view>
      </view>

      <!-- 难度提示（自动匹配，不让孩子手选） -->
      <view class="difficulty-hint">
        <text class="ph ph-star difficulty-icon"></text>
        <view class="difficulty-text">已为你准备好适合的题目，加油！</view>
      </view>

      <button class="ready-btn" @click="startGame">
        我准备好了！🚀
      </button>
    </view>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      gameType: 'visual',
      selectedDifficulty: 'L1'
    }
  },
  computed: {
    gameName() {
      return { visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解' }[this.gameType] || '综合挑战'
    },
    gameIcon() {
      return { visual: 'ph-eye', spelling: 'ph-puzzle-piece', comprehension: 'ph-book-open' }[this.gameType] || 'ph-star'
    }
  },
  onLoad(options) {
    if (options.game_type) this.gameType = options.game_type
    // 根据儿童年级自动匹配难度
    const child = getCurrentChild()
    this.selectedDifficulty = this._gradeToLevel(child?.grade)
  },
  methods: {
    _gradeToLevel(grade) {
      // 学龄前/一年级 → L1，二三年级 → L2，四年级及以上 → L3
      if (!grade || grade === 'pre' || grade === '1') return 'L1'
      if (grade === '2' || grade === '3') return 'L2'
      return 'L3'
    },
    goBack() {
      uni.navigateBack()
    },
    startGame() {
      uni.navigateTo({
        url: `/pages/child/game/index?game_type=${this.gameType}&difficulty=${this.selectedDifficulty}`
      })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
}

.back-btn { padding: 96rpx 48rpx 16rpx; }
.back-btn .ph { font-size: 40rpx; color: #9CA3AF; }

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 64rpx 64rpx;
}

.game-badge {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #EFF6FF;
  color: #3B82F6;
  padding: 12rpx 32rpx;
  border-radius: 50rpx;
  font-size: 26rpx;
  font-weight: 700;
  margin-bottom: 32rpx;
}
.game-badge .ph { font-size: 28rpx; }

.title {
  font-size: 44rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 56rpx;
  text-align: center;
}

.tips-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 48rpx;
}

.tip-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 28rpx 32rpx;
  border-radius: 32rpx;
}
.tip-card.blue { background: #EFF6FF; }
.tip-card.green { background: #ECFDF5; }
.tip-card.orange { background: #FEF3C7; }

.tip-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0,0,0,0.05);
  flex-shrink: 0;
}
.tip-icon .ph { font-size: 44rpx; }
.tip-card.blue .tip-icon .ph { color: #3B82F6; }
.tip-card.green .tip-icon .ph { color: #10B981; }
.tip-card.orange .tip-icon .ph { color: #F59E0B; }

.tip-text { font-size: 32rpx; font-weight: 600; color: #374151; }

/* 难度提示 */
.difficulty-hint {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: #FFFBEB;
  border: 1rpx solid #FDE68A;
  border-radius: 32rpx;
  padding: 24rpx 40rpx;
  margin-bottom: 48rpx;
  width: 100%;
}
.difficulty-icon { font-size: 36rpx; color: #F59E0B; }
.difficulty-text { font-size: 28rpx; color: #92400E; font-weight: 600; }

.ready-btn {
  width: 100%;
  max-width: 640rpx;
  background: #10B981;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(16,185,129,0.3);
}
</style>
