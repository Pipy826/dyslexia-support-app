<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">游戏报告</view>
      <button class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text> 问问AI
      </button>
    </view>

    <!-- 子女切换（多孩子时显示） -->
    <view class="child-tabs" v-if="children.length > 1">
      <view
        v-for="c in children"
        :key="c.id"
        :class="['child-tab', { active: currentChild && currentChild.id === c.id }]"
        @click="switchChild(c)"
      >
        {{ c.name }}
      </view>
    </view>

    <scroll-view class="page-content" scroll-y v-if="!loading">

      <!-- 有数据时 -->
      <template v-if="activityData && activityData.summary.total_plays > 0">

        <!-- 总体统计卡片 -->
        <view class="summary-card">
          <view class="summary-header">
            <view class="summary-child">
              <view class="summary-avatar">{{ activityData.child_name?.charAt(0) || '?' }}</view>
              <view class="summary-info">
                <view class="summary-name">{{ activityData.child_name }} 的游戏报告</view>
                <view class="summary-period">近 {{ activityData.period_days }} 天</view>
              </view>
            </view>
            <!-- 进步趋势标签 -->
            <view
              v-if="activityData.trend.direction"
              :class="['trend-badge', activityData.trend.direction]"
            >
              <text :class="['ph', trendIcon]"></text>
              {{ trendText }}
            </view>
          </view>

          <view class="summary-stats">
            <view class="stat-block">
              <view class="stat-num">{{ activityData.summary.total_plays }}</view>
              <view class="stat-label">游戏次数</view>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-block">
              <view class="stat-num" :class="accuracyClass">
                {{ activityData.summary.overall_accuracy != null ? activityData.summary.overall_accuracy + '%' : '--' }}
              </view>
              <view class="stat-label">平均正确率</view>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-block">
              <view class="stat-num streak">{{ activityData.summary.current_streak }}</view>
              <view class="stat-label">连续打卡天</view>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-block">
              <view class="stat-num">{{ activityData.summary.games_played_types }}</view>
              <view class="stat-label">游戏种类</view>
            </view>
          </view>
        </view>

        <!-- 进步趋势对比 -->
        <view class="section-title">近期进步趋势</view>
        <view class="trend-card" v-if="activityData.trend.direction">
          <view class="trend-row">
            <view class="trend-col">
              <view class="trend-col-label">前7天平均</view>
              <view class="trend-col-val">
                {{ activityData.trend.prev_7_avg != null ? activityData.trend.prev_7_avg + '%' : '暂无' }}
              </view>
            </view>
            <view class="trend-arrow">
              <text :class="['ph', trendIcon, 'trend-arrow-icon', activityData.trend.direction]"></text>
              <view class="trend-delta" :class="activityData.trend.direction" v-if="activityData.trend.delta != null">
                {{ activityData.trend.delta > 0 ? '+' : '' }}{{ activityData.trend.delta }}%
              </view>
            </view>
            <view class="trend-col">
              <view class="trend-col-label">近7天平均</view>
              <view class="trend-col-val highlight">
                {{ activityData.trend.recent_7_avg != null ? activityData.trend.recent_7_avg + '%' : '暂无' }}
              </view>
            </view>
          </view>
          <view class="trend-desc">{{ trendDesc }}</view>
        </view>
        <view class="trend-card empty-trend" v-else>
          <text class="ph ph-chart-line-up"></text>
          <view class="empty-trend-text">游戏次数增多后，这里会显示进步趋势</view>
        </view>

        <!-- 各游戏类型统计 -->
        <view class="section-title">各游戏表现</view>
        <view class="game-stats-list">
          <view
            class="game-stat-card"
            v-for="gs in activityData.game_stats"
            :key="gs.game_type"
            :style="{ '--gc': gs.color }"
          >
            <view class="gs-left">
              <view class="gs-icon" :style="{ background: gs.bg || 'rgba(79,158,248,0.1)' }">
                <text :class="'ph ' + gs.icon"></text>
              </view>
              <view class="gs-info">
                <view class="gs-name">{{ gs.game_name }}</view>
                <view class="gs-meta">
                  玩了 {{ gs.play_count }} 次
                  <text v-if="gs.last_played"> · {{ formatDate(gs.last_played) }}</text>
                </view>
              </view>
            </view>
            <view class="gs-right">
              <view class="gs-accuracy" v-if="gs.avg_accuracy != null">
                <view class="gs-acc-num" :class="accClass(gs.avg_accuracy)">{{ gs.avg_accuracy }}%</view>
                <view class="gs-acc-label">正确率</view>
              </view>
              <view class="gs-accuracy" v-else>
                <view class="gs-acc-num gray">--</view>
                <view class="gs-acc-label">正确率</view>
              </view>
            </view>
          </view>
        </view>

        <!-- 近期游戏记录 -->
        <view class="section-title">近期游戏记录</view>
        <view class="recent-list">
          <view
            class="recent-item"
            v-for="r in activityData.recent_records"
            :key="r.id"
            :style="{ '--rc': r.color }"
          >
            <view class="recent-icon">
              <text :class="'ph ' + r.icon"></text>
            </view>
            <view class="recent-info">
              <view class="recent-name">{{ r.game_name }}</view>
              <view class="recent-date">{{ formatDateTime(r.completed_at) }}</view>
            </view>
            <view class="recent-result">
              <view class="recent-stars" v-if="r.stars != null">
                <text v-for="i in 3" :key="i" :class="['star', { earned: i <= r.stars }]">⭐</text>
              </view>
              <view class="recent-acc" v-if="r.accuracy != null" :class="accClass(r.accuracy)">
                {{ r.accuracy }}%
              </view>
              <view class="recent-score" v-else-if="r.correct_count != null">
                {{ r.correct_count }}/{{ r.total_count }}
              </view>
            </view>
          </view>
        </view>

        <!-- 鼓励卡片 -->
        <view class="encourage-card">
          <view class="encourage-emoji">{{ encourageEmoji }}</view>
          <view class="encourage-text">{{ encourageText }}</view>
          <button class="encourage-btn" @click="goToTraining">查看训练计划 →</button>
        </view>

      </template>

      <!-- 无数据时 -->
      <view class="empty-state" v-else>
        <view class="empty-illustration">🎮</view>
        <view class="empty-title">还没有游戏记录</view>
        <view class="empty-desc">孩子完成游戏后，这里会显示详细的游戏情况报告</view>
        <button class="empty-btn" @click="goToChildMode">去玩游戏</button>
      </view>

    </scroll-view>

    <!-- 加载中 -->
    <view class="loading-area" v-if="loading">
      <view class="loading-spinner"></view>
      <view class="loading-text">加载中...</view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/report/index"></tab-bar>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getGameActivityReport } from '../../../api/report.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      children: [],
      currentChild: null,
      activityData: null,
      loading: false,
    }
  },
  computed: {
    trendIcon() {
      const dir = this.activityData?.trend?.direction
      if (dir === 'up') return 'ph-trend-up'
      if (dir === 'down') return 'ph-trend-down'
      return 'ph-minus'
    },
    trendText() {
      const dir = this.activityData?.trend?.direction
      if (dir === 'up') return '进步了'
      if (dir === 'down') return '需加油'
      if (dir === 'flat') return '保持稳定'
      if (dir === 'new') return '新记录'
      return ''
    },
    trendDesc() {
      const t = this.activityData?.trend
      if (!t) return ''
      if (t.direction === 'up') return `近7天正确率比前7天提升了 ${t.delta}%，继续保持！`
      if (t.direction === 'down') return `近7天正确率比前7天下降了 ${Math.abs(t.delta)}%，多练习会进步的！`
      if (t.direction === 'flat') return '近7天正确率与前7天基本持平，稳定发挥！'
      return '开始积累游戏数据，趋势分析即将开启！'
    },
    accuracyClass() {
      const acc = this.activityData?.summary?.overall_accuracy
      if (acc == null) return ''
      if (acc >= 80) return 'good'
      if (acc >= 60) return 'medium'
      return 'weak'
    },
    encourageEmoji() {
      const plays = this.activityData?.summary?.total_plays || 0
      const acc = this.activityData?.summary?.overall_accuracy || 0
      if (acc >= 85) return '🏆'
      if (acc >= 70) return '⭐'
      if (plays >= 10) return '💪'
      return '🌱'
    },
    encourageText() {
      const plays = this.activityData?.summary?.total_plays || 0
      const acc = this.activityData?.summary?.overall_accuracy || 0
      const name = this.activityData?.child_name || '孩子'
      if (acc >= 85) return `${name}表现非常棒！正确率高达 ${acc}%，继续保持这种好状态！`
      if (acc >= 70) return `${name}游戏表现不错，正确率 ${acc}%。坚持练习，会越来越好！`
      if (plays >= 10) return `${name}已经玩了 ${plays} 次游戏，坚持就是胜利！`
      return `${name}刚开始游戏之旅，多玩几次就会进步的！`
    },
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        this.children = await getChildren()
        if (this.children.length > 0) {
          const saved = getCurrentChild()
          this.currentChild = saved
            ? (this.children.find(c => c.id === saved.id) || this.children[0])
            : this.children[0]
          setCurrentChild(this.currentChild)
          await this.loadActivityReport()
        }
      } catch (e) {
        console.error('加载失败', e)
      } finally {
        this.loading = false
      }
    },
    async loadActivityReport() {
      if (!this.currentChild) return
      try {
        this.activityData = await getGameActivityReport(this.currentChild.id, 30)
      } catch (e) {
        console.error('加载游戏报告失败', e)
        this.activityData = null
      }
    },
    async switchChild(child) {
      this.currentChild = child
      setCurrentChild(child)
      this.loading = true
      await this.loadActivityReport()
      this.loading = false
    },
    accClass(acc) {
      if (acc >= 80) return 'good'
      if (acc >= 60) return 'medium'
      return 'weak'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },
    formatDateTime(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      const now = new Date()
      const diffMs = now - d
      const diffDays = Math.floor(diffMs / 86400000)
      if (diffDays === 0) return '今天 ' + `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
      if (diffDays === 1) return '昨天'
      if (diffDays < 7) return `${diffDays}天前`
      return `${d.getMonth() + 1}月${d.getDate()}日`
    },
    goToAiChat() {
      uni.navigateTo({ url: '/pages/parent/ai-chat/index' })
    },
    goBack() {
      uni.navigateBack()
    },
    goToTraining() {
      uni.navigateTo({ url: '/pages/parent/training/index' })
    },
    goToChildMode() {
      uni.reLaunch({ url: '/pages/child/child-training/index?tab=challenge' })
    },
  }
}
</script>

<style scoped>
/* ── 页面容器 ── */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 160rpx;
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* ── 头部 ── */
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95);
  padding: 56rpx 32rpx 20rpx;
  display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.header-title { font-size: 36rpx; font-weight: 800; color: #2D3748; }
.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
  flex-shrink: 0;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.ai-btn {
  display: flex; align-items: center; gap: 6rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8; border: 1rpx solid #BFDBFE;
  padding: 12rpx 24rpx; border-radius: 14rpx;
  font-size: 24rpx; font-weight: 700;
}
.ai-btn .ph { font-size: 24rpx; }

/* ── 子女切换 ── */
.child-tabs {
  display: flex; flex-direction: row; gap: 12rpx;
  padding: 12rpx 32rpx; background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  overflow-x: auto; width: 100%; box-sizing: border-box;
}
.child-tab {
  padding: 10rpx 24rpx; border-radius: 20rpx;
  font-size: 24rpx; font-weight: 600; color: #A0AEC0;
  background: #F5F7FA; white-space: nowrap; transition: all 0.2s;
}
.child-tab.active { background: #EFF6FF; color: #4F9EF8; }

/* ── 内容区 ── */
.page-content {
  flex: 1;
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
}

/* ── 总体统计卡片（白色风格，与其他页面统一） ── */
.summary-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.06);
  width: 100%; box-sizing: border-box;
}
.summary-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 24rpx;
}
.summary-child { display: flex; align-items: center; gap: 14rpx; }
.summary-avatar {
  width: 56rpx; height: 56rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  font-size: 28rpx; font-weight: 700; color: #4F9EF8; flex-shrink: 0;
}
.summary-info { display: flex; flex-direction: column; gap: 4rpx; }
.summary-name { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.summary-period { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

.trend-badge {
  display: flex; align-items: center; gap: 6rpx;
  padding: 8rpx 16rpx; border-radius: 20rpx;
  font-size: 22rpx; font-weight: 700; flex-shrink: 0;
}
.trend-badge.up { background: rgba(34,197,94,0.1); color: #22C55E; }
.trend-badge.down { background: rgba(255,107,107,0.1); color: #FF6B6B; }
.trend-badge.flat { background: #F5F7FA; color: #A0AEC0; }
.trend-badge.new { background: rgba(251,191,36,0.1); color: #D97706; }
.trend-badge .ph { font-size: 22rpx; }

.summary-stats {
  display: flex; flex-direction: row; align-items: center;
  background: #F8FAFF; border-radius: 16rpx; padding: 20rpx 0;
  width: 100%;
}
.stat-block { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6rpx; }
.stat-num { font-size: 40rpx; font-weight: 900; color: #2D3748; }
.stat-num.good { color: #22C55E; }
.stat-num.medium { color: #F97316; }
.stat-num.weak { color: #FF6B6B; }
.stat-num.streak { color: #F57F17; }
.stat-label { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }
.stat-divider { width: 1rpx; height: 48rpx; background: #E5E7EB; flex-shrink: 0; }

/* ── 区块标题 ── */
.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748;
  margin-bottom: 16rpx;
}

/* ── 趋势卡片 ── */
.trend-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 28rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.trend-row {
  display: flex; flex-direction: row; align-items: center;
  justify-content: space-between; margin-bottom: 16rpx;
}
.trend-col { display: flex; flex-direction: column; align-items: center; gap: 6rpx; flex: 1; }
.trend-col-label { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }
.trend-col-val { font-size: 36rpx; font-weight: 800; color: #2D3748; }
.trend-col-val.highlight { color: #4F9EF8; }
.trend-arrow { display: flex; flex-direction: column; align-items: center; gap: 6rpx; flex-shrink: 0; padding: 0 16rpx; }
.trend-arrow-icon { font-size: 36rpx; }
.trend-arrow-icon.up { color: #22C55E; }
.trend-arrow-icon.down { color: #FF6B6B; }
.trend-arrow-icon.flat { color: #A0AEC0; }
.trend-delta { font-size: 22rpx; font-weight: 700; }
.trend-delta.up { color: #22C55E; }
.trend-delta.down { color: #FF6B6B; }
.trend-delta.flat { color: #A0AEC0; }
.trend-desc { font-size: 22rpx; color: #718096; text-align: center; font-weight: 500; line-height: 1.6; }

.empty-trend {
  display: flex; flex-direction: column; align-items: center; gap: 12rpx;
  padding: 40rpx;
}
.empty-trend .ph { font-size: 48rpx; color: #D1D5DB; }
.empty-trend-text { font-size: 24rpx; color: #A0AEC0; text-align: center; }

/* ── 各游戏统计 ── */
.game-stats-list {
  display: flex; flex-direction: column; gap: 12rpx;
  margin-bottom: 24rpx; width: 100%;
}
.game-stat-card {
  background: #FFFFFF; border-radius: 20rpx; padding: 20rpx 24rpx;
  display: flex; flex-direction: row; align-items: center;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.06);
  border: 2rpx solid rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.gs-left { display: flex; align-items: center; gap: 16rpx; flex: 1; min-width: 0; }
.gs-icon {
  width: 64rpx; height: 64rpx; border-radius: 16rpx;
  background: rgba(0,0,0,0.05);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.gs-icon .ph { font-size: 30rpx; color: var(--gc); }
.gs-info { flex: 1; min-width: 0; }
.gs-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.gs-meta { font-size: 20rpx; color: #A0AEC0; margin-top: 4rpx; font-weight: 500; }
.gs-right { flex-shrink: 0; }
.gs-accuracy { display: flex; flex-direction: column; align-items: flex-end; gap: 4rpx; }
.gs-acc-num { font-size: 32rpx; font-weight: 800; }
.gs-acc-num.good { color: #22C55E; }
.gs-acc-num.medium { color: #F97316; }
.gs-acc-num.weak { color: #FF6B6B; }
.gs-acc-num.gray { color: #D1D5DB; }
.gs-acc-label { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

/* ── 近期记录 ── */
.recent-list {
  display: flex; flex-direction: column; gap: 10rpx;
  margin-bottom: 24rpx; width: 100%;
}
.recent-item {
  background: #FFFFFF; border-radius: 18rpx; padding: 20rpx 24rpx;
  display: flex; flex-direction: row; align-items: center; gap: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.recent-icon {
  width: 56rpx; height: 56rpx; border-radius: 14rpx;
  background: rgba(0,0,0,0.04);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.recent-icon .ph { font-size: 26rpx; color: var(--rc); }
.recent-info { flex: 1; min-width: 0; }
.recent-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.recent-date { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; }
.recent-result { display: flex; flex-direction: column; align-items: flex-end; gap: 4rpx; flex-shrink: 0; }
.recent-stars { display: flex; flex-direction: row; gap: 2rpx; }
.star { font-size: 22rpx; opacity: 0.2; }
.star.earned { opacity: 1; }
.recent-acc { font-size: 26rpx; font-weight: 700; }
.recent-acc.good { color: #22C55E; }
.recent-acc.medium { color: #F97316; }
.recent-acc.weak { color: #FF6B6B; }
.recent-score { font-size: 24rpx; font-weight: 700; color: #4F9EF8; }

/* ── 鼓励卡片 ── */
.encourage-card {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A; border-radius: 24rpx;
  padding: 32rpx; margin-bottom: 24rpx;
  display: flex; flex-direction: column; align-items: center; gap: 12rpx;
  width: 100%; box-sizing: border-box;
}
.encourage-emoji { font-size: 56rpx; }
.encourage-text { font-size: 26rpx; color: #92400E; text-align: center; line-height: 1.6; font-weight: 600; }
.encourage-btn {
  background: linear-gradient(135deg, #F59E0B, #D97706); color: #FFFFFF;
  border-radius: 14rpx; padding: 18rpx 40rpx;
  font-size: 24rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(245,158,11,0.3);
  margin-top: 8rpx;
}

/* ── 空状态 ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 100rpx 40rpx; width: 100%; box-sizing: border-box;
}
.empty-illustration { font-size: 100rpx; margin-bottom: 24rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #2D3748; margin-bottom: 12rpx; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; text-align: center; line-height: 1.6; margin-bottom: 40rpx; }
.empty-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; padding: 22rpx 56rpx;
  font-size: 26rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2);
}

/* ── 加载中 ── */
.loading-area {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 20rpx;
  padding: 100rpx 0; width: 100%;
}
.loading-spinner {
  width: 60rpx; height: 60rpx;
  border: 6rpx solid #F0F0F0; border-top-color: #4F9EF8;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 26rpx; color: #A0AEC0; }
</style>
