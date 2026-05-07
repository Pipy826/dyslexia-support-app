<template>
  <scroll-view class="today-tab" scroll-y>
    <!-- 今日进度卡片 -->
    <view class="progress-card" v-if="todayTasks.length > 0">
      <view class="progress-header">
        <view class="progress-info">
          <view class="progress-title">今日任务</view>
          <view class="progress-subtitle">{{ todayDateStr }} · 完成任务获得小星星！</view>
        </view>
        <view class="progress-count">
          {{ completedCount }}<text class="count-total">/{{ todayTasks.length }}</text>
        </view>
      </view>
      <view class="progress-track">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
    </view>

    <!-- 加载中 -->
    <view class="loading-row" v-if="loading">
      <text class="ph ph-circle-notch spin"></text> 加载中...
    </view>

    <!-- 今日任务列表 -->
    <view class="task-list" v-else-if="todayTasks.length > 0">
      <!-- 列表头 -->
      <view class="section-header">
        <view class="section-label-text">今日任务</view>
        <view class="see-all-btn" @click="goToAllTasks" v-if="todayTasks.length > 3">
          <text>查看全部</text>
          <text class="ph ph-caret-right"></text>
        </view>
      </view>

      <view
        v-for="task in previewTasks"
        :key="task.id || task.task_type"
        :class="['task-card', { completed: task.status === 'completed' }]"
      >
        <view class="task-icon-wrap" :style="taskIconStyle(task.task_type)">
          <text :class="'ph ' + getTaskIcon(task.task_type)"></text>
        </view>
        <view class="task-info">
          <view class="task-name">{{ task.task_name || getTaskName(task.task_type) }}</view>
          <view class="task-desc">{{ getTaskDesc(task.task_type) }}</view>
        </view>
        <button
          :class="['task-btn', { done: task.status === 'completed' }]"
          @click="startTask(task)"
          :disabled="task.status === 'completed'"
        >
          {{ task.status === 'completed' ? '已完成 ✓' : '去完成' }}
        </button>
      </view>

      <!-- 更多任务提示 -->
      <view class="more-tasks-hint" v-if="todayTasks.length > 3" @click="goToAllTasks">
        <text class="ph ph-list-bullets"></text>
        <text>还有 {{ todayTasks.length - 3 }} 个任务 · 查看全部</text>
        <text class="ph ph-caret-right"></text>
      </view>
    </view>

    <!-- 无今日任务 -->
    <view class="empty-area" v-else-if="!loading">
      <view class="empty-card">
        <text class="empty-emoji">🎮</text>
        <view class="empty-title">今天还没有任务</view>
        <view class="empty-desc">去挑战一下吧！</view>
        <button class="go-challenge-btn" @click="$emit('go-challenge')">
          <text class="ph ph-game-controller"></text> 去挑战
        </button>
      </view>
    </view>

    <view style="height: 160rpx;"></view>
  </scroll-view>
</template>

<script>
import { getTasks } from '../../api/training.js'
import { GAME_TASK_ICONS, GAME_TASK_DEFAULT_NAMES, GAME_TASK_DESCS, GAME_CARD_COLORS } from '../../utils/constants.js'

// 挑战游戏类型（今日任务 tab 显示）
const CHALLENGE_GAME_TYPES = new Set(['handwriting', 'flip_card', 'connect_game'])
// 关卡训练类型（训练 tab 显示）
const LEVEL_GAME_TYPES = new Set(['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination'])

export default {
  name: 'TodayTaskTab',
  props: {
    childId: { type: Number, default: null },
  },
  emits: ['go-challenge'],
  data() {
    return {
      allTasks: [],
      loading: false,
    }
  },
  computed: {
    todayDateStr() {
      const d = new Date()
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    todayStr() {
      return new Date().toISOString().split('T')[0]
    },
    todayTasks() {
      const today = this.todayStr
      return this.allTasks.filter(t => {
        const gameType = t.task_type || ''
        const scheduled = (t.scheduled_date || '').split('T')[0]
        const completed = (t.completed_at || '').split('T')[0]

        // 今日任务 = 挑战游戏类型（handwriting/flip_card/connect_game）
        // 未完成：只要是挑战类型就显示
        // 已完成：今天完成的挑战类型任务
        if (!CHALLENGE_GAME_TYPES.has(gameType)) return false
        if (t.status === 'completed') return completed === today
        return true
      })
    },
    previewTasks() {
      return this.todayTasks.slice(0, 3)
    },
    completedCount() { return this.todayTasks.filter(t => t.status === 'completed').length },
    progressPercent() {
      if (!this.todayTasks.length) return 0
      return Math.round((this.completedCount / this.todayTasks.length) * 100)
    },
  },
  watch: {
    childId: { immediate: true, handler(val) { if (val) this.loadTasks() } },
  },
  methods: {
    async loadTasks() {
      if (!this.childId) return
      this.loading = true
      try {
        this.allTasks = await getTasks(this.childId)
      } catch (e) {
        console.warn('加载今日任务失败', e)
      } finally {
        this.loading = false
      }
    },
    getTaskIcon(type) {
      const typeMap = { reading: 'comprehension' }
      return GAME_TASK_ICONS[typeMap[type] || type] || 'ph-star'
    },
    getTaskName(type) {
      const typeMap = { reading: 'comprehension' }
      return GAME_TASK_DEFAULT_NAMES[typeMap[type] || type] || '训练任务'
    },
    getTaskDesc(type) {
      const typeMap = { reading: 'comprehension' }
      return GAME_TASK_DESCS[typeMap[type] || type] || ''
    },
    taskIconStyle(type) {
      const typeMap = { reading: 'comprehension' }
      const colors = GAME_CARD_COLORS[typeMap[type] || type] || { color: '#4F9EF8', bg: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)' }
      return { background: colors.bg, '--icon-color': colors.color }
    },
    startTask(task) {
      if (task.status === 'completed') return
      const typeMap = { reading: 'comprehension' }
      const gameType = typeMap[task.task_type] || task.task_type || 'visual'
      const taskIdParam = task.id ? `&task_id=${task.id}` : ''

      // 挑战游戏（新三种）：直接跳对应游戏页
      const challengeRoutes = {
        handwriting: '/pages/child/handwriting-game/index',
        flip_card:   '/pages/child/flip-card-game/index',
        connect_game: '/pages/child/connect-game/index',
      }
      if (challengeRoutes[gameType]) {
        uni.navigateTo({ url: `${challengeRoutes[gameType]}?difficulty=L1${taskIdParam}` })
        return
      }

      // 训练关卡（其余6种）：直接进关卡选择器（level_mode）
      uni.navigateTo({
        url: `/pages/child/training-game/index?game_type=${gameType}&level_mode=true&difficulty=L1${taskIdParam}`
      })
    },
    goToAllTasks() {
      uni.navigateTo({ url: '/pages/child/all-tasks/index?type=challenge' })
    },
  },
}
</script>

<style scoped>
.today-tab {
  flex: 1;
  width: 100%;
  height: 100%;
  padding: 24rpx 28rpx 0;
  box-sizing: border-box;
}

.progress-card {
  background: linear-gradient(135deg, #FF8F00 0%, #F57F17 100%);
  border-radius: 28rpx; padding: 32rpx; margin-bottom: 28rpx; position: relative; overflow: hidden;
}
.progress-card::before {
  content: ''; position: absolute; top: -40%; right: -20%;
  width: 200rpx; height: 200rpx; border-radius: 50%; background: rgba(255,255,255,0.1);
}
.progress-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20rpx; position: relative; z-index: 1; }
.progress-title { font-size: 32rpx; font-weight: 700; color: rgba(255,255,255,0.95); }
.progress-subtitle { font-size: 22rpx; color: rgba(255,255,255,0.7); margin-top: 4rpx; }
.progress-count { font-size: 56rpx; font-weight: 900; color: #FFFFFF; line-height: 1; }
.count-total { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.progress-track { height: 10rpx; background: rgba(255,255,255,0.2); border-radius: 5rpx; overflow: hidden; position: relative; z-index: 1; }
.progress-fill { height: 100%; background: rgba(255,255,255,0.9); border-radius: 5rpx; transition: width 0.6s; }

.loading-row { display: flex; align-items: center; justify-content: center; gap: 12rpx; color: #A0AEC0; font-size: 26rpx; padding: 24rpx 0; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

.section-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 16rpx;
}
.section-label-text { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.see-all-btn {
  display: flex; align-items: center; gap: 4rpx;
  font-size: 24rpx; color: #FF8F00; font-weight: 600;
}
.see-all-btn .ph { font-size: 22rpx; }

.more-tasks-hint {
  display: flex; align-items: center; justify-content: center; gap: 10rpx;
  background: linear-gradient(135deg, #FFF8F0, #FFF3E0);
  border-radius: 20rpx; padding: 20rpx;
  font-size: 24rpx; color: #FF8F00; font-weight: 600;
  border: 2rpx dashed #FFE0B2;
}
.more-tasks-hint .ph { font-size: 26rpx; }

.task-list { display: flex; flex-direction: column; gap: 14rpx; }
.task-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 22rpx 20rpx;
  display: flex; align-items: center; gap: 18rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); transition: all 0.2s;
}
.task-card:active { transform: scale(0.98); }
.task-card.completed { opacity: 0.55; }
.task-icon-wrap {
  width: 88rpx; height: 88rpx; border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.task-icon-wrap .ph { font-size: 44rpx; color: var(--icon-color, #4F9EF8); }
.task-info { flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: flex-start; }
.task-name { font-size: 28rpx; font-weight: 700; color: #2D3748; width: 100%; }
.task-desc { font-size: 22rpx; color: #A0AEC0; margin-top: 4rpx; font-weight: 500; width: 100%; }
.task-btn {
  padding: 14rpx 24rpx;
  background: linear-gradient(135deg, #FF8F00, #F57F17); color: #FFFFFF;
  border-radius: 16rpx; font-size: 24rpx; font-weight: 700; flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(245,127,23,0.3);
}
.task-btn:active { transform: scale(0.95); }
.task-btn.done { background: #F5F5F5; color: #A0AEC0; box-shadow: none; }

/* 空状态 */
.empty-area { display: flex; align-items: center; justify-content: center; padding: 60rpx 0; }
.empty-card {
  background: #FFFFFF; border-radius: 32rpx; padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center; gap: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0,0,0,0.06); width: 100%;
}
.empty-emoji { font-size: 80rpx; line-height: 1; }
.empty-title { font-size: 32rpx; font-weight: 800; color: #2D3748; text-align: center; }
.empty-desc { font-size: 26rpx; color: #A0AEC0; font-weight: 500; text-align: center; }
.go-challenge-btn {
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF; border-radius: 24rpx; padding: 24rpx 48rpx;
  font-size: 28rpx; font-weight: 700;
  display: flex; flex-direction: row; align-items: center; gap: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(245,127,23,0.3);
  margin-top: 8rpx;
}
.go-challenge-btn:active { transform: scale(0.97); }
.go-challenge-btn .ph { font-size: 28rpx; }
</style>
