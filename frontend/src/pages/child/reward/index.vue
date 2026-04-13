<template>
  <view class="page-container">
    <!-- 星星动画区 -->
    <view class="stars-area">
      <view class="star left pop-in" style="animation-delay: 0.1s">
        <text class="ph ph-star"></text>
      </view>
      <view class="star center pop-in" style="animation-delay: 0.3s">
        <text class="ph ph-star"></text>
      </view>
      <view class="star right pop-in" style="animation-delay: 0.5s">
        <text class="ph ph-star"></text>
      </view>
    </view>

    <view class="content-area">
      <view class="congrats-title pop-in" style="animation-delay: 0.7s">太棒啦！</view>
      <view class="congrats-desc pop-in" style="animation-delay: 0.8s">
        你完成了所有的挑战<br>获得了 3 颗探险之星
      </view>

      <button class="return-btn pop-in" style="animation-delay: 1s" @click="returnHome">
        回到首页
      </button>

      <view class="parent-note pop-in" style="animation-delay: 1.1s">
        （结果已自动发送给爸爸妈妈）
      </view>
    </view>
  </view>
</template>

<script>
export default {
  onLoad() {
    // 清除筛查缓存，避免下次进入游戏复用旧ID
    uni.removeStorageSync('current_screening')
    uni.removeStorageSync('pending_task_id')
  },
  methods: {
    returnHome() {
      uni.redirectTo({ url: '/pages/child/home/index' })
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
  padding-bottom: env(safe-area-inset-bottom);
}

/* 星星动画区 */
.stars-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding-top: 120rpx;
  padding-bottom: 40rpx;
}

.star {
  display: flex;
  align-items: center;
  justify-content: center;
}

.star.left, .star.right {
  font-size: 80rpx;
  color: #F59E0B;
  padding-bottom: 40rpx;
}

.star.center {
  font-size: 120rpx;
  color: #F59E0B;
}

/* 内容区 */
.content-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 48rpx 120rpx;
}

.congrats-title {
  font-size: 64rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 24rpx;
}

.congrats-desc {
  font-size: 32rpx;
  color: #9CA3AF;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 80rpx;
}

.return-btn {
  width: 100%;
  max-width: 640rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

.parent-note {
  font-size: 22rpx;
  color: #D1D5DB;
  margin-top: 48rpx;
}

/* 动画 */
@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.pop-in {
  opacity: 0;
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
</style>
