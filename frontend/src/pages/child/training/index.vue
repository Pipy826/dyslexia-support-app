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
/* 创意训练乐园 - 任务卡片流 */
.page-container { min-height: 100vh; background: #F8FAFF; display: flex; flex-direction: column; padding-bottom: 140rpx; }

.top-bar {
  position: sticky; top: 0; z-index: 30;
  background: rgba(248, 250, 255, 0.95); backdrop-filter: blur(20rpx);
  padding: 56rpx 32rpx 20rpx; display: flex; justify-content: space-between; align-items: center;
}
.page-title { font-size: 40rpx; font-weight: 800; color: #2D3748; }
.stars-badge {
  display: flex; align-items: center; gap: 6rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  padding: 10rpx 20rpx; border-radius: 20rpx; box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.3);
}
.stars-badge .ph { font-size: 28rpx; color: #F57F17; }
.stars-count { font-size: 24rpx; font-weight: 700; color: #E65100; }

.content-area { flex: 1; padding: 24rpx 32rpx; }

.progress-card {
  background: linear-gradient(135deg, #4F9EF8 0%, #7C3AED 100%);
  border-radius: 28rpx; padding: 32rpx; margin-bottom: 32rpx; position: relative; overflow: hidden;
}
.progress-card::before {
  content: ''; position: absolute; top: -40%; right: -20%;
  width: 200rpx; height: 200rpx; border-radius: 50%; background: rgba(255, 255, 255, 0.1);
}
.progress-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24rpx; position: relative; z-index: 1; }
.progress-title { font-size: 32rpx; font-weight: 700; color: rgba(255, 255, 255, 0.9); }
.progress-subtitle { font-size: 22rpx; color: rgba(255, 255, 255, 0.6); margin-top: 4rpx; }
.progress-count { font-size: 56rpx; font-weight: 900; color: #FFFFFF; line-height: 1; }
.count-total { font-size: 28rpx; color: rgba(255, 255, 255, 0.6); }
.progress-track { height: 10rpx; background: rgba(255, 255, 255, 0.2); border-radius: 5rpx; overflow: hidden; position: relative; z-index: 1; }
.progress-fill { height: 100%; background: rgba(255, 255, 255, 0.9); border-radius: 5rpx; transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1); }

.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; display: flex; align-items: center; gap: 10rpx; }
.section-title::before { content: ''; display: inline-block; width: 5rpx; height: 24rpx; background: linear-gradient(180deg, #4F9EF8, #A78BFA); border-radius: 3rpx; }

.loading-row { display: flex; align-items: center; gap: 12rpx; color: #A0AEC0; font-size: 26rpx; font-weight: 600; padding: 24rpx 0; }
.loading-row .ph { font-size: 32rpx; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

.task-list { display: flex; flex-direction: column; gap: 16rpx; margin-bottom: 32rpx; }
.task-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 24rpx; display: flex; align-items: center; gap: 20rpx;
  position: relative; overflow: hidden; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
.task-card:active { transform: scale(0.98); }
.task-card.completed { opacity: 0.55; }
.task-tag {
  position: absolute; top: 0; right: 0;
  background: linear-gradient(135deg, #FF6B6B, #FF8E8E); color: #FFFFFF;
  font-size: 18rpx; font-weight: 700; padding: 6rpx 20rpx; border-radius: 0 24rpx 0 16rpx;
}
.task-icon { width: 96rpx; height: 96rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.task-icon .ph { font-size: 48rpx; }
.task-icon.green { background: linear-gradient(135deg, #DCFCE7, #BBF7D0); }
.task-icon.green .ph { color: #22C55E; }
.task-icon.blue { background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }
.task-icon.blue .ph { color: #4F9EF8; }
.task-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.task-icon.orange .ph { color: #F57F17; }
.task-info { flex: 1; }
.task-name { font-size: 30rpx; font-weight: 700; color: #2D3748; }
.task-desc { font-size: 22rpx; color: #A0AEC0; margin-top: 4rpx; font-weight: 500; }
.task-btn {
  padding: 14rpx 28rpx; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 14rpx; font-size: 24rpx; font-weight: 700; flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(59, 130, 246, 0.25); transition: all 0.2s;
}
.task-btn:active { transform: scale(0.95); }
.task-btn.done { background: #F5F5F5; color: #A0AEC0; box-shadow: none; }

.empty-hint { display: flex; flex-direction: column; align-items: center; gap: 12rpx; padding: 48rpx 0; color: #A0AEC0; font-size: 26rpx; font-weight: 600; }
.empty-hint .ph { font-size: 64rpx; color: #FFD93D; }

.achievements-grid { display: flex; gap: 16rpx; }
.achievement-card {
  flex: 1; background: #FFFFFF; border-radius: 20rpx; padding: 24rpx 12rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04); transition: all 0.2s;
}
.achievement-card .ph { font-size: 48rpx; color: #D1D5DB; margin-bottom: 8rpx; }
.achievement-card.active {
  background: linear-gradient(135deg, #FFFDE7, #FFF9C4);
  box-shadow: 0 4rpx 16rpx rgba(255, 213, 79, 0.2); transform: translateY(-4rpx);
}
.achievement-card.active .ph { color: #F57F17; }
.achievement-name { font-size: 20rpx; font-weight: 700; color: #A0AEC0; text-align: center; }
.achievement-card.active .achievement-name { color: #2D3748; }
.achievement-req { font-size: 18rpx; color: #D1D5DB; margin-top: 4rpx; text-align: center; font-weight: 500; }
.achievement-card.active .achievement-req { color: #F57F17; }
</style>
