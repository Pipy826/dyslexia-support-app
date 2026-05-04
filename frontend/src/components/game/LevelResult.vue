<template>
  <view class="level-result">
    <!-- 通关成功 -->
    <view class="result-content passed" v-if="result.passed">
      <view class="result-icon success">
        <text class="ph ph-trophy"></text>
      </view>
      <view class="result-title">恭喜通关！🎉</view>
      <view class="stars-container">
        <view 
          v-for="i in 3" 
          :key="i" 
          class="star" 
          :class="{ active: i <= result.stars_earned, animate: i <= result.stars_earned }"
          :style="{ animationDelay: (i * 0.2) + 's' }"
        >
          <text class="ph ph-star"></text>
        </view>
      </view>
      <view class="accuracy-display">
        正确率：<text class="accuracy-value">{{ Math.round(result.accuracy * 100) }}%</text>
      </view>
      <view class="unlocked-notice" v-if="unlockedNext">
        <text class="ph ph-unlock"></text> 新关卡已解锁！
      </view>
    </view>

    <!-- 未通关 -->
    <view class="result-content failed" v-else>
      <view class="result-icon fail">
        <text class="ph ph-heart-break"></text>
      </view>
      <view class="result-title">再接再厉！</view>
      <view class="accuracy-display">
        正确率：<text class="accuracy-value">{{ Math.round(result.accuracy * 100) }}%</text>
      </view>
      <view class="pass-condition">
        通关需要 {{ Math.round(result.pass_condition?.min_accuracy * 100 || 70) }}% 正确率
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons">
      <button class="action-btn retry" @click="handleRetry">
        <text class="ph ph-arrow-counter-clockwise"></text> 再试一次
      </button>
      <button class="action-btn back" @click="handleBackToLevels">
        <text class="ph ph-caret-left"></text> 返回关卡选择
      </button>
    </view>
  </view>
</template>

<script>
export default {
  name: 'LevelResult',
  props: {
    result: {
      type: Object,
      required: true
    }
  },
  emits: ['retry', 'back-to-levels'],
  computed: {
    // 检查是否解锁了下一关
    unlockedNext() {
      // 根据 passed 和 stars_earned 判断是否解锁下一关
      // 通关即解锁下一关
      return this.result.passed === true
    }
  },
  methods: {
    handleRetry() {
      this.$emit('retry')
    },
    handleBackToLevels() {
      this.$emit('back-to-levels')
    }
  }
}
</script>

<style scoped>
.level-result {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: linear-gradient(180deg, #f5f5f5 0%, #e8e8e8 100%);
}

.result-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 40px;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 600px;
}

.result-content.passed {
  border: 4px solid #52c41a;
}

.result-content.failed {
  border: 4px solid #faad14;
}

.result-icon {
  font-size: 100px;
  margin-bottom: 20px;
}

.result-icon.success {
  color: #52c41a;
}

.result-icon.fail {
  color: #faad14;
}

.result-title {
  font-size: 40px;
  font-weight: bold;
  color: #333;
  margin-bottom: 30px;
}

.stars-container {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.star {
  font-size: 60px;
  color: #d9d9d9;
  transition: all 0.3s ease;
}

.star.active {
  color: #faad14;
}

.star.animate {
  animation: starPop 0.5s ease forwards;
}

@keyframes starPop {
  0% { transform: scale(0); opacity: 0; }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); opacity: 1; }
}

.accuracy-display {
  font-size: 28px;
  color: #666;
  margin-bottom: 15px;
}

.accuracy-value {
  font-size: 36px;
  font-weight: bold;
  color: #333;
}

.pass-condition {
  font-size: 24px;
  color: #999;
  margin-bottom: 20px;
}

.unlocked-notice {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 28px;
  color: #52c41a;
  font-weight: 500;
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 600px;
  margin-top: 40px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px 40px;
  border-radius: 50px;
  font-size: 32px;
  font-weight: 500;
  border: none;
}

.action-btn.retry {
  background: linear-gradient(135deg, #4a90e2, #67c23a);
  color: #fff;
}

.action-btn.back {
  background: #fff;
  color: #666;
  border: 2px solid #d9d9d9;
}
</style>