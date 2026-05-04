<template>
  <view class="result-emoji-wrapper">
    <!-- 圆形背景卡片 -->
    <view
      class="emoji-card"
      :class="cardClass"
      :style="cardStyle"
    >
      <text class="emoji-icon" :class="{ 'emoji-bounce': stars === 3 }">
        {{ emojiIcon }}
      </text>
    </view>

    <!-- 文字描述 -->
    <text class="emoji-label" :class="labelClass">{{ labelText }}</text>
  </view>
</template>

<script>
export default {
  name: 'ResultEmoji',

  props: {
    /**
     * 星星数量，1-3
     */
    stars: {
      type: Number,
      required: true,
      validator: (val) => [1, 2, 3].includes(val),
    },
  },

  computed: {
    /** 根据星星数返回对应 emoji */
    emojiIcon() {
      const map = {
        1: '😊',
        2: '😄',
        3: '🎉',
      };
      return map[this.stars] || '😊';
    },

    /** 卡片 CSS class */
    cardClass() {
      return `emoji-card--stars-${this.stars}`;
    },

    /** 卡片内联样式（背景渐变） */
    cardStyle() {
      const backgrounds = {
        1: 'background: #E5E7EB;',                                          // 灰色背景
        2: 'background: #FEF9C3;',                                          // 黄色背景
        3: 'background: linear-gradient(135deg, #FEF08A, #FCD34D, #F59E0B);', // 金色渐变背景
      };
      return backgrounds[this.stars] || backgrounds[1];
    },

    /** label CSS class */
    labelClass() {
      return `emoji-label--stars-${this.stars}`;
    },

    /** 文字描述 */
    labelText() {
      const map = {
        1: '继续加油！',
        2: '做得不错！',
        3: '太厉害了！',
      };
      return map[this.stars] || '继续加油！';
    },
  },
};
</script>

<style scoped>
/* 整体容器：垂直居中排列 */
.result-emoji-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
}

/* 圆形背景卡片 */
.emoji-card {
  width: 200rpx;
  height: 200rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

/* 1 星：灰色边框 */
.emoji-card--stars-1 {
  border: 4rpx solid #D1D5DB;
}

/* 2 星：黄色边框 */
.emoji-card--stars-2 {
  border: 4rpx solid #FDE047;
}

/* 3 星：金色边框 + 发光效果 */
.emoji-card--stars-3 {
  border: 4rpx solid #F59E0B;
  box-shadow: 0 8rpx 32rpx rgba(245, 158, 11, 0.4);
}

/* emoji 图标：大尺寸 */
.emoji-icon {
  font-size: 120rpx;
  line-height: 1;
  display: block;
}

/* 3 星跳跃动画 */
.emoji-bounce {
  animation: emoji-jump 600ms ease-in-out infinite alternate;
  will-change: transform;
}

@keyframes emoji-jump {
  0% {
    transform: translateY(0) scale(1);
  }
  100% {
    transform: translateY(-16rpx) scale(1.08);
  }
}

/* 文字描述 */
.emoji-label {
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 20rpx;
  padding: 8rpx 24rpx;
}

/* 1 星：灰色文字 */
.emoji-label--stars-1 {
  color: #6B7280;
  background: #F3F4F6;
}

/* 2 星：橙黄色文字 */
.emoji-label--stars-2 {
  color: #D97706;
  background: #FEF3C7;
}

/* 3 星：金色文字 + 渐变背景 */
.emoji-label--stars-3 {
  color: #92400E;
  background: linear-gradient(135deg, #FEF08A, #FCD34D);
}
</style>
