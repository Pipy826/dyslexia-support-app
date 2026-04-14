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
      <view class="congrats-title pop-in" style="animation-delay: 0.7s">太棒啦！🎉</view>
      <view class="congrats-desc pop-in" style="animation-delay: 0.8s">
        你完成了所有的挑战<br>获得了 <text class="highlight">{{ starsEarned }}</text> 颗探险之星
      </view>

      <!-- 总星星数 -->
      <view class="total-stars pop-in" style="animation-delay: 0.9s">
        <text class="ph ph-star"></text>
        累计 {{ totalStars }} 颗星星
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
import { getTotalStars } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      starsEarned: 1,
      totalStars: 0
    }
  },
  onLoad() {
    uni.removeStorageSync('current_screening')
    uni.removeStorageSync('pending_task_id')
    this.loadStars()
  },
  methods: {
    async loadStars() {
      const child = getCurrentChild()
      if (!child) return
      try {
        const res = await getTotalStars(child.id)
        this.totalStars = res.total_stars || 0
      } catch (e) {
        console.warn('加载星星失败', e)
      }
    },
    returnHome() {
      uni.redirectTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF3C7 0%, #FFFFFF 50%);
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
}

.stars-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding-top: 120rpx;
  padding-bottom: 40rpx;
}

.star { display: flex; align-items: center; justify-content: center; }
.star.left, .star.right { font-size: 80rpx; color: #F59E0B; padding-bottom: 40rpx; }
.star.center { font-size: 128rpx; color: #F59E0B; }

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
  color: #6B7280;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 32rpx;
}
.congrats-desc .highlight {
  font-size: 48rpx;
  font-weight: 700;
  color: #F59E0B;
}

.total-stars {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #FEF3C7;
  padding: 16rpx 40rpx;
  border-radius: 50rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #D97706;
  margin-bottom: 64rpx;
  border: 1rpx solid #FDE68A;
}
.total-stars .ph { font-size: 32rpx; color: #F59E0B; }

.return-btn {
  width: 100%;
  max-width: 640rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 64rpx;
  padding: 32rpx;
  font-size: 40rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59,130,246,0.3);
}

.parent-note {
  font-size: 22rpx;
  color: #D1D5DB;
  margin-top: 48rpx;
}

@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.pop-in {
  opacity: 0;
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
</style>
