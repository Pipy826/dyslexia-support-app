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

      <!-- 难度选择 -->
      <view class="difficulty-section">
        <view class="difficulty-label">选择难度</view>
        <view class="difficulty-btns">
          <view
            v-for="d in difficulties"
            :key="d.value"
            :class="['diff-btn', { active: selectedDifficulty === d.value }]"
            @click="selectedDifficulty = d.value"
          >
            {{ d.label }}
          </view>
        </view>
      </view>

      <button class="ready-btn" @click="startGame">
        我准备好了！🚀
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      gameType: 'visual',
      selectedDifficulty: 'L1',
      difficulties: [
        { value: 'L1', label: '初级 ⭐' },
        { value: 'L2', label: '中级 ⭐⭐' },
        { value: 'L3', label: '高级 ⭐⭐⭐' }
      ]
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
  },
  methods: {
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

/* 难度选择 */
.difficulty-section {
  width: 100%;
  margin-bottom: 48rpx;
}
.difficulty-label {
  font-size: 26rpx;
  font-weight: 700;
  color: #6B7280;
  margin-bottom: 16rpx;
  text-align: center;
}
.difficulty-btns {
  display: flex;
  gap: 16rpx;
  justify-content: center;
}
.diff-btn {
  padding: 16rpx 32rpx;
  border-radius: 50rpx;
  border: 2rpx solid #E5E7EB;
  font-size: 24rpx;
  font-weight: 600;
  color: #6B7280;
  background: #FFFFFF;
  transition: all 0.2s;
}
.diff-btn.active {
  background: #EFF6FF;
  border-color: #3B82F6;
  color: #3B82F6;
}

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
