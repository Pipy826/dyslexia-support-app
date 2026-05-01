<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">全部动态</view>
    </view>

    <!-- 筛选栏 -->
    <view class="filter-bar">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        :class="['filter-tab', { active: activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >{{ tab.label }}</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <view v-if="filteredActivities.length > 0">
        <!-- 按日期分组 -->
        <view v-for="group in groupedActivities" :key="group.date">
          <view class="date-group-label">{{ group.dateLabel }}</view>
          <view
            v-for="item in group.items"
            :key="item.id"
            class="activity-card"
            @click="openDetail(item)"
          >
            <view class="activity-icon" :class="item.color">
              <text :class="'ph ' + item.icon"></text>
            </view>
            <view class="activity-content">
              <view class="activity-title">{{ item.title }}</view>
              <view class="activity-time">{{ item.timeStr }}</view>
            </view>
            <view class="activity-badge" :class="item.badgeColor" v-if="item.badge">
              {{ item.badge }}
            </view>
            <text class="ph ph-caret-right activity-arrow" v-if="item.reportId"></text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && filteredActivities.length === 0">
        <text class="ph ph-clock empty-icon"></text>
        <view class="empty-text">暂无动态记录</view>
        <view class="empty-hint">完成游戏或训练后将在这里显示</view>
      </view>

      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <text class="ph ph-circle-notch spin"></text> 加载中...
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getReports } from '../../../api/report.js'
import { getTasks, getGrowthRecords } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { friendlyRiskLevel } from '../../../utils/terminology.js'

const GAME_TYPE_NAMES = {
  visual: '找不同', spelling: '文字认读', comprehension: '阅读理解',
  working_memory: '记忆游戏', rapid_naming: '快速阅读', motor_coordination: '书写练习',
}

export default {
  data() {
    return {
      currentChild: null,
      allActivities: [],
      loading: false,
      activeTab: 'all',
      tabs: [
        { label: '全部', value: 'all' },
        { label: '游戏记录', value: 'game' },
        { label: '训练记录', value: 'training' },
      ],
    }
  },
  computed: {
    filteredActivities() {
      if (this.activeTab === 'all') return this.allActivities
      return this.allActivities.filter(a => a.type === this.activeTab)
    },
    groupedActivities() {
      const groups = {}
      for (const item of this.filteredActivities) {
        const key = item.dateKey
        if (!groups[key]) {
          groups[key] = { date: key, dateLabel: this.formatGroupDate(key), items: [] }
        }
        groups[key].items.push(item)
      }
      return Object.values(groups).sort((a, b) => b.date.localeCompare(a.date))
    },
  },
  onLoad() {
    this.currentChild = getCurrentChild()
    this.loadActivities()
  },
  methods: {
    async loadActivities() {
      if (!this.currentChild) return
      this.loading = true
      try {
        // 并行加载游戏报告 + 训练任务 + 成长记录
        const [reports, tasks, growthRecords] = await Promise.allSettled([
          getReports(this.currentChild.id, 50),
          getTasks(this.currentChild.id),
          getGrowthRecords(this.currentChild.id),
        ])

        const activities = []

        // 游戏记录（来自报告）
        const reportList = reports.status === 'fulfilled' ? (reports.value || []) : []
        for (const r of reportList) {
          const gameName = GAME_TYPE_NAMES[r.game_type] || '文字游戏'
          const riskLabel = friendlyRiskLevel(r.risk_level)
          activities.push({
            id: `report_${r.id}`,
            type: 'game',
            icon: 'ph-game-controller',
            color: 'blue',
            title: `完成「${gameName}」游戏`,
            badge: riskLabel,
            badgeColor: r.risk_level === 'low' ? 'green' : r.risk_level === 'medium' ? 'orange' : 'red',
            dateKey: this.toDateKey(r.created_at),
            timeStr: this.formatTime(r.created_at),
            reportId: r.id,
            score: r.overall_score,
          })
        }

        // 训练记录（已完成的任务）
        const taskList = tasks.status === 'fulfilled' ? (tasks.value || []) : []
        for (const t of taskList.filter(t => t.status === 'completed')) {
          activities.push({
            id: `task_${t.id}`,
            type: 'training',
            icon: 'ph-check-circle',
            color: 'green',
            title: `完成训练「${t.task_name}」`,
            badge: t.accuracy ? `正确率 ${t.accuracy}%` : '已完成',
            badgeColor: 'green',
            dateKey: this.toDateKey(t.completed_at || t.created_at),
            timeStr: this.formatTime(t.completed_at || t.created_at),
            reportId: null,
          })
        }

        // 成长记录
        const growthList = growthRecords.status === 'fulfilled' ? (growthRecords.value || []) : []
        for (const g of growthList) {
          activities.push({
            id: `growth_${g.id}`,
            type: 'training',
            icon: 'ph-trend-up',
            color: 'purple',
            title: g.title || '成长记录',
            badge: null,
            badgeColor: '',
            dateKey: this.toDateKey(g.created_at),
            timeStr: this.formatTime(g.created_at),
            reportId: null,
          })
        }

        // 按时间倒序排列
        activities.sort((a, b) => b.dateKey.localeCompare(a.dateKey) || b.timeStr.localeCompare(a.timeStr))
        this.allActivities = activities
      } catch (e) {
        console.error('加载动态失败', e)
      } finally {
        this.loading = false
      }
    },
    toDateKey(dateStr) {
      if (!dateStr) return '1970-01-01'
      return dateStr.slice(0, 10)
    },
    formatTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    },
    formatGroupDate(dateKey) {
      const today = new Date().toISOString().slice(0, 10)
      const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10)
      if (dateKey === today) return '今天'
      if (dateKey === yesterday) return '昨天'
      const d = new Date(dateKey)
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    openDetail(item) {
      if (item.reportId) {
        uni.navigateTo({ url: `/pages/parent/report/detail?id=${item.reportId}` })
      }
    },
    goBack() {
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

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }

.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

/* 筛选栏 */
.filter-bar {
  display: flex;
  gap: 12rpx;
  padding: 12rpx 32rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  flex-shrink: 0;
}

.filter-tab {
  padding: 10rpx 24rpx;
  border-radius: 9999rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #718096;
  background: #F5F7FA;
  transition: all 0.2s;
}

.filter-tab.active {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
}

/* 内容区 */
.page-content {
  flex: 1;
  padding: 16rpx 32rpx;
  box-sizing: border-box;
}

/* 日期分组标签 */
.date-group-label {
  font-size: 22rpx;
  font-weight: 700;
  color: #A0AEC0;
  padding: 16rpx 0 8rpx;
  letter-spacing: 1rpx;
}

/* 动态卡片 */
.activity-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 10rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
  transition: all 0.2s;
}

.activity-card:active { transform: scale(0.99); }

.activity-icon {
  width: 64rpx; height: 64rpx;
  border-radius: 16rpx;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.activity-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.activity-icon.blue .ph { font-size: 30rpx; color: #4F9EF8; }
.activity-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.activity-icon.green .ph { font-size: 30rpx; color: #22C55E; }
.activity-icon.purple { background: linear-gradient(135deg, #F5F3FF, #EDE9FE); }
.activity-icon.purple .ph { font-size: 30rpx; color: #7C3AED; }

.activity-content { flex: 1; min-width: 0; }

.activity-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-time {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 4rpx;
  font-weight: 500;
}

.activity-badge {
  font-size: 20rpx;
  font-weight: 700;
  padding: 6rpx 14rpx;
  border-radius: 10rpx;
  flex-shrink: 0;
}

.activity-badge.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); color: #22C55E; }
.activity-badge.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); color: #F57F17; }
.activity-badge.red { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); color: #FF6B6B; }

.activity-arrow { font-size: 24rpx; color: #D1D5DB; flex-shrink: 0; }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx;
  opacity: 0.6;
}

.empty-icon { font-size: 80rpx; color: #D1D5DB; margin-bottom: 20rpx; }
.empty-text { font-size: 28rpx; color: #A0AEC0; font-weight: 600; }
.empty-hint { font-size: 22rpx; color: #D1D5DB; margin-top: 8rpx; font-weight: 500; }

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  padding: 40rpx;
  font-size: 24rpx;
  color: #A0AEC0;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
