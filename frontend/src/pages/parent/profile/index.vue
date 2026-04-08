<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">我的</view>
      <view class="header-action">
        <text class="ph ph-gear"></text>
      </view>
    </view>

    <view class="page-content">
      <!-- 家长账号信息卡片 -->
      <view class="account-card">
        <view class="account-avatar">妈</view>
        <view class="account-info">
          <view class="account-name">小明妈妈</view>
          <view class="account-phone">138****5678</view>
        </view>
        <view class="account-badge">家庭基础版</view>
      </view>

      <!-- 儿童档案管理区 -->
      <view class="section-title">儿童档案管理</view>
      <view class="children-scroll">
        <!-- 档案 1 -->
        <view class="child-card selected" v-for="child in children" :key="child.id" @click="editChild(child.id)">
          <view class="child-dot"></view>
          <view class="child-avatar">
            <text class="ph ph-user"></text>
          </view>
          <view class="child-info">
            <view class="child-name">{{ child.name || '小明' }}</view>
            <view class="child-meta">{{ child.age || 7 }}岁 / {{ child.grade || '一年级' }}</view>
          </view>
        </view>
        <!-- 添加按钮 -->
        <view class="add-child-card" @click="goToCreateProfile">
          <view class="add-avatar">
            <text class="ph ph-plus"></text>
          </view>
          <view class="add-text">添加孩子</view>
        </view>
      </view>

      <!-- 服务与设置 -->
      <view class="section-title">服务与设置</view>
      <view class="menu-card">
        <view class="menu-item">
          <view class="menu-icon green">
            <text class="ph ph-clock"></text>
          </view>
          <view class="menu-label">任务与提醒设置</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item">
          <view class="menu-icon orange">
            <text class="ph ph-question"></text>
          </view>
          <view class="menu-label">帮助中心与常见问题</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item">
          <view class="menu-icon purple">
            <text class="ph ph-headset"></text>
          </view>
          <view class="menu-label">联系专业客服</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last">
          <view class="menu-icon gray">
            <text class="ph ph-info"></text>
          </view>
          <view class="menu-label">关于系统 (v1.0)</view>
          <text class="menu-arrow">›</text>
        </view>
      </view>

      <!-- 退出登录按钮 -->
      <button class="logout-btn" @click="logout">退出登录</button>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/profile/index"></tab-bar>
  </view>
</template>

<script>
import { getUser, clearAuth, getCurrentChild } from '../../../utils/auth.js'
import { getChildren } from '../../../api/child.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      user: null,
      children: [],
      selectedChild: null
    }
  },
  onShow() {
    this.user = getUser()
    this.selectedChild = getCurrentChild()
    this.loadChildren()
  },
  methods: {
    async loadChildren() {
      try {
        this.children = await getChildren()
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    logout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            clearAuth()
            uni.reLaunch({ url: '/pages/parent/auth/login' })
          }
        }
      })
    },
    goToCreateProfile() {
      uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
    },
    editChild(id) {
      uni.navigateTo({ url: `/pages/parent/profile/edit?id=${id}` })
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
  padding: 96rpx 48rpx 48rpx;
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

.header-action .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

/* 页面内容 */
.page-content {
  padding: 48rpx 48rpx;
}

/* 账号卡片 */
.account-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  padding: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
  display: flex;
  align-items: center;
  gap: 32rpx;
}

.account-avatar {
  width: 128rpx;
  height: 128rpx;
  border-radius: 50%;
  background: #EFF6FF;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  font-weight: 700;
  color: #3B82F6;
  flex-shrink: 0;
}

.account-info {
  flex: 1;
}

.account-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.account-phone {
  font-size: 26rpx;
  color: #6B7280;
  margin-top: 4rpx;
}

.account-badge {
  font-size: 20rpx;
  font-weight: 700;
  color: #3B82F6;
  background: #EFF6FF;
  padding: 8rpx 24rpx;
  border-radius: 50rpx;
}

/* 区域标题 */
.section-title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
  margin-bottom: 24rpx;
}

/* 儿童档案滚动区 */
.children-scroll {
  display: flex;
  gap: 24rpx;
  overflow-x: auto;
  margin-bottom: 48rpx;
  padding-bottom: 8rpx;
}

.child-card {
  min-width: 200rpx;
  background: #EFF6FF;
  border-radius: 32rpx;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  border: 1rpx solid #DBEAFE;
  position: relative;
}

.child-card.selected {
  background: #EFF6FF;
  border-color: #3B82F6;
}

.child-dot {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #3B82F6;
}

.child-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.child-avatar .ph {
  font-size: 40rpx;
  color: #3B82F6;
}

.child-info {
  text-align: center;
}

.child-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #374151;
}

.child-meta {
  font-size: 20rpx;
  color: #9CA3AF;
  margin-top: 2rpx;
}

.add-child-card {
  min-width: 200rpx;
  background: #F9FAFB;
  border-radius: 32rpx;
  padding: 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  border: 2rpx dashed #D1D5DB;
}

.add-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-avatar .ph {
  font-size: 36rpx;
  color: #9CA3AF;
}

.add-text {
  font-size: 24rpx;
  font-weight: 500;
  color: #9CA3AF;
}

/* 菜单卡片 */
.menu-card {
  background: #FFFFFF;
  border-radius: 48rpx;
  margin-bottom: 48rpx;
  border: 1rpx solid #F3F4F6;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 32rpx;
  padding: 40rpx 32rpx;
  border-bottom: 1rpx solid #F9FAFB;
}

.menu-item.last {
  border-bottom: none;
}

.menu-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon .ph {
  font-size: 28rpx;
}

.menu-icon.green { background: #ECFDF5; }
.menu-icon.green .ph { color: #10B981; }
.menu-icon.orange { background: #FEF3C7; }
.menu-icon.orange .ph { color: #F59E0B; }
.menu-icon.purple { background: #F3E8FF; }
.menu-icon.purple .ph { color: #8B5CF6; }
.menu-icon.gray { background: #F3F4F6; }
.menu-icon.gray .ph { color: #9CA3AF; }

.menu-label {
  flex: 1;
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
}

.menu-arrow {
  font-size: 32rpx;
  color: #D1D5DB;
}

/* 退出按钮 */
.logout-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #E5E7EB;
  color: #6B7280;
  border-radius: 32rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
}
</style>
