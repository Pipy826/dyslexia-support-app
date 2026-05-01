<template>
  <view :class="['mascot-container', state]">
    <view :class="['mascot-emoji', { bounce: isAnimating }]">
      {{ currentEmoji }}
    </view>
    <view class="mascot-bubble" v-if="message && showBubble">
      <text>{{ message }}</text>
    </view>
  </view>
</template>

<script>
import { MASCOT_EMOJIS, getRandomMessage } from '../../utils/mascot.js'

export default {
  name: 'Mascot',
  props: {
    state: {
      type: String,
      default: 'idle',
      validator: (v) => ['idle', 'excited', 'thinking', 'encouraging', 'celebrating'].includes(v),
    },
    showBubble: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      message: '',
      isAnimating: false,
    }
  },
  computed: {
    currentEmoji() {
      return MASCOT_EMOJIS[this.state] || MASCOT_EMOJIS.idle
    },
  },
  watch: {
    state(newState, oldState) {
      if (newState !== oldState) {
        this.triggerAnimation(newState)
      }
    },
  },
  mounted() {
    this.triggerAnimation(this.state)
  },
  methods: {
    triggerAnimation(state) {
      this.isAnimating = true
      // 根据状态设置话语
      const msgMap = {
        excited: 'correct',
        encouraging: 'wrong',
        celebrating: 'end',
        thinking: 'thinking',
        idle: 'start',
      }
      this.message = getRandomMessage(msgMap[state] || 'start')
      setTimeout(() => {
        this.isAnimating = false
      }, 600)
    },
  },
}
</script>

<style scoped>
.mascot-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
  position: relative;
}

.mascot-emoji {
  font-size: 64rpx;
  line-height: 1;
  transition: transform 0.2s;
}

.mascot-emoji.bounce {
  animation: mascotBounce 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes mascotBounce {
  0% { transform: scale(0.7) rotate(-10deg); }
  50% { transform: scale(1.2) rotate(5deg); }
  100% { transform: scale(1) rotate(0deg); }
}

/* 状态特效 */
.mascot-container.excited .mascot-emoji {
  filter: drop-shadow(0 0 8rpx rgba(255, 213, 79, 0.6));
}

.mascot-container.celebrating .mascot-emoji {
  animation: celebrate 0.8s cubic-bezier(0.34, 1.56, 0.64, 1) infinite alternate;
}

@keyframes celebrate {
  0% { transform: scale(1) rotate(-5deg); }
  100% { transform: scale(1.1) rotate(5deg); }
}

/* 气泡 */
.mascot-bubble {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16rpx;
  padding: 8rpx 16rpx;
  font-size: 20rpx;
  font-weight: 700;
  color: #2D3748;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
  white-space: nowrap;
  animation: bubbleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  max-width: 200rpx;
  text-align: center;
}

@keyframes bubbleIn {
  0% { transform: scale(0.8); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
</style>
