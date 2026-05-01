<template>
  <view class="drag-sort">
    <view class="sort-list">
      <view
        v-for="(item, idx) in currentItems"
        :key="item.id"
        class="sort-item"
      >
        <view class="sort-num">{{ idx + 1 }}</view>
        <view class="sort-content">{{ item.content }}</view>
        <view class="sort-btns" v-if="!disabled">
          <view
            :class="['sort-btn', { disabled: idx === 0 }]"
            @click="moveUp(idx)"
          >
            <text class="ph ph-caret-up"></text>
          </view>
          <view
            :class="['sort-btn', { disabled: idx === currentItems.length - 1 }]"
            @click="moveDown(idx)"
          >
            <text class="ph ph-caret-down"></text>
          </view>
        </view>
      </view>
    </view>

    <button
      v-if="!disabled"
      class="confirm-btn"
      @click="handleConfirm"
    >
      确认顺序 ✓
    </button>
  </view>
</template>

<script>
export default {
  name: 'DragSort',
  props: {
    items: {
      type: Array,
      required: true,
      validator: (val) => val.every(o => 'id' in o && 'content' in o),
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['change', 'confirm'],
  data() {
    return {
      currentItems: [],
    }
  },
  watch: {
    items: {
      immediate: true,
      handler(val) {
        // 初始化时随机打乱顺序
        const arr = [...val]
        for (let i = arr.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [arr[i], arr[j]] = [arr[j], arr[i]]
        }
        this.currentItems = arr
      },
    },
  },
  methods: {
    moveUp(index) {
      if (index === 0 || this.disabled) return
      const arr = [...this.currentItems];
      [arr[index - 1], arr[index]] = [arr[index], arr[index - 1]]
      this.currentItems = arr
      this.$emit('change', this.currentItems.map(item => item.id))
    },

    moveDown(index) {
      if (index === this.currentItems.length - 1 || this.disabled) return
      const arr = [...this.currentItems];
      [arr[index], arr[index + 1]] = [arr[index + 1], arr[index]]
      this.currentItems = arr
      this.$emit('change', this.currentItems.map(item => item.id))
    },

    handleConfirm() {
      if (this.disabled) return
      this.$emit('confirm', this.currentItems.map(item => item.id))
    },

    // 外部重置（换题时调用）
    reset() {
      const arr = [...this.items]
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]]
      }
      this.currentItems = arr
    },

    // 获取当前排列顺序（id数组）
    getCurrentOrder() {
      return this.currentItems.map(item => item.id)
    },
  },
}
</script>

<style scoped>
.drag-sort {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.sort-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  width: 100%;
}

.sort-item {
  background: #FFFFFF;
  border: 3rpx solid #E5E7EB;
  border-radius: 20rpx;
  padding: 24rpx 20rpx;
  display: flex;
  align-items: center;
  gap: 16rpx;
  transition: all 0.2s;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.sort-num {
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26rpx;
  font-weight: 800;
  color: #4F9EF8;
  flex-shrink: 0;
}

.sort-content {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
  line-height: 1.5;
}

.sort-btns {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
  flex-shrink: 0;
}

.sort-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F5F7FA;
  border: 2rpx solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.sort-btn .ph {
  font-size: 28rpx;
  color: #4F9EF8;
}

.sort-btn:active {
  background: #DBEAFE;
  transform: scale(0.92);
}

.sort-btn.disabled {
  opacity: 0.35;
  pointer-events: none;
}

.sort-btn.disabled .ph {
  color: #D1D5DB;
}

.confirm-btn {
  width: 100%;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 20rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 800;
  margin-top: 8rpx;
  box-shadow: 0 4rpx 12rpx rgba(34, 197, 94, 0.3);
  border: none;
  letter-spacing: 1rpx;
}

.confirm-btn:active {
  transform: translateY(3rpx);
  box-shadow: 0 1rpx 4rpx rgba(34, 197, 94, 0.2);
}
</style>
