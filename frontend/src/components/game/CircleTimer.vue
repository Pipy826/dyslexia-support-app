<template>
  <view :class="['circle-timer', { warning: timeLeft <= 3 }]">
    <!--
      跨平台圆形倒计时：使用双层半圆 CSS 方案
      原因：微信小程序不支持 SVG，conic-gradient 在部分小程序版本也不稳定
      方案：用两个半圆 view + rotate 实现圆形进度，兼容 H5 / 小程序 / App
    -->
    <view class="timer-ring">
      <!-- 左半圆（0~180度） -->
      <view class="half-circle left-half">
        <view class="half-fill left-fill" :style="leftStyle"></view>
      </view>
      <!-- 右半圆（180~360度） -->
      <view class="half-circle right-half">
        <view class="half-fill right-fill" :style="rightStyle"></view>
      </view>
    </view>
    <!-- 中央数字 -->
    <view class="timer-text" :style="{ color: timerTextColor }">{{ timeLeft }}</view>
  </view>
</template>

<script>
/**
 * CircleTimer — 圆形倒计时组件（跨平台版本）
 *
 * 使用双半圆 CSS 方案，兼容微信小程序、H5、App。
 *
 * 正确性属性：
 * - 属性9：进度比例始终在 [0, 1] 范围内
 * - 属性10：timerColor 始终返回三种颜色之一，无未覆盖情况
 */

export default {
  name: 'CircleTimer',
  props: {
    timeLeft: {
      type: Number,
      required: true,
      default: 10,
    },
    totalTime: {
      type: Number,
      required: true,
      default: 10,
    },
  },
  computed: {
    /**
     * 进度比例，始终在 [0, 1] 范围内（属性9）
     */
    progress() {
      if (this.totalTime <= 0) return 1
      return Math.max(0, Math.min(1, this.timeLeft / this.totalTime))
    },

    /**
     * 根据剩余时间返回颜色（属性10：始终返回三种颜色之一）
     */
    timerColor() {
      if (this.timeLeft <= 3) return '#FF6B6B'
      if (this.timeLeft <= 5) return '#F97316'
      return '#FFFFFF'
    },

    timerTextColor() {
      if (this.timeLeft <= 3) return '#FF6B6B'
      if (this.timeLeft <= 5) return '#F97316'
      return '#FFFFFF'
    },

    /**
     * 双半圆旋转角度计算
     * progress=1（满）→ 左右各旋转 180deg
     * progress=0（空）→ 左右各旋转 0deg
     */
    leftStyle() {
      // 左半圆控制 0~50% 进度（0~180deg）
      const p = this.progress
      const deg = p >= 0.5
        ? 180
        : Math.round(p * 360)
      return {
        transform: `rotate(${deg}deg)`,
        'background-color': this.timerColor,
        'transition': 'transform 0.9s linear, background-color 0.3s ease',
      }
    },

    rightStyle() {
      // 右半圆控制 50~100% 进度（180~360deg）
      const p = this.progress
      const deg = p >= 0.5
        ? Math.round((p - 0.5) * 360)
        : 0
      return {
        transform: `rotate(${deg}deg)`,
        'background-color': this.timerColor,
        'transition': 'transform 0.9s linear, background-color 0.3s ease',
      }
    },
  },
}
</script>

<style scoped>
.circle-timer {
  position: relative;
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 圆环容器 */
.timer-ring {
  position: absolute;
  top: 0; left: 0;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  /* 轨道背景色 */
  background: rgba(255, 255, 255, 0.2);
}

/* 半圆基础样式 */
.half-circle {
  position: absolute;
  top: 0;
  width: 40rpx;
  height: 80rpx;
  overflow: hidden;
}

.left-half {
  left: 0;
}

.right-half {
  right: 0;
}

/* 半圆填充 */
.half-fill {
  position: absolute;
  top: 0;
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  transform-origin: center center;
}

.left-fill {
  left: 0;
  transform-origin: 100% 50%;
}

.right-fill {
  right: 0;
  transform-origin: 0% 50%;
}

/* 内圆遮罩（形成圆环效果） */
.timer-ring::after {
  content: '';
  position: absolute;
  top: 10rpx; left: 10rpx;
  width: 60rpx; height: 60rpx;
  border-radius: 50%;
  /* 与游戏顶部渐变背景色匹配，用透明度模拟 */
  background: rgba(0, 0, 0, 0.25);
}

/* 中央数字 */
.timer-text {
  position: relative;
  z-index: 2;
  font-size: 26rpx;
  font-weight: 800;
  line-height: 1;
}

/* 警告状态：数字闪烁 */
.circle-timer.warning .timer-text {
  animation: blink 0.5s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>
