<template>
  <view class="page-container">
    <!-- 顶部庆祝区 -->
    <view class="celebrate-section" :style="{ background: themeGradient }">
      <view class="celebrate-bg"></view>
      <view class="celebrate-content">
        <view class="mascot-emoji">{{ abilityInfo.emoji }}</view>
        <view class="celebrate-title">完成挑战！</view>
        <view class="ability-label">{{ abilityInfo.label }}</view>
      </view>
    </view>

    <!-- 分数展示 -->
    <view class="score-card">
      <view class="score-number">{{ score }}</view>
      <view class="score-unit">分</view>
      <view class="score-bar-wrap">
        <view class="score-bar-track">
          <view class="score-bar-fill" :style="{ width: score + '%', background: themeColor }"></view>
        </view>
      </view>
      <view class="ability-desc">{{ abilityInfo.desc }}</view>
    </view>

    <!-- 排名卡片 -->
    <view class="ranking-card" v-if="rankingLoaded">
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
      <!-- 低分引导：低于平均分时显示筛查提示（中性语言，不暗示风险） -->
      <view class="screening-hint" v-if="ranking.suggest_screening" @click="goToScreeningQR">
        <view class="hint-icon">
          <text class="ph ph-clipboard-text"></text>
        </view>
        <view class="hint-content">
          <view class="hint-title">想了解孩子的读写能力？</view>
          <view class="hint-desc">扫码获取专业读写能力筛查工具，由专业老师解读结果</view>
        </view>
        <view class="hint-arrow">
          <text class="ph ph-arrow-right"></text>
        </view>
      </view>
    </view>

    <!-- 鼓励话语 -->
    <view class="encouragement-card" v-if="encouragement">
      <view class="enc-icon">💬</view>
      <view class="enc-text">{{ encouragement }}</view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-area">
      <button class="share-btn" @click="shareResult">
        <text class="ph ph-share-network"></text>
        分享这张卡片
      </button>
      <button class="replay-btn" @click="playAgain">
        <text class="ph ph-arrow-counter-clockwise"></text>
        再玩一次
      </button>
    </view>

    <!-- 注册引导区（游客模式） -->
    <view class="register-guide" v-if="isGuest">
      <view class="guide-divider">
        <view class="divider-line"></view>
        <view class="divider-text">想了解更多？</view>
        <view class="divider-line"></view>
      </view>
      <view class="guide-title">保存游戏记录，追踪成长变化</view>
      <view class="guide-desc">注册后可查看历次游戏成绩，了解孩子的阅读文字能力变化</view>
      <view class="guide-btns">
        <button class="wx-login-btn" @click="handleWechatLogin">
          <text class="ph" :class="isMpWeixin ? 'ph-wechat-logo' : 'ph-user-plus'"></text>
          {{ isMpWeixin ? '微信一键登录' : '注册账号（3秒完成）' }}
        </button>
        <view class="login-link" @click="goLogin">已有账号？登录</view>
      </view>
    </view>

    <!-- 已登录用户：返回首页 -->
    <view class="logged-action" v-else>
      <button class="home-btn" @click="goHome">
        <text class="ph ph-house"></text>
        回到首页
      </button>
    </view>
  </view>
</template>

<script>
import { getAbilityLabel } from '../../../utils/abilityLabels.js'
import { isGuestMode, getGuestId, clearGuestSession } from '../../../utils/guestSession.js'
import { getGameTheme } from '../../../utils/gameThemes.js'
import { post } from '../../../api/index.js'
import { getGameRanking } from '../../../api/screening.js'

export default {
  data() {
    return {
      score: 0,
      gameType: 'visual',
      guestId: '',
      encouragement: '',
      isGuest: true,
      isMpWeixin: false,
      ranking: null,
      rankingLoaded: false,
      abilityInfo: {
        label: '小小探险家',
        emoji: '🌟',
        desc: '你完成了挑战，真棒！',
      },
    }
  },
  computed: {
    themeColor() {
      return getGameTheme(this.gameType).primary
    },
    themeGradient() {
      return getGameTheme(this.gameType).gradient
    },
  },
  onLoad(options) {
    this.isGuest = isGuestMode()
    this.gameType = options.game_type || 'visual'
    this.guestId = options.guest_id || getGuestId() || ''

    // 检测是否在微信小程序环境
    try {
      const sysInfo = uni.getSystemInfoSync()
      this.isMpWeixin = sysInfo.uniPlatform === 'mp-weixin'
    } catch (e) {
      this.isMpWeixin = false
    }

    // 从本地存储读取游戏结果（游客模式由 prep/game 页面写入）
    try {
      const result = uni.getStorageSync('last_guest_result') || {}
      this.score = result.score || Number(options.score) || 0
      this.encouragement = result.encouragement || ''
      const info = getAbilityLabel(this.gameType, this.score)
      if (info) this.abilityInfo = info
    } catch (e) {
      this.score = Number(options.score) || 0
      const info = getAbilityLabel(this.gameType, this.score)
      if (info) this.abilityInfo = info
    }

    // 加载排名数据
    this.loadRanking()
  },
  methods: {
    async loadRanking() {
      if (!this.score) return
      try {
        const res = await getGameRanking(this.gameType, this.score)
        this.ranking = res
        this.rankingLoaded = true
      } catch (e) {
        // 静默失败，不影响主流程
        this.rankingLoaded = false
      }
    },
    goToScreeningQR() {
      // 跳转到家长端筛查页（二维码）
      if (this.isGuest) {
        // 游客先引导注册
        uni.showModal({
          title: '需要登录',
          content: '查看专业筛查二维码需要先注册账号',
          confirmText: '去注册',
          cancelText: '取消',
          success: (res) => {
            if (res.confirm) {
              uni.navigateTo({ url: '/pages/parent/auth/register' })
            }
          }
        })
      } else {
        uni.navigateTo({ url: '/pages/parent/screening/index' })
      }
    },
    shareResult() {
      const title = `我家孩子的${this.getGameName()}能力测试：${this.abilityInfo.label}！`
      const desc = `得了${this.score}分！快来测测你家孩子的读写能力～`
      // #ifdef MP-WEIXIN
      uni.showShareMenu({ withShareTicket: true })
      // #endif
      // #ifdef H5
      if (typeof navigator !== 'undefined' && navigator.share) {
        navigator.share({
          title,
          text: desc,
          url: typeof window !== 'undefined' ? window.location.href : '',
        }).catch(() => {})
      } else {
        uni.showToast({ title: '链接已复制，快去分享吧！', icon: 'none' })
      }
      // #endif
    },
    playAgain() {
      uni.redirectTo({
        url: `/pages/guest/play/index`,
      })
    },
    async handleWechatLogin() {
      // 非微信小程序环境，降级到手机号注册
      if (!this.isMpWeixin) {
        uni.navigateTo({ url: '/pages/parent/auth/register' })
        return
      }
      try {
        // 1. 获取微信授权码
        const loginResult = await uni.login({ provider: 'weixin' })
        const { code } = loginResult

        // 2. 发送给后端，携带 guest_id 迁移游客数据
        const res = await post('/api/auth/wx-login', {
          code,
          guest_id: this.guestId || undefined,
        })

        // 3. 存储 token，清除游客会话
        if (res && res.access_token) {
          uni.setStorageSync('token', res.access_token)
          clearGuestSession()

          // 4. 提示迁移结果
          if (res.migrated_count > 0) {
            uni.showToast({ title: `已保存 ${res.migrated_count} 条游戏记录`, icon: 'none', duration: 2000 })
          } else {
            uni.showToast({ title: '登录成功', icon: 'success', duration: 1500 })
          }

          // 5. 跳转家长首页
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/parent/home/index' })
          }, 1500)
        }
      } catch (err) {
        // 降级：跳转手机号注册
        uni.navigateTo({ url: '/pages/parent/auth/register' })
      }
    },
    goRegister() {
      uni.navigateTo({ url: '/pages/parent/auth/register' })
    },
    goLogin() {
      uni.navigateTo({ url: '/pages/parent/auth/login' })
    },
    goHome() {
      uni.reLaunch({ url: '/pages/child/child-training/index' })
    },
    getGameName() {
      const names = {
        visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
        working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
      }
      return names[this.gameType] || '读写能力'
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 60rpx;
}

/* 庆祝区 */
.celebrate-section {
  position: relative;
  padding: 80rpx 40rpx 60rpx;
  overflow: hidden;
}

.celebrate-bg {
  position: absolute;
  right: -80rpx;
  top: -80rpx;
  width: 320rpx;
  height: 320rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.celebrate-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mascot-emoji {
  font-size: 100rpx;
  margin-bottom: 16rpx;
  animation: bounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes bounce {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}

.celebrate-title {
  font-size: 48rpx;
  font-weight: 900;
  color: #FFFFFF;
  margin-bottom: 12rpx;
  letter-spacing: 2rpx;
}

.ability-label {
  font-size: 32rpx;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.2);
  padding: 10rpx 28rpx;
  border-radius: 9999rpx;
}

/* 分数卡片 */
.score-card {
  background: #FFFFFF;
  margin: 24rpx 32rpx;
  border-radius: 28rpx;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.score-number {
  font-size: 96rpx;
  font-weight: 900;
  color: #2D3748;
  line-height: 1;
  margin-bottom: 4rpx;
}

.score-unit {
  font-size: 28rpx;
  color: #A0AEC0;
  font-weight: 600;
  margin-bottom: 24rpx;
}

.score-bar-wrap {
  width: 100%;
  margin-bottom: 20rpx;
}

.score-bar-track {
  height: 16rpx;
  background: #F3F4F6;
  border-radius: 9999rpx;
  overflow: hidden;
}

.score-bar-fill {
  height: 100%;
  border-radius: 9999rpx;
  transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.ability-desc {
  font-size: 26rpx;
  color: #718096;
  text-align: center;
  font-weight: 500;
  line-height: 1.6;
}

/* 排名卡片 */
.ranking-card {
  background: #FFFFFF;
  margin: 0 32rpx 24rpx;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.ranking-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 0;
}

.ranking-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ranking-icon .ph {
  font-size: 32rpx;
  color: #F57F17;
}

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

/* 低分引导筛查提示 */
.screening-hint {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #BFDBFE;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-top: 16rpx;
  transition: all 0.2s;
}

.screening-hint:active {
  transform: scale(0.98);
}

.hint-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: rgba(79, 158, 248, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hint-icon .ph {
  font-size: 28rpx;
  color: #4F9EF8;
}

.hint-content { flex: 1; }

.hint-title {
  font-size: 24rpx;
  font-weight: 700;
  color: #1E40AF;
  margin-bottom: 4rpx;
}

.hint-desc {
  font-size: 20rpx;
  color: #3B82F6;
  font-weight: 500;
  line-height: 1.4;
}

.hint-arrow {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: rgba(79, 158, 248, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.hint-arrow .ph {
  font-size: 24rpx;
  color: #4F9EF8;
}

/* 鼓励话语 */
.encouragement-card {
  background: linear-gradient(135deg, #FFFDE7, #FFF9C4);
  border: 2rpx solid #FFE082;
  margin: 0 32rpx 24rpx;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.enc-icon {
  font-size: 36rpx;
  flex-shrink: 0;
}

.enc-text {
  font-size: 26rpx;
  color: #2D3748;
  font-weight: 500;
  line-height: 1.6;
  flex: 1;
}

/* 操作按钮 */
.action-area {
  padding: 0 32rpx;
  margin-bottom: 32rpx;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.share-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #7C3AED);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 6rpx 20rpx rgba(79, 158, 248, 0.35);
}

.share-btn .ph {
  font-size: 32rpx;
}

.replay-btn {
  width: 100%;
  background: #FFFFFF;
  color: #4F9EF8;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border: 3rpx solid #BFDBFE;
}

.replay-btn .ph {
  font-size: 32rpx;
}

/* 注册引导 */
.register-guide {
  margin: 0 32rpx;
  background: #FFFFFF;
  border-radius: 28rpx;
  padding: 32rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.guide-divider {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.divider-line {
  flex: 1;
  height: 2rpx;
  background: #E5E7EB;
}

.divider-text {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 600;
  white-space: nowrap;
}

.guide-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
  text-align: center;
}

.guide-desc {
  font-size: 22rpx;
  color: #A0AEC0;
  text-align: center;
  margin-bottom: 24rpx;
  font-weight: 500;
  line-height: 1.6;
}

.guide-btns {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  align-items: center;
}

.wx-login-btn {
  width: 100%;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.3);
}

.wx-login-btn .ph {
  font-size: 30rpx;
}

.login-link {
  font-size: 24rpx;
  color: #4F9EF8;
  font-weight: 600;
  text-decoration: underline;
}

/* 已登录用户操作 */
.logged-action {
  padding: 0 32rpx;
}

.home-btn {
  width: 100%;
  background: #FFFFFF;
  color: #4F9EF8;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border: 3rpx solid #BFDBFE;
}

.home-btn .ph {
  font-size: 32rpx;
}
</style>
