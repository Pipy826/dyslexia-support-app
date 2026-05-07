<template>
  <view class="page-container">
    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-caret-left"></text>
      </view>
      <view class="page-title">全部任务</view>
      <view class="placeholder"></view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar">
      <view
        v-for="tab in filterTabs"
        :key="tab.value"
        :class="['filter-tab', { active: activeFilter === tab.value }]"
        @click="activeFilter = tab.value"
      >{{ tab.label }}</view>
    </view>

    <!-- 内容区 -->
    <scroll-view class="page-content" scroll-y>

      <!-- 加载中 -->
      <view class="loading-row" v-if="loading">
        <text class="ph ph-circle-notch spin"></text>
        <text>加载中...</text>
      </view>

      <!-- 任务列表 -->
      <view v-else-if="filteredTasks.length > 0">
        <!-- 按日期分组 -->
        <view v-for="group in groupedTasks" :key="group.dateKey">
          <view class="date-group-label">{{ group.dateLabel }}</view>
          <view class="task-list">
            <view
              v-for="task in group.tasks"
              :key="task.id || task.task_type + task.created_at"
              :class="['task-card', { completed: task.status === 'completed' }]"
            >
              <!-- 推荐标签 -->
              <view class="task-tag recommended" v-if="isRecommended(task)">推荐</view>
              <!-- 今日标签 -->
              <view class="task-tag today" v-else-if="isToday(task)">今日</view>

              <view class="task-icon-wrap" :style="taskIconStyle(task.task_type)">
                <text :class="'ph ' + getTaskIcon(task.task_type)"></text>
              </view>

              <view class="task-info">
                <view class="task-name">{{ task.task_name || getTaskName(task.task_type) }}</view>
                <view class="task-meta">
                  <text class="task-desc">{{ getTaskDesc(task.task_type) }}</text>
                  <text class="task-date" v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</text>
                </view>
                <view class="task-status-row" v-if="task.status === 'completed' && task.accuracy != null">
                  <text class="ph ph-star-fill status-star"></text>
                  <text class="status-acc">正确率 {{ task.accuracy }}%</text>
                </view>
              </view>

              <button
                :class="['task-btn', { done: task.status === 'completed' }]"
                @click="startTask(task)"
                :disabled="task.status === 'completed'"
              >
                {{ task.status === 'completed' ? '已完成 ✓' : '去完成' }}
              </button>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else-if="!loading">
        <text class="empty-emoji">📋</text>
        <view class="empty-title">
          {{ activeFilter === 'pending' ? '没有待完成的任务' : activeFilter === 'completed' ? '还没有完成的任务' : activeFilter === 'challenge' ? '没有挑战游戏任务' : activeFilter === 'training' ? '没有关卡训练任务' : '暂无任务记录' }}
        </view>
        <view class="empty-desc">
          {{ activeFilter === 'challenge' ? '去挑战页面开始游戏吧！' : activeFilter === 'training' ? '去训练页面开始关卡挑战吧！' : '完成游戏或训练后会在这里显示' }}
        </view>
        <button class="go-challenge-btn" @click="goChallenge">
          <text class="ph ph-game-controller"></text> 去挑战
        </button>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getTasks } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { GAME_TASK_ICONS, GAME_TASK_DEFAULT_NAMES, GAME_TASK_DESCS, GAME_CARD_COLORS } from '../../../utils/constants.js'

// 与组件保持一致的分类定义
const CHALLENGE_GAME_TYPES = new Set(['handwriting', 'flip_card', 'connect_game'])
const LEVEL_GAME_TYPES = new Set(['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination'])

export default {
  name: 'AllTasks',
  data() {
    return {
      child: null,
      allTasks: [],
      loading: false,
      // 'all' | 'today' | 'training' — 初始值由 URL 参数决定
      activeFilter: 'all',
      filterTabs: [
        { value: 'all',       label: '全部' },
        { value: 'challenge', label: '挑战游戏' },
        { value: 'training',  label: '关卡训练' },
        { value: 'pending',   label: '待完成' },
        { value: 'completed', label: '已完成' },
      ],
    }
  },
  computed: {
    todayStr() {
      return new Date().toISOString().split('T')[0]
    },
    filteredTasks() {
      const today = this.todayStr
      return this.allTasks.filter(t => {
        if (this.activeFilter === 'challenge') {
          // 挑战游戏：handwriting/flip_card/connect_game
          return CHALLENGE_GAME_TYPES.has(t.task_type)
        }
        if (this.activeFilter === 'training') {
          // 关卡训练：前6种
          return LEVEL_GAME_TYPES.has(t.task_type)
        }
        if (this.activeFilter === 'pending') {
          return t.status !== 'completed'
        }
        if (this.activeFilter === 'completed') {
          return t.status === 'completed'
        }
        return true // 'all'
      }).sort((a, b) => {
        // 未完成的排前面，再按日期降序
        if (a.status !== b.status) {
          return a.status === 'completed' ? 1 : -1
        }
        const da = a.scheduled_date || a.created_at || ''
        const db = b.scheduled_date || b.created_at || ''
        return db.localeCompare(da)
      })
    },
    groupedTasks() {
      const today = this.todayStr
      const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0]
      const groups = {}
      for (const task of this.filteredTasks) {
        const dateKey = (task.scheduled_date || task.created_at || '').split('T')[0] || 'unknown'
        if (!groups[dateKey]) {
          let label = dateKey
          if (dateKey === today) label = '今天'
          else if (dateKey === yesterday) label = '昨天'
          else if (dateKey && dateKey !== 'unknown') {
            const d = new Date(dateKey)
            label = `${d.getMonth() + 1}月${d.getDate()}日`
          } else {
            label = '其他'
          }
          groups[dateKey] = { dateKey, dateLabel: label, tasks: [] }
        }
        groups[dateKey].tasks.push(task)
      }
      return Object.values(groups).sort((a, b) => {
        if (a.dateKey === 'unknown') return 1
        if (b.dateKey === 'unknown') return -1
        return b.dateKey.localeCompare(a.dateKey)
      })
    },
    firstPendingId() {
      const first = this.filteredTasks.find(t => t.status !== 'completed')
      return first?.id
    },
  },
  onLoad(options) {
    if (options.type && ['all', 'challenge', 'training', 'pending', 'completed'].includes(options.type)) {
      this.activeFilter = options.type
    }
    // 兼容旧的 today 参数
    if (options.type === 'today') {
      this.activeFilter = 'challenge'
    }
  },
  onShow() {
    this.child = getCurrentChild()
    if (this.child) this.loadTasks()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        this.allTasks = await getTasks(this.child.id)
      } catch (e) {
        console.warn('加载任务失败', e)
      } finally {
        this.loading = false
      }
    },
    isRecommended(task) {
      return task.status !== 'completed' && task.id === this.firstPendingId
    },
    isToday(task) {
      const scheduled = (task.scheduled_date || '').split('T')[0]
      return scheduled === this.todayStr
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      const today = this.todayStr
      const ds = dateStr.split('T')[0]
      if (ds === today) return '今天'
      return `${d.getMonth() + 1}月${d.getDate()}日`
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

      const challengeRoutes = {
        handwriting: '/pages/child/handwriting-game/index',
        flip_card:   '/pages/child/flip-card-game/index',
        connect_game: '/pages/child/connect-game/index',
      }
      if (challengeRoutes[gameType]) {
        uni.navigateTo({ url: `${challengeRoutes[gameType]}?difficulty=L1${taskIdParam}` })
        return
      }
      uni.navigateTo({
        url: `/pages/child/training-game/index?game_type=${gameType}&level_mode=true&difficulty=L1${taskIdParam}`
      })
    },
    goChallenge() {
      uni.navigateBack()
    },
    goBack() {
      uni.navigateBack()
    },
  },
}
</script>

<style scoped>
.page-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F5F7FA;
  overflow: hidden;
}

/* 顶部栏 */
.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 56rpx 32rpx 20rpx;
  background: #FFFFFF;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
  flex-shrink: 0;
}
.back-btn {
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  background: #F5F7FA;
  display: flex; align-items: center; justify-content: center;
}
.back-btn .ph { font-size: 32rpx; color: #2D3748; }
.back-btn:active { background: #EFF6FF; }
.page-title { font-size: 34rpx; font-weight: 800; color: #2D3748; }
.placeholder { width: 64rpx; }

/* 筛选栏 */
.filter-bar {
  display: flex;
  flex-direction: row;
  gap: 0;
  padding: 16rpx 24rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  flex-shrink: 0;
  overflow-x: auto;
}
.filter-tab {
  flex-shrink: 0;
  padding: 12rpx 28rpx;
  border-radius: 40rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #A0AEC0;
  background: transparent;
  transition: all 0.2s;
  margin-right: 8rpx;
}
.filter-tab.active {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  box-shadow: 0 2rpx 8rpx rgba(59,130,246,0.25);
}

/* 内容区 */
.page-content {
  flex: 1;
  min-height: 0;
  padding: 24rpx 28rpx 0;
  box-sizing: border-box;
}

/* 加载 */
.loading-row {
  display: flex; align-items: center; justify-content: center; gap: 12rpx;
  color: #A0AEC0; font-size: 26rpx; padding: 60rpx 0;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 日期分组标签 */
.date-group-label {
  font-size: 22rpx;
  font-weight: 700;
  color: #A0AEC0;
  padding: 8rpx 4rpx 12rpx;
  letter-spacing: 1rpx;
}

/* 任务列表 */
.task-list { display: flex; flex-direction: column; gap: 14rpx; margin-bottom: 20rpx; }

.task-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 22rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 18rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
  border: 2rpx solid transparent;
}
.task-card:active { transform: scale(0.98); }
.task-card.completed {
  opacity: 0.6;
  background: #FAFAFA;
}

/* 标签 */
.task-tag {
  position: absolute; top: 0; right: 0;
  font-size: 18rpx; font-weight: 700;
  padding: 6rpx 20rpx;
  border-radius: 0 24rpx 0 16rpx;
}
.task-tag.recommended {
  background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
  color: #FFFFFF;
}
.task-tag.today {
  background: linear-gradient(135deg, #FF8F00, #F57F17);
  color: #FFFFFF;
}

/* 图标 */
.task-icon-wrap {
  width: 88rpx; height: 88rpx;
  border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.task-icon-wrap .ph { font-size: 44rpx; color: var(--icon-color, #4F9EF8); }

/* 任务信息 */
.task-info { flex: 1; min-width: 0; }
.task-name { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 4rpx; }
.task-meta { display: flex; align-items: center; flex-wrap: wrap; }
.task-desc { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }
.task-date { font-size: 22rpx; color: #CBD5E0; font-weight: 500; }
.task-status-row {
  display: flex; align-items: center; gap: 6rpx; margin-top: 6rpx;
}
.status-star { font-size: 22rpx; color: #F59E0B; }
.status-acc { font-size: 22rpx; color: #F59E0B; font-weight: 700; }

/* 按钮 */
.task-btn {
  padding: 14rpx 24rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 16rpx;
  font-size: 24rpx;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(59,130,246,0.25);
}
.task-btn:active { transform: scale(0.95); }
.task-btn.done {
  background: #F5F5F5;
  color: #A0AEC0;
  box-shadow: none;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx;
  gap: 16rpx;
}
.empty-emoji { font-size: 80rpx; line-height: 1; }
.empty-title { font-size: 30rpx; font-weight: 800; color: #2D3748; text-align: center; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; font-weight: 500; text-align: center; }
.go-challenge-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 24rpx 48rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex; flex-direction: row; align-items: center; gap: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(59,130,246,0.3);
  margin-top: 8rpx;
}
.go-challenge-btn:active { transform: scale(0.97); }
.go-challenge-btn .ph { font-size: 28rpx; }
</style>
