<template>
  <view class="page-container">
    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-caret-left"></text>
      </view>
      <view class="page-title">关卡挑战 🏆</view>
      <view class="placeholder"></view>
    </view>

    <scroll-view class="content-scroll" scroll-y>
      <!-- 难度选择 -->
      <view class="section">
        <view class="section-label">选择难度</view>
        <view class="difficulty-row">
          <view
            v-for="d in difficulties"
            :key="d.value"
            :class="['difficulty-btn', { active: selectedDifficulty === d.value }]"
            @click="selectedDifficulty = d.value"
          >
            <text class="diff-emoji">{{ d.emoji }}</text>
            <text class="diff-label">{{ d.label }}</text>
          </view>
        </view>
      </view>

      <!-- 游戏类型选择 -->
      <view class="section">
        <view class="section-label">选择游戏</view>
        <view class="game-grid">
          <view
            v-for="game in levelGames"
            :key="game.type"
            :class="['game-card', { active: selectedGame === game.type }]"
            @click="selectedGame = game.type"
          >
            <view class="game-icon-wrap" :style="{ background: game.bg }">
              <text :class="'ph ' + game.icon" :style="{ color: game.color }"></text>
            </view>
            <view class="game-name">{{ game.name }}</view>
            <text v-if="selectedGame === game.type" class="ph ph-check-circle game-check" :style="{ color: game.color }"></text>
          </view>
        </view>
      </view>

      <!-- 关卡列表 -->
      <view class="section" v-if="selectedGame && selectedDifficulty">
        <view class="section-label">选择关卡</view>

        <view class="loading-row" v-if="levelsLoading">
          <text class="ph ph-circle-notch spin"></text>
          <text>加载中...</text>
        </view>

        <view class="error-row" v-else-if="levelsError">
          <text class="ph ph-warning-circle"></text>
          <text>{{ levelsError }}</text>
          <view class="retry-btn" @click="loadLevels">重试</view>
        </view>

        <view class="levels-list" v-else>
          <view
            v-for="level in levels"
            :key="level.level_id"
            :class="['level-row', { locked: !level.unlocked, passed: level.passed }]"
            @click="startLevel(level)"
          >
            <view :class="['level-badge', { passed: level.passed, locked: !level.unlocked }]">
              <text v-if="level.passed" class="ph ph-check-bold"></text>
              <text v-else-if="!level.unlocked" class="ph ph-lock"></text>
              <text v-else class="badge-num">{{ level.level_num }}</text>
            </view>
            <view class="level-info">
              <view class="level-title">{{ level.title }}</view>
              <view class="level-meta">
                <text class="meta-count">{{ level.question_count }} 题</text>
                <text class="meta-dot">·</text>
                <text v-if="level.passed" class="meta-passed">已通关 {{ Math.round((level.best_accuracy || 0) * 100) }}%</text>
                <text v-else-if="level.unlocked" class="meta-unlocked">可挑战</text>
                <text v-else class="meta-locked">未解锁</text>
              </view>
            </view>
            <text v-if="level.passed" class="ph ph-star level-star"></text>
            <text v-else-if="level.unlocked" class="ph ph-caret-right level-arrow"></text>
            <text v-else class="ph ph-lock level-lock"></text>
          </view>

          <view class="empty-hint" v-if="levels.length === 0">
            <text class="ph ph-smiley-sad"></text>
            <text>暂无关卡数据</text>
          </view>
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { get } from '../../../api/index.js'
import { getCurrentChild } from '../../../utils/auth.js'

const LEVEL_GAMES = [
  { type: 'visual',             name: '找不同',   icon: 'ph-eye',            color: '#4F9EF8', bg: 'linear-gradient(135deg,#EFF6FF,#DBEAFE)' },
  { type: 'spelling',           name: '拼字识别', icon: 'ph-text-aa',        color: '#A78BFA', bg: 'linear-gradient(135deg,#F5F3FF,#EDE9FE)' },
  { type: 'comprehension',      name: '文字理解', icon: 'ph-book-open',      color: '#22C55E', bg: 'linear-gradient(135deg,#F0FDF4,#DCFCE7)' },
  { type: 'working_memory',     name: '工作记忆', icon: 'ph-brain',          color: '#F97316', bg: 'linear-gradient(135deg,#FFF7ED,#FFEDD5)' },
  { type: 'rapid_naming',       name: '快速命名', icon: 'ph-lightning',      color: '#EAB308', bg: 'linear-gradient(135deg,#FEFCE8,#FEF9C3)' },
  { type: 'motor_coordination', name: '精细动作', icon: 'ph-pencil-simple',  color: '#EC4899', bg: 'linear-gradient(135deg,#FDF2F8,#FCE7F3)' },
  { type: 'flip_card',          name: '翻牌记忆', icon: 'ph-cards',          color: '#7C3AED', bg: 'linear-gradient(135deg,#F5F3FF,#EDE9FE)' },
  { type: 'connect_game',       name: '连一连',   icon: 'ph-link',           color: '#16A34A', bg: 'linear-gradient(135deg,#F0FDF4,#DCFCE7)' },
  { type: 'handwriting',        name: '手写汉字', icon: 'ph-pencil-line',    color: '#F57F17', bg: 'linear-gradient(135deg,#FFF8F0,#FFF3E0)' },
]

export default {
  data() {
    return {
      child: null,
      selectedGame: 'visual',
      selectedDifficulty: 'L1',
      difficulties: [
        { value: 'L1', label: '初级', emoji: '🌱' },
        { value: 'L2', label: '中级', emoji: '🌿' },
        { value: 'L3', label: '高级', emoji: '🌳' },
      ],
      levelGames: LEVEL_GAMES,
      levels: [],
      levelsLoading: false,
      levelsError: null,
      _authFailed: false,
    }
  },
  watch: {
    selectedGame()      { if (!this._authFailed) this.loadLevels() },
    selectedDifficulty(){ if (!this._authFailed) this.loadLevels() },
  },
  onLoad(options) {
    this.child = getCurrentChild()
    if (!this.child) {
      uni.showToast({ title: '请先在家长端选择孩子档案', icon: 'none' })
      setTimeout(() => uni.navigateBack(), 1500)
      return
    }
    if (options?.game_type)  this.selectedGame = options.game_type
    if (options?.difficulty) this.selectedDifficulty = options.difficulty
    this.loadLevels()
  },
  methods: {
    async loadLevels() {
      if (!this.selectedGame || !this.selectedDifficulty || !this.child?.id) return
      if (this._authFailed) return
      this.levelsLoading = true
      this.levelsError = null
      try {
        const res = await get('/api/training/levels', {
          game_type: this.selectedGame,
          difficulty: this.selectedDifficulty,
          child_id: this.child.id,
        }, {}, true)
        this.levels = res.levels || []
      } catch (e) {
        const code = e?._statusCode
        if (code === 403 || code === 404) {
          this._authFailed = true
          this.levelsError = '孩子档案已失效，请重新登录后再试'
        } else {
          this.levelsError = '加载失败，请重试'
        }
      } finally {
        this.levelsLoading = false
      }
    },
    startLevel(level) {
      if (!level.unlocked) {
        uni.showToast({ title: '请先通过上一关！', icon: 'none' })
        return
      }
      uni.navigateTo({
        url: `/pages/child/training-game/index?game_type=${this.selectedGame}&level_mode=true&difficulty=${this.selectedDifficulty}&level_id=${level.level_id}`,
      })
    },
    goBack() {
      // #ifdef H5
      if (typeof window !== 'undefined' && window.history) {
        window.history.back()
        return
      }
      // #endif
      uni.navigateBack()
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
}

/* 顶部栏 — 与儿童端一致 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 56rpx 32rpx 20rpx;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 30;
}
.back-btn {
  width: 72rpx; height: 72rpx;
  border-radius: 50%;
  background: #F5F7FA;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.back-btn:active { transform: scale(0.92); background: #EFF6FF; }
.back-btn .ph { font-size: 36rpx; color: #2D3748; }
.page-title { font-size: 34rpx; font-weight: 800; color: #2D3748; }
.placeholder { width: 72rpx; }

/* 内容滚动区 */
.content-scroll { flex: 1; }

.section { padding: 28rpx 32rpx 0; }
.section-label {
  font-size: 26rpx; font-weight: 700; color: #2D3748;
  margin-bottom: 16rpx;
}

/* 难度选择 */
.difficulty-row { display: flex; gap: 16rpx; }
.difficulty-btn {
  flex: 1; display: flex; flex-direction: column; align-items: center;
  padding: 20rpx 10rpx; background: #FFFFFF; border-radius: 20rpx;
  border: 3rpx solid transparent;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.difficulty-btn:active { transform: scale(0.96); }
.difficulty-btn.active {
  border-color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
}
.diff-emoji { font-size: 40rpx; margin-bottom: 8rpx; }
.diff-label { font-size: 22rpx; color: #718096; font-weight: 600; }
.difficulty-btn.active .diff-label { color: #4F9EF8; }

/* 游戏网格 */
.game-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
}
.game-card {
  background: #FFFFFF; border-radius: 20rpx; padding: 20rpx 12rpx;
  display: flex; flex-direction: column; align-items: center;
  border: 3rpx solid transparent; position: relative;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.game-card:active { transform: scale(0.95); }
.game-card.active { border-color: #4F9EF8; background: #EFF6FF; }
.game-icon-wrap {
  width: 80rpx; height: 80rpx; border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 10rpx;
}
.game-icon-wrap .ph { font-size: 38rpx; }
.game-name { font-size: 22rpx; color: #2D3748; font-weight: 600; text-align: center; }
.game-check {
  position: absolute; top: 8rpx; right: 8rpx;
  font-size: 28rpx;
}

/* 关卡列表 */
.loading-row, .error-row {
  display: flex; align-items: center; gap: 12rpx;
  padding: 32rpx 0; color: #A0AEC0; font-size: 26rpx; font-weight: 600;
}
.retry-btn {
  margin-left: 12rpx; padding: 8rpx 24rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF; border-radius: 20rpx; font-size: 22rpx; font-weight: 700;
}

.levels-list { display: flex; flex-direction: column; gap: 14rpx; }

.level-row {
  background: #FFFFFF; border-radius: 20rpx; padding: 24rpx 24rpx;
  display: flex; align-items: center; gap: 20rpx;
  box-shadow: 0 2rpx 10rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.level-row:active { transform: scale(0.98); }
.level-row.locked { opacity: 0.55; }
.level-row.passed { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }

.level-badge {
  width: 64rpx; height: 64rpx; border-radius: 50%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25);
}
.level-badge.passed {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  box-shadow: 0 4rpx 12rpx rgba(34,197,94,0.25);
}
.level-badge.locked {
  background: #E5E7EB;
  box-shadow: none;
}
.level-badge .ph { font-size: 28rpx; color: #FFFFFF; }
.badge-num { font-size: 28rpx; font-weight: 800; color: #FFFFFF; }

.level-info { flex: 1; }
.level-title { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.level-meta { display: flex; align-items: center; gap: 8rpx; margin-top: 4rpx; }
.meta-count { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }
.meta-dot { font-size: 22rpx; color: #CBD5E0; }
.meta-passed { font-size: 22rpx; color: #22C55E; font-weight: 600; }
.meta-unlocked { font-size: 22rpx; color: #4F9EF8; font-weight: 600; }
.meta-locked { font-size: 22rpx; color: #CBD5E0; font-weight: 500; }

.level-star { font-size: 36rpx; color: #F59E0B; flex-shrink: 0; }
.level-arrow { font-size: 32rpx; color: #CBD5E0; flex-shrink: 0; }
.level-lock { font-size: 28rpx; color: #CBD5E0; flex-shrink: 0; }

.empty-hint {
  display: flex; flex-direction: column; align-items: center; gap: 12rpx;
  padding: 48rpx 0; color: #A0AEC0; font-size: 26rpx; font-weight: 600;
}
.empty-hint .ph { font-size: 64rpx; color: #CBD5E0; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }
</style>
