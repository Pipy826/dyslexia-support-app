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
        { pagePath: '/pages/parent/screening/index', text: '游戏', icon: 'ph ph-game-controller', activeIcon: 'ph-fill ph-game-controller' },
        { pagePath: '/pages/parent/articles/index', text: '科普', icon: 'ph ph-newspaper', activeIcon: 'ph-fill ph-newspaper' },
        { pagePath: '/pages/parent/training/index', text: '训练', icon: 'ph ph-squares-four', activeIcon: 'ph-fill ph-squares-four' },
        { pagePath: '/pages/parent/profile/index', text: '我的', icon: 'ph ph-user', activeIcon: 'ph-fill ph-user' }
      ],
      childTabs: [
        { pagePath: '/pages/child/child-training/index', text: '挑战', icon: 'ph-fill ph-game-controller', activeIcon: 'ph-fill ph-game-controller' },
        { pagePath: '/pages/child/training/index', text: '训练乐园', icon: 'ph-fill ph-tree', activeIcon: 'ph-fill ph-tree' }
      ]
    }
  },
  computed: {
    currentPath() {
      if (this.current) return this.current
      const pages = getCurrentPages()
      if (!pages || pages.length === 0) return ''
      const route = pages[pages.length - 1]?.route || ''
      return route.startsWith('/') ? route : '/' + route
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
/* 浮动导航栏 - 小程序兼容，不用 gap */
.tab-bar {
  position: fixed;
  bottom: 16rpx;
  left: 16rpx;
  right: 16rpx;
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  align-items: center;
  padding: 12rpx 8rpx;
  padding-bottom: calc(12rpx + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.95);
  border-radius: 28rpx;
  z-index: 999;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08), 0 0 0 1rpx rgba(0, 0, 0, 0.04);
  overflow: hidden;
  box-sizing: border-box;
}

/* 家长端：5个均分 */
.tab-bar-parent {
  padding: 12rpx 4rpx;
  padding-bottom: calc(12rpx + env(safe-area-inset-bottom));
}

/* 儿童端：2个，用 justify-content:space-around 自动居中，不用 gap */
.tab-bar-child {
  justify-content: space-around;
  padding: 16rpx 40rpx;
  padding-bottom: calc(16rpx + env(safe-area-inset-bottom));
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #9CA3AF;
  padding: 10rpx 16rpx;
  border-radius: 16rpx;
  position: relative;
  flex-shrink: 0;
}

/* 激活状态：只用颜色变化，不用 background（避免首页 common.scss 覆盖问题） */
.tab-item.active {
  color: #4F9EF8;
}

.tab-item.active::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  width: 32rpx;
  height: 4rpx;
  background: #4F9EF8;
  border-radius: 2rpx;
  margin-left: -16rpx;
}

.tab-icon {
  font-size: 40rpx;
  line-height: 1;
  display: block;
  margin-bottom: 4rpx;
}

.tab-label {
  font-size: 20rpx;
  font-weight: 600;
  display: block;
}

.tab-label-bold {
  font-weight: 700;
}
</style>
