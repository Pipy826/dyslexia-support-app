<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">我的</view>
      <view class="header-action" @click="goToSettings">
        <text class="ph ph-gear"></text>
      </view>
    </view>

    <view class="page-content">
      <!-- 家长账号信息卡片 -->
      <view class="account-card">
        <view class="account-avatar">{{ user?.username?.charAt(0)?.toUpperCase() || '我' }}</view>
        <view class="account-info">
          <view class="account-name">{{ user?.username || '用户' }}</view>
          <view class="account-phone">{{ maskPhone(user?.phone) }}</view>
        </view>
        <view class="account-badge">家庭基础版</view>
      </view>

      <!-- 儿童档案管理区 -->
      <view class="section-title">儿童档案管理</view>
      <view class="children-scroll">
        <!-- 档案列表 -->
        <view class="child-card selected" v-for="child in children" :key="child.id" @click="viewChildProfile(child.id)">
          <view class="child-dot"></view>
          <view class="child-avatar">
            <text class="ph ph-user"></text>
          </view>
          <view class="child-info">
            <view class="child-name">{{ child.name }}</view>
            <view class="child-meta">{{ calcAge(child.birth_date) }}岁 / {{ gradeLabel(child.grade) }}</view>
          </view>
          <view class="child-delete-btn" @click.stop="confirmDeleteChild(child)">
            <text class="ph ph-trash"></text>
          </view>
        </view>        <!-- 添加按钮 -->
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
        <view class="menu-item" @click="showInviteCode">
          <view class="menu-icon orange">
            <text class="ph ph-share-network"></text>
          </view>
          <view class="menu-label">邀请好友</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToReminder">
          <view class="menu-icon green">
            <text class="ph ph-clock"></text>
          </view>
          <view class="menu-label">任务与提醒设置</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToAccountEdit">
          <view class="menu-icon blue">
            <text class="ph ph-user-gear"></text>
          </view>
          <view class="menu-label">账号设置</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToHelp">
          <view class="menu-icon orange">
            <text class="ph ph-question"></text>
          </view>
          <view class="menu-label">帮助中心与常见问题</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToContact">
          <view class="menu-icon purple">
            <text class="ph ph-headset"></text>
          </view>
          <view class="menu-label">联系专业客服</view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item last" @click="goToAbout">
          <view class="menu-icon gray">
            <text class="ph ph-info"></text>
          </view>
          <view class="menu-label">关于系统 (v1.0.0)</view>
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
import { getUser, clearAuth, getCurrentChild, setCurrentChild, removeCurrentChild } from '../../../utils/auth.js'
import { getChildren, deleteChild } from '../../../api/child.js'
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
    maskPhone(phone) {
      if (!phone) return '未绑定手机'
      return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    },
    calcAge(birthDate) {
      if (!birthDate) return '?'
      return new Date().getFullYear() - new Date(birthDate).getFullYear()
    },
    gradeLabel(grade) {
      const map = {
        '幼儿园': '学龄前', '学前': '学龄前', 'preschool': '学龄前',
        '一年级': '一年级', '二年级': '二年级', '三年级': '三年级',
        '四年级': '四年级', '五年级': '五/六年级', '六年级': '六年级',
        // 兼容旧数据
        'pre': '学龄前', '1': '一年级', '2': '二年级',
        '3': '三年级', '4': '四年级', '5+': '五/六年级'
      }
      return map[grade] || grade || '未知年级'
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
    goToReminder() {
      uni.navigateTo({ url: '/pages/parent/reminder/index' })
    },
    async showInviteCode() {
      try {
        const { get } = await import('../../../api/index.js')
        const res = await get('/api/auth/invite-code')
        const code = res.invite_code || ''
        uni.showModal({
          title: '邀请好友',
          content: `你的邀请码：${code}\n\n分享给好友，邀请他们一起发现孩子的读写潜力！`,
          confirmText: '复制邀请码',
          cancelText: '关闭',
          success: (result) => {
            if (result.confirm) {
              uni.setClipboardData({
                data: code,
                success: () => {
                  uni.showToast({ title: '邀请码已复制！', icon: 'success' })
                },
              })
            }
          },
        })
      } catch (e) {
        uni.showToast({ title: '获取邀请码失败', icon: 'none' })
      }
    },
    goToAccountEdit() {
      uni.navigateTo({ url: '/pages/parent/account/edit' })
    },
    goToHelp() {
      uni.navigateTo({ url: '/pages/parent/help/index' })
    },
    goToContact() {
      uni.navigateTo({ url: '/pages/parent/help/contact' })
    },
    goToSettings() {
      uni.navigateTo({ url: '/pages/parent/settings/index' })
    },
    goToAbout() {
      uni.navigateTo({ url: '/pages/parent/about/index' })
    },
    goToCreateProfile() {
      uni.navigateTo({ url: '/pages/parent/auth/create-profile' })
    },
    viewChildProfile(id) {
      uni.navigateTo({ url: `/pages/parent/child-profile/index?child_id=${id}` })
    },
    editChild(id) {
      uni.navigateTo({ url: `/pages/parent/profile/edit?id=${id}` })
    },
    confirmDeleteChild(child) {
      uni.showModal({
        title: '删除档案',
        content: `确定要删除"${child.name}"的档案吗？删除后所有相关数据将无法恢复。`,
        confirmText: '删除',
        confirmColor: '#FF6B6B',
        success: async (res) => {
          if (res.confirm) {
            try {
              await deleteChild(child.id)
              // 如果删除的是当前选中的孩子，清除本地缓存，避免后续操作引用已删除档案
              if (this.selectedChild?.id === child.id) {
                removeCurrentChild()
                this.selectedChild = null
              }
              uni.showToast({ title: '档案已删除', icon: 'success' })
              await this.loadChildren()
              // 如果还有其他孩子，自动选中第一个
              if (this.children.length > 0 && !this.selectedChild) {
                this.selectedChild = this.children[0]
                setCurrentChild(this.children[0])
              }
            } catch (e) {
              uni.showToast({ title: '删除失败，请重试', icon: 'none' })
            }
          }
        }
      })
    }
  }
}
</script>


<style scoped>
/* 我的页面 - 统一创意风格 */
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 160rpx;
  overflow-x: hidden;
}

/* 头部 - 与首页一致的紧凑设计 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.header-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
}

.header-action .ph {
  font-size: 32rpx;
  color: #A0AEC0;
}

/* 页面内容 */
.page-content {
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 账号卡片 */
.account-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.account-avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 700;
  color: #4F9EF8;
  flex-shrink: 0;
  border: 3rpx solid rgba(79, 158, 248, 0.2);
}

.account-info { flex: 1; }

.account-name {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
}

.account-phone {
  font-size: 22rpx;
  color: #A0AEC0;
  margin-top: 3rpx;
  font-weight: 500;
}

.account-badge {
  font-size: 18rpx;
  font-weight: 700;
  color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  padding: 6rpx 18rpx;
  border-radius: 10rpx;
}

/* 区域标题 */
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
}

/* 儿童档案区 */
.children-scroll {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.child-card {
  width: calc(50% - 8rpx);
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  position: relative;
  transition: all 0.2s;
  box-sizing: border-box;
}

.child-card:active { transform: scale(0.96); }

.child-card.selected {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  box-shadow: 0 2rpx 12rpx rgba(79, 158, 248, 0.15);
}

.child-dot {
  position: absolute;
  top: 12rpx;
  right: 12rpx;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: #4F9EF8;
}

.child-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.06);
}

.child-avatar .ph {
  font-size: 32rpx;
  color: #4F9EF8;
}

.child-info { text-align: center; }

.child-name {
  font-size: 24rpx;
  font-weight: 700;
  color: #2D3748;
}

.child-meta {
  font-size: 18rpx;
  color: #A0AEC0;
  margin-top: 2rpx;
  font-weight: 500;
}

.child-delete-btn {
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  background: rgba(255, 107, 107, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.child-delete-btn:active {
  background: rgba(255, 107, 107, 0.25);
  transform: scale(0.9);
}

.child-delete-btn .ph {
  font-size: 22rpx;
  color: #FF6B6B;
}

.add-child-card {
  width: calc(50% - 8rpx);
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  border: 2rpx dashed #DBEAFE;
  transition: all 0.2s;
  box-sizing: border-box;
}

.add-child-card:active { background: #EFF6FF; }

.add-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #F5F5F5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-avatar .ph {
  font-size: 28rpx;
  color: #A0AEC0;
}

.add-text {
  font-size: 20rpx;
  font-weight: 600;
  color: #A0AEC0;
}

/* 菜单卡片 */
.menu-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  margin-bottom: 24rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 28rpx 24rpx;
  border-bottom: 1rpx solid #F5F5F5;
  transition: all 0.2s;
}

.menu-item:active { background: #F8FAFF; }

.menu-item.last { border-bottom: none; }

.menu-icon {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.menu-icon .ph { font-size: 26rpx; }
.menu-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.menu-icon.blue .ph { color: #4F9EF8; }
.menu-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.menu-icon.green .ph { color: #22C55E; }
.menu-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.menu-icon.orange .ph { color: #F57F17; }
.menu-icon.purple { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.menu-icon.purple .ph { color: #4F9EF8; }
.menu-icon.gray { background: #F5F5F5; }
.menu-icon.gray .ph { color: #A0AEC0; }

.menu-label {
  flex: 1;
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.menu-arrow {
  font-size: 28rpx;
  color: #D1D5DB;
}

/* 退出按钮 */
.logout-btn {
  width: 100%;
  background: #FFFFFF;
  border: 2rpx solid #E5E7EB;
  color: #A0AEC0;
  border-radius: 16rpx;
  padding: 24rpx;
  font-size: 26rpx;
  font-weight: 700;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
  transition: all 0.2s;
}

.logout-btn:active { background: #FFF5F5; color: #FF6B6B; border-color: #FFE4E4; }
</style>
