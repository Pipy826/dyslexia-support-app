<template>
  <view class="page-container">
    <!-- 顶部 -->
    <view class="top-bar">
      <view class="page-title">训练乐园</view>
      <view class="stars-badge">
        <text class="ph ph-star"></text>
        <view class="stars-count">{{ totalStars }} 颗</view>
      </view>
    </view>

    <view class="content-area">
      <!-- 今日进度 -->
      <view class="progress-card">
        <view class="progress-header">
          <view class="progress-info">
            <view class="progress-title">今日任务</view>
            <view class="progress-subtitle">完成任务获得小星星哦！</view>
          </view>
          <view class="progress-count">
            {{ completedCount }}<text class="count-total">/{{ tasks.length || 3 }}</text>
          </view>
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
        </view>
      </view>

      <!-- 任务列表 -->
      <view class="section-title">我的任务</view>

      <!-- 加载中 -->
      <view class="loading-row" v-if="loading">
        <text class="ph ph-circle-notch spin"></text> 加载中...
      </view>

      <view class="task-list" v-else>
        <view
          v-for="task in tasks"
          :key="task.id || task.task_type"
          :class="['task-card', { completed: task.status === 'completed' }]"
        >
          <!-- 推荐标签（第一个未完成的任务） -->
          <view class="task-tag" v-if="isRecommended(task)">推荐</view>

          <view :class="['task-icon', taskColor(task.task_type)]">
            <text :class="'ph ' + taskIcon(task.task_type)"></text>
          </view>

          <view class="task-info">
            <view class="task-name">{{ task.task_name || taskDefaultName(task.task_type) }}</view>
            <view class="task-desc">{{ taskDesc(task.task_type) }}</view>
          </view>

          <button
            :class="['task-btn', { done: task.status === 'completed' }]"
            @click="startTask(task)"
            :disabled="task.status === 'completed'"
          >
            {{ task.status === 'completed' ? '已完成 ✓' : '去完成' }}
          </button>
        </view>

        <!-- 无任务时的默认展示 -->
        <view class="empty-hint" v-if="tasks.length === 0 && !loading">
          <text class="ph ph-calendar-blank"></text>
          <view>今日暂无任务，请家长在训练页面创建</view>
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
    </view>

    <!-- 底部导航 -->
    <view class="bottom-nav">
      <view class="nav-item" @click="goToChallenge">
        <text class="ph ph-game-controller"></text>
        <view class="nav-label">挑战</view>
      </view>
      <view class="nav-item active">
        <text class="ph-fill ph-tree"></text>
        <view class="nav-label">训练乐园</view>
      </view>
    </view>
  </view>
</template>

<script>
import { getTasks, getTotalStars } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      tasks: [],
      totalStars: 0,
      child: null,
      loading: true
    }
  },
  computed: {
    completedCount() {
      return this.tasks.filter(t => t.status === 'completed').length
    },
    progressPercent() {
      if (!this.tasks.length) return 0
      return Math.round((this.completedCount / this.tasks.length) * 100)
    }
  },
  onShow() {
    this.child = getCurrentChild()
    if (this.child) {
      this.loadData()
    } else {
      this.loading = false
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const [allTasks, starRes] = await Promise.all([
          getTasks(this.child.id),
          getTotalStars(this.child.id)
        ])
        // 取今日任务，没有则取最近3条
        const today = new Date().toISOString().split('T')[0]
        let todayTasks = allTasks.filter(t => {
          const d = (t.scheduled_date || t.created_at || '').split('T')[0]
          return d === today
        })
        this.tasks = todayTasks.length > 0 ? todayTasks : allTasks.slice(0, 3)
        this.totalStars = starRes.total_stars || 0
      } catch (e) {
        console.error('加载失败', e)
      } finally {
        this.loading = false
      }
    },
    isRecommended(task) {
      if (task.status === 'completed') return false
      // 第一个未完成的任务标记为推荐
      const firstPending = this.tasks.find(t => t.status !== 'completed')
      return firstPending && (firstPending.id === task.id || firstPending.task_type === task.task_type)
    },
    startTask(task) {
      if (task.status === 'completed') return
      if (task.id) {
        uni.setStorageSync('pending_task_id', task.id)
      }
      // reading 映射到 comprehension（后端不支持 reading 类型）
      const typeMap = { reading: 'comprehension' }
      const gameType = typeMap[task.task_type] || task.task_type || 'visual'
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${gameType}`
      })
    },
    taskIcon(type) {
      return { visual: 'ph-eye', spelling: 'ph-puzzle-piece', reading: 'ph-book-open', comprehension: 'ph-book-open' }[type] || 'ph-star'
    },
    taskColor(type) {
      return { visual: 'orange', spelling: 'blue', reading: 'green', comprehension: 'green' }[type] || 'blue'
    },
    taskDefaultName(type) {
      return { visual: '火眼金睛', spelling: '拼字小达人', reading: '故事大王', comprehension: '故事大王' }[type] || '训练任务'
    },
    taskDesc(type) {
      return { visual: '找出不一样的字', spelling: '把字拼完整', reading: '读句子选图片', comprehension: '读句子选图片' }[type] || ''
    },
    goToChallenge() {
      uni.redirectTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  padding-bottom: 168rpx;
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title { font-size: 48rpx; font-weight: 700; color: #374151; }

.stars-badge {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #FEF3C7;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  border: 1rpx solid #FDE68A;
}
.stars-badge .ph { font-size: 32rpx; color: #F59E0B; }
.stars-count { font-size: 26rpx; font-weight: 700; color: #D97706; }

.content-area { flex: 1; padding: 32rpx 48rpx; }

/* 进度卡片 */
.progress-card {
  background: #EFF6FF;
  border-radius: 48rpx;
  padding: 40rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DBEAFE;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32rpx;
}
.progress-title { font-size: 40rpx; font-weight: 700; color: #374151; }
.progress-subtitle { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }
.progress-count { font-size: 64rpx; font-weight: 800; color: #3B82F6; }
.count-total { font-size: 32rpx; color: #93C5FD; }
.progress-track {
  height: 28rpx;
  background: #FFFFFF;
  border-radius: 14rpx;
  overflow: hidden;
  border: 1rpx solid #DBEAFE;
}
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3B82F6, #10B981);
  border-radius: 14rpx;
  transition: width 0.6s ease;
}

.section-title { font-size: 32rpx; font-weight: 700; color: #374151; margin-bottom: 24rpx; }

/* 加载 */
.loading-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  color: #9CA3AF;
  font-size: 26rpx;
  padding: 32rpx 0;
}
.loading-row .ph { font-size: 36rpx; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 48rpx;
}

.task-card {
  background: #FFFFFF;
  border: 4rpx solid #F3F4F6;
  border-radius: 48rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  position: relative;
  overflow: hidden;
  transition: all 0.2s;
}
.task-card.completed { opacity: 0.65; }

.task-tag {
  position: absolute;
  top: 0; right: 0;
  background: #EF4444;
  color: #FFFFFF;
  font-size: 18rpx;
  font-weight: 700;
  padding: 8rpx 24rpx;
  border-radius: 0 44rpx 0 24rpx;
}

.task-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.task-icon .ph { font-size: 56rpx; }
.task-icon.green { background: #ECFDF5; }
.task-icon.green .ph { color: #10B981; }
.task-icon.blue { background: #EFF6FF; }
.task-icon.blue .ph { color: #3B82F6; }
.task-icon.orange { background: #FEF3C7; }
.task-icon.orange .ph { color: #F59E0B; }

.task-info { flex: 1; }
.task-name { font-size: 34rpx; font-weight: 700; color: #374151; }
.task-desc { font-size: 22rpx; color: #9CA3AF; margin-top: 4rpx; }

.task-btn {
  padding: 16rpx 32rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  font-size: 24rpx;
  font-weight: 700;
  flex-shrink: 0;
}
.task-btn.done { background: #F3F4F6; color: #9CA3AF; }

/* 空状态 */
.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 64rpx 0;
  color: #9CA3AF;
  font-size: 26rpx;
}
.empty-hint .ph { font-size: 64rpx; color: #D1D5DB; }

/* 成就 */
.achievements-grid { display: flex; gap: 24rpx; }

.achievement-card {
  flex: 1;
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 32rpx 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2rpx solid #F3F4F6;
}
.achievement-card .ph { font-size: 56rpx; color: #D1D5DB; margin-bottom: 12rpx; }
.achievement-card.active { border-color: #FDE68A; background: #FFFBEB; }
.achievement-card.active .ph { color: #F59E0B; }
.achievement-name { font-size: 22rpx; font-weight: 700; color: #9CA3AF; text-align: center; }
.achievement-card.active .achievement-name { color: #374151; }
.achievement-req { font-size: 18rpx; color: #D1D5DB; margin-top: 4rpx; text-align: center; }
.achievement-card.active .achievement-req { color: #F59E0B; }

/* 底部导航 */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  height: 168rpx;
  background: #FFFFFF;
  border-top: 1rpx solid #F3F4F6;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 16rpx 96rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  gap: 160rpx;
  z-index: 100;
}
.nav-item { display: flex; flex-direction: column; align-items: center; gap: 8rpx; color: #9CA3AF; }
.nav-item.active { color: #3B82F6; }
.nav-item .ph, .nav-item .ph-fill { font-size: 48rpx; }
.nav-label { font-size: 22rpx; font-weight: 500; }
.nav-item.active .nav-label { font-weight: 700; }
</style>
