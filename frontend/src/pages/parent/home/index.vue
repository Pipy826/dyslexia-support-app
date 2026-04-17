<template>
  <view class="page-container">
    <!-- 顶部信息栏 -->
    <view class="top-bar">
      <view class="user-info" @click="showChildPicker">
        <view class="avatar">{{ currentChild?.name?.charAt(0) || '?' }}</view>
        <view class="user-text">
          <view class="greeting">{{ greeting }}，{{ user?.username || '家长' }}</view>
          <view class="current-child">当前档案：{{ currentChild ? currentChild.name + ' (' + getAge(currentChild.birth_date) + '岁)' : '请选择孩子' }} ▼</view>
        </view>
      </view>
      <view class="notification">
        <text class="ph ph-bell"></text>
        <view class="notification-dot" v-if="hasUnread"></view>
      </view>
    </view>

    <!-- 儿童切换弹窗 -->
    <view class="modal-overlay" v-if="showPicker" @click="showPicker = false">
      <view class="picker-sheet" @click.stop>
        <view class="picker-title">选择孩子档案</view>
        <view
          v-for="child in children"
          :key="child.id"
          :class="['picker-item', { active: currentChild?.id === child.id }]"
          @click="selectChild(child)"
        >
          <view class="picker-avatar">{{ child.name.charAt(0) }}</view>
          <view class="picker-info">
            <view class="picker-name">{{ child.name }}</view>
            <view class="picker-meta">{{ getAge(child.birth_date) }}岁 / {{ child.grade || '' }}</view>
          </view>
          <text v-if="currentChild?.id === child.id" class="ph ph-check picker-check"></text>
        </view>
        <view class="picker-add" @click="goToCreateProfile">
          <text class="ph ph-plus"></text> 添加新档案
        </view>
      </view>
    </view>

    <view class="page-content">
      <!-- 每日 AI 贴士 -->
      <view class="daily-tip-card" v-if="dailyTip" @click="showAiChat">
        <view class="tip-left">
          <view class="tip-icon">
            <text class="ph-fill ph-lightbulb"></text>
          </view>
          <view class="tip-content">
            <view class="tip-label">今日 AI 建议</view>
            <view class="tip-text">{{ dailyTip }}</view>
          </view>
        </view>
        <text class="ph ph-arrow-right tip-arrow"></text>
      </view>

      <!-- 核心引导卡片 -->
      <view class="guide-card" v-if="!recentReport">
        <view class="guide-decoration"></view>
        <view class="guide-icon">
          <text class="ph ph-star"></text>
        </view>
        <view class="guide-tag">系统建议</view>
        <view class="guide-title">初步能力筛查</view>
        <view class="guide-desc">{{ currentChild ? currentChild.name : '孩子' }}尚未进行全面的读写能力筛查，建议抽出15分钟了解孩子的现状，生成定制专属干预计划。</view>
        <button class="guide-btn" @click="goToScreening">立即发起筛查</button>
      </view>

      <!-- 有报告时显示最新报告摘要 -->
      <view class="guide-card report-card" v-else @click="goToReport">
        <view class="guide-decoration"></view>
        <view class="guide-tag" :class="recentReport.risk_level">{{ riskLabel(recentReport.risk_level) }}</view>
        <view class="guide-title">最新评估报告</view>
        <view class="guide-desc">{{ recentReport.summary || '点击查看详细报告和干预建议' }}</view>
        <button class="guide-btn" @click.stop="goToReport">查看报告详情</button>
      </view>

      <!-- 四宫格快捷入口 -->
      <view class="grid-section">
        <view class="grid-item" @click="goToReport">
          <view class="grid-icon blue">
            <text class="ph ph-file-text"></text>
          </view>
          <view class="grid-label">评估报告</view>
        </view>
        <view class="grid-item" @click="goToTraining">
          <view class="grid-icon green">
            <text class="ph ph-calendar-check"></text>
          </view>
          <view class="grid-label">训练计划</view>
        </view>
        <view class="grid-item" @click="goToGrowthAnalysis">
          <view class="grid-icon orange">
            <text class="ph ph-trend-up"></text>
          </view>
          <view class="grid-label">成长分析</view>
        </view>
        <view class="grid-item" @click="showAiChat">
          <view class="grid-icon purple">
            <text class="ph ph-robot"></text>
          </view>
          <view class="grid-label">AI问答</view>
        </view>
      </view>

      <!-- 近期动态模块 -->
      <view class="section-header">
        <view class="section-title">近期动态</view>
        <view class="more-link" @click="goToReport">查看全部</view>
      </view>

      <view class="activity-list" v-if="activities.length > 0">
        <view class="activity-card" v-for="(item, i) in activities" :key="i">
          <view class="activity-icon" :class="item.color">
            <text :class="'ph ' + item.icon"></text>
          </view>
          <view class="activity-content">
            <view class="activity-title">{{ item.title }}</view>
            <view class="activity-time">{{ item.time }}</view>
          </view>
          <view class="activity-status" v-if="item.status">{{ item.status }}</view>
        </view>
      </view>

      <view class="activity-list" v-else>
        <view class="activity-card">
          <view class="activity-icon blue">
            <text class="ph ph-info"></text>
          </view>
          <view class="activity-content">
            <view class="activity-title">完成档案创建</view>
            <view class="activity-time">欢迎使用本系统</view>
          </view>
          <view class="activity-status">已就绪</view>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/home/index"></tab-bar>
  </view>
</template>

<script>
import { getCurrentChild, setCurrentChild, getUser } from '../../../utils/auth.js'
import { getChildren } from '../../../api/child.js'
import { getReports } from '../../../api/report.js'
import { getDailyTip } from '../../../api/ai.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      user: null,
      currentChild: null,
      children: [],
      recentReport: null,
      showPicker: false,
      hasUnread: false,
      activities: [],
      dailyTip: '',
    }
  },
  computed: {
    greeting() {
      const h = new Date().getHours()
      if (h < 6) return '凌晨好'
      if (h < 12) return '早上好'
      if (h < 14) return '中午好'
      if (h < 18) return '下午好'
      return '晚上好'
    }
  },
  onShow() {
    this.user = getUser()
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.children = await getChildren()
        if (this.children.length > 0) {
          const saved = getCurrentChild()
          if (saved) {
            this.currentChild = this.children.find(c => c.id === saved.id) || this.children[0]
          } else {
            this.currentChild = this.children[0]
          }
          setCurrentChild(this.currentChild)
          await this.loadRecentReport()
        } else {
          // 没有孩子档案，引导创建
          uni.showModal({
            title: '欢迎使用',
            content: '请先创建孩子的档案，以便开始筛查和训练。',
            showCancel: false,
            confirmText: '立即创建',
            success: () => {
              uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
            }
          })
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadRecentReport() {
      if (!this.currentChild) return
      try {
        const reports = await getReports(this.currentChild.id)
        this.recentReport = reports[0] || null
        this.buildActivities(reports)
        // 有报告才加载每日贴士
        if (this.recentReport) {
          this.loadDailyTip()
        }
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    async loadDailyTip() {
      try {
        const res = await getDailyTip(this.currentChild.id)
        this.dailyTip = res.tip
      } catch (e) {
        // 静默失败，不影响主流程
      }
    },
    buildActivities(reports) {
      this.activities = reports.slice(0, 3).map(r => ({
        icon: 'ph-file-text',
        color: 'blue',
        title: `完成筛查评估 · ${this.riskLabel(r.risk_level)}`,
        time: this.formatDate(r.created_at),
        status: r.risk_level === 'low' ? '良好' : r.risk_level === 'medium' ? '需关注' : '重点关注'
      }))
    },
    getAge(birthDate) {
      if (!birthDate) return '?'
      const birth = new Date(birthDate)
      const now = new Date()
      return now.getFullYear() - birth.getFullYear()
    },
    riskLabel(level) {
      return { low: '低风险', medium: '中风险', high: '高风险' }[level] || level
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    showChildPicker() {
      if (this.children.length > 1) this.showPicker = true
    },
    selectChild(child) {
      this.currentChild = child
      setCurrentChild(child)
      this.showPicker = false
      this.recentReport = null
      this.activities = []
      this.loadRecentReport()
    },
    goToCreateProfile() {
      this.showPicker = false
      uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    goToReport() {
      if (this.recentReport?.id) {
        uni.navigateTo({ url: `/pages/parent/report/detail?id=${this.recentReport.id}` })
      } else {
        uni.navigateTo({ url: '/pages/parent/report/index' })
      }
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/parent/training/index' })
    },
    showAiChat() {
      uni.navigateTo({ url: '/pages/parent/ai-chat/index' })
    },
    goToGrowthAnalysis() {
      if (this.currentChild) {
        uni.navigateTo({ url: `/pages/parent/growth/index?child_id=${this.currentChild.id}` })
      }
    }
  }
}
</script>

<style scoped>
@import '@/styles/common.scss';

.page-container {
  min-height: 100vh;
  background: #F9FAFB;
  padding-bottom: 196rpx;
}

/* 顶部信息栏 */
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

.user-info {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #EFF6FF;
  border: 1rpx solid #BFDBFE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #3B82F6;
}

.user-text .greeting {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
}

.user-text .current-child {
  font-size: 22rpx;
  color: #6B7280;
  margin-top: 4rpx;
}

.notification {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #F9FAFB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.notification .ph {
  font-size: 40rpx;
  color: #6B7280;
}

.notification-dot {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #EF4444;
}

/* 页面内容 */
.page-content {
  padding: 32rpx 48rpx;
}

/* 每日 AI 贴士 */
.daily-tip-card {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 1rpx solid #FDE68A;
  border-radius: 40rpx;
  padding: 28rpx 32rpx;
  margin-bottom: 32rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.tip-left {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
  flex: 1;
}

.tip-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F59E0B;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tip-icon .ph {
  font-size: 32rpx;
  color: #FFFFFF;
}

.tip-content { flex: 1; }

.tip-label {
  font-size: 20rpx;
  font-weight: 700;
  color: #D97706;
  letter-spacing: 1rpx;
  margin-bottom: 6rpx;
}

.tip-text {
  font-size: 26rpx;
  color: #374151;
  line-height: 1.6;
}

.tip-arrow {
  font-size: 32rpx;
  color: #D97706;
  flex-shrink: 0;
}

/* 引导卡片 */
.guide-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
  position: relative;
  overflow: hidden;
}

.guide-decoration {
  position: absolute;
  right: -32rpx;
  top: -32rpx;
  width: 192rpx;
  height: 192rpx;
  border-radius: 50%;
  background: #EFF6FF;
  opacity: 0.5;
}

.guide-icon {
  width: 48rpx;
  height: 48rpx;
  background: #EFF6FF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
}

.guide-icon .ph {
  font-size: 24rpx;
  color: #3B82F6;
}

.guide-tag {
  font-size: 20rpx;
  font-weight: 700;
  color: #3B82F6;
  letter-spacing: 2rpx;
  margin-bottom: 8rpx;
}

.guide-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 16rpx;
}

.guide-desc {
  font-size: 26rpx;
  color: #6B7280;
  line-height: 1.6;
  margin-bottom: 40rpx;
}

.guide-btn {
  width: 100%;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

/* 四宫格 */
.grid-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32rpx;
  margin-bottom: 48rpx;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.grid-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 32rpx;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
  border: 1rpx solid #F9FAFB;
}

.grid-icon .ph {
  font-size: 48rpx;
}

.grid-icon.blue { color: #3B82F6; }
.grid-icon.green { color: #10B981; }
.grid-icon.orange { color: #F59E0B; }
.grid-icon.purple { color: #8B5CF6; }

.grid-label {
  font-size: 22rpx;
  color: #4B5563;
}

/* 区域标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.more-link {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 动态列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.activity-card {
  background: #FFFFFF;
  padding: 32rpx;
  border-radius: 40rpx;
  border: 1rpx solid #F3F4F6;
  display: flex;
  align-items: center;
  gap: 32rpx;
}

.activity-card.muted {
  opacity: 0.6;
}

.activity-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon.blue { background: #EFF6FF; }
.activity-icon.blue .ph { color: #3B82F6; }
.activity-icon.gray { background: #F3F4F6; }
.activity-icon.gray .ph { color: #9CA3AF; }

.activity-icon .ph {
  font-size: 32rpx;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.activity-time {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.activity-status {
  font-size: 22rpx;
  font-weight: 500;
  color: #3B82F6;
  background: #EFF6FF;
  padding: 8rpx 24rpx;
  border-radius: 16rpx;
}

.activity-status-text {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 儿童切换弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
}

.picker-sheet {
  background: #FFFFFF;
  width: 100%;
  border-radius: 48rpx 48rpx 0 0;
  padding: 48rpx 48rpx calc(48rpx + env(safe-area-inset-bottom));
}

.picker-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 32rpx;
  text-align: center;
}

.picker-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  padding: 24rpx;
  border-radius: 24rpx;
  margin-bottom: 16rpx;
}

.picker-item.active {
  background: #EFF6FF;
}

.picker-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #DBEAFE;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 700;
  color: #3B82F6;
}

.picker-info { flex: 1; }

.picker-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.picker-meta {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.picker-check {
  font-size: 32rpx;
  color: #3B82F6;
}

.picker-add {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx;
  color: #3B82F6;
  font-size: 26rpx;
  font-weight: 700;
  border: 2rpx dashed #BFDBFE;
  border-radius: 24rpx;
  margin-top: 8rpx;
}

/* 报告卡片变体 */
.guide-card.report-card .guide-tag.low { color: #10B981; }
.guide-card.report-card .guide-tag.medium { color: #F59E0B; }
.guide-card.report-card .guide-tag.high { color: #EF4444; }
</style>
