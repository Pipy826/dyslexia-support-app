<template>
  <!-- 翻牌组件：CSS 3D 翻转动画，300ms -->
  <view
    :class="['flip-card-wrapper', { 'is-matched': isMatched }]"
    @click="handleClick"
  >
    <view :class="['flip-card-inner', { flipped: isFlipped || isMatched }]">

      <!-- 背面：渐变紫色 + 🌟 图案 -->
      <view class="flip-card-back">
        <text class="back-star">🌟</text>
      </view>

      <!-- 正面：emoji 大字体 或 文字 -->
      <view class="flip-card-front">
        <text v-if="content && content.type === 'emoji'" class="front-emoji">
          {{ content.content }}
        </text>
        <text v-else-if="content && content.type === 'text'" class="front-text">
          {{ content.content }}
        </text>
      </view>

    </view>
  </view>
</template>

<script>
export default {
  name: 'FlipCard',

  props: {
    isFlipped: { type: Boolean, default: false },
    isMatched: { type: Boolean, default: false },
    content: { type: Object, default: () => ({ type: 'emoji', content: '🌟' }) },
    disabled: { type: Boolean, default: false },
  },

  emits: ['click'],

  methods: {
    handleClick() {
      if (this.isMatched || this.disabled) return
      this.$emit('click')
    },
  },
}
</script>

<style scoped>
.flip-card-wrapper {
  width: 100%;
  aspect-ratio: 1 / 1.1;
  perspective: 800rpx;
  cursor: pointer;
  border-radius: 20rpx;
  transition: box-shadow 0.3s;
}

.flip-card-wrapper.is-matched {
  box-shadow: 0 0 0 4rpx #22C55E, 0 4rpx 16rpx rgba(34, 197, 94, 0.3);
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 0.3s ease;
  border-radius: 20rpx;
}

.flip-card-inner.flipped {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
  border-radius: 20rpx;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.flip-card-back {
  background: linear-gradient(135deg, #A78BFA 0%, #7C3AED 100%);
  box-shadow: 0 4rpx 16rpx rgba(124, 58, 237, 0.25);
}

.back-star {
  font-size: 56rpx;
  opacity: 0.85;
  transform: rotate(-10deg);
}

.flip-card-front {
  background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
  border: 3rpx solid #FDE68A;
  transform: rotateY(180deg);
  box-shadow: 0 4rpx 16rpx rgba(251, 191, 36, 0.15);
  padding: 8rpx;
}

.front-emoji { font-size: 72rpx; line-height: 1; }
.front-text {
  font-size: 44rpx;
  font-weight: 900;
  color: #92400E;
  text-align: center;
  line-height: 1.3;
  word-break: break-all;
  letter-spacing: 2rpx;
}
</style>
