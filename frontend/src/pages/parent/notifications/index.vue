<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">消息通知</view>
      <view class="clear-btn" @click="markAll" v-if="hasUnread">全部已读</view>
    </view>

    <!-- 加载中 -->
    <view class="loading-state" v-if="loading">
      <text class="ph ph-circle-notch spin"></text>
    </view>

    <scroll-view class="page-content" scroll-y v-else @scrolltolower="loadMore">
      <view class="notif-list" v-if="notifications.length > 0">
        <view
          class="notif-item"
          v-for="n in notifications"
          :key="n.id"
          :class="{ unread: !n.is_read }"
          @click="handleNotif(n)"
        >
          <view class="notif-icon" :class="notifColor(n.notif_type)">
            <text :class="'ph ' + (n.icon || 'ph-bell')"></text>
          </view>
          <view class="notif-body">
            <view class="notif-title">{{ n.title }}</view>
            <view class="notif-desc">{{ n.body }}</view>
            <view class="notif-time">{{ formatTime(n.created_at) }}</view>
          </view>
          <view class="unread-dot" v-if="!n.is_read"></view>
        </view>
      </view>

      <view class="empty-state" v-else>
        <text class="ph ph-bell-slash empty-icon"></text>
        <view class="empty-title">暂无通知</view>
        <view class="empty-desc">完成训练或筛查后，系统会在这里提醒您</view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getNotifications, markAsRead, markAllRead } from '../../../api/notification.js'

export default {
  data() {
    return {
      notifications: [],
      loading: true,
    }
  },
  computed: {
    hasUnread() {
      return this.notifications.some(n => !n.is_read)
    }
  },
  onLoad() {
    this.loadNotifications()
  },
  onShow() {
    // 每次显示时刷新
    if (!this.loading) this.loadNotifications()
  },
  methods: {
    async loadNotifications() {
      this.loading = true
      try {
        this.notifications = await getNotifications()
      } catch (e) {
        // 降级：显示空列表
        this.notifications = []
      } finally {
        this.loading = false
      }
    },

    async handleNotif(n) {
      // 标记已读
      if (!n.is_read) {
        try {
          await markAsRead(n.id)
          n.is_read = true
        } catch (e) { /* 静默 */ }
      }
      // 跳转
      const routes = {
        training: '/pages/parent/training/index',
        screening: '/pages/parent/screening/index',
        report: '/pages/parent/report/index',
      }
      if (n.action && routes[n.action]) {
        uni.navigateTo({ url: routes[n.action] })
      }
    },

    async markAll() {
      try {
        await markAllRead()
        this.notifications = this.notifications.map(n => ({ ...n, is_read: true }))
        uni.showToast({ title: '已全部标记已读', icon: 'success', duration: 1000 })
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },

    notifColor(type) {
      const map = {
        training_complete: 'green',
        training_reminder: 'blue',
        reassess: 'orange',
        report: 'blue',
        system: 'gray',
      }
      return map[type] || 'blue'
    },

    formatTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      const now = new Date()
      const diff = now - d
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`
      if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`
      if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`
      return `${d.getMonth() + 1}/${d.getDate()}`
    },

    goBack() { uni.navigateBack() },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center; box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { flex: 1; font-size: 30rpx; font-weight: 700; color: #2D3748; }
.clear-btn { font-size: 22rpx; color: #4F9EF8; font-weight: 700; padding: 8rpx 16rpx; }

.loading-state { display: flex; justify-content: center; align-items: center; height: 60vh; }
.loading-state .ph { font-size: 64rpx; color: #4F9EF8; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

.notif-list { display: flex; flex-direction: column; gap: 12rpx; }
.notif-item {
  background: #FFFFFF; border-radius: 20rpx; padding: 24rpx;
  display: flex; align-items: flex-start; gap: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); position: relative;
  transition: all 0.2s;
}
.notif-item:active { transform: scale(0.98); }
.notif-item.unread { background: linear-gradient(135deg, #FAFEFF, #F0F7FF); border-left: 4rpx solid #4F9EF8; }

.notif-icon { width: 64rpx; height: 64rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.notif-icon .ph { font-size: 30rpx; }
.notif-icon.green { background: rgba(34,197,94,0.1); }
.notif-icon.green .ph { color: #22C55E; }
.notif-icon.orange { background: rgba(245,127,23,0.1); }
.notif-icon.orange .ph { color: #F57F17; }
.notif-icon.blue { background: rgba(79,158,248,0.1); }
.notif-icon.blue .ph { color: #4F9EF8; }
.notif-icon.gray { background: #F5F5F5; }
.notif-icon.gray .ph { color: #A0AEC0; }

.notif-body { flex: 1; }
.notif-title { font-size: 26rpx; font-weight: 700; color: #2D3748; margin-bottom: 6rpx; }
.notif-desc { font-size: 22rpx; color: #718096; line-height: 1.6; margin-bottom: 8rpx; }
.notif-time { font-size: 20rpx; color: #A0AEC0; }

.unread-dot { position: absolute; top: 20rpx; right: 20rpx; width: 14rpx; height: 14rpx; border-radius: 50%; background: #FF6B6B; }

.empty-state { display: flex; flex-direction: column; align-items: center; padding: 120rpx 40rpx; }
.empty-icon { font-size: 80rpx; color: #D1D5DB; margin-bottom: 24rpx; }
.empty-title { font-size: 30rpx; font-weight: 700; color: #2D3748; margin-bottom: 12rpx; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; text-align: center; line-height: 1.6; }
</style>
