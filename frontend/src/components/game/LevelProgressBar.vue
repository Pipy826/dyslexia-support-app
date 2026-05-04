<template>
  <view class="level-progress-bar">
    <view class="progress-info">
      <text class="progress-text">第 {{ current }} 题 / 共 {{ total }} 题</text>
    </view>
    <view class="progress-track">
      <view class="progress-fill" :style="{ width: progressPercent + '%' }"></view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'LevelProgressBar',
  props: {
    current: {
      type: Number,
      required: true,
      validator: (value) => value >= 1
    },
    total: {
      type: Number,
      required: true,
      validator: (value) => value >= 1
    }
  },
  computed: {
    progressPercent() {
      if (this.total === 0) return 0
      return Math.round((this.current / this.total) * 100)
    }
  }
}
</script>

<style scoped>
.level-progress-bar {
  padding: 20px 30px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.progress-info {
  margin-bottom: 12px;
}

.progress-text {
  font-size: 28px;
  color: #333;
  font-weight: 500;
}

.progress-track {
  height: 12px;
  background: #e8e8e8;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4a90e2, #67c23a);
  border-radius: 6px;
  transition: width 0.3s ease;
}
</style>