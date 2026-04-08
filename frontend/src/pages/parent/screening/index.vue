<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">能力筛查</view>
      <view class="header-action">
        <text class="ph ph-question"></text>
      </view>
    </view>

    <view class="page-content">
      <!-- 筛查对象信息区 -->
      <view class="child-info-card">
        <view class="child-avatar">
          <text class="ph ph-user"></text>
        </view>
        <view class="child-details">
          <view class="child-label">当前评测对象</view>
          <view class="child-name">小明 <text class="child-meta">一年级 / 7岁</text></view>
        </view>
        <view class="switch-btn">切换</view>
      </view>

      <!-- 发起筛查动作区 -->
      <view class="section-title">开始新筛查</view>
      <view class="screening-card">
        <view class="screening-header">
          <view class="screening-icon blue">
            <text class="ph ph-game-controller"></text>
          </view>
          <view class="screening-info">
            <view class="screening-name">综合读写能力初筛</view>
            <view class="screening-desc">通过拼写、视觉辨识、阅读理解等互动游戏，全面评估孩子的基础能力状态。</view>
          </view>
        </view>

        <!-- 家长须知 -->
        <view class="notice-box">
          <view class="notice-title">
            <text class="ph ph-warning"></text> 家长准备须知
          </view>
          <ul class="notice-list">
            <li>耗时约 10-15 分钟，请确保时间充足。</li>
            <li>找一个安静、无打扰的环境。</li>
            <li class="highlight">评测过程中请让孩子独立完成，家长切勿提示答案。</li>
          </ul>
        </view>

        <!-- 发起按钮 -->
        <button class="start-btn" @click="showHandoverModal">进入儿童端开始筛查</button>
      </view>

      <!-- 历史记录区 -->
      <view class="section-header">
        <view class="section-title">历史筛查记录</view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state">
        <view class="empty-icon">
          <text class="ph ph-clock"></text>
        </view>
        <view class="empty-text">暂无历史筛查记录</view>
        <view class="empty-hint">完成初筛后将在这里生成成长报告</view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/screening/index"></tab-bar>

    <!-- 交接设备提示弹窗 -->
    <view class="modal-overlay" v-if="showModal" @click="hideModal">
      <view class="modal-content" @click.stop>
        <view class="modal-icon">
          <text class="ph ph-device-mobile"></text>
        </view>
        <view class="modal-title">请把手机交给孩子</view>
        <view class="modal-desc">即将进入儿童互动模式。<br>系统将在游戏过程中自动记录数据，结束后会自动生成报告。</view>
        <button class="modal-btn primary" @click="transferToChild">已交给孩子，开始游戏</button>
        <button class="modal-btn secondary" @click="hideModal">稍后再测</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild } from '../../../utils/auth.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      showModal: false
    }
  },
  onLoad() {
    this.currentChild = getCurrentChild()
  },
  methods: {
    showHandoverModal() {
      this.showModal = true
    },
    hideModal() {
      this.showModal = false
    },
    transferToChild() {
      this.showModal = false
      uni.navigateTo({ url: '/pages/child/home/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 196rpx;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
}

.header-action .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

/* 页面内容 */
.page-content {
  padding: 32rpx 48rpx;
}

/* 儿童信息卡片 */
.child-info-card {
  display: flex;
  align-items: center;
  gap: 32rpx;
  background: #F9FAFB;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 48rpx;
}

.child-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
}

.child-avatar .ph {
  font-size: 48rpx;
  color: #9CA3AF;
}

.child-details {
  flex: 1;
}

.child-label {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 4rpx;
}

.child-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #374151;
}

.child-meta {
  font-size: 22rpx;
  font-weight: 400;
  color: #9CA3AF;
  margin-left: 16rpx;
}

.switch-btn {
  font-size: 26rpx;
  font-weight: 500;
  color: #3B82F6;
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 筛查卡片 */
.screening-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #E5E7EB;
}

.screening-header {
  display: flex;
  gap: 32rpx;
  margin-bottom: 40rpx;
}

.screening-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.screening-icon.blue {
  background: #EFF6FF;
}

.screening-icon.blue .ph {
  font-size: 48rpx;
  color: #3B82F6;
}

.screening-info {
  flex: 1;
}

.screening-name {
  font-size: 32rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.screening-desc {
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.5;
}

/* 须知盒子 */
.notice-box {
  background: #F9FAFB;
  border-radius: 32rpx;
  padding: 32rpx;
  margin-bottom: 40rpx;
  border: 1rpx solid #F3F4F6;
}

.notice-title {
  font-size: 22rpx;
  font-weight: 700;
  color: #4B5563;
  margin-bottom: 16rpx;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.notice-title .ph {
  color: #F59E0B;
  font-size: 28rpx;
}

.notice-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.notice-list li {
  font-size: 22rpx;
  color: #6B7280;
  line-height: 2;
  display: flex;
  align-items: flex-start;
  gap: 16rpx;
}

.notice-list li::before {
  content: '';
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #9CA3AF;
  margin-top: 16rpx;
  flex-shrink: 0;
}

.notice-list li.highlight {
  color: #F59E0B;
}

.notice-list li.highlight::before {
  background: #F59E0B;
}

/* 开始按钮 */
.start-btn {
  width: 100%;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

/* 区域标题头 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24rpx;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;
  opacity: 0.7;
}

.empty-icon {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: #F3F4F6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.empty-icon .ph {
  font-size: 64rpx;
  color: #D1D5DB;
}

.empty-text {
  font-size: 28rpx;
  color: #9CA3AF;
}

.empty-hint {
  font-size: 22rpx;
  color: #D1D5DB;
  margin-top: 8rpx;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding-bottom: 64rpx;
}

.modal-content {
  background: #FFFFFF;
  width: 90%;
  max-width: 640rpx;
  border-radius: 64rpx;
  padding: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.modal-icon {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.modal-icon .ph {
  font-size: 64rpx;
  color: #3B82F6;
}

.modal-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 16rpx;
  text-align: center;
}

.modal-desc {
  font-size: 26rpx;
  color: #6B7280;
  text-align: center;
  line-height: 1.6;
  margin-bottom: 40rpx;
}

.modal-btn {
  width: 100%;
  border-radius: 32rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  margin-bottom: 24rpx;
}

.modal-btn.primary {
  background: #3B82F6;
  color: #FFFFFF;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

.modal-btn.secondary {
  background: #FFFFFF;
  border: 2rpx solid #E5E7EB;
  color: #6B7280;
}
</style>
