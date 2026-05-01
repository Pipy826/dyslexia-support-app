<template>
  <view class="badge-grid">
    <view
      v-for="badge in allBadges"
      :key="badge.key"
      :class="['badge-item', badge.earned ? 'earned' : 'locked', badge.isNew ? 'new-badge' : '']"
      @click="showBadgeDetail(badge)"
    >
      <view class="badge-icon">{{ badge.icon }}</view>
      <view class="badge-name">{{ badge.name }}</view>
      <view class="badge-new-tag" v-if="badge.isNew">NEW</view>
    </view>

    <!-- 徽章详情弹窗 -->
    <view class="badge-modal" v-if="selectedBadge" @click.self="selectedBadge = null">
      <view class="badge-modal-content">
        <view class="badge-modal-icon">{{ selectedBadge.icon }}</view>
        <view class="badge-modal-name">{{ selectedBadge.name }}</view>
        <view class="badge-modal-desc">{{ selectedBadge.desc }}</view>
        <view class="badge-modal-time" v-if="selectedBadge.earned && selectedBadge.earnedAt">
          获得时间：{{ formatDate(selectedBadge.earnedAt) }}
        </view>
        <view class="badge-modal-hint" v-else>
          {{ selectedBadge.desc }}
        </view>
        <button class="badge-modal-close" @click="selectedBadge = null">关闭</button>
      </view>
    </view>
  </view>
</template>

<script>
// 所有徽章定义（与后端 BADGE_DEFINITIONS 保持一致）
const BADGE_DEFS = [
  { key: 'first_game',    name: '初次探险',   icon: '🚀', desc: '完成第一次能力探索' },
  { key: 'week_streak',   name: '坚持一周',   icon: '🔥', desc: '连续7天完成挑战' },
  { key: 'month_streak',  name: '月度冠军',   icon: '🏆', desc: '连续30天完成挑战' },
  { key: 'all_games',     name: '全能探险家', icon: '🌟', desc: '完成全部6种游戏' },
  { key: 'perfect_score', name: '完美表现',   icon: '💎', desc: '单次游戏正确率100%' },
  { key: 'speed_demon',   name: '闪电侠',     icon: '⚡', desc: '平均反应时间低于2秒' },
]

export default {
  name: 'BadgeGrid',
  props: {
    // 已获得的徽章列表（来自 API）
    earnedBadges: {
      type: Array,
      default: () => [],
    },
    // 新获得的徽章 key 列表（用于显示 NEW 标记和闪光动画）
    newBadgeKeys: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      selectedBadge: null,
    }
  },
  computed: {
    allBadges() {
      return BADGE_DEFS.map(def => {
        const earned = this.earnedBadges.find(b => b.badge_key === def.key)
        return {
          ...def,
          earned: !!earned,
          earnedAt: earned?.earned_at || null,
          isNew: this.newBadgeKeys.includes(def.key),
        }
      })
    },
  },
  methods: {
    showBadgeDetail(badge) {
      this.selectedBadge = badge
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
    },
  },
}
</script>

<style scoped>
.badge-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  width: 100%;
}

.badge-item {
  width: calc(33.33% - 11rpx);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  padding: 20rpx 12rpx;
  border-radius: 20rpx;
  position: relative;
  transition: all 0.2s;
  box-sizing: border-box;
}

.badge-item:active { transform: scale(0.95); }

/* 已获得：彩色 */
.badge-item.earned {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border: 2rpx solid #FDE68A;
  box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15);
}

/* 未获得：灰色 */
.badge-item.locked {
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  opacity: 0.6;
}

/* 新获得：闪光动画 */
.badge-item.new-badge {
  animation: shimmerBadge 1.5s ease-in-out 3;
}

@keyframes shimmerBadge {
  0%, 100% { box-shadow: 0 4rpx 12rpx rgba(245, 158, 11, 0.15); }
  50% { box-shadow: 0 0 0 6rpx rgba(245, 158, 11, 0.4), 0 4rpx 20rpx rgba(245, 158, 11, 0.3); }
}

.badge-icon {
  font-size: 48rpx;
  line-height: 1;
}

.badge-item.locked .badge-icon {
  filter: grayscale(100%);
}

.badge-name {
  font-size: 20rpx;
  font-weight: 700;
  color: #374151;
  text-align: center;
}

.badge-item.locked .badge-name {
  color: #9CA3AF;
}

/* NEW 标签 */
.badge-new-tag {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #EF4444;
  color: #FFFFFF;
  font-size: 16rpx;
  font-weight: 800;
  padding: 2rpx 10rpx;
  border-radius: 8rpx;
}

/* 弹窗 */
.badge-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.badge-modal-content {
  background: #FFFFFF;
  width: 80%;
  max-width: 560rpx;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.85); }
  to { opacity: 1; transform: scale(1); }
}

.badge-modal-icon { font-size: 80rpx; }
.badge-modal-name { font-size: 36rpx; font-weight: 800; color: #1F2937; }
.badge-modal-desc { font-size: 26rpx; color: #6B7280; text-align: center; line-height: 1.6; }
.badge-modal-time { font-size: 22rpx; color: #9CA3AF; }
.badge-modal-hint { font-size: 22rpx; color: #9CA3AF; text-align: center; }

.badge-modal-close {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  margin-top: 8rpx;
}
</style>
