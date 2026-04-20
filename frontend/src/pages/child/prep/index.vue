<template>
  <view class="page-container">
    <view class="back-btn" @click="goBack">
      <text class="ph ph-arrow-left"></text>
    </view>

    <!-- 卡通角色欢迎动画区 -->
    <view class="mascot-area">
      <view class="mascot-body" :class="{ bounce: mascotBounce }">
        <view class="mascot-face">
          <view class="mascot-eyes">
            <view class="eye left" :class="{ blink: eyeBlink }"></view>
            <view class="eye right" :class="{ blink: eyeBlink }"></view>
          </view>
          <view class="mascot-mouth"></view>
        </view>
        <view class="mascot-antenna">
          <view class="antenna-ball"></view>
        </view>
      </view>
      <!-- 对话气泡 -->
      <view class="speech-bubble" :class="{ show: showBubble }">
        <view class="bubble-text">{{ bubbleText }}</view>
      </view>
      <!-- 装饰星星 -->
      <view class="deco-star s1"><text class="ph ph-star-fill"></text></view>
      <view class="deco-star s2"><text class="ph ph-star-fill"></text></view>
      <view class="deco-star s3"><text class="ph ph-star-fill"></text></view>
    </view>

    <view class="content-area">
      <view class="game-badge">
        <text :class="'ph ' + gameIcon"></text>
        {{ gameName }}
      </view>

      <view class="title">挑战前的小准备</view>

      <!-- 步骤式引导（逐步显示） -->
      <view class="steps-list">
        <view
          class="step-card"
          v-for="(step, i) in steps"
          :key="i"
          :class="['step-' + step.color, { visible: i < visibleSteps }]"
        >
          <view class="step-icon">
            <text :class="'ph ' + step.icon"></text>
          </view>
          <view class="step-content">
            <view class="step-title">{{ step.title }}</view>
            <view class="step-desc">{{ step.desc }}</view>
          </view>
          <view class="step-check" v-if="i < visibleSteps">
            <text class="ph ph-check-circle"></text>
          </view>
        </view>
      </view>

      <!-- 家长辅助提示层 -->
      <view class="parent-hint" v-if="showParentHint">
        <view class="parent-hint-header">
          <text class="ph ph-user-circle"></text>
          <view class="parent-hint-title">家长提示</view>
          <view class="parent-hint-close" @click="showParentHint = false">
            <text class="ph ph-x"></text>
          </view>
        </view>
        <view class="parent-hint-text">
          请将设备交给孩子，确保环境安静。游戏约需 <text class="bold">3-5 分钟</text>，请勿中途打扰。孩子答错时不要纠正，让系统自动记录。
        </view>
      </view>

      <!-- 难度提示 -->
      <view class="difficulty-hint">
        <text class="ph ph-star difficulty-icon"></text>
        <view class="difficulty-text">已为你准备好适合的题目，加油！</view>
        <view class="parent-hint-btn" @click="showParentHint = !showParentHint">
          <text class="ph ph-info"></text>
        </view>
      </view>

      <button class="ready-btn" :class="{ pulse: readyPulse }" @click="startGame">
        <text class="ph ph-rocket"></text> 我准备好了！
      </button>
    </view>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'

const BUBBLE_TEXTS = [
  '嗨！准备好了吗？🌟',
  '今天的挑战超有趣！',
  '你一定可以的！💪',
  '加油，我陪着你！🚀',
]

export default {
  data() {
    return {
      gameType: 'visual',
      grade: '',
      // 动画状态
      mascotBounce: false,
      eyeBlink: false,
      showBubble: false,
      bubbleText: '',
      bubbleIndex: 0,
      visibleSteps: 0,
      readyPulse: false,
      showParentHint: false,
      steps: [
        { icon: 'ph-headphones', color: 'blue', title: '找个安静的地方', desc: '关掉电视，找个安静的角落' },
        { icon: 'ph-eye', color: 'green', title: '仔细看，认真听', desc: '每道题都要认真思考哦' },
        { icon: 'ph-smiley', color: 'orange', title: '不用害怕答错', desc: '这只是一个有趣的游戏！' },
      ],
      _timers: [],
    }
  },
  computed: {
    gameName() {
      const names = {
        visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
        working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
      }
      return names[this.gameType] || '综合挑战'
    },
    gameIcon() {
      const icons = {
        visual: 'ph-eye', spelling: 'ph-text-aa', comprehension: 'ph-book-open',
        working_memory: 'ph-brain', rapid_naming: 'ph-lightning', motor_coordination: 'ph-hand',
      }
      return icons[this.gameType] || 'ph-star'
    }
  },
  onLoad(options) {
    if (options.game_type) this.gameType = options.game_type
    if (options.grade) {
      this.grade = options.grade
    } else {
      const child = getCurrentChild()
      this.grade = child?.grade || ''
    }
    this.startAnimations()
  },
  onUnload() {
    this._timers.forEach(t => clearTimeout(t))
  },
  methods: {
    startAnimations() {
      // 1. 吉祥物弹跳
      this._t(() => { this.mascotBounce = true }, 200)
      this._t(() => { this.mascotBounce = false }, 800)

      // 2. 显示对话气泡
      this._t(() => {
        this.bubbleText = BUBBLE_TEXTS[0]
        this.showBubble = true
      }, 400)

      // 3. 逐步显示步骤卡片
      this._t(() => { this.visibleSteps = 1 }, 700)
      this._t(() => { this.visibleSteps = 2 }, 1100)
      this._t(() => { this.visibleSteps = 3 }, 1500)

      // 4. 开始按钮脉冲
      this._t(() => { this.readyPulse = true }, 2000)

      // 5. 眨眼循环
      this._startBlinking()

      // 6. 气泡文字轮换
      this._startBubbleRotation()
    },

    _t(fn, delay) {
      const id = setTimeout(fn, delay)
      this._timers.push(id)
      return id
    },

    _startBlinking() {
      const blink = () => {
        this.eyeBlink = true
        this._t(() => { this.eyeBlink = false }, 150)
        this._t(blink, 2500 + Math.random() * 2000)
      }
      this._t(blink, 1500)
    },

    _startBubbleRotation() {
      const rotate = () => {
        this.bubbleIndex = (this.bubbleIndex + 1) % BUBBLE_TEXTS.length
        this.showBubble = false
        this._t(() => {
          this.bubbleText = BUBBLE_TEXTS[this.bubbleIndex]
          this.showBubble = true
        }, 300)
        this._t(rotate, 3500)
      }
      this._t(rotate, 3500)
    },

    goBack() {
      uni.navigateBack()
    },

    startGame() {
      const gradeParam = this.grade ? `&grade=${this.grade}` : ''
      uni.navigateTo({
        url: `/pages/child/game/index?game_type=${this.gameType}${gradeParam}`
      })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #EFF6FF 0%, #F5F7FA 40%);
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

.back-btn {
  padding: 56rpx 32rpx 0;
  display: inline-flex;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }

/* ── 吉祥物区域 ── */
.mascot-area {
  width: 100%;
  height: 280rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 吉祥物身体 */
.mascot-body {
  width: 140rpx;
  height: 140rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  border-radius: 50%;
  position: relative;
  box-shadow: 0 8rpx 32rpx rgba(59, 130, 246, 0.4);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: float 3s ease-in-out infinite;
}
.mascot-body.bounce {
  transform: scale(1.15);
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12rpx); }
}

/* 天线 */
.mascot-antenna {
  position: absolute;
  top: -28rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 6rpx;
  height: 28rpx;
  background: #93C5FD;
  border-radius: 3rpx;
}
.antenna-ball {
  position: absolute;
  top: -14rpx;
  left: 50%;
  transform: translateX(-50%);
  width: 18rpx;
  height: 18rpx;
  background: #FFD93D;
  border-radius: 50%;
  box-shadow: 0 0 8rpx rgba(255, 217, 61, 0.6);
  animation: antennaPulse 1.5s ease-in-out infinite;
}
@keyframes antennaPulse {
  0%, 100% { transform: translateX(-50%) scale(1); box-shadow: 0 0 8rpx rgba(255,217,61,0.6); }
  50% { transform: translateX(-50%) scale(1.3); box-shadow: 0 0 16rpx rgba(255,217,61,0.9); }
}

/* 脸部 */
.mascot-face {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -45%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
}
.mascot-eyes {
  display: flex;
  gap: 20rpx;
}
.eye {
  width: 20rpx;
  height: 20rpx;
  background: #FFFFFF;
  border-radius: 50%;
  position: relative;
  transition: transform 0.1s;
}
.eye::after {
  content: '';
  position: absolute;
  top: 4rpx;
  left: 4rpx;
  width: 10rpx;
  height: 10rpx;
  background: #1E40AF;
  border-radius: 50%;
}
.eye.blink {
  transform: scaleY(0.1);
}
.mascot-mouth {
  width: 36rpx;
  height: 18rpx;
  border-bottom: 5rpx solid #FFFFFF;
  border-left: 5rpx solid transparent;
  border-right: 5rpx solid transparent;
  border-radius: 0 0 18rpx 18rpx;
}

/* 对话气泡 */
.speech-bubble {
  position: absolute;
  right: 60rpx;
  top: 20rpx;
  background: #FFFFFF;
  border-radius: 20rpx;
  border-bottom-left-radius: 4rpx;
  padding: 16rpx 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.1);
  max-width: 240rpx;
  opacity: 0;
  transform: scale(0.8) translateY(10rpx);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.speech-bubble.show {
  opacity: 1;
  transform: scale(1) translateY(0);
}
.speech-bubble::before {
  content: '';
  position: absolute;
  bottom: -14rpx;
  left: 20rpx;
  border: 8rpx solid transparent;
  border-top-color: #FFFFFF;
}
.bubble-text {
  font-size: 24rpx;
  font-weight: 700;
  color: #2D3748;
  white-space: nowrap;
}

/* 装饰星星 */
.deco-star {
  position: absolute;
  animation: twinkle 2s ease-in-out infinite;
}
.deco-star .ph { color: #FFD93D; }
.s1 { top: 30rpx; left: 60rpx; font-size: 28rpx; animation-delay: 0s; }
.s2 { top: 60rpx; right: 80rpx; font-size: 20rpx; animation-delay: 0.5s; }
.s3 { bottom: 30rpx; left: 100rpx; font-size: 24rpx; animation-delay: 1s; }
@keyframes twinkle {
  0%, 100% { opacity: 0.4; transform: scale(1) rotate(0deg); }
  50% { opacity: 1; transform: scale(1.2) rotate(15deg); }
}

/* ── 内容区 ── */
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
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(79, 158, 248, 0.15);
}
.game-badge .ph { font-size: 26rpx; }

.title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 28rpx;
  text-align: center;
}

/* ── 步骤卡片 ── */
.steps-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-bottom: 24rpx;
}

.step-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  opacity: 0;
  transform: translateX(-20rpx);
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.step-card.visible {
  opacity: 1;
  transform: translateX(0);
}
.step-blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.step-green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.step-orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }

.step-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.step-icon .ph { font-size: 32rpx; }
.step-blue .step-icon .ph { color: #4F9EF8; }
.step-green .step-icon .ph { color: #22C55E; }
.step-orange .step-icon .ph { color: #F57F17; }

.step-content { flex: 1; }
.step-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.step-desc { font-size: 20rpx; color: #718096; margin-top: 2rpx; font-weight: 500; }

.step-check .ph { font-size: 32rpx; }
.step-blue .step-check .ph { color: #4F9EF8; }
.step-green .step-check .ph { color: #22C55E; }
.step-orange .step-check .ph { color: #F57F17; }

/* ── 家长辅助提示层 ── */
.parent-hint {
  width: 100%;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FDE68A;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 16rpx;
  animation: slideDown 0.3s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10rpx); }
  to { opacity: 1; transform: translateY(0); }
}
.parent-hint-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 10rpx;
}
.parent-hint-header .ph { font-size: 28rpx; color: #F59E0B; }
.parent-hint-title { flex: 1; font-size: 24rpx; font-weight: 700; color: #92400E; }
.parent-hint-close .ph { font-size: 24rpx; color: #A0AEC0; }
.parent-hint-text { font-size: 22rpx; color: #78350F; line-height: 1.7; font-weight: 500; }
.parent-hint-text .bold { font-weight: 700; color: #92400E; }

/* ── 难度提示 ── */
.difficulty-hint {
  display: flex;
  align-items: center;
  gap: 12rpx;
  background: #FFFFFF;
  border: 2rpx solid #FFE082;
  border-radius: 20rpx;
  padding: 18rpx 24rpx;
  margin-bottom: 32rpx;
  width: 100%;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.15);
}
.difficulty-icon { font-size: 30rpx; color: #F57F17; }
.difficulty-text { flex: 1; font-size: 24rpx; color: #92400E; font-weight: 600; }
.parent-hint-btn {
  width: 48rpx; height: 48rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.parent-hint-btn .ph { font-size: 24rpx; color: #F57F17; }

/* ── 开始按钮 ── */
.ready-btn {
  width: 100%;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 32rpx;
  font-size: 34rpx;
  font-weight: 800;
  box-shadow: 0 6rpx 0 #15803D, 0 8rpx 24rpx rgba(34, 197, 94, 0.35);
  letter-spacing: 2rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  transition: all 0.2s;
}
.ready-btn .ph { font-size: 34rpx; }
.ready-btn:active { transform: translateY(6rpx); box-shadow: 0 1rpx 0 #15803D; }
.ready-btn.pulse {
  animation: readyPulse 1.5s ease-in-out infinite;
}
@keyframes readyPulse {
  0%, 100% { box-shadow: 0 6rpx 0 #15803D, 0 8rpx 24rpx rgba(34, 197, 94, 0.35); }
  50% { box-shadow: 0 6rpx 0 #15803D, 0 8rpx 40rpx rgba(34, 197, 94, 0.6); transform: scale(1.02); }
}
</style>
