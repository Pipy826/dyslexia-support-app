<template>
  <view class="page-container">
    <!-- 步骤指示器 -->
    <view class="step-dots">
      <view
        v-for="i in totalSteps"
        :key="i"
        :class="['dot', { active: currentStep === i - 1, passed: currentStep > i - 1 }]"
      ></view>
    </view>

    <!-- 跳过按钮 -->
    <view class="skip-btn" @click="finish" v-if="currentStep < totalSteps - 1">跳过</view>

    <!-- 引导内容 -->
    <view class="slide-wrap">
      <view
        v-for="(slide, i) in slides"
        :key="i"
        :class="['slide', { active: currentStep === i }]"
      >
        <view class="slide-illustration">
          <view class="illus-bg" :style="{ background: slide.bgColor }"></view>
          <text :class="['ph', slide.icon, 'illus-icon']" :style="{ color: slide.iconColor }"></text>
        </view>
        <view class="slide-title">{{ slide.title }}</view>
        <view class="slide-desc">{{ slide.desc }}</view>
        <view class="slide-tags" v-if="slide.tags">
          <view class="tag" v-for="tag in slide.tags" :key="tag">{{ tag }}</view>
        </view>
      </view>
    </view>

    <!-- 底部操作区 -->
    <view class="bottom-area">
      <!-- 最后一步：隐私协议确认 -->
      <view class="privacy-section" v-if="currentStep === totalSteps - 1">
        <view class="privacy-box">
          <view class="privacy-header">
            <text class="ph ph-shield-check privacy-icon"></text>
            <view class="privacy-title">隐私与数据说明</view>
          </view>
          <view class="privacy-items">
            <view class="privacy-item">
              <text class="ph ph-check-circle item-check"></text>
              <view class="item-text">儿童行为数据仅用于本产品内的能力评估，不对外共享</view>
            </view>
            <view class="privacy-item">
              <text class="ph ph-check-circle item-check"></text>
              <view class="item-text">本产品不是医疗诊断工具，结果仅供家庭参考</view>
            </view>
            <view class="privacy-item">
              <text class="ph ph-check-circle item-check"></text>
              <view class="item-text">您可随时删除账号及所有相关数据</view>
            </view>
          </view>
        </view>
        <view class="agree-row" @click="agreed = !agreed">
          <view :class="['agree-check', { checked: agreed }]">
            <text class="ph ph-check" v-if="agreed"></text>
          </view>
          <view class="agree-text">
            我已阅读并同意 <text class="link">《用户服务协议》</text> 和 <text class="link">《隐私政策》</text>
          </view>
        </view>
      </view>

      <!-- 下一步 / 开始使用 按钮 -->
      <button
        class="next-btn"
        :class="{ disabled: currentStep === totalSteps - 1 && !agreed }"
        @click="handleNext"
        :disabled="currentStep === totalSteps - 1 && !agreed"
      >
        {{ currentStep < totalSteps - 1 ? '下一步' : '开始使用' }}
        <text class="ph ph-arrow-right btn-arrow" v-if="currentStep < totalSteps - 1"></text>
      </button>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentStep: 0,
      agreed: false,
      slides: [
        {
          icon: 'ph-magnifying-glass',
          iconColor: '#4F9EF8',
          bgColor: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
          title: '早发现，不焦虑',
          desc: '通过游戏化互动，在家就能完成儿童读写能力初步筛查，帮助家长更早了解孩子的能力特点。',
          tags: ['游戏化筛查', '10分钟完成', '无需专业知识'],
        },
        {
          icon: 'ph-chart-bar',
          iconColor: '#22C55E',
          bgColor: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
          title: '可解释，看得懂',
          desc: '系统将复杂的行为数据转化为清晰的能力画像，AI 助手用通俗语言帮您理解每一项结果。',
          tags: ['能力雷达图', 'AI 解读报告', '通俗易懂'],
        },
        {
          icon: 'ph-target',
          iconColor: '#F57F17',
          bgColor: 'linear-gradient(135deg, #FFF9C4, #FFE082)',
          title: '可干预，有方向',
          desc: '根据筛查结果，系统自动推荐个性化家庭训练方案，每天15分钟，在家就能持续改善。',
          tags: ['个性化训练', '每日任务', '家长陪伴'],
        },
        {
          icon: 'ph-trend-up',
          iconColor: '#A78BFA',
          bgColor: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
          title: '可追踪，看变化',
          desc: '持续记录每次筛查与训练数据，形成成长趋势图，让您清晰看到孩子的每一点进步。',
          tags: ['成长趋势图', '阶段复评', '长期陪伴'],
        },
        {
          icon: 'ph-shield-check',
          iconColor: '#22C55E',
          bgColor: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
          title: '开始之前',
          desc: '请确认以下隐私说明，我们承诺保护您和孩子的数据安全。',
          tags: null,
        },
      ],
    }
  },
  computed: {
    totalSteps() {
      return this.slides.length
    },
  },
  methods: {
    handleNext() {
      if (this.currentStep < this.totalSteps - 1) {
        this.currentStep++
      } else {
        this.finish()
      }
    },
    finish() {
      // 标记已完成引导
      uni.setStorageSync('onboarding_done', true)
      uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  display: flex;
  flex-direction: column;
  padding: 80rpx 48rpx 60rpx;
  position: relative;
  overflow-x: hidden;
}

/* 步骤点 */
.step-dots {
  display: flex;
  gap: 12rpx;
  margin-bottom: 16rpx;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #E5E7EB;
  transition: all 0.3s;
}

.dot.active {
  width: 32rpx;
  border-radius: 6rpx;
  background: #4F9EF8;
}

.dot.passed {
  background: #BFDBFE;
}

/* 跳过 */
.skip-btn {
  position: absolute;
  top: 80rpx;
  right: 48rpx;
  font-size: 26rpx;
  color: #A0AEC0;
  font-weight: 600;
}

/* 幻灯片 */
.slide-wrap {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.slide {
  display: none;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.slide.active {
  display: flex;
  animation: slideIn 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(40rpx); }
  to { opacity: 1; transform: translateX(0); }
}

/* 插图 */
.slide-illustration {
  width: 280rpx;
  height: 280rpx;
  border-radius: 56rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 56rpx;
  overflow: hidden;
}

.illus-bg {
  position: absolute;
  inset: 0;
  border-radius: 56rpx;
}

.illus-icon {
  font-size: 120rpx;
  position: relative;
  z-index: 1;
}

.slide-title {
  font-size: 44rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 24rpx;
  text-align: center;
}

.slide-desc {
  font-size: 28rpx;
  color: #718096;
  line-height: 1.8;
  text-align: center;
  margin-bottom: 32rpx;
  font-weight: 500;
}

.slide-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: center;
}

.tag {
  background: #F5F7FA;
  color: #718096;
  font-size: 22rpx;
  font-weight: 600;
  padding: 10rpx 24rpx;
  border-radius: 20rpx;
}

/* 底部 */
.bottom-area {
  padding-top: 24rpx;
}

/* 隐私说明 */
.privacy-box {
  background: #F8FAFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  border: 1rpx solid #E5E7EB;
}

.privacy-header {
  display: flex;
  align-items: center;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.privacy-icon {
  font-size: 32rpx;
  color: #22C55E;
}

.privacy-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
}

.privacy-items {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.privacy-item {
  display: flex;
  align-items: flex-start;
  gap: 12rpx;
}

.item-check {
  font-size: 26rpx;
  color: #22C55E;
  flex-shrink: 0;
  margin-top: 2rpx;
}

.item-text {
  font-size: 24rpx;
  color: #718096;
  line-height: 1.6;
  font-weight: 500;
}

/* 协议勾选 */
.agree-row {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.agree-check {
  width: 36rpx;
  height: 36rpx;
  border-radius: 10rpx;
  border: 2rpx solid #D1D5DB;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2rpx;
  transition: all 0.2s;
}

.agree-check.checked {
  background: #4F9EF8;
  border-color: #4F9EF8;
}

.agree-check .ph {
  font-size: 20rpx;
  color: #FFFFFF;
}

.agree-text {
  font-size: 24rpx;
  color: #718096;
  line-height: 1.6;
}

.agree-text .link {
  color: #4F9EF8;
}

/* 下一步按钮 */
.next-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  font-size: 32rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  box-shadow: 0 6rpx 20rpx rgba(59, 130, 246, 0.3);
  transition: all 0.2s;
}

.next-btn:active {
  transform: scale(0.97);
}

.next-btn.disabled {
  background: #E5E7EB;
  color: #A0AEC0;
  box-shadow: none;
}

.btn-arrow {
  font-size: 30rpx;
}
</style>
