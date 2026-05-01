<template>
  <view class="page-container">
    <!-- 顶部导航栏 -->
    <view class="nav-bar">
      <view class="nav-back" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="nav-title">成长日记</view>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 加载中 -->
    <view class="loading-state" v-if="loading">
      <view class="loading-spinner"></view>
      <text class="loading-text">正在加载成长日记...</text>
    </view>

    <!-- 加载失败 / 空状态 -->
    <view class="empty-state" v-else-if="!diaryData">
      <view class="empty-icon">
        <text class="ph ph-book-open-text"></text>
      </view>
      <view class="empty-title">暂无成长记录</view>
      <view class="empty-desc">完成游戏后，这里会记录孩子的成长轨迹</view>
      <button class="empty-btn" @click="goToScreening">开始能力探索</button>
    </view>

    <!-- 日记内容 -->
    <scroll-view scroll-y class="page-scroll" v-else>
      <!-- 日记头部 -->
      <view class="diary-header">
        <view class="diary-date">{{ todayStr }}</view>
        <view class="diary-title">{{ diaryData.child_name }}的成长日记</view>
      </view>

      <!-- 今天的冒险 -->
      <view class="section-card" v-if="diaryData.latest_ability">
        <view class="section-header">
          <text class="section-emoji">🌟</text>
          <text class="section-title">今天的冒险</text>
        </view>
        <view class="adventure-card">
          <view class="adventure-emoji">{{ diaryData.latest_ability.ability_emoji }}</view>
          <view class="adventure-info">
            <view class="adventure-label">{{ diaryData.latest_ability.ability_label }}</view>
            <view class="adventure-desc">{{ diaryData.latest_ability.ability_desc }}</view>
            <view class="adventure-score">
              <text class="score-num">{{ diaryData.latest_ability.score }}</text>
              <text class="score-unit">分</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 能力地图 -->
      <view class="section-card" v-if="hasDimensions">
        <view class="section-header">
          <text class="section-emoji">🗺️</text>
          <text class="section-title">能力地图</text>
        </view>
        <ability-map :dimensions="diaryData.dimensions"></ability-map>
      </view>

      <!-- 成长轨迹 -->
      <view class="section-card" v-if="diaryData.score_history && diaryData.score_history.length > 0">
        <view class="section-header">
          <text class="section-emoji">📈</text>
          <text class="section-title">成长轨迹</text>
          <text class="section-sub">近{{ diaryData.score_history.length }}次游戏</text>
        </view>
        <!-- 纯 CSS 折线图 -->
        <view class="growth-chart">
          <view class="chart-points">
            <view
              class="chart-point-wrap"
              v-for="(item, index) in diaryData.score_history"
              :key="index"
            >
              <!-- 连接线（除最后一个点外） -->
              <view
                class="chart-line"
                v-if="index < diaryData.score_history.length - 1"
                :style="getLineStyle(index)"
              ></view>
              <!-- 数据点 -->
              <view class="chart-dot-col">
                <view class="chart-dot" :style="getDotStyle(item.stars)">
                  <text class="dot-stars">{{ item.stars }}</text>
                </view>
                <view class="chart-date">{{ formatShortDate(item.date) }}</view>
                <view class="chart-game">{{ getGameShortName(item.game_type) }}</view>
              </view>
            </view>
          </view>
          <!-- Y轴星级参考线 -->
          <view class="chart-legend">
            <view class="legend-row" v-for="n in [5,4,3,2,1]" :key="n">
              <text class="legend-star">{{ '⭐'.repeat(n) }}</text>
            </view>
          </view>
        </view>
        <!-- 简洁折线图（flex 实现） -->
        <view class="growth-bars">
          <view
            class="growth-bar-item"
            v-for="(item, index) in diaryData.score_history"
            :key="index"
          >
            <view class="bar-track">
              <view
                class="bar-fill"
                :style="{ height: (item.stars / 5 * 100) + '%', background: getBarColor(item.stars) }"
              ></view>
            </view>
            <view class="bar-stars">{{ item.stars }}★</view>
            <view class="bar-date">{{ formatShortDate(item.date) }}</view>
          </view>
        </view>
      </view>

      <!-- 灯塔小精灵说 -->
      <view class="section-card lighthouse-card" v-if="diaryData.ai_observation">
        <view class="section-header">
          <text class="section-emoji">💡</text>
          <text class="section-title">灯塔小精灵说</text>
        </view>
        <view class="lighthouse-bubble">
          <view class="lighthouse-avatar">🦋</view>
          <view class="lighthouse-text">{{ diaryData.ai_observation }}</view>
        </view>
      </view>

      <!-- 今日推荐练习 -->
      <view class="section-card" v-if="diaryData.recommended_games && diaryData.recommended_games.length > 0">
        <view class="section-header">
          <text class="section-emoji">🎯</text>
          <text class="section-title">今日推荐练习</text>
        </view>
        <view class="recommend-list">
          <view
            class="recommend-item"
            v-for="(game, index) in diaryData.recommended_games"
            :key="index"
            @click="startGame(game.game_type)"
          >
            <view class="recommend-icon" :style="{ background: getGameBg(game.game_type) }">
              <text>{{ getGameEmoji(game.game_type) }}</text>
            </view>
            <view class="recommend-info">
              <view class="recommend-name">{{ game.game_name }}</view>
              <view class="recommend-reason">{{ game.reason }}</view>
            </view>
            <view class="recommend-arrow">
              <text class="ph ph-arrow-right"></text>
            </view>
          </view>
        </view>
      </view>

      <view class="bottom-space"></view>
    </scroll-view>
  </view>
</template>

<script>
import { get } from '../../../api/index.js'
import AbilityMap from '../../../components/ability/AbilityMap.vue'

const GAME_EMOJI = {
  visual: '👁️',
  spelling: '✨',
  comprehension: '📖',
  working_memory: '🧠',
  rapid_naming: '⚡',
  motor_coordination: '🎯',
}

const GAME_SHORT_NAME = {
  visual: '视觉',
  spelling: '拼字',
  comprehension: '理解',
  working_memory: '记忆',
  rapid_naming: '命名',
  motor_coordination: '动作',
}

const GAME_BG = {
  visual: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
  spelling: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
  comprehension: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
  working_memory: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)',
  rapid_naming: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)',
  motor_coordination: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)',
}

export default {
  name: 'GrowthDiary',
  components: { AbilityMap },
  data() {
    return {
      childId: null,
      diaryData: null,
      loading: false,
    }
  },
  computed: {
    todayStr() {
      const d = new Date()
      return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
    },
    hasDimensions() {
      return this.diaryData && this.diaryData.dimensions && Object.keys(this.diaryData.dimensions).length > 0
    },
  },
  onLoad(options) {
    if (options && options.child_id) {
      this.childId = parseInt(options.child_id)
    }
    this.loadDiary()
  },
  methods: {
    async loadDiary() {
      if (!this.childId) {
        // 尝试从本地存储获取当前孩子
        try {
          const { getCurrentChild } = await import('../../../utils/auth.js')
          const child = getCurrentChild()
          if (child && child.id) {
            this.childId = child.id
          }
        } catch (e) {
          console.error('获取当前孩子失败', e)
        }
      }
      if (!this.childId) {
        this.diaryData = null
        return
      }
      this.loading = true
      try {
        this.diaryData = await get(`/api/reports/growth-diary/${this.childId}`)
      } catch (e) {
        console.error('加载成长日记失败', e)
        this.diaryData = null
      } finally {
        this.loading = false
      }
    },
    goBack() {
      uni.navigateBack()
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    startGame(gameType) {
      uni.navigateTo({ url: `/pages/child/prep/index?game_type=${gameType}` })
    },
    formatShortDate(dateStr) {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      if (parts.length >= 3) {
        return `${parts[1]}/${parts[2]}`
      }
      return dateStr
    },
    getGameEmoji(gameType) {
      return GAME_EMOJI[gameType] || '🎮'
    },
    getGameShortName(gameType) {
      return GAME_SHORT_NAME[gameType] || gameType
    },
    getGameBg(gameType) {
      return GAME_BG[gameType] || 'linear-gradient(135deg, #F9FAFB, #F3F4F6)'
    },
    getDotStyle(stars) {
      const colors = {
        1: '#EF4444',
        2: '#F97316',
        3: '#EAB308',
        4: '#22C55E',
        5: '#4F9EF8',
      }
      const color = colors[stars] || '#A0AEC0'
      return {
        background: color,
        boxShadow: `0 2rpx 8rpx ${color}66`,
      }
    },
    getBarColor(stars) {
      const colors = {
        1: 'linear-gradient(180deg, #EF4444, #FCA5A5)',
        2: 'linear-gradient(180deg, #F97316, #FDBA74)',
        3: 'linear-gradient(180deg, #EAB308, #FDE047)',
        4: 'linear-gradient(180deg, #22C55E, #86EFAC)',
        5: 'linear-gradient(180deg, #4F9EF8, #93C5FD)',
      }
      return colors[stars] || 'linear-gradient(180deg, #A0AEC0, #CBD5E0)'
    },
    getLineStyle(index) {
      // 简单的连接线样式（水平线）
      const history = this.diaryData.score_history
      if (!history || index >= history.length - 1) return {}
      const curr = history[index].stars
      const next = history[index + 1].stars
      const diff = next - curr
      // 根据趋势设置颜色
      const color = diff > 0 ? '#22C55E' : diff < 0 ? '#EF4444' : '#A0AEC0'
      return { borderTopColor: color }
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

/* 导航栏 */
.nav-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.nav-back {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16rpx;
  background: #F3F4F6;
}
.nav-back:active { background: #E5E7EB; }
.nav-back .ph { font-size: 32rpx; color: #4A5568; }

.nav-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #2D3748;
}

.nav-placeholder {
  width: 64rpx;
}

/* 加载状态 */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24rpx;
  padding: 100rpx 0;
}

.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border: 6rpx solid #F0F0F0;
  border-top-color: #4F9EF8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-size: 26rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;
}

.empty-icon .ph {
  font-size: 96rpx;
  color: #D1D5DB;
}

.empty-title {
  font-size: 32rpx;
  font-weight: 700;
  color: #2D3748;
  margin: 24rpx 0 12rpx;
}

.empty-desc {
  font-size: 24rpx;
  color: #A0AEC0;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 40rpx;
}

.empty-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 22rpx 56rpx;
  font-size: 26rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}
.empty-btn:active { transform: scale(0.97); }

/* 滚动区域 */
.page-scroll {
  flex: 1;
  height: 0;
}

/* 日记头部 */
.diary-header {
  padding: 32rpx 32rpx 0;
  text-align: center;
}

.diary-date {
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 500;
  margin-bottom: 8rpx;
}

.diary-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
}

/* 通用卡片 */
.section-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx 28rpx 24rpx;
  margin: 20rpx 24rpx 0;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10rpx;
  margin-bottom: 20rpx;
}

.section-emoji {
  font-size: 32rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  flex: 1;
}

.section-sub {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 今天的冒险 */
.adventure-card {
  display: flex;
  align-items: center;
  gap: 24rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 20rpx;
  padding: 24rpx;
}

.adventure-emoji {
  font-size: 64rpx;
  flex-shrink: 0;
}

.adventure-info {
  flex: 1;
}

.adventure-label {
  font-size: 30rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 6rpx;
}

.adventure-desc {
  font-size: 22rpx;
  color: #718096;
  line-height: 1.5;
  margin-bottom: 10rpx;
}

.adventure-score {
  display: flex;
  align-items: baseline;
  gap: 4rpx;
}

.score-num {
  font-size: 36rpx;
  font-weight: 800;
  color: #4F9EF8;
}

.score-unit {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 成长轨迹 - 柱状图 */
.growth-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 160rpx;
  padding: 0 8rpx;
  gap: 8rpx;
}

.growth-bar-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6rpx;
  height: 100%;
}

.bar-track {
  flex: 1;
  width: 100%;
  background: #F3F4F6;
  border-radius: 8rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
}

.bar-fill {
  width: 100%;
  border-radius: 8rpx;
  transition: height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 8rpx;
}

.bar-stars {
  font-size: 18rpx;
  font-weight: 700;
  color: #4A5568;
}

.bar-date {
  font-size: 16rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 折线图（隐藏，保留备用） */
.growth-chart {
  display: none;
}

/* 灯塔小精灵 */
.lighthouse-card {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 1rpx solid #FDE68A;
}

.lighthouse-bubble {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
}

.lighthouse-avatar {
  font-size: 48rpx;
  flex-shrink: 0;
}

.lighthouse-text {
  flex: 1;
  font-size: 26rpx;
  color: #92400E;
  line-height: 1.8;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
}

/* 推荐练习 */
.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.recommend-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  border-radius: 16rpx;
  background: #F9FAFB;
  transition: all 0.2s;
}
.recommend-item:active { transform: scale(0.98); background: #F3F4F6; }

.recommend-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  flex-shrink: 0;
}

.recommend-info {
  flex: 1;
}

.recommend-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 4rpx;
}

.recommend-reason {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.recommend-arrow .ph {
  font-size: 28rpx;
  color: #CBD5E0;
}

.bottom-space {
  height: 60rpx;
}
</style>
