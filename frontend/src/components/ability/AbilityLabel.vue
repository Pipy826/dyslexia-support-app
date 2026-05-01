<template>
  <view class="ability-label-wrap" :style="{ background: bgGradient }">
    <view class="ability-emoji">{{ labelInfo.emoji }}</view>
    <view class="ability-content">
      <view class="ability-name">{{ labelInfo.label }}</view>
      <view class="ability-desc">{{ labelInfo.desc }}</view>
    </view>
  </view>
</template>

<script>
import { getAbilityLabel } from '../../utils/abilityLabels.js'

export default {
  name: 'AbilityLabel',
  props: {
    gameType: {
      type: String,
      required: true,
    },
    score: {
      type: Number,
      default: 0,
    },
  },
  computed: {
    labelInfo() {
      return getAbilityLabel(this.gameType, this.score) || {
        label: '小小探险家',
        emoji: '🌟',
        desc: '你完成了挑战，真棒！',
      }
    },
    bgGradient() {
      const theme = getGameTheme(this.gameType)
      // 使用游戏主题色的浅色渐变背景
      const colorMap = {
        visual: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
        spelling: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
        comprehension: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
        working_memory: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)',
        rapid_naming: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)',
        motor_coordination: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)',
      }
      return colorMap[this.gameType] || 'linear-gradient(135deg, #F5F7FA, #EFF6FF)'
    },
  },
}
</script>

<style scoped>
.ability-label-wrap {
  display: flex;
  align-items: center;
  gap: 16rpx;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
}

.ability-emoji {
  font-size: 48rpx;
  flex-shrink: 0;
}

.ability-content {
  flex: 1;
}

.ability-name {
  font-size: 28rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 4rpx;
}

.ability-desc {
  font-size: 22rpx;
  color: #718096;
  font-weight: 500;
  line-height: 1.5;
}
</style>
