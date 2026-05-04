<template>
  <view class="page-container">
    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-caret-left"></text>
      </view>
      <view class="page-title">排行榜 🏆</view>
      <view class="placeholder"></view>
    </view>

    <!-- 范围切换 -->
    <view class="scope-tabs">
      <view
        :class="['scope-tab', { active: scope === 'global' }]"
        @click="switchScope('global')"
      >
        <text class="ph ph-globe"></text> 总榜
      </view>
      <view
        :class="['scope-tab', { active: scope === 'weekly' }]"
        @click="switchScope('weekly')"
      >
        <text class="ph ph-calendar-week"></text> 本周
      </view>
    </view>

    <!-- 我的排名卡片 -->
    <view class="my-rank-card" v-if="myRank">
      <view class="my-rank-left">
        <view class="my-avatar">{{ childName?.charAt(0) || '我' }}</view>
        <view class="my-info">
          <view class="my-name">{{ childName }}</view>
          <view class="my-stars">
            <text class="ph ph-star-fill"></text>
            {{ myRank.star_count }} 颗星星
          </view>
        </view>
      </view>
      <view class="my-rank-right">
        <view class="my-rank-num">第 {{ myRank.rank }} 名</view>
        <view class="my-rank-total">共 {{ totalParticipants }} 人</view>
      </view>
    </view>

    <!-- 加载中 -->
    <view class="loading-area" v-if="loading">
      <text class="ph ph-circle-notch spin"></text>
      <text>加载中...</text>
    </view>

    <!-- 排行榜列表 -->
    <scroll-view class="rank-list" scroll-y v-else-if="rankings.length > 0">
      <!-- 前三名特殊展示 -->
      <view class="top3-area" v-if="rankings.length >= 3">
        <view class="top3-item second" v-if="rankings[1]">
          <view class="top3-crown">🥈</view>
          <view class="top3-avatar" :class="{ me: rankings[1].is_me }">{{ rankings[1].avatar_initial }}</view>
          <view class="top3-name">{{ rankings[1].display_name }}</view>
          <view class="top3-stars">⭐ {{ rankings[1].star_count }}</view>
        </view>
        <view class="top3-item first" v-if="rankings[0]">
          <view class="top3-crown">🥇</view>
          <view class="top3-avatar" :class="{ me: rankings[0].is_me }">{{ rankings[0].avatar_initial }}</view>
          <view class="top3-name">{{ rankings[0].display_name }}</view>
          <view class="top3-stars">⭐ {{ rankings[0].star_count }}</view>
        </view>
        <view class="top3-item third" v-if="rankings[2]">
          <view class="top3-crown">🥉</view>
          <view class="top3-avatar" :class="{ me: rankings[2].is_me }">{{ rankings[2].avatar_initial }}</view>
          <view class="top3-name">{{ rankings[2].display_name }}</view>
          <view class="top3-stars">⭐ {{ rankings[2].star_count }}</view>
        </view>
      </view>

      <!-- 4名以后列表 -->
      <view class="rank-rows">
        <view
          v-for="item in rankings.slice(3)"
          :key="item.child_id"
          :class="['rank-row', { me: item.is_me }]"
        >
          <view class="rank-num">{{ item.rank }}</view>
          <view class="rank-avatar">{{ item.avatar_initial }}</view>
          <view class="rank-name">{{ item.display_name }}</view>
          <view class="rank-stars">
            <text class="ph ph-star-fill"></text>
            {{ item.star_count }}
          </view>
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>

    <!-- 空状态 -->
    <view class="empty-area" v-else-if="!loading">
      <text class="empty-icon">🌟</text>
      <view class="empty-title">还没有排名数据</view>
      <view class="empty-desc">完成更多挑战，获得星星，登上排行榜！</view>
    </view>
  </view>
</template>

<script>
import { getLeaderboard } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      scope: 'global',
      rankings: [],
      myRank: null,
      totalParticipants: 0,
      loading: false,
      child: null,
    }
  },
  computed: {
    childName() { return this.child?.name || '我' },
  },
  onLoad() {
    this.child = getCurrentChild()
    this.loadRanking()
  },
  onShow() {
    this.child = getCurrentChild()
  },
  methods: {
    async loadRanking() {
      if (!this.child?.id) return
      this.loading = true
      try {
        const res = await getLeaderboard(this.child.id, this.scope, 20)
        this.rankings = res.rankings || []
        this.myRank = res.my_rank || null
        this.totalParticipants = res.total_participants || 0
      } catch (e) {
        console.warn('加载排名失败', e)
      } finally {
        this.loading = false
      }
    },
    switchScope(s) {
      this.scope = s
      this.loadRanking()
    },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.reLaunch({ url: '/pages/child/child-training/index' })
      }
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
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 顶部栏 */
.top-bar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 56rpx 32rpx 20rpx;
  background: rgba(255,255,255,0.95);
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
  position: sticky; top: 0; z-index: 30;
  width: 100%; box-sizing: border-box;
}
.back-btn {
  width: 72rpx; height: 72rpx; border-radius: 50%;
  background: #F5F7FA;
  display: flex; align-items: center; justify-content: center;
}
.back-btn:active { transform: scale(0.92); background: #EFF6FF; }
.back-btn .ph { font-size: 36rpx; color: #2D3748; }
.page-title { font-size: 34rpx; font-weight: 800; color: #2D3748; }
.placeholder { width: 72rpx; }

/* 范围切换 */
.scope-tabs {
  display: flex; gap: 16rpx;
  padding: 20rpx 32rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  width: 100%; box-sizing: border-box;
}
.scope-tab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8rpx;
  padding: 16rpx; border-radius: 16rpx;
  font-size: 26rpx; font-weight: 600; color: #A0AEC0;
  background: #F5F7FA; transition: all 0.2s;
}
.scope-tab.active {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
}
.scope-tab .ph { font-size: 26rpx; }

/* 我的排名卡片 */
.my-rank-card {
  margin: 24rpx 32rpx 0;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  border-radius: 24rpx; padding: 28rpx;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 8rpx 24rpx rgba(59,130,246,0.3);
  width: calc(100% - 64rpx); box-sizing: border-box;
}
.my-rank-left { display: flex; align-items: center; gap: 16rpx; }
.my-avatar {
  width: 72rpx; height: 72rpx; border-radius: 50%;
  background: rgba(255,255,255,0.25);
  display: flex; align-items: center; justify-content: center;
  font-size: 30rpx; font-weight: 700; color: #FFFFFF;
}
.my-name { font-size: 28rpx; font-weight: 700; color: #FFFFFF; }
.my-stars { font-size: 22rpx; color: rgba(255,255,255,0.8); margin-top: 4rpx; display: flex; align-items: center; gap: 6rpx; }
.my-stars .ph { font-size: 22rpx; color: #FCD34D; }
.my-rank-right { text-align: right; }
.my-rank-num { font-size: 36rpx; font-weight: 900; color: #FFFFFF; }
.my-rank-total { font-size: 20rpx; color: rgba(255,255,255,0.7); margin-top: 4rpx; }

/* 加载 */
.loading-area {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 16rpx; color: #A0AEC0; font-size: 26rpx; padding: 80rpx 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin 1s linear infinite; display: inline-block; font-size: 48rpx; }

/* 排行榜 */
.rank-list { flex: 1; padding: 24rpx 32rpx 0; width: 100%; box-sizing: border-box; }

/* 前三名 */
.top3-area {
  display: flex; align-items: flex-end; justify-content: center;
  gap: 16rpx; margin-bottom: 32rpx; padding: 24rpx 0;
  background: #FFFFFF; border-radius: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.top3-item {
  display: flex; flex-direction: column; align-items: center; gap: 8rpx;
  flex: 1;
}
.top3-item.first { transform: translateY(-16rpx); }
.top3-crown { font-size: 48rpx; line-height: 1; }
.top3-avatar {
  width: 80rpx; height: 80rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  font-size: 32rpx; font-weight: 700; color: #4F9EF8;
  border: 4rpx solid #BFDBFE;
}
.top3-item.first .top3-avatar {
  width: 96rpx; height: 96rpx; font-size: 40rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  color: #D97706; border-color: #FCD34D;
}
.top3-avatar.me { border-color: #4F9EF8; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; }
.top3-name { font-size: 22rpx; font-weight: 700; color: #2D3748; text-align: center; }
.top3-stars { font-size: 20rpx; color: #F57F17; font-weight: 600; }

/* 4名以后 */
.rank-rows { display: flex; flex-direction: column; gap: 10rpx; width: 100%; }
.rank-row {
  background: #FFFFFF; border-radius: 18rpx; padding: 20rpx 24rpx;
  display: flex; align-items: center; gap: 16rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
  width: 100%; box-sizing: border-box;
}
.rank-row.me {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #BFDBFE;
}
.rank-num { width: 48rpx; font-size: 26rpx; font-weight: 800; color: #A0AEC0; text-align: center; flex-shrink: 0; }
.rank-avatar {
  width: 56rpx; height: 56rpx; border-radius: 50%;
  background: #F5F7FA;
  display: flex; align-items: center; justify-content: center;
  font-size: 24rpx; font-weight: 700; color: #718096; flex-shrink: 0;
}
.rank-row.me .rank-avatar { background: #4F9EF8; color: #FFFFFF; }
.rank-name { flex: 1; font-size: 26rpx; font-weight: 700; color: #2D3748; }
.rank-stars { display: flex; align-items: center; gap: 6rpx; font-size: 26rpx; font-weight: 700; color: #F57F17; flex-shrink: 0; }
.rank-stars .ph { font-size: 24rpx; color: #FCD34D; }

/* 空状态 */
.empty-area {
  flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 80rpx 40rpx; gap: 16rpx; width: 100%; box-sizing: border-box;
}
.empty-icon { font-size: 80rpx; }
.empty-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; text-align: center; line-height: 1.6; }
</style>
