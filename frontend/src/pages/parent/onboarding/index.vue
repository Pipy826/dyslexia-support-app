<template>
  <view class="page-container">
    <!-- 步骤指示器 -->
    <view class="step-dots">
      <view
        v-for="i in 3"
        :key="i"
        :class="['dot', { active: currentStep === i - 1 }]"
      ></view>
    </view>

    <!-- 步骤内容 -->
    <view class="step-content">

      <!-- 第1步：欢迎页 -->
      <view class="step-page" v-if="currentStep === 0">
        <view class="step-illustration">
          <view class="illus-circle">
            <text class="ph ph-lighthouse illus-icon"></text>
          </view>
          <view class="illus-dots">
            <view class="illus-dot" v-for="i in 5" :key="i"></view>
          </view>
        </view>
        <view class="step-title">欢迎来到悦读小灯塔！</view>
        <view class="step-desc">
          我们帮助家长了解孩子的<text class="highlight">阅读和书写学习特点</text>，通过有趣的小游戏发现孩子的学习优势和成长空间。
        </view>
        <view class="feature-list">
          <view class="feature-item">
            <view class="feature-icon blue">
              <text class="ph ph-game-controller"></text>
            </view>
            <view class="feature-text">
              <view class="feature-title">趣味小游戏</view>
              <view class="feature-desc">孩子在轻松愉快的游戏中展示能力</view>
            </view>
          </view>
          <view class="feature-item">
            <view class="feature-icon green">
              <text class="ph ph-chart-bar"></text>
            </view>
            <view class="feature-text">
              <view class="feature-title">能力成长报告</view>
              <view class="feature-desc">了解孩子在各方面的表现和进步</view>
            </view>
          </view>
          <view class="feature-item">
            <view class="feature-icon orange">
              <text class="ph ph-plant"></text>
            </view>
            <view class="feature-text">
              <view class="feature-title">个性化成长训练</view>
              <view class="feature-desc">针对性的练习帮助孩子持续进步</view>
            </view>
          </view>
        </view>
      </view>

      <!-- 第2步：功能介绍 -->
      <view class="step-page" v-if="currentStep === 1">
        <view class="step-illustration">
          <view class="illus-circle purple">
            <text class="ph ph-star illus-icon"></text>
          </view>
        </view>
        <view class="step-title">如何使用悦读小灯塔？</view>
        <view class="step-desc">只需三步，轻松了解孩子的学习特点</view>

        <view class="steps-list">
          <view class="step-item">
            <view class="step-num">1</view>
            <view class="step-info">
              <view class="step-item-title">🎮 孩子完成趣味游戏</view>
              <view class="step-item-desc">6种有趣的小游戏，每次约15分钟，孩子独立完成</view>
            </view>
          </view>
          <view class="step-connector"></view>
          <view class="step-item">
            <view class="step-num">2</view>
            <view class="step-info">
              <view class="step-item-title">📊 查看能力成长报告</view>
              <view class="step-item-desc">系统自动生成报告，AI帮你解读孩子的学习特点</view>
            </view>
          </view>
          <view class="step-connector"></view>
          <view class="step-item">
            <view class="step-num">3</view>
            <view class="step-info">
              <view class="step-item-title">🌱 开展针对性训练</view>
              <view class="step-item-desc">根据报告制定训练计划，持续跟踪孩子的成长变化</view>
            </view>
          </view>
        </view>
      </view>

      <!-- 第3步：温馨提示 -->
      <view class="step-page" v-if="currentStep === 2">
        <view class="step-illustration">
          <view class="illus-circle warm">
            <text class="ph ph-heart illus-icon"></text>
          </view>
        </view>
        <view class="step-title">温馨提示</view>
        <view class="step-desc">在开始使用前，请了解以下重要说明</view>

        <view class="notice-card">
          <view class="notice-item">
            <text class="ph ph-check-circle notice-icon green"></text>
            <view class="notice-text">本系统通过游戏化方式评估孩子的读写相关能力，帮助家长了解孩子的学习特点</view>
          </view>
          <view class="notice-divider"></view>
          <view class="notice-item">
            <text class="ph ph-info notice-icon blue"></text>
            <view class="notice-text">评估结果<text class="bold">仅供家庭参考</text>，不代表医学诊断，不能替代专业医疗评估</view>
          </view>
          <view class="notice-divider"></view>
          <view class="notice-item">
            <text class="ph ph-hospital notice-icon orange"></text>
            <view class="notice-text">如对孩子的读写能力有疑虑，建议咨询<text class="bold">专业医疗机构或教育专家</text>进行正式评估</view>
          </view>
          <view class="notice-divider"></view>
          <view class="notice-item">
            <text class="ph ph-shield-check notice-icon purple"></text>
            <view class="notice-text">我们重视孩子的隐私保护，所有数据仅用于生成个人报告，不会对外共享</view>
          </view>
        </view>
      </view>

    </view>

    <!-- 底部按钮 -->
    <view class="bottom-bar">
      <button
        v-if="currentStep < 2"
        class="next-btn"
        @click="nextStep"
      >
        下一步
        <text class="ph ph-arrow-right"></text>
      </button>
      <button
        v-else
        class="start-btn"
        @click="finishOnboarding"
      >
        我明白了，开始使用 🚀
      </button>
      <view class="skip-link" v-if="currentStep < 2" @click="finishOnboarding">跳过</view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      currentStep: 0,
    }
  },
  methods: {
    nextStep() {
      if (this.currentStep < 2) {
        this.currentStep++
      }
    },
    finishOnboarding() {
      // 写入本地存储，后续不再显示引导流程（幂等性保证）
      uni.setStorageSync('onboarding_completed', true)
      uni.reLaunch({ url: '/pages/parent/home/index' })
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
  padding: 56rpx 0 0;
  overflow-x: hidden;
}

/* 步骤指示器 */
.step-dots {
  display: flex;
  justify-content: center;
  gap: 12rpx;
  padding: 24rpx 0 0;
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
  background: #3B82F6;
}

/* 步骤内容 */
.step-content {
  flex: 1;
  padding: 32rpx 48rpx;
  overflow-y: auto;
}

.step-page {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* 插画区 */
.step-illustration {
  position: relative;
  margin-bottom: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.illus-circle {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(59, 130, 246, 0.15);
}

.illus-circle.purple {
  background: linear-gradient(135deg, #F5F3FF, #EDE9FE);
  box-shadow: 0 8rpx 32rpx rgba(124, 58, 237, 0.15);
}

.illus-circle.warm {
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  box-shadow: 0 8rpx 32rpx rgba(239, 68, 68, 0.15);
}

.illus-icon {
  font-size: 72rpx;
  color: #3B82F6;
}

.illus-circle.purple .illus-icon {
  color: #7C3AED;
}

.illus-circle.warm .illus-icon {
  color: #EF4444;
}

.illus-dots {
  position: absolute;
  top: 0;
  right: -20rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.illus-dot {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #BFDBFE;
}

/* 标题和描述 */
.step-title {
  font-size: 40rpx;
  font-weight: 800;
  color: #1F2937;
  text-align: center;
  margin-bottom: 16rpx;
}

.step-desc {
  font-size: 28rpx;
  color: #6B7280;
  text-align: center;
  line-height: 1.7;
  margin-bottom: 40rpx;
}

.highlight {
  color: #3B82F6;
  font-weight: 700;
}

/* 功能列表（第1步） */
.feature-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 24rpx;
  background: #F9FAFB;
  border-radius: 20rpx;
  padding: 24rpx;
}

.feature-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon.blue {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
}

.feature-icon.blue .ph {
  color: #3B82F6;
}

.feature-icon.green {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
}

.feature-icon.green .ph {
  color: #22C55E;
}

.feature-icon.orange {
  background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
}

.feature-icon.orange .ph {
  color: #F97316;
}

.feature-icon .ph {
  font-size: 36rpx;
}

.feature-text {
  flex: 1;
}

.feature-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 4rpx;
}

.feature-desc {
  font-size: 22rpx;
  color: #9CA3AF;
  font-weight: 500;
}

/* 步骤列表（第2步） */
.steps-list {
  width: 100%;
}

.step-item {
  display: flex;
  align-items: flex-start;
  gap: 20rpx;
}

.step-num {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: #FFFFFF;
  font-size: 24rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.3);
}

.step-info {
  flex: 1;
  padding-top: 8rpx;
}

.step-item-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 6rpx;
}

.step-item-desc {
  font-size: 22rpx;
  color: #9CA3AF;
  line-height: 1.6;
  font-weight: 500;
}

.step-connector {
  width: 2rpx;
  height: 32rpx;
  background: #E5E7EB;
  margin-left: 23rpx;
  margin-top: 4rpx;
  margin-bottom: 4rpx;
}

/* 提示卡片（第3步） */
.notice-card {
  width: 100%;
  background: #F9FAFB;
  border-radius: 24rpx;
  padding: 8rpx 0;
  border: 2rpx solid #F3F4F6;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
  padding: 24rpx 28rpx;
}

.notice-icon {
  font-size: 36rpx;
  flex-shrink: 0;
  margin-top: 2rpx;
}

.notice-icon.green { color: #22C55E; }
.notice-icon.blue { color: #3B82F6; }
.notice-icon.orange { color: #F97316; }
.notice-icon.purple { color: #7C3AED; }

.notice-text {
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.7;
  font-weight: 500;
}

.bold {
  font-weight: 700;
  color: #374151;
}

.notice-divider {
  height: 1rpx;
  background: #F3F4F6;
  margin: 0 28rpx;
}

/* 底部按钮 */
.bottom-bar {
  padding: 24rpx 48rpx calc(48rpx + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
}

.next-btn {
  width: 100%;
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

.next-btn .ph {
  font-size: 28rpx;
}

.start-btn {
  width: 100%;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  font-size: 30rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(34, 197, 94, 0.3);
}

.skip-link {
  font-size: 24rpx;
  color: #9CA3AF;
  font-weight: 500;
}
</style>
