<template>
  <scroll-view
    class="level-map"
    scroll-x
    :scroll-left="scrollLeft"
    scroll-with-animation
  >
    <view class="level-track">
      <view
        v-for="(level, idx) in levels"
        :key="idx"
        class="level-node-wrap"
      >
        <!-- 连接线（第一个关卡左侧不显示） -->
        <view
          v-if="idx > 0"
          :class="['connector', levels[idx - 1].status === 'completed' ? 'done' : 'locked']"
        ></view>

        <!-- 关卡节点 -->
        <view :class="['level-node', level.status]" :id="`level-${idx}`">
          <text class="level-icon">{{ levelIcon(level.status) }}</text>
          <view v-if="level.status === 'current'" class="pulse-ring"></view>
        </view>

        <!-- 关卡编号 -->
        <view :class="['level-label', level.status]">第{{ idx + 1 }}关</view>
      </view>
    </view>
  </scroll-view>
</template>

<script>
export default {
  name: 'LevelMap',
  props: {
    questions: {
      type: Array,
      required: true,
    },
    currentIndex: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      scrollLeft: 0,
    }
  },
  computed: {
    levels() {
      return buildLevels(this.questions, this.currentIndex)
    },
    currentLevelIndex() {
      return Math.floor(this.currentIndex / 3)
    },
  },
  watch: {
    currentIndex() {
      this.$nextTick(() => {
        this.scrollToCurrentLevel()
      })
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.scrollToCurrentLevel()
    })
  },
  methods: {
    levelIcon(status) {
      const icons = {
        completed: '⭐',
        current: '🎯',
        locked: '🔒',
      }
      return icons[status] || '🔒'
    },

    scrollToCurrentLevel() {
      // 每个节点宽度约 140rpx + 连接线 60rpx = 200rpx
      // 换算为 px（rpx / 750 * screenWidth）
      const screenWidth = uni.getSystemInfoSync().windowWidth
      const nodeWidthPx = (200 / 750) * screenWidth
      const targetScrollLeft = Math.max(0, this.currentLevelIndex * nodeWidthPx - screenWidth / 2 + nodeWidthPx / 2)
      this.scrollLeft = targetScrollLeft
    },
  },
}

/**
 * 将题目数组按每3题分组，计算每关状态
 * @param {Array} questions - 题目数组
 * @param {number} currentIndex - 当前题目索引（0-based）
 * @returns {Array<{ questions: Array, status: 'completed'|'current'|'locked' }>}
 */
export function buildLevels(questions, currentIndex) {
  const levels = []
  for (let i = 0; i < questions.length; i += 3) {
    const levelQuestions = questions.slice(i, i + 3)
    const levelStart = i
    const levelEnd = i + levelQuestions.length - 1

    let status = 'locked'
    if (currentIndex > levelEnd) {
      status = 'completed'
    } else if (currentIndex >= levelStart && currentIndex <= levelEnd) {
      status = 'current'
    }

    levels.push({ questions: levelQuestions, status })
  }
  return levels
}
</script>

<style scoped>
.level-map {
  width: 100%;
  white-space: nowrap;
}

.level-track {
  display: inline-flex;
  align-items: center;
  padding: 16rpx 32rpx;
  min-width: 100%;
}

/* 关卡节点容器 */
.level-node-wrap {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
}

/* 连接线 */
.connector {
  width: 60rpx;
  height: 6rpx;
  border-radius: 3rpx;
  margin-bottom: 28rpx; /* 与节点垂直对齐 */
  align-self: center;
  /* 连接线在节点之间，需要调整布局 */
  position: relative;
  top: -14rpx; /* 微调垂直位置与节点中心对齐 */
}

.connector.done {
  background: linear-gradient(90deg, #22C55E, #4ADE80);
}

.connector.locked {
  background: repeating-linear-gradient(
    90deg,
    #CBD5E0 0rpx,
    #CBD5E0 12rpx,
    transparent 12rpx,
    transparent 20rpx
  );
}

/* 关卡节点 */
.level-node {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.level-node.completed {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.4);
}

.level-node.current {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  box-shadow: 0 4rpx 20rpx rgba(79, 158, 248, 0.5);
}

.level-node.locked {
  background: linear-gradient(135deg, #E5E7EB, #D1D5DB);
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.08);
}

.level-icon {
  font-size: 44rpx;
  line-height: 1;
}

/* 当前关卡脉冲动画 */
.pulse-ring {
  position: absolute;
  top: -12rpx;
  left: -12rpx;
  right: -12rpx;
  bottom: -12rpx;
  border-radius: 50%;
  border: 4rpx solid rgba(79, 158, 248, 0.5);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.9);
    opacity: 1;
  }
  70% {
    transform: scale(1.15);
    opacity: 0;
  }
  100% {
    transform: scale(0.9);
    opacity: 0;
  }
}

/* 关卡编号标签 */
.level-label {
  margin-top: 12rpx;
  font-size: 22rpx;
  font-weight: 700;
  white-space: nowrap;
}

.level-label.completed {
  color: #22C55E;
}

.level-label.current {
  color: #4F9EF8;
}

.level-label.locked {
  color: #A0AEC0;
}
</style>
