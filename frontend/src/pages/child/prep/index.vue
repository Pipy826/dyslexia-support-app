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
    // difficulty 由 game/index.vue 根据 grade 向后端请求，prep 不再自行映射
  },
  methods: {
    goBack() {
      uni.navigateBack()
    },
    startGame() {
      // 只传 game_type，难度由后端根据孩子档案的 grade 自动映射
      uni.navigateTo({
        url: `/pages/child/game/index?game_type=${this.gameType}`
      })
    }
  }
}
</script>

<style scoped>
/* 创意准备页面 - 简洁引导 */
.page-container {
  min-height: 100vh;
  background: #F8FAFF;
  display: flex;
  flex-direction: column;
}

.back-btn {
  padding: 56rpx 32rpx 16rpx;
  display: inline-flex;
}

.back-btn .ph {
  font-size: 36rpx;
  color: #718096;
  transition: all 0.2s;
}

.back-btn:active .ph {
  color: #4F9EF8;
  transform: translateX(-4rpx);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 32rpx 64rpx;
}

.game-badge {
  display: flex;
  align-items: center;
  gap: 10rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  padding: 10rpx 24rpx;
  border-radius: 16rpx;
  font-size: 24rpx;
  font-weight: 700;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(79, 158, 248, 0.15);
}

.game-badge .ph {
  font-size: 26rpx;
}

.title {
  font-size: 40rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 40rpx;
  text-align: center;
}

.tips-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.tip-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
  border-radius: 20rpx;
  transition: all 0.2s;
}

.tip-card:active {
  transform: scale(0.98);
}

.tip-card.blue {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
}

.tip-card.green {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
}

.tip-card.orange {
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
}

.tip-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.tip-icon .ph {
  font-size: 36rpx;
}

.tip-card.blue .tip-icon .ph { color: #4F9EF8; }
.tip-card.green .tip-icon .ph { color: #22C55E; }
.tip-card.orange .tip-icon .ph { color: #F57F17; }

.tip-text {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
}

/* 难度提示 */
.difficulty-hint {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #FFFFFF;
  border: 2rpx solid #FFE082;
  border-radius: 20rpx;
  padding: 20rpx 28rpx;
  margin-bottom: 40rpx;
  width: 100%;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.15);
}

.difficulty-icon {
  font-size: 32rpx;
  color: #F57F17;
}

.difficulty-text {
  font-size: 26rpx;
  color: #92400E;
  font-weight: 600;
}

.ready-btn {
  width: 100%;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
  font-size: 36rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.3);
  letter-spacing: 2rpx;
  transition: all 0.2s;
}

.ready-btn:active {
  transform: scale(0.97);
}
</style>
