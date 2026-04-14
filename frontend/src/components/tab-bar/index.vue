<template>
  <view class="tab-bar" :class="[`tab-bar-${type}`]">
    <!-- 家长端 5 导航 -->
    <template v-if="type === 'parent'">
      <view
        v-for="item in parentTabs"
        :key="item.pagePath"
        class="tab-item"
        :class="{ active: currentPath === item.pagePath }"
        @click="switchTab(item.pagePath)"
      >
        <text class="tab-icon" :class="currentPath === item.pagePath ? item.activeIcon : item.icon"></text>
        <text class="tab-label" :class="currentPath === item.pagePath ? 'tab-label-bold' : ''">{{ item.text }}</text>
      </view>
    </template>

    <!-- 儿童端 2 导航 -->
    <template v-else-if="type === 'child'">
      <view
        v-for="item in childTabs"
        :key="item.pagePath"
        class="tab-item"
        :class="{ active: currentPath === item.pagePath }"
        @click="switchTab(item.pagePath)"
      >
        <text class="tab-icon" :class="currentPath === item.pagePath ? item.activeIcon : item.icon"></text>
        <text class="tab-label" :class="currentPath === item.pagePath ? 'tab-label-bold' : ''">{{ item.text }}</text>
      </view>
    </template>
  </view>
</template>

<script>
export default {
  name: 'TabBar',
  props: {
    type: {
      type: String,
      default: 'parent' // 'parent' | 'child'
    },
    current: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      parentTabs: [
        { pagePath: '/pages/parent/home/index', text: '首页', icon: 'ph ph-house', activeIcon: 'ph-fill ph-house' },
        { pagePath: '/pages/parent/screening/index', text: '筛查', icon: 'ph ph-magnifying-glass', activeIcon: 'ph-fill ph-magnifying-glass' },
        { pagePath: '/pages/parent/report/index', text: '报告', icon: 'ph ph-chart-pie', activeIcon: 'ph-fill ph-chart-pie' },
        { pagePath: '/pages/parent/training/index', text: '训练', icon: 'ph ph-squares-four', activeIcon: 'ph-fill ph-squares-four' },
        { pagePath: '/pages/parent/profile/index', text: '我的', icon: 'ph ph-user', activeIcon: 'ph-fill ph-user' }
      ],
      childTabs: [
        { pagePath: '/pages/child/home/index', text: '挑战', icon: 'ph-fill ph-game-controller', activeIcon: 'ph-fill ph-game-controller' },
        { pagePath: '/pages/child/training/index', text: '训练乐园', icon: 'ph-fill ph-tree', activeIcon: 'ph-fill ph-tree' }
      ]
    }
  },
  computed: {
    currentPath() {
      return this.current || getCurrentPages()[getCurrentPages().length - 1]?.route || ''
    }
  },
  methods: {
    switchTab(pagePath) {
      if (this.currentPath === pagePath) return
      // 项目使用自定义导航栏，无原生 tabBar 配置
      // 用 reLaunch 清空页面栈后跳转，避免页面堆积
      uni.reLaunch({ url: pagePath })
    }
  }
}
</script>

<style scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 168rpx;
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  padding: 16rpx 32rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
  background: #FFFFFF;
  border-top: 1rpx solid #F3F4F6;
  z-index: 999;
}

.tab-bar-parent {
  padding-left: 16rpx;
  padding-right: 16rpx;
}

.tab-bar-child {
  justify-content: center;
  gap: 160rpx;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  color: #9CA3AF;
  padding: 8rpx 16rpx;
}

.tab-item.active {
  color: #3B82F6;
}

.tab-icon {
  font-size: 44rpx;
  line-height: 1;
}

.tab-label {
  font-size: 20rpx;
  font-weight: 500;
}

.tab-label-bold {
  font-weight: 700;
}
</style>
