<template>
  <view class="level-selector">

    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="handleBack">
        <text class="ph ph-caret-left"></text>
      </view>
      <view class="title-area">
        <text class="title-text">{{ gameTypeName }}</text>
        <text class="subtitle-text">{{ difficultyLabel }} · 关卡挑战</text>
      </view>
      <view class="placeholder"></view>
    </view>

    <!-- 加载中 -->
    <view class="state-area" v-if="loading">
      <text class="ph ph-circle-notch spin state-icon"></text>
      <text class="state-text">加载中...</text>
    </view>

    <!-- 错误 -->
    <view class="state-area" v-else-if="error">
      <text class="ph ph-warning-circle state-icon error-icon"></text>
      <text class="state-text error-text">{{ error }}</text>
      <view class="retry-btn" @click="loadLevels">
        <text class="ph ph-arrow-clockwise"></text>
        <text>重试</text>
      </view>
    </view>

    <!-- 关卡列表 -->
    <view class="levels-section" v-else>
      <view class="section-hint">点击已解锁的关卡开始挑战</view>
      <scroll-view scroll-y class="levels-scroll">
        <view class="levels-col">
          <view
            v-for="level in levels"
            :key="level.level_id"
            :class="['level-row', {
              'row-passed': level.passed,
              'row-unlocked': level.unlocked && !level.passed,
              'row-locked': !level.unlocked,
            }]"
            @click="handleLevelClick(level)"
          >
            <!-- 编号徽章 -->
            <view :class="['row-badge', {
              'badge-passed': level.passed,
              'badge-unlocked': level.unlocked && !level.passed,
              'badge-locked': !level.unlocked,
            }]">
              <text v-if="level.passed" class="ph ph-check-bold badge-icon"></text>
              <text v-else-if="!level.unlocked" class="ph ph-lock badge-icon"></text>
              <text v-else class="badge-num">{{ level.level_num }}</text>
            </view>

            <!-- 关卡信息 -->
            <view class="row-info">
              <view class="row-title">{{ level.title }}</view>
              <view class="row-meta">
                <text v-if="level.question_count" class="meta-count">{{ level.question_count }} 题</text>
                <text class="meta-dot" v-if="level.question_count">·</text>
                <text v-if="level.passed" class="status-passed">已通关 {{ Math.round((level.best_accuracy || 0) * 100) }}%</text>
                <text v-else-if="level.unlocked" class="status-unlocked">可挑战</text>
                <text v-else class="status-locked">未解锁</text>
              </view>
            </view>

            <!-- 右侧图标 -->
            <text v-if="level.passed" class="ph ph-star row-star"></text>
            <text v-else-if="level.unlocked" class="ph ph-caret-right row-arrow"></text>
            <text v-else class="ph ph-lock row-lock"></text>
          </view>
        </view>
      </scroll-view>
    </view>

  </view>
</template>

<script>
import { get } from '@/api'

const GAME_NAMES = {
  visual:             '视觉辨识',
  spelling:           '拼字识别',
  comprehension:      '文字理解',
  working_memory:     '工作记忆',
  rapid_naming:       '快速命名',
  motor_coordination: '精细动作',
  flip_card:          '翻牌记忆',
  connect_game:       '连一连',
  handwriting:        '手写汉字',
}

const DIFFICULTY_LABELS = { L1: '初级', L2: '中级', L3: '高级' }

export default {
  name: 'LevelSelector',
  props: {
    gameType:   { type: String, required: true },
    difficulty: { type: String, required: true },
    childId:    { type: Number, required: true },
  },
  emits: ['select-level', 'back'],
  data() {
    return {
      levels: [],
      loading: true,
      error: null,
    }
  },
  computed: {
    gameTypeName()    { return GAME_NAMES[this.gameType] || this.gameType },
    difficultyLabel() { return DIFFICULTY_LABELS[this.difficulty] || this.difficulty },
  },
  mounted() {
    this.loadLevels()
  },
  methods: {
    async loadLevels() {
      this.loading = true
      this.error = null
      try {
        const res = await get('/api/training/levels', {
          game_type: this.gameType,
          difficulty: this.difficulty,
          child_id: this.childId,
        })
        this.levels = res.levels || []
      } catch (e) {
        this.error = e.message || '加载失败，请重试'
      } finally {
        this.loading = false
      }
    },
    handleLevelClick(level) {
      if (!level.unlocked) {
        uni.showToast({ title: '请先通过上一关！', icon: 'none' })
        return
      }
      this.$emit('select-level', level.level_id)
    },
    handleBack() {
      this.$emit('back')
    },
  },
}
</script>

<style scoped>
.level-selector {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

/* ── 顶部栏 ── */
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
  flex-shrink: 0;
}
.back-btn:active { transform: scale(0.92); background: #EFF6FF; }
.back-btn .ph { font-size: 36rpx; color: #2D3748; }

.title-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}
.title-text { font-size: 32rpx; font-weight: 800; color: #2D3748; }
.subtitle-text { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }

.placeholder { width: 72rpx; flex-shrink: 0; }

/* ── 状态区域 ── */
.state-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20rpx;
  padding: 80rpx 0;
}
.state-icon { font-size: 72rpx; color: #A0AEC0; }
.error-icon { color: #FF6B6B; }
.state-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
.error-text { color: #FF6B6B; }

.retry-btn {
  display: flex; align-items: center; gap: 8rpx;
  padding: 16rpx 40rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF; border-radius: 20rpx;
  font-size: 26rpx; font-weight: 700;
}
.retry-btn .ph { font-size: 26rpx; }

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* ── 关卡区域 ── */
.levels-section {
  flex: 1;
  padding: 28rpx 0 40rpx;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.section-hint {
  font-size: 24rpx;
  color: #A0AEC0;
  font-weight: 500;
  padding: 0 32rpx;
  margin-bottom: 20rpx;
}

.levels-scroll { flex: 1; }
.levels-col {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  padding: 0 32rpx 16rpx;
}

/* ── 关卡行 ── */
.level-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
  border-radius: 24rpx;
  padding: 24rpx 24rpx;
  transition: all 0.2s;
}
.level-row:active { transform: scale(0.98); }

.row-passed {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border: 2rpx solid #22C55E;
  box-shadow: 0 2rpx 12rpx rgba(34,197,94,0.12);
}
.row-unlocked {
  background: #FFFFFF;
  border: 2rpx solid #E5E7EB;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
}
.row-locked {
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  opacity: 0.6;
}

/* 编号徽章 */
.row-badge {
  width: 72rpx; height: 72rpx;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.badge-passed {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  box-shadow: 0 4rpx 12rpx rgba(34,197,94,0.3);
}
.badge-unlocked {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.3);
}
.badge-locked { background: #E5E7EB; }
.badge-icon { font-size: 32rpx; color: #FFFFFF; }
.badge-num { font-size: 30rpx; font-weight: 800; color: #FFFFFF; }

/* 行内容 */
.row-info { flex: 1; min-width: 0; }
.row-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 6rpx; }
.row-locked .row-title { color: #9CA3AF; }
.row-meta { display: flex; align-items: center; gap: 8rpx; }
.meta-count { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }
.meta-dot { font-size: 22rpx; color: #CBD5E0; }
.status-passed { font-size: 22rpx; font-weight: 700; color: #22C55E; }
.status-unlocked { font-size: 22rpx; color: #4F9EF8; font-weight: 600; }
.status-locked { font-size: 22rpx; color: #CBD5E0; }

/* 右侧图标 */
.row-star { font-size: 36rpx; color: #F59E0B; flex-shrink: 0; }
.row-arrow { font-size: 32rpx; color: #CBD5E0; flex-shrink: 0; }
.row-lock { font-size: 28rpx; color: #CBD5E0; flex-shrink: 0; }
</style>
