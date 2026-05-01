<template>
  <view class="ability-map">
    <view
      v-for="item in abilityItems"
      :key="item.gameType"
      class="ability-row"
    >
      <view class="ability-row-left">
        <view class="ability-icon" :style="{ color: item.color }">
          <text :class="'ph ' + item.icon"></text>
        </view>
        <view class="ability-name">{{ item.name }}</view>
      </view>
      <view class="stars-row">
        <view
          v-for="n in 5"
          :key="n"
          :class="['star', n <= item.stars ? 'filled' : 'empty']"
          :style="n <= item.stars ? { color: item.color } : {}"
        >
          <text :class="n <= item.stars ? 'ph-fill ph-star' : 'ph ph-star'"></text>
        </view>
      </view>
    </view>
    <view class="map-empty" v-if="abilityItems.length === 0">
      <text class="ph ph-map-trifold"></text>
      <text>完成游戏后查看能力地图</text>
    </view>
  </view>
</template>

<script>
import { scoreToStars, getGameTypeName } from '../../utils/abilityLabels.js'

const GAME_ICONS = {
  visual: { icon: 'ph-eye', color: '#4F9EF8' },
  spelling: { icon: 'ph-text-aa', color: '#A78BFA' },
  comprehension: { icon: 'ph-book-open', color: '#22C55E' },
  working_memory: { icon: 'ph-brain', color: '#F97316' },
  rapid_naming: { icon: 'ph-lightning', color: '#EAB308' },
  motor_coordination: { icon: 'ph-hand', color: '#EC4899' },
}

export default {
  name: 'AbilityMap',
  props: {
    /**
     * 各游戏类型分数对象，格式：{ visual: 80, spelling: 65, ... }
     */
    dimensions: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    abilityItems() {
      const order = ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']
      return order
        .filter(type => this.dimensions[type] !== undefined)
        .map(type => ({
          gameType: type,
          name: getGameTypeName(type),
          score: this.dimensions[type],
          stars: scoreToStars(this.dimensions[type]),
          ...GAME_ICONS[type],
        }))
    },
  },
}
</script>

<style scoped>
.ability-map {
  width: 100%;
}

.ability-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
}

.ability-row:last-child {
  border-bottom: none;
}

.ability-row-left {
  display: flex;
  align-items: center;
  gap: 12rpx;
  flex: 1;
}

.ability-icon {
  width: 44rpx;
  height: 44rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ability-icon .ph {
  font-size: 28rpx;
}

.ability-name {
  font-size: 24rpx;
  font-weight: 600;
  color: #4A5568;
}

.stars-row {
  display: flex;
  gap: 4rpx;
}

.star .ph {
  font-size: 28rpx;
}

.star.filled .ph {
  /* color 由 :style 注入 */
}

.star.empty .ph {
  color: #E5E7EB;
}

/* 空状态 */
.map-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  padding: 32rpx 0;
  color: #CBD5E0;
  font-size: 24rpx;
  font-weight: 500;
}

.map-empty .ph {
  font-size: 48rpx;
}
</style>
