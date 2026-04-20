<template>
  <view class="page-container">
    <!-- 星星动画区 -->
    <view class="stars-area">
      <view class="star star-left pop-in" style="animation-delay: 0.1s">
        <text class="ph ph-star-fill"></text>
      </view>
      <view class="star star-center pop-in" style="animation-delay: 0.3s">
        <text class="ph ph-star-fill"></text>
      </view>
      <view class="star star-right pop-in" style="animation-delay: 0.5s">
        <text class="ph ph-star-fill"></text>
      </view>
    </view>

    <view class="content-area">
      <view class="congrats-title pop-in" style="animation-delay: 0.7s">太棒啦！🎉</view>
      <view class="congrats-desc pop-in" style="animation-delay: 0.8s">
        你完成了所有的挑战<br>获得了 <text class="highlight">{{ starsEarned }}</text> 颗探险之星
      </view>

      <!-- AI 鼓励话语 -->
      <view class="ai-encouragement pop-in" style="animation-delay: 1s" v-if="encouragement">
        <view class="ai-enc-avatar">
          <text class="ph-fill ph-robot"></text>
        </view>
        <view class="ai-enc-bubble">
          <view class="ai-enc-text">{{ encouragement }}</view>
        </view>
      </view>

      <!-- 加载中占位 -->
      <view class="ai-encouragement-loading pop-in" style="animation-delay: 1s" v-else-if="encLoading">
        <view class="enc-dots">
          <view class="enc-dot"></view>
          <view class="enc-dot"></view>
          <view class="enc-dot"></view>
        </view>
      </view>

      <!-- 总星星数 -->
      <view class="total-stars pop-in" style="animation-delay: 1.1s">
        <text class="ph ph-star"></text>
        累计 {{ totalStars }} 颗星星
      </view>

      <button class="return-btn pop-in" style="animation-delay: 1.2s" @click="returnHome">
        回到首页
      </button>

      <view class="parent-note pop-in" style="animation-delay: 1.3s">
        （结果已自动发送给爸爸妈妈）
      </view>
    </view>
  </view>
</template>

<script>
import { getTotalStars } from '../../../api/training.js'
import { getEncouragement } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      starsEarned: 1,
      totalStars: 0,
      encouragement: '',
      encLoading: false,
    }
  },
  onLoad(options) {
    uni.removeStorageSync('current_screening')
    uni.removeStorageSync('pending_task_id')

    // 从路由参数或 storage 获取游戏结果
    const gameResult = uni.getStorageSync('last_game_result') || {}
    this.starsEarned = gameResult.stars || 1

    this.loadStars()
    this.loadEncouragement(gameResult)
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

    async loadEncouragement(gameResult) {
      const child = getCurrentChild()
      if (!child) return

      this.encLoading = true
      try {
        const res = await getEncouragement({
          child_id: child.id,
          game_type: gameResult.game_type || 'visual',
          score: gameResult.score || 80,
          correct_count: gameResult.correct_count || 8,
          total_count: gameResult.total_count || 10,
        })
        this.encouragement = res.encouragement
      } catch (e) {
        // 降级到固定话语
        const score = gameResult.score || 80
        if (score >= 80) {
          this.encouragement = `哇，${child.name}太厉害了！🌟 继续加油！`
        } else if (score >= 60) {
          this.encouragement = `${child.name}做得很棒！💪 再练练会更厉害的！`
        } else {
          this.encouragement = `${child.name}已经很努力了！🌈 下次一定会更好！`
        }
      } finally {
        this.encLoading = false
      }
    },

    returnHome() {
      uni.removeStorageSync('last_game_result')
      uni.redirectTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>


<style scoped>
/* 创意奖励页面 - 全屏庆祝 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  padding-bottom: env(safe-area-inset-bottom);
  position: relative;
  overflow-x: hidden;
}

.page-container::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 40%;
  background: linear-gradient(180deg, #EFF6FF 0%, transparent 100%);
  pointer-events: none;
}

.stars-area {
  width: 100%;
  height: 280rpx;
  position: relative;
  flex-shrink: 0;
  margin-top: 60rpx;
  margin-bottom: 16rpx;
}

/* 绝对定位三颗星，位置完全可控 */
.star {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
}

.star-left {
  left: 50%;
  bottom: 20rpx;
  transform: translateX(-160rpx);
  font-size: 88rpx;
  color: #4F9EF8;
  filter: drop-shadow(0 4rpx 8rpx rgba(79, 158, 248, 0.35));
}

.star-center {
  left: 50%;
  bottom: 40rpx;
  transform: translateX(-50%);
  font-size: 144rpx;
  color: #4F9EF8;
  filter: drop-shadow(0 6rpx 20rpx rgba(79, 158, 248, 0.45));
  animation: starPulse 2s ease-in-out infinite;
}

.star-right {
  left: 50%;
  bottom: 20rpx;
  transform: translateX(72rpx);
  font-size: 88rpx;
  color: #4F9EF8;
  filter: drop-shadow(0 4rpx 8rpx rgba(79, 158, 248, 0.35));
}

@keyframes starPulse { 0%, 100% { transform: translateX(-50%) scale(1); } 50% { transform: translateX(-50%) scale(1.08); } }

.content-area {
  display: flex; flex-direction: column; align-items: center;
  padding: 0 32rpx 80rpx; position: relative; z-index: 1;
}

.congrats-title { font-size: 56rpx; font-weight: 800; color: #2D3748; margin-bottom: 16rpx; letter-spacing: 2rpx; }

.congrats-desc { font-size: 28rpx; color: #718096; text-align: center; line-height: 1.7; margin-bottom: 32rpx; font-weight: 500; }
.congrats-desc .highlight { font-size: 44rpx; font-weight: 800; color: #F57F17; }

.ai-encouragement { display: flex; align-items: flex-end; gap: 12rpx; margin-bottom: 32rpx; max-width: 600rpx; width: 100%; }
.ai-enc-avatar {
  width: 64rpx; height: 64rpx; border-radius: 50%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.25);
}
.ai-enc-avatar .ph { font-size: 32rpx; color: #FFFFFF; }
.ai-enc-bubble {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 2rpx solid #BFDBFE;
  border-radius: 24rpx; border-bottom-left-radius: 6rpx; padding: 20rpx 24rpx; flex: 1;
  box-shadow: 0 2rpx 12rpx rgba(59, 130, 246, 0.08);
}
.ai-enc-text { font-size: 26rpx; color: #2D3748; line-height: 1.6; font-weight: 500; }

.ai-encouragement-loading { display: flex; justify-content: center; margin-bottom: 32rpx; height: 64rpx; align-items: center; }
.enc-dots { display: flex; gap: 12rpx; }
.enc-dot { width: 16rpx; height: 16rpx; border-radius: 50%; background: #4F9EF8; animation: enc-bounce 1.2s infinite; }
.enc-dot:nth-child(2) { animation-delay: 0.2s; }
.enc-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes enc-bounce {
  0%, 80%, 100% { transform: scale(0.6) translateY(0); opacity: 0.4; }
  40% { transform: scale(1.1) translateY(-10rpx); opacity: 1; }
}

.total-stars {
  display: flex; align-items: center; gap: 10rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  padding: 16rpx 36rpx; border-radius: 20rpx; font-size: 26rpx; font-weight: 700; color: #2D3748;
  margin-bottom: 48rpx; box-shadow: 0 4rpx 12rpx rgba(79, 158, 248, 0.15);
}
.total-stars .ph { font-size: 28rpx; color: #4F9EF8; }

.return-btn {
  width: 100%; max-width: 600rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 20rpx; padding: 32rpx; font-size: 36rpx; font-weight: 800;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3); letter-spacing: 2rpx; transition: all 0.2s;
}
.return-btn:active { transform: scale(0.97); }

@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}
.pop-in { opacity: 0; animation: popIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards; }
</style>
