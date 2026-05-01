<template>
  <view class="image-choice">
    <view class="image-grid">
      <view
        v-for="(option, index) in options"
        :key="index"
        :class="['image-item', getItemClass(index)]"
        @click="handleClick(index)"
      >
        <image
          :src="option.src"
          class="choice-image"
          mode="aspectFill"
        />
        <view class="choice-label">{{ option.label }}</view>
        <!-- 答题后状态图标 -->
        <view class="status-icon" v-if="answered">
          <text v-if="isCorrectOption(index)" class="ph-fill ph-check-circle correct-icon"></text>
          <text v-else-if="index === selectedIndex" class="ph-fill ph-x-circle wrong-icon"></text>
        </view>
      </view>
    </view>

    <!-- 放大预览弹窗 -->
    <view class="preview-overlay" v-if="previewSrc" @click="closePreview">
      <view class="preview-container" @click.stop>
        <image :src="previewSrc" class="preview-image" mode="aspectFit" />
        <button class="preview-close" @click="closePreview">
          <text class="ph ph-x"></text>
        </button>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'ImageChoice',
  props: {
    options: {
      type: Array,
      required: true,
      validator: (val) => val.every(o => 'src' in o && 'label' in o && 'value' in o),
    },
    correctValue: {
      default: null,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['select'],
  data() {
    return {
      selectedIndex: null,
      answered: false,
      previewSrc: null,
    }
  },
  watch: {
    // 当 disabled 变为 true 时，标记为已答题状态
    disabled(val) {
      if (val) this.answered = true
    },
  },
  methods: {
    handleClick(index) {
      if (this.disabled || this.answered) {
        // 已选中的图片再次点击 → 放大预览
        if (index === this.selectedIndex) {
          this.previewSrc = this.options[index].src
        }
        return
      }

      if (this.selectedIndex === index) {
        // 点击已选中的图片 → 放大预览
        this.previewSrc = this.options[index].src
        return
      }

      this.selectedIndex = index
      this.$emit('select', this.options[index].value)
    },

    getItemClass(index) {
      if (this.answered) {
        if (this.isCorrectOption(index)) return 'correct'
        if (index === this.selectedIndex) return 'wrong'
        return ''
      }
      return this.selectedIndex === index ? 'selected' : ''
    },

    isCorrectOption(index) {
      return this.correctValue !== null &&
        this.correctValue !== undefined &&
        this.options[index].value === this.correctValue
    },

    closePreview() {
      this.previewSrc = null
    },

    // 外部重置（换题时调用）
    reset() {
      this.selectedIndex = null
      this.answered = false
      this.previewSrc = null
    },
  },
}
</script>

<style scoped>
.image-choice {
  width: 100%;
}

/* 2列网格 */
.image-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  width: 100%;
}

.image-item {
  width: calc(50% - 10rpx);
  border-radius: 24rpx;
  border: 5rpx solid #E5E7EB;
  overflow: hidden;
  background: #FFFFFF;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.06);
  transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  box-sizing: border-box;
}

.image-item:active {
  transform: scale(0.96);
}

.image-item.selected {
  border-color: #4F9EF8;
  box-shadow: 0 0 0 4rpx rgba(79, 158, 248, 0.25), 0 4rpx 16rpx rgba(79, 158, 248, 0.2);
}

.image-item.correct {
  border-color: #22C55E;
  box-shadow: 0 0 0 4rpx rgba(34, 197, 94, 0.25), 0 4rpx 16rpx rgba(34, 197, 94, 0.2);
}

.image-item.wrong {
  border-color: #FF6B6B;
  box-shadow: 0 0 0 4rpx rgba(255, 107, 107, 0.25), 0 4rpx 16rpx rgba(255, 107, 107, 0.2);
}

.choice-image {
  width: 100%;
  height: 220rpx;
  display: block;
}

.choice-label {
  padding: 16rpx 20rpx;
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  text-align: center;
  background: #FAFAFA;
}

.image-item.selected .choice-label {
  color: #4F9EF8;
  background: #EFF6FF;
}

.image-item.correct .choice-label {
  color: #22C55E;
  background: #F0FDF4;
}

.image-item.wrong .choice-label {
  color: #FF6B6B;
  background: #FFF5F5;
}

/* 状态图标（答题后） */
.status-icon {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  width: 52rpx;
  height: 52rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}

.correct-icon {
  font-size: 44rpx;
  color: #22C55E;
}

.wrong-icon {
  font-size: 44rpx;
  color: #FF6B6B;
}

/* 放大预览 */
.preview-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  z-index: 9000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-container {
  position: relative;
  width: 90%;
  max-width: 700rpx;
}

.preview-image {
  width: 100%;
  height: 600rpx;
  border-radius: 24rpx;
}

.preview-close {
  position: absolute;
  top: -24rpx;
  right: -24rpx;
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.2);
}

.preview-close .ph {
  font-size: 36rpx;
  color: #2D3748;
}
</style>
