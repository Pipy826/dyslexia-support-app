<template>
  <view v-if="visible" class="celebration-overlay">
    <view
      v-for="(star, index) in stars"
      :key="index"
      class="star-particle"
      :style="star.style"
    >
      {{ star.emoji }}
    </view>
  </view>
</template>

<script>
export default {
  name: 'CelebrationAnimation',

  emits: ['done'],

  data() {
    return {
      visible: false,
      stars: [],
      timer: null,
    };
  },

  methods: {
    /**
     * 触发庆祝动画，持续 700ms 后自动隐藏并 emit 'done'
     */
    play() {
      this.stars = this._generateStars();
      this.visible = true;

      if (this.timer) {
        clearTimeout(this.timer);
      }

      // 700ms 后隐藏（在 600-800ms 范围内）
      this.timer = setTimeout(() => {
        this.visible = false;
        this.timer = null;
        this.$emit('done');
      }, 700);
    },

    /**
     * 生成 10 颗星星粒子，随机方向、颜色、大小
     */
    _generateStars() {
      const emojis = ['⭐', '🌟', '✨', '💫', '⭐', '🌟', '✨', '💫', '⭐', '🌟'];
      const colors = ['#FFD700', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8'];

      return emojis.map((emoji, index) => {
        // 将 10 颗星星均匀分布在 360 度圆周上，加入随机偏移
        const baseAngle = (index / emojis.length) * 360;
        const angle = baseAngle + (Math.random() * 40 - 20); // ±20度随机偏移
        const distance = 80 + Math.random() * 80; // 80-160rpx 飞散距离
        const rad = (angle * Math.PI) / 180;
        const tx = Math.cos(rad) * distance;
        const ty = Math.sin(rad) * distance;
        const size = 28 + Math.floor(Math.random() * 20); // 28-48rpx
        const delay = Math.random() * 100; // 0-100ms 随机延迟
        const color = colors[index % colors.length];

        return {
          emoji,
          style: [
            `--tx: ${tx}rpx`,
            `--ty: ${ty}rpx`,
            `font-size: ${size}rpx`,
            `color: ${color}`,
            `animation-delay: ${delay}ms`,
          ].join('; '),
        };
      });
    },
  },

  beforeUnmount() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  },
};
</script>

<style scoped>
/* 覆盖层：fixed 定位，高 z-index，不阻塞父组件操作 */
.celebration-overlay {
  position: fixed;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  z-index: 9999;
  pointer-events: none; /* 不拦截触摸事件 */
}

/* 单颗星星粒子 */
.star-particle {
  position: absolute;
  top: 0;
  left: 0;
  transform: translate(-50%, -50%);
  animation: star-burst 700ms ease-out forwards;
  will-change: transform, opacity;
  line-height: 1;
}

/* 星星爆炸关键帧：从中心飞散 + 缩放 + 淡出 */
@keyframes star-burst {
  0% {
    transform: translate(-50%, -50%) translate(0, 0) scale(0.2);
    opacity: 1;
  }
  40% {
    opacity: 1;
    transform: translate(-50%, -50%) translate(calc(var(--tx) * 0.6), calc(var(--ty) * 0.6)) scale(1.3);
  }
  100% {
    transform: translate(-50%, -50%) translate(var(--tx), var(--ty)) scale(0.5);
    opacity: 0;
  }
}
</style>
