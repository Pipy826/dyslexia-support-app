<template>
  <scroll-view class="training-tab" scroll-y>
    <!-- 进度卡片 -->
    <view class="progress-card">
      <view class="progress-header">
        <view class="progress-info">
          <view class="progress-title">训练任务</view>
          <view class="progress-subtitle">完成任务获得小星星哦！</view>
        </view>
        <view class="progress-count">
          {{ completedCount }}<text class="count-total">/{{ tasks.length || 0 }}</text>
        </view>
      </view>
      <view class="progress-track">
        <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
      </view>
    </view>

    <!-- 任务列表 -->
    <view class="section-title">我的任务</view>

    <view class="loading-row" v-if="loading">
      <text class="ph ph-circle-notch spin"></text> 加载中...
    </view>

    <view class="task-list" v-else>
      <view
        v-for="task in tasks"
        :key="task.id || task.task_type"
        :class="['task-card', { completed: task.status === 'completed' }]"
      >
        <view class="task-tag" v-if="isRecommended(task)">推荐</view>
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

      <view class="empty-hint" v-if="tasks.length === 0 && !loading">
        <text class="empty-emoji">📋</text>
        <view class="empty-text">暂无任务，请家长在训练页面创建</view>
      </view>
    </view>

    <!-- 成就系统 -->
    <view class="section-title">我的成就</view>
    <view class="achievements-grid">
      <view :class="['achievement-card', totalStars >= 3 ? 'active' : '']">
        <text class="ph ph-medal"></text>
        <view class="achievement-name">初出茅庐</view>
        <view class="achievement-req">获得3颗星</view>
      </view>
      <view :class="['achievement-card', totalStars >= 10 ? 'active' : '']">
        <text class="ph ph-trophy"></text>
        <view class="achievement-name">训练达人</view>
        <view class="achievement-req">获得10颗星</view>
      </view>
      <view :class="['achievement-card', totalStars >= 30 ? 'active' : '']">
        <text class="ph ph-crown"></text>
        <view class="achievement-name">语言之王</view>
        <view class="achievement-req">获得30颗星</view>
      </view>
    </view>

    <view style="height: 160rpx;"></view>
  </scroll-view>
</template>

<script>
import { getTasks } from '../../api/training.js'
import { getCurrentChild } from '../../utils/auth.js'
import { GAME_TASK_ICONS, GAME_TASK_DEFAULT_NAMES, GAME_TASK_DESCS, GAME_CARD_COLORS } from '../../utils/constants.js'

export default {
  name: 'TrainingTab',
  props: {
    childId: { type: Number, default: null },
    totalStars: { type: Number, default: 0 },
  },
  data() {
    return {
      tasks: [],
      loading: false,
    }
  },
  computed: {
    completedCount() { return this.tasks.filter(t => t.status === 'completed').length },
    progressPercent() {
      if (!this.tasks.length) return 0
      return Math.round((this.completedCount / this.tasks.length) * 100)
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
        const allTasks = await getTasks(this.childId)
        // 训练tab只显示家长在训练计划页手动创建的任务（有scheduled_date）
        // 按日期降序，只取最近7天内的未完成任务 + 今日已完成任务
        const today = new Date().toISOString().split('T')[0]
        const sevenDaysAgo = new Date(Date.now() - 7 * 86400000).toISOString().split('T')[0]
        this.tasks = allTasks.filter(t => {
          const d = (t.scheduled_date || '').split('T')[0]
          if (!d) return false  // 没有scheduled_date的是游戏自动创建的，不显示
          if (t.status === 'completed' && d !== today) return false  // 非今日已完成的不显示
          return d >= sevenDaysAgo  // 只显示最近7天的
        }).slice(0, 10)
      } catch (e) {
        console.warn('加载任务失败', e)
      } finally {
        this.loading = false
      }
    },
    isRecommended(task) {
      if (task.status === 'completed') return false
      const first = this.tasks.find(t => t.status !== 'completed')
      return first && (first.id === task.id || first.task_type === task.task_type)
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
      const child = getCurrentChild()
      const gradeParam = child?.grade ? `&grade=${encodeURIComponent(child.grade)}` : ''
      const taskIdParam = task.id ? `&task_id=${task.id}` : ''

      const newGames = ['handwriting', 'flip_card', 'connect_game']
      if (newGames.includes(gameType)) {
        // 新三种游戏也经过引导页，引导页会透传 task_id 和 difficulty
        const diffParam = `&difficulty=L1`
        uni.navigateTo({ url: `/pages/child/prep/index?game_type=${gameType}${taskIdParam}${diffParam}` })
      } else {
        uni.navigateTo({ url: `/pages/child/training-game/index?game_type=${gameType}${gradeParam}${taskIdParam}` })
      }
    },
  },
}
</script>

<style scoped>
.training-tab {
  flex: 1;
  width: 100%;
  height: 100%;
  padding: 24rpx 28rpx 0;
  box-sizing: border-box;
}

.progress-card {
  background: linear-gradient(135deg, #4F9EF8 0%, #3B82F6 100%);
  border-radius: 28rpx; padding: 32rpx; margin-bottom: 28rpx; position: relative; overflow: hidden;
}
.progress-card::before {
  content: ''; position: absolute; top: -40%; right: -20%;
  width: 200rpx; height: 200rpx; border-radius: 50%; background: rgba(255,255,255,0.1);
}
.progress-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20rpx; position: relative; z-index: 1; }
.progress-title { font-size: 32rpx; font-weight: 700; color: rgba(255,255,255,0.9); }
.progress-subtitle { font-size: 22rpx; color: rgba(255,255,255,0.6); margin-top: 4rpx; }
.progress-count { font-size: 56rpx; font-weight: 900; color: #FFFFFF; line-height: 1; }
.count-total { font-size: 28rpx; color: rgba(255,255,255,0.6); }
.progress-track { height: 10rpx; background: rgba(255,255,255,0.2); border-radius: 5rpx; overflow: hidden; position: relative; z-index: 1; }
.progress-fill { height: 100%; background: rgba(255,255,255,0.9); border-radius: 5rpx; transition: width 0.6s; }

.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
  text-align: center;
}

.loading-row { display: flex; align-items: center; justify-content: center; gap: 12rpx; color: #A0AEC0; font-size: 26rpx; padding: 24rpx 0; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

.task-list { display: flex; flex-direction: column; gap: 14rpx; margin-bottom: 28rpx; }
.task-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 22rpx 20rpx;
  display: flex; align-items: center; gap: 18rpx;
  position: relative; overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
}
.task-card:active { transform: scale(0.98); }
.task-card.completed { opacity: 0.55; }
.task-tag {
  position: absolute; top: 0; right: 0;
  background: linear-gradient(135deg, #FF6B6B, #FF8E8E); color: #FFFFFF;
  font-size: 18rpx; font-weight: 700; padding: 6rpx 20rpx; border-radius: 0 24rpx 0 16rpx;
}
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
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; font-size: 24rpx; font-weight: 700; flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(59,130,246,0.25);
}
.task-btn:active { transform: scale(0.95); }
.task-btn.done { background: #F5F5F5; color: #A0AEC0; box-shadow: none; }

.empty-hint { display: flex; flex-direction: column; align-items: center; gap: 12rpx; padding: 48rpx 0; }
.empty-emoji { font-size: 64rpx; }
.empty-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }

.achievements-grid { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.achievement-card {
  flex: 1; background: #FFFFFF; border-radius: 20rpx; padding: 24rpx 12rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); transition: all 0.2s;
}
.achievement-card .ph { font-size: 48rpx; color: #D1D5DB; margin-bottom: 8rpx; }
.achievement-card.active {
  background: linear-gradient(135deg, #FFFDE7, #FFF9C4);
  box-shadow: 0 4rpx 16rpx rgba(255,213,79,0.2); transform: translateY(-4rpx);
}
.achievement-card.active .ph { color: #F57F17; }
.achievement-name { font-size: 20rpx; font-weight: 700; color: #A0AEC0; text-align: center; width: 100%; }
.achievement-card.active .achievement-name { color: #2D3748; }
.achievement-req { font-size: 18rpx; color: #D1D5DB; margin-top: 4rpx; text-align: center; font-weight: 500; width: 100%; }
.achievement-card.active .achievement-req { color: #F57F17; }
</style>
