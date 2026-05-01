<template>
  <view :class="['attention-badge', levelClass]">
    <text class="ph ph-heart badge-icon"></text>
    <text class="badge-text">{{ levelText }}</text>
  </view>
</template>

<script>
import { friendlyRiskLevel, attentionLevelClass } from '../../utils/terminology.js'

export default {
  name: 'AttentionBadge',
  props: {
    level: {
      type: String,
      required: true,
      validator: (value) => ['high', 'medium', 'low'].includes(value)
    }
  },
  computed: {
    levelText() {
      return friendlyRiskLevel(this.level)
    },
    levelClass() {
      return attentionLevelClass(this.level)
    }
  }
}
</script>

<style scoped>
.attention-badge {
  display: inline-flex;
  align-items: center;
  gap: 6rpx;
  padding: 6rpx 20rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  font-weight: 700;
  border: 2rpx solid;
}

.badge-icon {
  font-size: 20rpx;
}

/* 温暖色调，非警告色调 */
.attention-badge.attention-high {
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  color: #EF4444;
  border-color: #FECACA;
}

.attention-badge.attention-medium {
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  color: #D97706;
  border-color: #FDE68A;
}

.attention-badge.attention-low {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  color: #22C55E;
  border-color: #86EFAC;
}
</style>
