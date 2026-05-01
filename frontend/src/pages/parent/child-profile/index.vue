<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack"><text class="ph ph-arrow-left"></text></view>
      <view class="header-title">儿童档案</view>
      <view class="edit-btn" @click="goToEdit"><text class="ph ph-pencil"></text></view>
    </view>

    <scroll-view class="page-content" scroll-y v-if="child">
      <!-- 头像与基本信息 -->
      <view class="profile-hero">
        <view class="hero-avatar">
          <image v-if="child.avatar_url" :src="child.avatar_url" class="avatar-img" mode="aspectFill" />
          <text v-else class="ph ph-user avatar-placeholder"></text>
        </view>
        <view class="hero-name">{{ child.name }}</view>
        <view class="hero-meta">{{ genderLabel }} · {{ age }}岁 · {{ child.grade || '未设置年级' }}</view>
        <view class="hero-tags">
          <view class="hero-tag" v-if="child.has_difficulty">
            <text class="ph ph-warning-circle"></text> 已标记困难
          </view>
          <view class="hero-tag eval" v-if="child.has_professional_eval">
            <text class="ph ph-certificate"></text> 有机构评估经历
          </view>
        </view>
      </view>

      <!-- 探索统计 -->
      <view class="stats-row">
        <view class="stat-card">
          <view class="stat-val blue">{{ screeningCount }}</view>
          <view class="stat-label">探索次数</view>
        </view>
        <view class="stat-card">
          <view class="stat-val" :class="latestRiskClass">{{ latestRiskLabel }}</view>
          <view class="stat-label">最新关注等级</view>
        </view>
        <view class="stat-card">
          <view class="stat-val green">{{ completedTaskCount }}</view>
          <view class="stat-label">完成训练</view>
        </view>
        <view class="stat-card">
          <view class="stat-val orange">{{ totalStars }}</view>
          <view class="stat-label">获得星星</view>
        </view>
      </view>

      <!-- 基本信息 -->
      <view class="section-title">基本信息</view>
      <view class="info-card">
        <view class="info-row">
          <view class="info-label">姓名</view>
          <view class="info-val">{{ child.name }}</view>
        </view>
        <view class="info-row">
          <view class="info-label">性别</view>
          <view class="info-val">{{ genderLabel }}</view>
        </view>
        <view class="info-row">
          <view class="info-label">出生日期</view>
          <view class="info-val">{{ child.birth_date }}</view>
        </view>
        <view class="info-row">
          <view class="info-label">当前年级</view>
          <view class="info-val">{{ child.grade || '未设置' }}</view>
        </view>
        <view class="info-row">
          <view class="info-label">创建时间</view>
          <view class="info-val">{{ formatDate(child.created_at) }}</view>
        </view>
        <view class="info-row">
          <view class="info-label">已有困难表现</view>
          <view class="info-val" :class="child.has_difficulty ? 'orange' : 'gray'">
            {{ child.has_difficulty ? '是' : '否' }}
          </view>
        </view>
        <view class="info-row last">
          <view class="info-label">机构评估经历</view>
          <view class="info-val" :class="child.has_professional_eval ? 'blue' : 'gray'">
            {{ child.has_professional_eval ? '有' : '无' }}
          </view>
        </view>
      </view>

      <!-- 历史探索记录 -->
      <view class="section-title" v-if="screenings.length > 0">历史探索记录</view>
      <view class="screening-list" v-if="screenings.length > 0">
        <view
          class="screening-item"
          v-for="s in screenings"
          :key="s.id"
          @click="viewReport(s)"
        >
          <view class="screening-icon" :class="s.risk_level">
            <text class="ph ph-file-text"></text>
          </view>
          <view class="screening-info">
            <view class="screening-name">{{ gameTypeName(s.game_type) }}能力探索</view>
            <view class="screening-date">{{ formatDate(s.created_at) }}</view>
          </view>
          <view class="screening-right">
            <view class="screening-score">{{ s.score }}分</view>
            <view class="screening-badge" :class="s.risk_level">{{ riskLabel(s.risk_level) }}</view>
          </view>
        </view>
      </view>

      <!-- 操作按钮 -->
      <view class="action-btns">
        <button class="action-btn primary" @click="goToScreening">
          <text class="ph ph-play"></text> 开始能力探索
        </button>
        <button class="action-btn danger" @click="confirmDelete">
          <text class="ph ph-trash"></text> 删除档案
        </button>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <view class="loading-state" v-else>
      <view class="loading-spinner"></view>
      <view>加载中...</view>
    </view>
  </view>
</template>

<script>
import { getChild, deleteChild } from '../../../api/child.js'
import { getScreeningHistory } from '../../../api/screening.js'
import { getTasks, getTotalStars } from '../../../api/training.js'
import { getReportByScreening } from '../../../api/report.js'

export default {
  data() {
    return {
      childId: null,
      child: null,
      screenings: [],
      completedTaskCount: 0,
      totalStars: 0,
    }
  },
  onLoad(options) {
    this.childId = parseInt(options.child_id)
    this.loadData()
  },
  computed: {
    age() {
      if (!this.child?.birth_date) return '?'
      return new Date().getFullYear() - new Date(this.child.birth_date).getFullYear()
    },
    genderLabel() {
      return this.child?.gender === 'female' ? '女孩' : '男孩'
    },
    screeningCount() { return this.screenings.length },
    latestRiskLabel() {
      const s = this.screenings[0]
      return s ? { low: '表现良好', medium: '有些地方可以加强', high: '需要更多关注' }[s.risk_level] || '—' : '暂无'
    },
    latestRiskClass() {
      const s = this.screenings[0]
      return s ? { low: 'green', medium: 'orange', high: 'red' }[s.risk_level] || 'gray' : 'gray'
    },
  },
  methods: {
    async loadData() {
      try {
        const [child, screenings, tasks, stars] = await Promise.all([
          getChild(this.childId),
          getScreeningHistory(this.childId),
          getTasks(this.childId, 'completed'),
          getTotalStars(this.childId),
        ])
        this.child = child
        this.screenings = screenings
        this.completedTaskCount = tasks.length
        this.totalStars = stars.total_stars || 0
      } catch (e) {
        console.error('加载失败', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    async viewReport(screening) {
      try {
        const report = await getReportByScreening(screening.id)
        uni.navigateTo({ url: `/pages/parent/report/detail?id=${report.id}` })
      } catch (e) {
        uni.showToast({ title: '暂无报告', icon: 'none' })
      }
    },
    goToEdit() {
      uni.navigateTo({ url: `/pages/parent/profile/edit?child_id=${this.childId}` })
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    confirmDelete() {
      uni.showModal({
        title: '删除档案',
        content: `确定要删除 ${this.child?.name} 的档案吗？所有相关数据将被清除，此操作不可恢复。`,
        confirmColor: '#FF6B6B',
        success: async (res) => {
          if (res.confirm) {
            try {
              await deleteChild(this.childId)
              uni.showToast({ title: '已删除', icon: 'success' })
              setTimeout(() => uni.navigateBack(), 1000)
            } catch (e) {
              uni.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        },
      })
    },
    gameTypeName(type) {
      return { visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解', working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作' }[type] || type
    },
    riskLabel(level) {
      return { low: '表现良好', medium: '有些地方可以加强', high: '需要更多关注' }[level] || level
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`
    },
    goBack() { uni.navigateBack() },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx; display: flex; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { flex: 1; font-size: 30rpx; font-weight: 700; color: #2D3748; }
.edit-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #EFF6FF; display: flex; align-items: center; justify-content: center; }
.edit-btn .ph { font-size: 28rpx; color: #4F9EF8; }

.page-content { padding: 0 32rpx 24rpx; width: 100%; box-sizing: border-box; }

/* 头像区 */
.profile-hero { display: flex; flex-direction: column; align-items: center; padding: 40rpx 0 32rpx; }
.hero-avatar {
  width: 160rpx; height: 160rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20rpx; overflow: hidden;
  box-shadow: 0 4rpx 20rpx rgba(79,158,248,0.2);
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-placeholder { font-size: 72rpx; color: #4F9EF8; }
.hero-name { font-size: 44rpx; font-weight: 800; color: #2D3748; margin-bottom: 8rpx; }
.hero-meta { font-size: 26rpx; color: #718096; font-weight: 500; margin-bottom: 16rpx; }
.hero-tags { display: flex; gap: 12rpx; flex-wrap: wrap; justify-content: center; }
.hero-tag {
  display: flex; align-items: center; gap: 6rpx;
  background: rgba(245,127,23,0.1); color: #F57F17;
  font-size: 20rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 12rpx;
}
.hero-tag.eval { background: rgba(79,158,248,0.1); color: #4F9EF8; }
.hero-tag .ph { font-size: 20rpx; }

/* 统计行 */
.stats-row { display: flex; gap: 12rpx; margin-bottom: 24rpx; width: 100%; box-sizing: border-box; }
.stat-card { flex: 1; min-width: 0; background: #FFFFFF; border-radius: 20rpx; padding: 20rpx 8rpx; display: flex; flex-direction: column; align-items: center; gap: 6rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); overflow: hidden; }
.stat-val { font-size: 40rpx; font-weight: 800; }
.stat-val.blue { color: #4F9EF8; }
.stat-val.green { color: #22C55E; }
.stat-val.orange { color: #F57F17; }
.stat-val.red { color: #FF6B6B; }
.stat-val.gray { color: #A0AEC0; font-size: 24rpx; }
.stat-label { font-size: 18rpx; color: #A0AEC0; font-weight: 600; }

/* 区域标题 */
.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; }

/* 信息卡 */
.info-card { background: #FFFFFF; border-radius: 24rpx; padding: 8rpx 28rpx; margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); }
.info-row { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 0; border-bottom: 1rpx solid #F5F5F5; }
.info-row.last { border-bottom: none; }
.info-label { font-size: 26rpx; color: #718096; font-weight: 500; }
.info-val { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.info-val.orange { color: #F57F17; }
.info-val.blue { color: #4F9EF8; }
.info-val.gray { color: #A0AEC0; }

/* 探索记录 */
.screening-list { display: flex; flex-direction: column; gap: 12rpx; margin-bottom: 24rpx; }
.screening-item { background: #FFFFFF; border-radius: 20rpx; padding: 20rpx 24rpx; display: flex; align-items: center; gap: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); transition: all 0.2s; }
.screening-item:active { transform: scale(0.98); }
.screening-icon { width: 60rpx; height: 60rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.screening-icon.low { background: rgba(34,197,94,0.1); }
.screening-icon.low .ph { color: #22C55E; font-size: 28rpx; }
.screening-icon.medium { background: rgba(245,127,23,0.1); }
.screening-icon.medium .ph { color: #F57F17; font-size: 28rpx; }
.screening-icon.high { background: rgba(255,107,107,0.1); }
.screening-icon.high .ph { color: #FF6B6B; font-size: 28rpx; }
.screening-info { flex: 1; }
.screening-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.screening-date { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; }
.screening-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6rpx; }
.screening-score { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.screening-badge { font-size: 18rpx; font-weight: 700; padding: 4rpx 12rpx; border-radius: 8rpx; }
.screening-badge.low { background: rgba(34,197,94,0.1); color: #22C55E; }
.screening-badge.medium { background: rgba(245,127,23,0.1); color: #F57F17; }
.screening-badge.high { background: rgba(255,107,107,0.1); color: #FF6B6B; }

/* 操作按钮 */
.action-btns { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.action-btn { flex: 1; border-radius: 16rpx; padding: 24rpx; font-size: 26rpx; font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 8rpx; transition: all 0.2s; }
.action-btn:active { transform: scale(0.97); }
.action-btn.primary { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2); }
.action-btn.danger { background: #FFFFFF; border: 2rpx solid #FECACA; color: #FF6B6B; }
.action-btn .ph { font-size: 26rpx; }

/* 加载 */
.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 160rpx 0; gap: 20rpx; color: #A0AEC0; font-size: 26rpx; }
.loading-spinner { width: 64rpx; height: 64rpx; border: 5rpx solid #DBEAFE; border-top-color: #4F9EF8; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
</style>
