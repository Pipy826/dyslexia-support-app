<template>
  <scroll-view class="challenge-tab" scroll-y>
    <!-- 插画区 -->
    <view class="illustration-area">
      <view class="illustration-card">
        <view class="animal-row">
          <text class="animal-emoji">🐱</text>
          <view class="title-block">
            <view class="main-title">文字游戏大挑战</view>
            <view class="sub-title">选一个游戏，赢取小星星！</view>
          </view>
          <text class="animal-emoji">🐶</text>
        </view>
        <view class="deco-row">
          <text class="deco-emoji">🐰</text>
          <text class="deco-emoji">🍎</text>
          <text class="deco-emoji">🌟</text>
          <text class="deco-emoji">🍌</text>
          <text class="deco-emoji">🌸</text>
        </view>
      </view>
    </view>

    <!-- 关卡挑战入口 -->
    <view class="level-challenge-entry" @click="goToLevelSelect">
      <view class="level-entry-icon">
        <text class="ph ph-trophy"></text>
      </view>
      <view class="level-entry-text">
        <view class="level-entry-title">关卡挑战</view>
        <view class="level-entry-desc">闯关解锁新课程</view>
      </view>
      <view class="level-entry-arrow">
        <text class="ph ph-caret-right"></text>
      </view>
    </view>

    <!-- 游戏卡片列表 -->
    <view class="game-list">
      <view
        v-for="g in allGames"
        :key="g.type"
        :class="['game-card', { active: selectedType === g.type }]"
        :style="{ '--c': g.color, '--bg': g.bg }"
        @click="selectedType = g.type"
      >
        <view class="card-icon">
          <text class="card-animal">{{ g.animal }}</text>
        </view>
        <view class="card-body">
          <view class="card-name">{{ g.name }}</view>
          <view class="card-desc">{{ g.desc }}</view>
        </view>
        <view class="card-check" v-if="selectedType === g.type">
          <text class="ph ph-check-circle"></text>
        </view>
      </view>
    </view>

    <!-- 开始按钮 -->
    <view class="start-area">
      <button class="start-btn" @click="startGame">
        <text class="ph ph-play-circle"></text> 开始游戏
      </button>
      <view class="tip-text">
        <text class="ph ph-info"></text> 请在安静环境下独立完成
      </view>
    </view>

    <view style="height: 160rpx;"></view>
  </scroll-view>
</template>

<script>
import AudioManager from '../../utils/audio.js'
import {
  GAME_CARD_COLORS,
  GAME_THEME_ANIMALS,
  GAME_TASK_DEFAULT_NAMES,
  GAME_TASK_DESCS,
  GAME_ROUTES,
} from '../../utils/constants.js'

const ALL_GAME_TYPES = [
  'comprehension', 'spelling', 'rapid_naming', 'visual',
  'working_memory', 'motor_coordination',
  'handwriting', 'flip_card', 'connect_game',
]

export default {
  name: 'ChallengeTab',
  props: {
    childGrade: { type: String, default: '' },
    initialGameType: { type: String, default: '' },
    initialLevelMode: { type: Boolean, default: false },
  },
  data() {
    return {
      selectedType: 'visual',
      allGames: ALL_GAME_TYPES.map(type => ({
        type,
        name: GAME_TASK_DEFAULT_NAMES[type] || type,
        desc: GAME_TASK_DESCS[type] || '',
        color: (GAME_CARD_COLORS[type] || {}).color || '#4F9EF8',
        bg: (GAME_CARD_COLORS[type] || {}).bg || '#EFF6FF',
        animal: (GAME_THEME_ANIMALS[type] || {}).emoji || '🎮',
      })),
      _autoStarted: false,
    }
  },
  mounted() {
    // 从家长端任务跳转过来时，自动选中游戏类型并直接开始
    if (this.initialGameType && !this._autoStarted) {
      this._autoStarted = true
      this.selectedType = this.initialGameType
      this.$nextTick(() => {
        if (this.initialLevelMode) {
          // 关卡训练：直接跳关卡选择页（不播音效，避免 NotAllowedError）
          uni.navigateTo({
            url: `/pages/child/level-select/index?game_type=${this.initialGameType}&difficulty=L1`
          })
        } else {
          // 挑战游戏：直接开始（不播音效，避免 NotAllowedError）
          this._startGameSilent()
        }
      })
    }
  },
  methods: {
    /** 静默开始游戏（无音效，用于自动跳转场景） */
    _startGameSilent() {
      const route = GAME_ROUTES[this.selectedType]
      if (!route) return
      const gradeParam = this.childGrade ? `&grade=${encodeURIComponent(this.childGrade)}` : ''
      uni.navigateTo({ url: `${route}?game_type=${this.selectedType}${gradeParam}` })
    },
    startGame() {
      AudioManager.playSFX('click')
      const route = GAME_ROUTES[this.selectedType]
      if (!route) return

      // 所有游戏都先经过引导页（prep），引导页会根据游戏类型跳转到对应游戏
      const gradeParam = this.childGrade ? `&grade=${encodeURIComponent(this.childGrade)}` : ''
      uni.navigateTo({ url: `${route}?game_type=${this.selectedType}${gradeParam}` })
    },
    goToLevelSelect() {
      AudioManager.playSFX('click')
      uni.navigateTo({ url: '/pages/child/level-select/index' })
    },
  },
}
</script>

<style scoped>
.challenge-tab {
  flex: 1;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
}

/* 插画区 */
.illustration-area { padding: 24rpx 28rpx 0; }
.illustration-card {
  background: linear-gradient(135deg, #FFF8F0, #FFF3E0);
  border-radius: 28rpx;
  padding: 28rpx 24rpx 20rpx;
  border: 2rpx solid #FFE0B2;
  box-shadow: 0 4rpx 16rpx rgba(245, 127, 23, 0.1);
  margin-bottom: 20rpx;
}
.animal-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16rpx;
}
.animal-emoji { font-size: 56rpx; line-height: 1; }
.title-block { flex: 1; text-align: center; }
.main-title { font-size: 30rpx; font-weight: 800; color: #3E2723; }
.sub-title { font-size: 22rpx; color: #8D6E63; font-weight: 500; margin-top: 4rpx; }
.deco-row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 20rpx;
}
.deco-emoji { font-size: 36rpx; animation: bounce 2s ease-in-out infinite; }
.deco-emoji:nth-child(2) { animation-delay: 0.2s; }
.deco-emoji:nth-child(3) { animation-delay: 0.4s; }
.deco-emoji:nth-child(4) { animation-delay: 0.6s; }
.deco-emoji:nth-child(5) { animation-delay: 0.8s; }
@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6rpx); } }

/* 关卡挑战入口 */
.level-challenge-entry {
  margin: 0 28rpx 20rpx;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 22rpx;
  padding: 28rpx 24rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 6rpx 20rpx rgba(102, 126, 234, 0.35);
}
.level-entry-icon {
  width: 80rpx;
  height: 80rpx;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.level-entry-icon .ph { font-size: 44rpx; color: #fff; }
.level-entry-text { flex: 1; }
.level-entry-title { font-size: 30rpx; font-weight: 700; color: #fff; }
.level-entry-desc { font-size: 22rpx; color: rgba(255,255,255,0.8); margin-top: 4rpx; }
.level-entry-arrow .ph { font-size: 36rpx; color: rgba(255,255,255,0.7); }

/* 游戏卡片 */
.game-list { padding: 0 28rpx; display: flex; flex-direction: column; gap: 12rpx; }
.game-card {
  background: #FFFFFF;
  border-radius: 22rpx;
  padding: 20rpx 22rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 18rpx;
  border: 2rpx solid transparent;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.game-card:active { transform: scale(0.98); }
.game-card.active {
  background: var(--bg);
  border-color: var(--c);
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08);
}
.card-icon {
  width: 72rpx; height: 72rpx;
  border-radius: 18rpx;
  background: var(--bg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  font-size: 40rpx;
}
.game-card.active .card-icon { background: rgba(255,255,255,0.7); }
.card-animal { font-size: 40rpx; line-height: 1; }
.card-body { flex: 1; min-width: 0; }
.card-name { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.card-desc { font-size: 22rpx; color: #A0AEC0; font-weight: 500; margin-top: 2rpx; }
.card-check { flex-shrink: 0; }
.card-check .ph { font-size: 32rpx; color: var(--c); }

/* 开始按钮 */
.start-area { padding: 24rpx 28rpx 0; }
.start-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 32rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 20rpx rgba(245, 127, 23, 0.35);
  display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 10rpx;
  margin-bottom: 16rpx;
  box-sizing: border-box;
}
.start-btn:active { transform: scale(0.97); }
.start-btn .ph { font-size: 32rpx; }
.tip-text {
  display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 6rpx;
  font-size: 22rpx; color: #CBD5E0; font-weight: 500; text-align: center;
}
.tip-text .ph { font-size: 22rpx; }
</style>
