<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">评估报告</view>
      <button class="ai-btn" @click="goToAiChat">
        <text class="ph ph-robot"></text> 问问AI
      </button>
    </view>

    <view class="page-content">
      <!-- 总体结论卡片 -->
      <view class="conclusion-card">
        <view class="report-time">生成时间：今天 10:15</view>
        <view class="conclusion-row">
          <view class="conclusion-indicator orange"></view>
          <view class="conclusion-title">中风险 / 需关注</view>
        </view>
        <view class="conclusion-desc">
          经过全面行为数据分析，小明在<text class="highlight">拼写稳定性</text>与<text class="highlight">视觉辨识</text>维度表现出一定困难。这并非学习态度问题，建议在家庭中开展针对性干预训练。
        </view>
      </view>

      <!-- 能力多维剖析 -->
      <view class="section-title">能力多维剖析</view>
      <view class="ability-card">
        <!-- 视觉辨识 -->
        <view class="ability-item">
          <view class="ability-header">
            <view class="ability-name">视觉辨识能力</view>
            <view class="ability-tag orange">偏弱</view>
          </view>
          <view class="ability-progress">
            <view class="progress-track">
              <view class="progress-fill orange" style="width: 40%"></view>
            </view>
          </view>
          <view class="ability-hint">易混淆形近字，扫视容易漏字。</view>
        </view>

        <!-- 拼写能力 -->
        <view class="ability-item">
          <view class="ability-header">
            <view class="ability-name">拼写输出能力</view>
            <view class="ability-tag orange">偏弱</view>
          </view>
          <view class="ability-progress">
            <view class="progress-track">
              <view class="progress-fill orange" style="width: 45%"></view>
            </view>
          </view>
          <view class="ability-hint">作答犹豫期长，部件颠倒发生率高。</view>
        </view>

        <!-- 阅读理解 -->
        <view class="ability-item">
          <view class="ability-header">
            <view class="ability-name">阅读理解能力</view>
            <view class="ability-tag green">良好</view>
          </view>
          <view class="ability-progress">
            <view class="progress-track">
              <view class="progress-fill green" style="width: 80%"></view>
            </view>
          </view>
          <view class="ability-hint">能准确提取语句核心信息。</view>
        </view>

        <!-- 注意力 -->
        <view class="ability-item">
          <view class="ability-header">
            <view class="ability-name">任务注意力</view>
            <view class="ability-tag green">良好</view>
          </view>
          <view class="ability-progress">
            <view class="progress-track">
              <view class="progress-fill green" style="width: 75%"></view>
            </view>
          </view>
          <view class="ability-hint">能够持续完成15分钟连续任务。</view>
        </view>
      </view>

      <!-- 家长建议 -->
      <view class="section-title">结果怎么看？</view>
      <view class="advice-card">
        <view class="advice-icon">
          <text class="ph ph-lightbulb"></text>
        </view>
        <view class="advice-header">
          <text class="ph ph-info"></text>
          <view class="advice-title">理解孩子的表现</view>
        </view>
        <view class="advice-desc">
          小明在识字阅读时表现慢，并非"不用心"，而是他的<text class="highlight">视觉信息加工速度</text>尚未发育完全。这是典型的发展阶段问题，通过科学陪伴可以显著改善。
        </view>
        <button class="advice-btn" @click="goToTraining">查看专属干预方案 →</button>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/report/index"></tab-bar>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getReports } from '../../../api/report.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      children: [],
      currentChild: null,
      reports: []
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.children = await getChildren()
        if (this.children.length > 0) {
          const saved = getCurrentChild()
          if (saved) {
            this.currentChild = this.children.find(c => c.id === saved.id) || this.children[0]
          } else {
            this.currentChild = this.children[0]
          }
          setCurrentChild(this.currentChild)
          this.loadReports()
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadReports() {
      if (!this.currentChild) return
      try {
        this.reports = await getReports(this.currentChild.id)
      } catch (e) {
        console.error('加载报告失败', e)
      }
    },
    goToAiChat() {
      uni.navigateTo({ url: '/pages/parent/ai-chat/index' })
    },
    goToTraining() {
      uni.switchTab({ url: '/pages/parent/training/index' })
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
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
  border-bottom: 1rpx solid #F3F4F6;
}

.header-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: #F3E8FF;
  color: #7C3AED;
  border: 1rpx solid #EDE9FE;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  font-size: 22rpx;
  font-weight: 700;
}

.ai-btn .ph {
  font-size: 28rpx;
}

/* 页面内容 */
.page-content {
  padding: 48rpx 48rpx;
}

/* 结论卡片 */
.conclusion-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.report-time {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 16rpx;
}

.conclusion-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.conclusion-indicator {
  width: 6rpx;
  height: 48rpx;
  border-radius: 3rpx;
}

.conclusion-indicator.orange {
  background: #F59E0B;
}

.conclusion-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #1F2937;
}

.conclusion-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
}

.conclusion-desc .highlight {
  font-weight: 700;
  color: #F59E0B;
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 能力卡片 */
.ability-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
}

.ability-item {
  margin-bottom: 40rpx;
}

.ability-item:last-child {
  margin-bottom: 0;
}

.ability-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 12rpx;
}

.ability-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.ability-tag {
  font-size: 20rpx;
  font-weight: 700;
  padding: 4rpx 16rpx;
  border-radius: 8rpx;
}

.ability-tag.orange {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.ability-tag.green {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.ability-progress {
  margin-bottom: 12rpx;
}

.progress-track {
  height: 16rpx;
  background: #F3F4F6;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s;
}

.progress-fill.orange {
  background: #F59E0B;
}

.progress-fill.green {
  background: #10B981;
}

.ability-hint {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 建议卡片 */
.advice-card {
  background: #EFF6FF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #DBEAFE;
  position: relative;
}

.advice-icon {
  position: absolute;
  top: 32rpx;
  right: 32rpx;
  font-size: 80rpx;
  color: #BFDBFE;
}

.advice-header {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.advice-header .ph {
  font-size: 28rpx;
  color: #3B82F6;
}

.advice-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.advice-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 32rpx;
}

.advice-desc .highlight {
  font-weight: 700;
  color: #3B82F6;
}

.advice-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #DBEAFE;
  color: #3B82F6;
  border-radius: 32rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}
</style>
