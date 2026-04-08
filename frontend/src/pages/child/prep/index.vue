<template>
  <view class="page-container">
    <!-- 返回按钮 -->
    <view class="back-btn" @click="goBack">
      <text class="ph ph-arrow-left"></text>
    </view>

    <!-- 内容区 -->
    <view class="content-area">
      <view class="title">挑战前的小准备</view>

      <view class="tips-list">
        <view class="tip-card blue">
          <view class="tip-icon">
            <text class="ph ph-headphones"></text>
          </view>
          <view class="tip-text">找一个安静的地方</view>
        </view>

        <view class="tip-card green">
          <view class="tip-icon">
            <text class="ph ph-eye"></text>
          </view>
          <view class="tip-text">仔细看，认真听</view>
        </view>

        <view class="tip-card red">
          <view class="tip-icon">
            <text class="ph ph-hand"></text>
          </view>
          <view class="tip-text">不用害怕答错哦</view>
        </view>
      </view>

      <button class="ready-btn" @click="startGame">
        我准备好了！
      </button>
    </view>
  </view>
</template>

<script>
export default {
  methods: {
    goBack() {
      uni.navigateBack()
    },
    startGame() {
      uni.navigateTo({ url: '/pages/child/game/index' })
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

/* 返回按钮 */
.back-btn {
  padding: 96rpx 48rpx 32rpx;
}

.back-btn .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

/* 内容区 */
.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0 64rpx;
}

.title {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 80rpx;
  text-align: center;
}

/* 提示列表 */
.tips-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 32rpx;
  margin-bottom: 80rpx;
}

.tip-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 32rpx;
  border-radius: 32rpx;
}

.tip-card.blue {
  background: #EFF6FF;
}

.tip-card.green {
  background: #ECFDF5;
}

.tip-card.red {
  background: #FEF2F2;
}

.tip-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.tip-icon .ph {
  font-size: 48rpx;
}

.tip-card.blue .tip-icon .ph {
  color: #3B82F6;
}

.tip-card.green .tip-icon .ph {
  color: #10B981;
}

.tip-card.red .tip-icon .ph {
  color: #EF4444;
}

.tip-text {
  font-size: 34rpx;
  font-weight: 500;
  color: #374151;
}

/* 准备按钮 */
.ready-btn {
  width: 100%;
  max-width: 640rpx;
  background: #10B981;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(16, 185, 129, 0.3);
}
</style>
