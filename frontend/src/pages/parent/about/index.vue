<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">关于系统</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- Logo 区域 -->
      <view class="logo-section">
        <view class="app-logo">
          <text class="ph ph-book-open"></text>
        </view>
        <view class="app-name">悦读小灯塔</view>
        <view class="app-slogan">儿童读写障碍智能筛查与干预系统</view>
        <view class="app-version">版本 v1.0.0</view>
      </view>

      <!-- 系统介绍 -->
      <view class="section-title">系统介绍</view>
      <view class="info-card">
        <view class="info-text">
          悦读小灯塔是一款专注于儿童读写障碍早期筛查与干预的智能系统。通过游戏化的评估方式和科学的训练方案，帮助家长及时发现孩子的读写困难，并提供针对性的支持与指导。
        </view>
      </view>

      <!-- 核心功能 -->
      <view class="section-title">核心功能</view>
      <view class="feature-list">
        <view class="feature-item">
          <view class="feature-icon blue">
            <text class="ph ph-game-controller"></text>
          </view>
          <view class="feature-info">
            <view class="feature-label">游戏化筛查</view>
            <view class="feature-desc">9大维度能力评估，轻松完成</view>
          </view>
        </view>
        <view class="feature-item">
          <view class="feature-icon green">
            <text class="ph ph-chart-line"></text>
          </view>
          <view class="feature-info">
            <view class="feature-label">智能报告</view>
            <view class="feature-desc">可视化能力图谱，一目了然</view>
          </view>
        </view>
        <view class="feature-item">
          <view class="feature-icon orange">
            <text class="ph ph-barbell"></text>
          </view>
          <view class="feature-info">
            <view class="feature-label">针对性训练</view>
            <view class="feature-desc">个性化训练方案，科学有效</view>
          </view>
        </view>
        <view class="feature-item">
          <view class="feature-icon purple">
            <text class="ph ph-robot"></text>
          </view>
          <view class="feature-info">
            <view class="feature-label">AI 智能问答</view>
            <view class="feature-desc">专业知识随时咨询，贴心陪伴</view>
          </view>
        </view>
      </view>

      <!-- 团队信息 -->
      <view class="section-title">开发团队</view>
      <view class="info-card">
        <view class="info-text">
          本系统由专业的教育科技团队开发，结合儿童心理学、特殊教育学和人工智能技术，致力于为有读写困难的儿童提供科学、有效的支持。
        </view>
      </view>

      <!-- 联系方式 -->
      <view class="section-title">联系我们</view>
      <view class="contact-list">
        <view class="contact-row">
          <view class="contact-label">
            <text class="ph ph-envelope"></text>
            邮箱
          </view>
          <view class="contact-value">support@dyslexia-app.com</view>
        </view>
        <view class="contact-row">
          <view class="contact-label">
            <text class="ph ph-globe"></text>
            官网
          </view>
          <view class="contact-value">www.dyslexia-app.com</view>
        </view>
      </view>

      <!-- 法律信息 -->
      <view class="legal-links">
        <view class="legal-link" @click="goToPrivacy">隐私政策</view>
        <view class="legal-divider">|</view>
        <view class="legal-link" @click="goToTerms">用户协议</view>
      </view>

      <!-- 版权信息 -->
      <view class="copyright">
      © 2026 悦读小灯塔 All Rights Reserved
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  methods: {
    goBack() {
      uni.navigateBack()
    },
    goToPrivacy() {
      uni.navigateTo({ url: '/pages/parent/legal/privacy' })
    },
    goToTerms() {
      uni.navigateTo({ url: '/pages/parent/legal/terms' })
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  overflow-x: hidden;
}

.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.back-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.back-btn .ph {
  font-size: 28rpx;
  color: #718096;
}

.header-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
}

.page-content {
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
}

/* Logo 区域 */
.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40rpx 0 32rpx;
}

.app-logo {
  width: 120rpx;
  height: 120rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

.app-logo .ph {
  font-size: 64rpx;
  color: #FFFFFF;
}

.app-name {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
}

.app-slogan {
  font-size: 22rpx;
  color: #718096;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 12rpx;
}

.app-version {
  font-size: 20rpx;
  color: #A0AEC0;
  background: #F5F5F5;
  padding: 6rpx 20rpx;
  border-radius: 12rpx;
  font-weight: 600;
}

/* 区域标题 */
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
}

/* 信息卡片 */
.info-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.info-text {
  font-size: 26rpx;
  color: #718096;
  line-height: 1.8;
  font-weight: 500;
}

/* 功能列表 */
.feature-list {
  background: #FFFFFF;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx 28rpx;
  border-bottom: 1rpx solid #F5F5F5;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-icon .ph {
  font-size: 26rpx;
}

.feature-icon.blue {
  background: rgba(79, 158, 248, 0.1);
}

.feature-icon.blue .ph {
  color: #4F9EF8;
}

.feature-icon.green {
  background: rgba(34, 197, 94, 0.1);
}

.feature-icon.green .ph {
  color: #22C55E;
}

.feature-icon.orange {
  background: rgba(245, 127, 23, 0.1);
}

.feature-icon.orange .ph {
  color: #F57F17;
}

.feature-icon.purple {
  background: rgba(167, 139, 250, 0.1);
}

.feature-icon.purple .ph {
  color: #A78BFA;
}

.feature-info {
  flex: 1;
}

.feature-label {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.feature-desc {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 2rpx;
  font-weight: 500;
}

/* 联系方式 */
.contact-list {
  background: #FFFFFF;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.contact-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 28rpx;
  border-bottom: 1rpx solid #F5F5F5;
}

.contact-row:last-child {
  border-bottom: none;
}

.contact-label {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #718096;
}

.contact-label .ph {
  font-size: 24rpx;
  color: #4F9EF8;
}

.contact-value {
  font-size: 24rpx;
  color: #2D3748;
  font-weight: 600;
}

/* 法律链接 */
.legal-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.legal-link {
  font-size: 22rpx;
  color: #4F9EF8;
  font-weight: 600;
}

.legal-divider {
  font-size: 22rpx;
  color: #D1D5DB;
}

/* 版权信息 */
.copyright {
  text-align: center;
  font-size: 20rpx;
  color: #A0AEC0;
  padding: 16rpx 0;
}
</style>
