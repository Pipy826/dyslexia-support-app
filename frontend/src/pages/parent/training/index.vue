<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">干预与训练</view>
      <view class="header-subtitle">已为小明定制专属的家庭提升计划</view>
    </view>

    <view class="page-content">
      <!-- 今日进度概览 -->
      <view class="today-card">
        <view class="today-decoration"></view>
        <view class="today-header">
          <view class="today-info">
            <view class="today-title">今日任务表</view>
            <view class="today-meta">周三 · 预计用时 15 分钟</view>
          </view>
          <view class="today-count">
            <view class="count-ring">0/3</view>
          </view>
        </view>

        <!-- 家长陪伴贴士 -->
        <view class="tips-box">
          <text class="ph ph-heart"></text>
          <view class="tips-text">家长请在旁陪伴，当孩子遇到困难时多给予鼓励，<text class="bold">切勿直接给出答案或指责</text>。</view>
        </view>
      </view>

      <!-- 待完成的任务 -->
      <view class="section-title">待完成的任务</view>
      <view class="task-list">
        <!-- 任务 1 -->
        <view class="task-card">
          <view class="task-icon orange">
            <text class="ph ph-eye"></text>
          </view>
          <view class="task-info">
            <view class="task-name">火眼金睛 (视觉训练)</view>
            <view class="task-desc">提升形近字辨识能力</view>
          </view>
          <button class="task-btn" @click="startTask('visual')">去完成</button>
        </view>

        <!-- 任务 2 -->
        <view class="task-card">
          <view class="task-icon blue">
            <text class="ph ph-puzzle-piece"></text>
          </view>
          <view class="task-info">
            <view class="task-name">字形保卫战</view>
            <view class="task-desc">强化汉字结构记忆</view>
          </view>
          <button class="task-btn" @click="startTask('spelling')">去完成</button>
        </view>

        <!-- 任务 3 -->
        <view class="task-card">
          <view class="task-icon green">
            <text class="ph ph-book-open"></text>
          </view>
          <view class="task-info">
            <view class="task-name">亲子共读打卡</view>
            <view class="task-desc">培养语感与阅读兴趣</view>
          </view>
          <button class="task-btn" @click="startTask('reading')">去完成</button>
        </view>
      </view>

      <!-- 阶段小结预告 -->
      <view class="milestone-card">
        <text class="ph ph-flag"></text>
        <view class="milestone-info">
          <view class="milestone-title">阶段复评预告</view>
          <view class="milestone-desc">连续坚持训练 <text class="highlight">14天</text> 后，系统将提示进行下一轮效果复评。</view>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/training/index"></tab-bar>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const children = await getChildren()
        if (children.length > 0) {
          const saved = getCurrentChild()
          if (saved) {
            this.currentChild = children.find(c => c.id === saved.id) || children[0]
          } else {
            this.currentChild = children[0]
          }
          setCurrentChild(this.currentChild)
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    startTask(type) {
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
}

.header-title {
  font-size: 40rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.header-subtitle {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 页面内容 */
.page-content {
  padding: 32rpx 48rpx;
}

/* 今日卡片 */
.today-card {
  background: #F9FAFB;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
  position: relative;
  overflow: hidden;
}

.today-decoration {
  position: absolute;
  right: -32rpx;
  top: -32rpx;
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: #ECFDF5;
  opacity: 0.5;
}

.today-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
  position: relative;
  z-index: 1;
}

.today-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.today-meta {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.count-ring {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  border: 8rpx solid #10B981;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  font-size: 28rpx;
  font-weight: 700;
  color: #10B981;
}

/* 贴士 */
.tips-box {
  background: #FFFFFF;
  border-radius: 32rpx;
  padding: 24rpx;
  display: flex;
  gap: 24rpx;
  align-items: flex-start;
  border: 1rpx solid #F3F4F6;
  position: relative;
  z-index: 1;
}

.tips-box .ph {
  font-size: 36rpx;
  color: #EF4444;
  flex-shrink: 0;
}

.tips-text {
  font-size: 22rpx;
  color: #4B5563;
  line-height: 1.7;
}

.tips-text .bold {
  font-weight: 700;
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 48rpx;
}

.task-card {
  background: #FFFFFF;
  border-radius: 40rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  gap: 32rpx;
  border: 1rpx solid #F3F4F6;
}

.task-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-icon .ph {
  font-size: 48rpx;
}

.task-icon.orange {
  background: #FEF3C7;
}
.task-icon.orange .ph {
  color: #F59E0B;
}

.task-icon.blue {
  background: #EFF6FF;
}
.task-icon.blue .ph {
  color: #3B82F6;
}

.task-icon.green {
  background: #ECFDF5;
}
.task-icon.green .ph {
  color: #10B981;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.task-desc {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.task-btn {
  padding: 16rpx 32rpx;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  font-size: 22rpx;
  font-weight: 700;
}

/* 里程碑卡片 */
.milestone-card {
  background: #F9FAFB;
  border: 1rpx solid #F3F4F6;
  border-radius: 32rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.milestone-card .ph {
  font-size: 64rpx;
  color: #D1D5DB;
}

.milestone-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.milestone-desc {
  font-size: 22rpx;
  color: #6B7280;
  margin-top: 4rpx;
}

.milestone-desc .highlight {
  font-weight: 700;
  color: #3B82F6;
}
</style>
