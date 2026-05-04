<template>
  <view class="page-container">
    <!-- 顶部渐变背景 -->
    <view class="top-bg"></view>

    <!-- 星星飞入动画区 -->
    <view class="stars-area">
      <view
        v-for="(star, i) in starItems"
        :key="i"
        class="star-item"
        :style="{ animationDelay: (i * 0.15) + 's', left: star.left, top: star.top }"
      >
        <text class="ph ph-star-fill"></text>
      </view>
    </view>

    <scroll-view class="content-area" scroll-y>
      <view class="content-inner">
      <!-- 标题 -->
      <view class="congrats-title pop-in" style="animation-delay: 0.5s">太棒啦！🎉</view>
      <view class="congrats-desc pop-in" style="animation-delay: 0.6s">
        获得了 <text class="highlight">{{ starsEarned }}</text> 颗探险之星
        <text v-if="streakBonus > 0" class="bonus-text">（+{{ streakBonus }} 连续奖励）</text>
      </view>

      <!-- 数据摘要卡片 -->
      <view class="stats-card pop-in" style="animation-delay: 0.7s" v-if="gameResult.total_count > 0">
        <view class="stat-item">
          <view class="stat-value">{{ accuracyText }}</view>
          <view class="stat-label">正确率</view>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <view class="stat-value">{{ speedText }}</view>
          <view class="stat-label">反应速度</view>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <view class="stat-value">{{ focusStars }}</view>
          <view class="stat-label">专注度</view>
        </view>
      </view>

      <!-- 排名卡片 -->
      <view class="ranking-card pop-in" style="animation-delay: 0.8s" v-if="rankingLoaded">
        <view class="ranking-row">
          <view class="ranking-icon">
            <text class="ph ph-ranking"></text>
          </view>
          <view class="ranking-info">
            <view class="ranking-title">
              成绩超过了
              <text class="ranking-highlight">{{ ranking.percentile }}%</text>
              的玩家
            </view>
            <view class="ranking-sub">共 {{ ranking.total_players }} 人参与 · 平均分 {{ ranking.avg_score }} 分</view>
          </view>
        </view>
        <!-- 低分时显示筛查引导（中性语言） -->
        <view class="screening-hint" v-if="ranking.suggest_screening" @click="goToScreeningQR">
          <view class="hint-icon"><text class="ph ph-clipboard-text"></text></view>
          <view class="hint-content">
            <view class="hint-title">想了解孩子的读写能力？</view>
            <view class="hint-desc">扫码获取专业读写能力筛查工具</view>
          </view>
          <text class="ph ph-arrow-right hint-arrow"></text>
        </view>
      </view>

      <!-- 连续打卡展示 -->
      <view class="streak-card pop-in" style="animation-delay: 0.85s" v-if="currentStreak > 0">
        <text class="streak-fire">🔥</text>
        <view class="streak-info">
          <view class="streak-title">连续挑战 {{ currentStreak }} 天！</view>
          <view class="streak-hint" v-if="nextMilestone > 0">
            再坚持 {{ nextMilestone - currentStreak }} 天解锁特别徽章 🏅
          </view>
          <view class="streak-hint" v-else>
            你已经达成所有连续打卡里程碑！🏆
          </view>
        </view>
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

      <!-- 新获得徽章展示 -->
      <view class="new-badges-section pop-in" style="animation-delay: 1.15s" v-if="newBadgeKeys.length > 0">
        <view class="new-badges-title">🏅 新获得徽章！</view>
        <view class="new-badges-row">
          <view class="new-badge-item" v-for="key in newBadgeKeys" :key="key">
            <view class="new-badge-icon">{{ getBadgeIcon(key) }}</view>
            <view class="new-badge-name">{{ getBadgeName(key) }}</view>
          </view>
        </view>
      </view>

      <!-- 总星星数 -->
      <view class="total-stars pop-in" style="animation-delay: 1.1s">
        <text class="ph ph-star"></text>
        累计 {{ totalStars }} 颗星星
      </view>

      <!-- 操作按钮 -->
      <view class="btn-row pop-in" style="animation-delay: 1.2s">
        <button class="continue-btn" @click="continueChallenge">
          <text class="ph ph-play"></text> 继续挑战
        </button>
        <button class="return-btn" @click="returnHome">
          回到首页
        </button>
      </view>

      <view class="parent-note pop-in" style="animation-delay: 1.3s">
        （结果已自动发送给爸爸妈妈）
      </view>

      <view style="height: 80rpx;"></view>
      </view><!-- end content-inner -->
    </scroll-view>
  </view>
</template>

<script>
import { getTotalStars } from '../../../api/training.js'
import { getEncouragement } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { getGameRanking } from '../../../api/screening.js'

export default {
  data() {
    return {
      starsEarned: 1,
      streakBonus: 0,
      currentStreak: 0,
      totalStars: 0,
      encouragement: '',
      encLoading: false,
      gameResult: {},
      newBadgeKeys: [],
      ranking: null,
      rankingLoaded: false,
      // 星星飞入位置
      starItems: [
        { left: '30%', top: '20%' },
        { left: '50%', top: '10%' },
        { left: '70%', top: '20%' },
      ],
    }
  },
  computed: {
    accuracyText() {
      const { correct_count, total_count } = this.gameResult
      if (!total_count) return '--'
      const pct = Math.round((correct_count / total_count) * 100)
      return pct + '%'
    },
    speedText() {
      const score = this.gameResult.score || 0
      if (score >= 80) return '⚡ 快'
      if (score >= 60) return '🚀 中'
      return '🐢 慢'
    },
    focusStars() {
      const score = this.gameResult.score || 0
      const filled = Math.round(score / 20)
      return '★'.repeat(Math.max(1, filled)) + '☆'.repeat(Math.max(0, 5 - filled))
    },
    nextMilestone() {
      const s = this.currentStreak
      if (s < 3) return 3
      if (s < 7) return 7
      if (s < 30) return 30
      return 0
    },
  },
  onLoad() {
    uni.removeStorageSync('current_screening')
    uni.removeStorageSync('pending_task_id')

    const gameResult = uni.getStorageSync('last_game_result') || {}
    this.gameResult = gameResult
    this.starsEarned = gameResult.stars || 1
    this.streakBonus = gameResult.streak_bonus || 0
    this.currentStreak = gameResult.current_streak || 0
    this.newBadgeKeys = gameResult.new_badges || []

    // 根据获得的星星数调整星星显示数量
    const count = Math.min(5, Math.max(1, this.starsEarned + this.streakBonus))
    this.starItems = Array.from({ length: count }, (_, i) => ({
      left: (20 + i * 15) + '%',
      top: (10 + (i % 2) * 15) + '%',
    }))

    this.loadStars()
    this.loadEncouragement(gameResult)
    this.loadRanking(gameResult)
  },
  methods: {
    async loadRanking(gameResult) {
      const score = gameResult.score || 0
      const gameType = gameResult.game_type || 'visual'
      if (!score) return
      try {
        const res = await getGameRanking(gameType, score)
        this.ranking = res
        this.rankingLoaded = true
      } catch (e) {
        // 静默失败
      }
    },
    goToScreeningQR() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
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
        const score = gameResult.score || 80
        const name = child.name || '小朋友'
        if (score >= 80) {
          this.encouragement = `哇，${name}太厉害了！🌟 继续加油！`
        } else if (score >= 60) {
          this.encouragement = `${name}做得很棒！💪 再练练会更厉害的！`
        } else {
          this.encouragement = `${name}已经很努力了！🌈 下次一定会更好！`
        }
      } finally {
        this.encLoading = false
      }
    },

    continueChallenge() {
      uni.removeStorageSync('last_game_result')
      uni.redirectTo({ url: '/pages/child/child-training/index' })
    },

    returnHome() {
      uni.removeStorageSync('last_game_result')
      uni.redirectTo({ url: '/pages/child/child-training/index' })
    },

    getBadgeIcon(key) {
      const icons = {
        first_game: '🚀', week_streak: '🔥', month_streak: '🏆',
        all_games: '🌟', perfect_score: '💎', speed_demon: '⚡',
      }
      return icons[key] || '🏅'
    },

    getBadgeName(key) {
      const names = {
        first_game: '初次探险', week_streak: '坚持一周', month_streak: '月度冠军',
        all_games: '全能探险家', perfect_score: '完美表现', speed_demon: '闪电侠',
      }
      return names[key] || key
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* 顶部渐变背景 */
.top-bg {
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 50%;
  background: linear-gradient(180deg, #EFF6FF 0%, transparent 100%);
  pointer-events: none;
}

/* 星星飞入动画区 */
.stars-area {
  width: 100%;
  height: 200rpx;
  position: relative;
  flex-shrink: 0;
  margin-top: 80rpx;
}

.star-item {
  position: absolute;
  font-size: 80rpx;
  color: #4F9EF8;
  filter: drop-shadow(0 4rpx 12rpx rgba(79, 158, 248, 0.4));
  opacity: 0;
  animation: starFly 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes starFly {
  0% { transform: scale(0) rotate(-180deg); opacity: 0; }
  60% { transform: scale(1.3) rotate(10deg); opacity: 1; }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

/* 内容区 */
.content-area {
  flex: 1;
  position: relative;
  z-index: 1;
}

.content-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 32rpx 80rpx;
  width: 100%;
  box-sizing: border-box;
}

.congrats-title {
  font-size: 56rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 12rpx;
  letter-spacing: 2rpx;
  text-align: center;
  width: 100%;
}

.congrats-desc {
  font-size: 28rpx;
  color: #718096;
  text-align: center;
  line-height: 1.7;
  margin-bottom: 32rpx;
  font-weight: 500;
  width: 100%;
}

.congrats-desc .highlight {
  font-size: 44rpx;
  font-weight: 800;
  color: #F57F17;
}

.bonus-text {
  font-size: 22rpx;
  color: #22C55E;
  font-weight: 700;
}

/* 数据摘要卡片 */
.stats-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx 0;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
}

.stat-value {
  font-size: 32rpx;
  font-weight: 800;
  color: #2D3748;
}

.stat-label {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.stat-divider {
  width: 2rpx;
  height: 48rpx;
  background: #F3F4F6;
}

/* 排名卡片 */
.ranking-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.ranking-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.ranking-icon {
  width: 64rpx; height: 64rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.ranking-icon .ph { font-size: 32rpx; color: #F57F17; }

.ranking-info { flex: 1; }

.ranking-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  line-height: 1.4;
}

.ranking-highlight {
  font-size: 32rpx;
  font-weight: 900;
  color: #F57F17;
}

.ranking-sub {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 4rpx;
  font-weight: 500;
}

/* 筛查引导提示 */
.screening-hint {
  display: flex;
  align-items: center;
  gap: 14rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #BFDBFE;
  border-radius: 16rpx;
  padding: 18rpx 20rpx;
  margin-top: 16rpx;
  transition: all 0.2s;
}

.screening-hint:active { transform: scale(0.98); }

.hint-icon {
  width: 52rpx; height: 52rpx;
  border-radius: 12rpx;
  background: rgba(79, 158, 248, 0.15);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.hint-icon .ph { font-size: 26rpx; color: #4F9EF8; }

.hint-content { flex: 1; }

.hint-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #1E40AF;
  margin-bottom: 2rpx;
}

.hint-desc {
  font-size: 20rpx;
  color: #3B82F6;
  font-weight: 500;
}

.hint-arrow { font-size: 22rpx; color: #4F9EF8; flex-shrink: 0; }

/* 连续打卡卡片 */
.streak-card {
  width: 100%;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FDE68A;
  border-radius: 24rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.1);
}

.streak-fire {
  font-size: 48rpx;
  flex-shrink: 0;
}

.streak-info {
  flex: 1;
}

.streak-title {
  font-size: 28rpx;
  font-weight: 800;
  color: #92400E;
  margin-bottom: 4rpx;
}

.streak-hint {
  font-size: 22rpx;
  color: #B45309;
  font-weight: 500;
}

/* AI 鼓励 */
.ai-encouragement {
  display: flex;
  align-items: flex-end;
  gap: 12rpx;
  margin-bottom: 24rpx;
  width: 100%;
}

.ai-enc-avatar {
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.25);
}

.ai-enc-avatar .ph { font-size: 32rpx; color: #FFFFFF; }

.ai-enc-bubble {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #BFDBFE;
  border-radius: 24rpx;
  border-bottom-left-radius: 6rpx;
  padding: 20rpx 24rpx;
  flex: 1;
}

.ai-enc-text { font-size: 26rpx; color: #2D3748; line-height: 1.6; font-weight: 500; }

.ai-encouragement-loading {
  display: flex; justify-content: center;
  margin-bottom: 24rpx; height: 64rpx; align-items: center;
}

.enc-dots { display: flex; gap: 12rpx; }
.enc-dot {
  width: 16rpx; height: 16rpx; border-radius: 50%;
  background: #4F9EF8;
  animation: enc-bounce 1.2s infinite;
}
.enc-dot:nth-child(2) { animation-delay: 0.2s; }
.enc-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes enc-bounce {
  0%, 80%, 100% { transform: scale(0.6) translateY(0); opacity: 0.4; }
  40% { transform: scale(1.1) translateY(-10rpx); opacity: 1; }
}

/* 总星星数 */
.total-stars {
  display: flex; align-items: center; gap: 10rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  padding: 16rpx 36rpx; border-radius: 20rpx;
  font-size: 26rpx; font-weight: 700; color: #2D3748;
  margin-bottom: 40rpx;
  box-shadow: 0 4rpx 12rpx rgba(79, 158, 248, 0.15);
}

.total-stars .ph { font-size: 28rpx; color: #4F9EF8; }

/* 按钮行 */
.btn-row {
  width: 100%;
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
}

.continue-btn {
  flex: 1;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  transition: all 0.2s;
}

.continue-btn:active { transform: scale(0.97); }
.continue-btn .ph { font-size: 26rpx; }

.return-btn {
  flex: 1;
  background: #FFFFFF;
  color: #718096;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  border: 2rpx solid #E5E7EB;
  transition: all 0.2s;
}

.return-btn:active { background: #F5F5F5; }

.parent-note {
  font-size: 22rpx;
  color: #A0AEC0;
  text-align: center;
  font-weight: 500;
  width: 100%;
}

/* 新获得徽章 */
.new-badges-section {
  width: 100%;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FDE68A;
  border-radius: 24rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.new-badges-title {
  font-size: 26rpx;
  font-weight: 800;
  color: #92400E;
  margin-bottom: 16rpx;
  text-align: center;
}

.new-badges-row {
  display: flex;
  justify-content: center;
  gap: 24rpx;
  flex-wrap: wrap;
}

.new-badge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  animation: badgePop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

@keyframes badgePop {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.new-badge-icon { font-size: 56rpx; }
.new-badge-name { font-size: 20rpx; font-weight: 700; color: #92400E; }

/* 入场动画 */
@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.05); }
  100% { transform: scale(1); opacity: 1; }
}

.pop-in {
  opacity: 0;
  animation: popIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
</style>
