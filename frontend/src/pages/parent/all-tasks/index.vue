<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">全部任务</view>
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

    <scroll-view class="page-content" scroll-y>

      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <text class="ph ph-circle-notch spin"></text> 加载中...
      </view>

      <!-- 任务列表（按日期分组） -->
      <view v-else-if="filteredTasks.length > 0">
        <view v-for="group in groupedTasks" :key="group.dateKey">
          <view class="date-group-label">{{ group.dateLabel }}</view>
          <view class="task-list">
            <view
              v-for="task in group.tasks"
              :key="task.id"
              class="task-card"
              :class="{ completed: task.status === 'completed' }"
            >
              <view class="task-icon" :class="iconColor(task.task_type)">
                <text :class="'ph ' + taskIcon(task.task_type)"></text>
              </view>
              <view class="task-info">
                <view class="task-name">{{ task.task_name || taskName(task.task_type) }}</view>
                <view class="task-meta">
                  <text class="task-desc">{{ taskDesc(task.task_type) }}</text>
                  <text class="task-date" v-if="task.scheduled_date"> · {{ formatDate(task.scheduled_date) }}</text>
                </view>
                <!-- 完成结果 -->
                <view class="task-result" v-if="task.status === 'completed' && task.accuracy != null">
                  <view class="result-tag" :class="task.accuracy >= 80 ? 'green' : task.accuracy >= 60 ? 'orange' : 'red'">
                    正确率 {{ task.accuracy }}%
                  </view>
                  <view class="result-detail">答对 {{ task.correct_count }}/{{ task.total_count }} 题</view>
                </view>
              </view>
              <button
                class="task-btn"
                :class="{ done: task.status === 'completed' }"
                @click="startTask(task)"
                :disabled="task.status === 'completed'"
              >{{ task.status === 'completed' ? '已完成' : '去完成' }}</button>
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else-if="!loading">
        <text class="ph ph-clipboard-text empty-icon"></text>
        <view class="empty-title">
          {{ activeFilter === 'pending' ? '没有待完成的任务' : activeFilter === 'completed' ? '还没有完成的任务' : '暂无任务记录' }}
        </view>
        <view class="empty-hint">可以在训练计划页面为孩子创建任务</view>
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getTasks } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

const TASK_ICONS = {
  visual: 'ph-eye', spelling: 'ph-puzzle-piece', comprehension: 'ph-book-open',
  working_memory: 'ph-brain', rapid_naming: 'ph-lightning', motor_coordination: 'ph-hand',
  handwriting: 'ph-pencil-line', flip_card: 'ph-cards', connect_game: 'ph-link',
  reading: 'ph-book-open',
}
const TASK_NAMES = {
  visual: '火眼金睛', spelling: '拼字识别', comprehension: '故事大王',
  working_memory: '记忆训练', rapid_naming: '快速命名', motor_coordination: '精细动作',
  handwriting: '汉字书写', flip_card: '翻牌记忆', connect_game: '连一连',
  reading: '阅读理解',
}
const TASK_DESCS = {
  visual: '视觉辨识训练', spelling: '汉字结构记忆', comprehension: '阅读理解训练',
  working_memory: '工作记忆提升', rapid_naming: '命名速度训练', motor_coordination: '手眼协调训练',
  handwriting: '笔顺书写练习', flip_card: '词汇记忆配对', connect_game: '语义理解连线',
}

export default {
  data() {
    return {
      currentChild: null,
      allTasks: [],
      loading: false,
      activeFilter: 'all',
      filterTabs: [
        { value: 'all',       label: '全部' },
        { value: 'pending',   label: '待完成' },
        { value: 'completed', label: '已完成' },
        { value: 'today',     label: '今日' },
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
        if (this.activeFilter === 'pending')   return t.status !== 'completed'
        if (this.activeFilter === 'completed') return t.status === 'completed'
        if (this.activeFilter === 'today') {
          const d = (t.scheduled_date || t.created_at || '').split('T')[0]
          return d === today
        }
        return true
      }).sort((a, b) => {
        // 未完成排前面，再按日期降序
        if (a.status !== b.status) return a.status === 'completed' ? 1 : -1
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
        const dateKey = (task.scheduled_date || task.created_at || '').split('T')[0] || 'other'
        if (!groups[dateKey]) {
          let label = dateKey
          if (dateKey === today) label = '今天'
          else if (dateKey === yesterday) label = '昨天'
          else if (dateKey && dateKey !== 'other') {
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
        if (a.dateKey === 'other') return 1
        if (b.dateKey === 'other') return -1
        return b.dateKey.localeCompare(a.dateKey)
      })
    },
  },
  onLoad(options) {
    if (options.filter && ['all', 'pending', 'completed', 'today'].includes(options.filter)) {
      this.activeFilter = options.filter
    }
  },
  onShow() {
    this.currentChild = getCurrentChild()
    if (this.currentChild) this.loadTasks()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        this.allTasks = await getTasks(this.currentChild.id)
      } catch (e) {
        console.warn('加载任务失败', e)
      } finally {
        this.loading = false
      }
    },
    taskIcon(type) { return TASK_ICONS[type] || 'ph-star' },
    taskName(type) { return TASK_NAMES[type] || type },
    taskDesc(type) { return TASK_DESCS[type] || '' },
    iconColor(type) {
      if (['visual', 'working_memory'].includes(type)) return 'orange'
      if (['spelling', 'rapid_naming', 'flip_card', 'connect_game'].includes(type)) return 'blue'
      return 'green'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const ds = dateStr.split('T')[0]
      if (ds === this.todayStr) return '今天'
      const d = new Date(ds)
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    startTask(task) {
      if (task.status === 'completed') return
      if (task.id) uni.setStorageSync('pending_task_id', task.id)
      const VALID_GAME_TYPES = new Set([
        'visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination',
        'handwriting', 'flip_card', 'connect_game',
      ])
      const typeMap = {
        reading: 'comprehension', reading_comprehension: 'comprehension',
        phonological: 'spelling', attention: 'visual',
        short_term_memory: 'working_memory', fine_motor_control: 'motor_coordination',
      }
      const rawType = task.task_type || 'visual'
      const gameType = VALID_GAME_TYPES.has(rawType) ? rawType : (typeMap[rawType] || 'visual')
      const isLevelGame = !['handwriting', 'flip_card', 'connect_game'].includes(gameType)
      const levelParam = isLevelGame ? '&level_mode=true' : ''
      uni.reLaunch({
        url: `/pages/child/child-training/index?tab=challenge&game_type=${gameType}${levelParam}`
      })
    },
    goBack() { uni.navigateBack() },
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

/* 头部 */
.page-header {
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
.header-title { font-size: 34rpx; font-weight: 800; color: #2D3748; }
.placeholder { width: 64rpx; }

/* 筛选栏 */
.filter-bar {
  display: flex;
  flex-direction: row;
  padding: 16rpx 24rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  flex-shrink: 0;
  gap: 8rpx;
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
.loading-state {
  display: flex; align-items: center; justify-content: center; gap: 12rpx;
  color: #A0AEC0; font-size: 26rpx; padding: 60rpx 0;
}
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

/* 日期分组 */
.date-group-label {
  font-size: 22rpx;
  font-weight: 700;
  color: #A0AEC0;
  padding: 8rpx 4rpx 12rpx;
  letter-spacing: 1rpx;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 14rpx;
  margin-bottom: 20rpx;
}

.task-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
  transition: all 0.2s;
  border: 2rpx solid transparent;
}
.task-card:active { transform: scale(0.98); }
.task-card.completed { opacity: 0.6; background: #FAFAFA; }

.task-icon {
  width: 80rpx; height: 80rpx;
  border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.task-icon .ph { font-size: 40rpx; }
.task-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.task-icon.orange .ph { color: #F57F17; }
.task-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.task-icon.blue .ph { color: #4F9EF8; }
.task-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.task-icon.green .ph { color: #22C55E; }

.task-info { flex: 1; min-width: 0; }
.task-name { font-size: 26rpx; font-weight: 700; color: #2D3748; margin-bottom: 4rpx; }
.task-meta { display: flex; align-items: center; flex-wrap: wrap; }
.task-desc { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }
.task-date { font-size: 20rpx; color: #CBD5E0; font-weight: 500; }

.task-result { display: flex; align-items: center; gap: 10rpx; margin-top: 8rpx; }
.result-tag { font-size: 18rpx; font-weight: 700; padding: 4rpx 12rpx; border-radius: 8rpx; }
.result-tag.green { background: rgba(34,197,94,0.1); color: #22C55E; }
.result-tag.orange { background: rgba(245,127,23,0.1); color: #F57F17; }
.result-tag.red { background: rgba(255,107,107,0.1); color: #FF6B6B; }
.result-detail { font-size: 18rpx; color: #A0AEC0; font-weight: 500; }

.task-btn {
  padding: 14rpx 28rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  box-shadow: 0 2rpx 8rpx rgba(59,130,246,0.2);
  flex-shrink: 0;
}
.task-btn:active { transform: scale(0.95); }
.task-btn.done { background: #F5F5F5; color: #A0AEC0; box-shadow: none; }

/* 空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 80rpx 40rpx; gap: 16rpx;
}
.empty-icon { font-size: 80rpx; color: #D1D5DB; }
.empty-title { font-size: 30rpx; font-weight: 800; color: #2D3748; text-align: center; }
.empty-hint { font-size: 24rpx; color: #A0AEC0; font-weight: 500; text-align: center; }
</style>
