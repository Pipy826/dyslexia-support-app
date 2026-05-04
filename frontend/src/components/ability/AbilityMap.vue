<template>
  <view class="ability-map">
    <!-- 加载中 -->
    <view class="map-loading" v-if="loading">
      <text class="ph ph-circle-notch spin"></text>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 有数据 -->
    <template v-else-if="abilityItems.length > 0">
      <!-- 数据来源说明 -->
      <view class="map-source-bar">
        <text class="ph ph-game-controller source-icon"></text>
        <text class="source-text">基于 {{ totalPlays }} 次游戏成绩 · 近30天</text>
        <text class="source-update">{{ updateLabel }}</text>
      </view>

      <!-- 能力行 -->
      <view
        v-for="item in abilityItems"
        :key="item.gameType"
        class="ability-row"
      >
        <view class="ability-row-left">
          <view class="ability-icon-wrap" :style="{ background: item.bg }">
            <text :class="'ph ' + item.icon" :style="{ color: item.color }"></text>
          </view>
          <view class="ability-info">
            <view class="ability-name">{{ item.name }}</view>
            <view class="ability-sub">
              <text class="play-count">玩了{{ item.playCount }}次</text>
              <text class="sub-dot">·</text>
              <text class="accuracy-text" :style="{ color: item.color }">正确率{{ item.accuracy }}%</text>
            </view>
          </view>
        </view>
        <view class="ability-right">
          <!-- 进度条 -->
          <view class="progress-bar-wrap">
            <view
              class="progress-bar-fill"
              :style="{ width: item.accuracy + '%', background: item.color }"
            ></view>
          </view>
          <!-- 星星 -->
          <view class="stars-row">
            <text
              v-for="n in 5"
              :key="n"
              :class="n <= item.stars ? 'ph-fill ph-star star filled' : 'ph ph-star star empty'"
              :style="n <= item.stars ? { color: item.color } : {}"
            ></text>
          </view>
        </view>
      </view>

      <!-- 未玩过的游戏 -->
      <view class="unplayed-section" v-if="unplayedItems.length > 0">
        <view class="unplayed-label">还没玩过</view>
        <view class="unplayed-row">
          <view
            v-for="item in unplayedItems"
            :key="item.gameType"
            class="unplayed-chip"
          >
            <text :class="'ph ' + item.icon" :style="{ color: item.color }"></text>
            <text class="chip-name">{{ item.name }}</text>
          </view>
        </view>
      </view>
    </template>

    <!-- 空状态：从未玩过 -->
    <view class="map-empty" v-else>
      <text class="ph ph-game-controller empty-icon"></text>
      <text class="empty-title">还没有游戏记录</text>
      <text class="empty-hint">带孩子玩几局，能力地图就会出现</text>
    </view>
  </view>
</template>

<script>
import { scoreToStars, getGameTypeName } from '../../utils/abilityLabels.js'
import { get } from '../../api/index.js'

const GAME_META = {
  visual:             { icon: 'ph-eye',           color: '#4F9EF8', bg: 'linear-gradient(135deg,#EFF6FF,#DBEAFE)' },
  spelling:           { icon: 'ph-text-aa',        color: '#A78BFA', bg: 'linear-gradient(135deg,#F5F3FF,#EDE9FE)' },
  comprehension:      { icon: 'ph-book-open',      color: '#22C55E', bg: 'linear-gradient(135deg,#F0FDF4,#DCFCE7)' },
  working_memory:     { icon: 'ph-brain',          color: '#F97316', bg: 'linear-gradient(135deg,#FFF7ED,#FFEDD5)' },
  rapid_naming:       { icon: 'ph-lightning',      color: '#EAB308', bg: 'linear-gradient(135deg,#FEFCE8,#FEF9C3)' },
  motor_coordination: { icon: 'ph-pencil-simple',  color: '#EC4899', bg: 'linear-gradient(135deg,#FDF2F8,#FCE7F3)' },
}

const GAME_ORDER = ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']

export default {
  name: 'AbilityMap',
  props: {
    /**
     * 孩子ID，用于拉取游戏活动数据
     */
    childId: {
      type: [Number, String],
      default: null,
    },
    /**
     * 兼容旧用法：直接传入维度分数对象 { visual: 80, ... }
     * 当 childId 未传时使用此数据
     */
    dimensions: {
      type: Object,
      default: () => ({}),
    },
  },
  data() {
    return {
      loading: false,
      gameStats: [],   // 从API拉取的游戏统计
      totalPlays: 0,
      lastUpdated: null,
    }
  },
  computed: {
    updateLabel() {
      if (!this.lastUpdated) return ''
      const d = new Date(this.lastUpdated)
      return `${d.getMonth() + 1}/${d.getDate()} 更新`
    },
    // 玩过的游戏，按正确率排序
    abilityItems() {
      if (this.gameStats.length > 0) {
        // 优先用游戏活动数据
        return GAME_ORDER
          .map(type => {
            const stat = this.gameStats.find(s => s.game_type === type)
            if (!stat || stat.avg_accuracy == null) return null
            return {
              gameType: type,
              name: getGameTypeName(type),
              accuracy: stat.avg_accuracy,
              playCount: stat.play_count,
              stars: scoreToStars(stat.avg_accuracy),
              ...GAME_META[type],
            }
          })
          .filter(Boolean)
      }
      // 降级：用传入的 dimensions
      return GAME_ORDER
        .filter(type => this.dimensions[type] !== undefined)
        .map(type => ({
          gameType: type,
          name: getGameTypeName(type),
          accuracy: this.dimensions[type],
          playCount: null,
          stars: scoreToStars(this.dimensions[type]),
          ...GAME_META[type],
        }))
    },
    // 还没玩过的游戏
    unplayedItems() {
      if (this.gameStats.length === 0) return []
      const playedTypes = new Set(this.gameStats.filter(s => s.play_count > 0).map(s => s.game_type))
      return GAME_ORDER
        .filter(type => !playedTypes.has(type))
        .map(type => ({
          gameType: type,
          name: getGameTypeName(type),
          ...GAME_META[type],
        }))
    },
  },
  watch: {
    childId: {
      immediate: true,
      handler(val) {
        if (val) this.loadGameActivity()
      },
    },
  },
  methods: {
    async loadGameActivity() {
      if (!this.childId) return
      this.loading = true
      try {
        const res = await get(`/api/reports/game-activity/${this.childId}`, { days: 30 }, {}, true)
        this.gameStats = res.game_stats || []
        this.totalPlays = res.summary?.total_plays || 0
        // 取最近一条记录的时间作为更新时间
        const recent = res.recent_records?.[0]
        this.lastUpdated = recent?.completed_at || null
      } catch (e) {
        // 静默失败，降级到 dimensions prop
        this.gameStats = []
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.ability-map {
  width: 100%;
}

/* 加载 */
.map-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 32rpx 0;
  color: #A0AEC0;
}
.loading-text { font-size: 24rpx; font-weight: 500; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; font-size: 28rpx; }

/* 数据来源说明条 */
.map-source-bar {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
  padding-bottom: 12rpx;
  border-bottom: 1rpx solid #F3F4F6;
}
.source-icon { font-size: 22rpx; color: #A0AEC0; }
.source-text { font-size: 20rpx; color: #A0AEC0; font-weight: 500; flex: 1; }
.source-update { font-size: 18rpx; color: #CBD5E0; }

/* 能力行 */
.ability-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14rpx 0;
  border-bottom: 1rpx solid #F9FAFB;
  gap: 12rpx;
}
.ability-row:last-child { border-bottom: none; }

.ability-row-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
  min-width: 0;
}

.ability-icon-wrap {
  width: 52rpx;
  height: 52rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ability-icon-wrap .ph { font-size: 26rpx; }

.ability-info { flex: 1; min-width: 0; }
.ability-name { font-size: 24rpx; font-weight: 700; color: #2D3748; margin-bottom: 4rpx; }
.ability-sub { display: flex; align-items: center; gap: 6rpx; }
.play-count { font-size: 18rpx; color: #A0AEC0; font-weight: 500; }
.sub-dot { font-size: 18rpx; color: #CBD5E0; }
.accuracy-text { font-size: 18rpx; font-weight: 700; }

/* 右侧：进度条 + 星星 */
.ability-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6rpx;
  flex-shrink: 0;
}

.progress-bar-wrap {
  width: 120rpx;
  height: 8rpx;
  background: #F3F4F6;
  border-radius: 9999rpx;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  border-radius: 9999rpx;
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.stars-row { display: flex; gap: 2rpx; }
.star { font-size: 22rpx; }
.star.empty { color: #E5E7EB; }

/* 未玩过 */
.unplayed-section { margin-top: 16rpx; padding-top: 12rpx; border-top: 1rpx solid #F3F4F6; }
.unplayed-label { font-size: 20rpx; color: #CBD5E0; font-weight: 600; margin-bottom: 10rpx; }
.unplayed-row { display: flex; flex-wrap: wrap; gap: 10rpx; }
.unplayed-chip {
  display: flex;
  align-items: center;
  gap: 6rpx;
  background: #F9FAFB;
  border-radius: 9999rpx;
  padding: 6rpx 16rpx;
}
.unplayed-chip .ph { font-size: 20rpx; }
.chip-name { font-size: 20rpx; color: #A0AEC0; font-weight: 500; }

/* 空状态 */
.map-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
  padding: 32rpx 0;
}
.empty-icon { font-size: 56rpx; color: #CBD5E0; }
.empty-title { font-size: 26rpx; font-weight: 700; color: #A0AEC0; }
.empty-hint { font-size: 22rpx; color: #CBD5E0; font-weight: 500; }
</style>
