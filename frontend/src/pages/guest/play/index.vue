<template>
  <view class="page-container">
    <!-- 顶部品牌区 -->
    <view class="hero-section">
      <view class="hero-bg"></view>
      <view class="hero-content">
        <view class="brand-icon">🌟</view>
        <view class="brand-name">悦读小灯塔</view>
        <view class="brand-tagline">趣味文字游戏 · 亲子互动 · 每日打卡</view>
        <view class="brand-sub">随便玩玩，顺便了解孩子的读写小秘密</view>
        <view class="hero-badge">
          <text class="ph ph-play-circle"></text>
          立即试玩，无需注册！
        </view>
      </view>
    </view>

    <!-- 游戏选择区 -->
    <view class="section-title-row">
      <view class="section-title">选一个游戏开始吧 🎮</view>
      <view class="section-sub">6种趣味挑战，发现孩子的读写小秘密</view>
    </view>

    <view class="game-grid">
      <view
        v-for="g in gameTypes"
        :key="g.type"
        :class="['game-card', { active: selectedType === g.type }]"
        :style="{ '--c': g.color, '--bg': g.bg }"
        @click="selectedType = g.type"
      >
        <view class="game-card-top">
          <view class="game-icon">
            <text :class="'ph ' + g.icon"></text>
          </view>
          <view class="game-check" v-if="selectedType === g.type">
            <text class="ph ph-check-circle"></text>
          </view>
        </view>
        <view class="game-name">{{ g.name }}</view>
        <view class="game-desc">{{ g.desc }}</view>
        <view class="game-time">
          <text class="ph ph-clock"></text>
          约{{ g.minutes }}分钟
        </view>
      </view>
    </view>

    <!-- 开始按钮 -->
    <view class="action-area">
      <button class="start-btn" @click="startGame">
        <text class="ph ph-rocket"></text>
        开始挑战！
      </button>
      <view class="tip-row">
        <text class="ph ph-shield-check"></text>
        <text>无需注册，完全免费，结果仅供参考</text>
      </view>
    </view>

    <!-- 登录入口 -->
    <view class="login-row">
      <view class="login-text">已有账号？</view>
      <view class="login-link" @click="goToLogin">登录查看完整报告</view>
    </view>

    <!-- 底部说明 -->
    <view class="footer-note">
      <text class="ph ph-info"></text>
      本游戏仅供家庭参考，结果不代表医学诊断
    </view>

    <!-- 专业筛查引导区 -->
    <view class="screening-section">
      <view class="screening-divider">
        <view class="divider-line"></view>
        <view class="divider-text">想更深入了解？</view>
        <view class="divider-line"></view>
      </view>
      <view class="screening-card">
        <view class="screening-card-header">
          <view class="screening-badge">专业筛查</view>
          <view class="screening-title">读写能力风险筛查</view>
          <view class="screening-desc">由专业团队提供，扫码即可完成，结果由专业老师解读</view>
        </view>
        <view class="screening-qr-wrap">
          <image
            class="screening-qr"
            src="/static/images/screening_qr.png"
            mode="aspectFit"
            @error="qrError = true"
          />
          <view class="screening-qr-placeholder" v-if="qrError">
            <text class="ph ph-qr-code"></text>
            <text>筛查二维码</text>
          </view>
        </view>
        <view class="screening-tips">
          <view class="screening-tip">
            <text class="ph ph-check-circle"></text>
            <text>专业团队设计，科学可靠</text>
          </view>
          <view class="screening-tip">
            <text class="ph ph-check-circle"></text>
            <text>筛查数据由专业老师查看</text>
          </view>
          <view class="screening-tip">
            <text class="ph ph-check-circle"></text>
            <text>高风险可联系专业导师</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getOrCreateGuestSession } from '../../../utils/guestSession.js'

const GAME_TYPES = [
  {
    type: 'visual',
    name: '视觉辨识',
    desc: '找不同，练眼力',
    icon: 'ph-eye',
    color: '#4F9EF8',
    bg: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
    minutes: 3,
  },
  {
    type: 'spelling',
    name: '拼字识别',
    desc: '认汉字，练拼写',
    icon: 'ph-text-aa',
    color: '#A78BFA',
    bg: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
    minutes: 3,
  },
  {
    type: 'comprehension',
    name: '文字理解',
    desc: '读故事，练理解',
    icon: 'ph-book-open',
    color: '#22C55E',
    bg: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
    minutes: 4,
  },
  {
    type: 'working_memory',
    name: '工作记忆',
    desc: '记序列，练记忆',
    icon: 'ph-brain',
    color: '#F97316',
    bg: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)',
    minutes: 4,
  },
  {
    type: 'rapid_naming',
    name: '快速命名',
    desc: '快说出，练反应',
    icon: 'ph-lightning',
    color: '#EAB308',
    bg: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)',
    minutes: 3,
  },
  {
    type: 'motor_coordination',
    name: '精细动作',
    desc: '判线条，练协调',
    icon: 'ph-hand',
    color: '#EC4899',
    bg: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)',
    minutes: 3,
  },
]

export default {
  data() {
    return {
      selectedType: 'visual',
      gameTypes: GAME_TYPES,
      qrError: false,
    }
  },
  onLoad(options) {
    // 记录分享来源
    if (options.ref) {
      try {
        uni.setStorageSync('share_ref', options.ref)
      } catch (e) {}
    }
    // 如果已登录，跳转到儿童端首页
    try {
      const token = uni.getStorageSync('token')
      if (token) {
        uni.reLaunch({ url: '/pages/child/child-training/index' })
      }
    } catch (e) {}
  },
  methods: {
    startGame() {
      // 确保游客会话存在
      const session = getOrCreateGuestSession()
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${this.selectedType}&guest_mode=true&guest_id=${session.guest_id}`,
      })
    },
    goToLogin() {
      uni.navigateTo({ url: '/pages/parent/auth/login' })
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

/* 顶部品牌区 */
.hero-section {
  position: relative;
  background: linear-gradient(135deg, #4F9EF8 0%, #7C3AED 100%);
  padding: 80rpx 40rpx 60rpx;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  right: -60rpx;
  top: -60rpx;
  width: 300rpx;
  height: 300rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.brand-icon {
  font-size: 80rpx;
  margin-bottom: 16rpx;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

.brand-name {
  font-size: 44rpx;
  font-weight: 900;
  color: #FFFFFF;
  margin-bottom: 8rpx;
  letter-spacing: 2rpx;
}

.brand-tagline {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8rpx;
  font-weight: 600;
  letter-spacing: 1rpx;
}

.brand-sub {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 28rpx;
  font-weight: 400;
}

.hero-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: rgba(255, 255, 255, 0.2);
  border: 2rpx solid rgba(255, 255, 255, 0.4);
  border-radius: 9999rpx;
  padding: 12rpx 28rpx;
  font-size: 24rpx;
  color: #FFFFFF;
  font-weight: 700;
}

.hero-badge .ph {
  font-size: 28rpx;
}

/* 区域标题 */
.section-title-row {
  padding: 32rpx 32rpx 16rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 6rpx;
}

.section-sub {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 游戏网格 */
.game-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  padding: 0 32rpx;
  margin-bottom: 32rpx;
}

.game-card {
  width: calc(50% - 8rpx);
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx 20rpx;
  border: 3rpx solid transparent;
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.game-card:active {
  transform: scale(0.96);
}

.game-card.active {
  background: var(--bg);
  border-color: var(--c);
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.1);
}

.game-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12rpx;
}

.game-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 18rpx;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.game-card.active .game-icon {
  background: rgba(255, 255, 255, 0.7);
}

.game-icon .ph {
  font-size: 32rpx;
  color: var(--c);
}

.game-check .ph {
  font-size: 32rpx;
  color: var(--c);
}

.game-name {
  font-size: 28rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 4rpx;
}

.game-desc {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 500;
  margin-bottom: 12rpx;
}

.game-time {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 20rpx;
  color: #CBD5E0;
  font-weight: 500;
}

.game-time .ph {
  font-size: 20rpx;
}

/* 操作区 */
.action-area {
  padding: 0 32rpx;
  margin-bottom: 24rpx;
}

.start-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #7C3AED);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  font-size: 34rpx;
  font-weight: 900;
  box-shadow: 0 8rpx 24rpx rgba(79, 158, 248, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  margin-bottom: 16rpx;
  letter-spacing: 2rpx;
  transition: all 0.2s;
}

.start-btn:active {
  transform: scale(0.97);
}

.start-btn .ph {
  font-size: 36rpx;
}

.tip-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.tip-row .ph {
  font-size: 22rpx;
  color: #22C55E;
}

/* 登录入口 */
.login-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 16rpx 32rpx;
  margin-bottom: 24rpx;
}

.login-text {
  font-size: 26rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.login-link {
  font-size: 26rpx;
  color: #4F9EF8;
  font-weight: 700;
  text-decoration: underline;
}

/* 底部说明 */
.footer-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: #CBD5E0;
  font-weight: 500;
  padding: 0 32rpx;
  margin-bottom: 40rpx;
}

.footer-note .ph {
  font-size: 20rpx;
}

/* 专业筛查引导区 */
.screening-section {
  padding: 0 32rpx 60rpx;
}

.screening-divider {
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

.screening-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.05);
  border: 2rpx solid #EDE9FE;
}

.screening-card-header {
  margin-bottom: 20rpx;
}

.screening-badge {
  display: inline-block;
  background: linear-gradient(135deg, #7C3AED, #A78BFA);
  color: #FFFFFF;
  font-size: 18rpx;
  font-weight: 700;
  padding: 4rpx 16rpx;
  border-radius: 9999rpx;
  margin-bottom: 10rpx;
}

.screening-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
}

.screening-desc {
  font-size: 22rpx;
  color: #718096;
  line-height: 1.6;
  font-weight: 500;
}

.screening-qr-wrap {
  width: 200rpx;
  height: 200rpx;
  margin: 0 auto 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #F5F7FA;
  border: 2rpx solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.screening-qr {
  width: 100%;
  height: 100%;
}

.screening-qr-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  color: #A0AEC0;
  font-size: 18rpx;
}

.screening-qr-placeholder .ph {
  font-size: 60rpx;
  color: #A78BFA;
}

.screening-tips {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.screening-tip {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 22rpx;
  color: #4A5568;
  font-weight: 500;
}

.screening-tip .ph {
  font-size: 24rpx;
  color: #7C3AED;
  flex-shrink: 0;
}
</style>
