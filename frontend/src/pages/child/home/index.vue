<template>
  <view class="page-container">
    <!-- 顶部栏：问候 + 星星 + 退出 -->
    <view class="top-bar">
      <view class="user-info">
        <view class="avatar">
          <image v-if="childAvatar" :src="childAvatar" class="avatar-img" mode="aspectFill" />
          <text v-else>{{ childInitial }}</text>
        </view>
        <view class="user-text">
          <view class="hello">你好，{{ childName }}！</view>
          <view class="welcome">准备好今天的挑战了吗？</view>
        </view>
      </view>
      <view class="top-right">
        <view class="stars-badge">
          <text class="ph ph-star"></text>
          <view class="stars-count">{{ totalStars }}</view>
        </view>
        <view class="exit-btn" @click="showExitModal = true">
          <text class="ph ph-sign-out"></text>
        </view>
      </view>
    </view>

    <!-- 内容区：可滚动 -->
    <scroll-view class="content-area" scroll-y>
      <!-- 插画区 -->
      <view class="illustration bounce">
        <view class="illustration-bg"></view>
        <view class="illustration-main">
          <text class="ph ph-rocket"></text>
          <view class="dots">
            <view class="dot red"></view>
            <view class="dot green"></view>
            <view class="dot blue"></view>
          </view>
        </view>
      </view>

      <view class="title">语言探险之旅</view>
      <view class="subtitle">选一个挑战，收集小星星！</view>

      <!-- 游戏类型卡片 -->
      <view class="game-grid">
        <view
          v-for="g in allGameTypes"
          :key="g.type"
          :class="['game-card', { active: selectedGameType === g.type }]"
          :style="{ '--c': g.color, '--bg': g.bg }"
          @click="selectedGameType = g.type"
        >
          <view class="game-card-icon">
            <text :class="'ph ' + g.icon"></text>
          </view>
          <view class="game-card-body">
            <view class="game-card-name">{{ g.name }}</view>
            <view class="game-card-desc">{{ g.desc }}</view>
          </view>
          <view class="game-card-check" v-if="selectedGameType === g.type">
            <text class="ph ph-check-circle"></text>
          </view>
        </view>
      </view>

      <!-- 开始按钮 -->
      <button class="start-btn" @click="startChallenge">
        <text class="ph ph-play"></text> 开始挑战
      </button>

      <view class="parent-tip">
        <text class="ph ph-info"></text> 请在安静环境下独立完成
      </view>

      <!-- 底部安全区 -->
      <view style="height: 160rpx;"></view>
    </scroll-view>

    <!-- 底部导航 -->
    <view class="child-tab-bar">
      <view class="child-tab-item active" @click="goToHome">
        <text class="ph-fill ph-game-controller"></text>
        <view class="child-tab-label">挑战</view>
      </view>
      <view class="child-tab-item" @click="goToTraining">
        <text class="ph-fill ph-tree"></text>
        <view class="child-tab-label">训练乐园</view>
      </view>
    </view>

    <!-- 退出验证弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click.self="cancelExit">
      <view class="exit-modal">
        <view class="exit-modal-icon">
          <text class="ph ph-lock"></text>
        </view>
        <view class="exit-modal-title">退出儿童模式</view>
        <view class="exit-modal-desc">请输入家长登录密码以退出</view>

        <view class="pwd-input-wrap">
          <text class="ph ph-lock-key pwd-icon"></text>
          <input
            class="pwd-input"
            :type="showPwd ? 'text' : 'password'"
            v-model="exitPassword"
            placeholder="请输入家长密码"
            :password="!showPwd"
            @confirm="confirmExit"
          />
          <view class="pwd-eye" @click="showPwd = !showPwd">
            <text :class="showPwd ? 'ph ph-eye' : 'ph ph-eye-slash'"></text>
          </view>
        </view>

        <view class="exit-error" v-if="exitError">
          <text class="ph ph-warning-circle"></text> {{ exitError }}
        </view>

        <button
          class="exit-confirm-btn"
          :class="{ loading: exitLoading }"
          @click="confirmExit"
          :disabled="exitLoading"
        >
          <text class="ph ph-circle-notch spin" v-if="exitLoading"></text>
          <text v-else>确认退出</text>
        </button>
        <button class="exit-cancel-btn" @click="cancelExit">继续游戏</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild, getUser } from '../../../utils/auth.js'
import { getTotalStars } from '../../../api/training.js'
import { login } from '../../../api/auth.js'
import { getBaseUrl } from '../../../api/index.js'

const ALL_GAME_TYPES = [
  {
    type: 'visual',
    name: '视觉辨识',
    desc: '找不同，练眼力',
    icon: 'ph-eye',
    color: '#4F9EF8',
    bg: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
  },
  {
    type: 'spelling',
    name: '拼字识别',
    desc: '认汉字，练拼写',
    icon: 'ph-text-aa',
    color: '#A78BFA',
    bg: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
  },
  {
    type: 'comprehension',
    name: '文字理解',
    desc: '读故事，练理解',
    icon: 'ph-book-open',
    color: '#22C55E',
    bg: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
  },
  {
    type: 'working_memory',
    name: '工作记忆',
    desc: '记序列，练记忆',
    icon: 'ph-brain',
    color: '#F97316',
    bg: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)',
  },
  {
    type: 'rapid_naming',
    name: '快速命名',
    desc: '快说出，练反应',
    icon: 'ph-lightning',
    color: '#EAB308',
    bg: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)',
  },
  {
    type: 'motor_coordination',
    name: '精细动作',
    desc: '判线条，练协调',
    icon: 'ph-hand',
    color: '#EC4899',
    bg: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)',
  },
]

export default {
  data() {
    return {
      child: null,
      totalStars: 0,
      selectedGameType: 'visual',
      allGameTypes: ALL_GAME_TYPES,
      // 退出弹窗
      showExitModal: false,
      exitPassword: '',
      exitError: '',
      exitLoading: false,
      showPwd: false,
    }
  },
  computed: {
    childName() {
      return this.child?.name || '小朋友'
    },
    childInitial() {
      return this.child?.name?.charAt(0) || '🌟'
    },
    childAvatar() {
      if (!this.child?.avatar_url) return null
      const url = this.child.avatar_url
      if (url.startsWith('http')) return url
      return getBaseUrl() + url
    },
  },
  onShow() {
    this.child = getCurrentChild()
    if (!this.child) {
      uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
      return
    }
    this.loadStars()
  },
  // 拦截手势/物理返回键，必须输入密码才能退出儿童模式
  onBackPress(options) {
    // H5 手势返回和小程序物理返回键都拦截
    this.showExitModal = true
    return true  // 返回 true 阻止默认返回行为，H5 下 uni-app 会静默处理错误
  },
  methods: {
    async loadStars() {
      try {
        const res = await getTotalStars(this.child.id)
        this.totalStars = res.total_stars || 0
      } catch (e) {
        console.warn('加载星星失败', e)
      }
    },
    goToHome() {
      // 已在首页，不跳转
    },
    goToTraining() {
      uni.redirectTo({ url: '/pages/child/training/index' })
    },
    startChallenge() {
      if (!this.child) {
        uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
        return
      }
      const gradeParam = this.child.grade ? `&grade=${encodeURIComponent(this.child.grade)}` : ''
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${this.selectedGameType}${gradeParam}`,
      })
    },

    // ── 退出逻辑 ──────────────────────────────────────────────────────────────
    cancelExit() {
      this.showExitModal = false
      this.exitPassword = ''
      this.exitError = ''
      this.showPwd = false
    },
    async confirmExit() {
      if (!this.exitPassword) {
        this.exitError = '请输入密码'
        return
      }
      this.exitLoading = true
      this.exitError = ''
      try {
        const user = getUser()
        if (!user?.username) {
          this.exitError = '无法获取家长账号信息'
          this.exitLoading = false
          return
        }
        // 直接用 uni.request 绕过全局拦截器，避免密码错误时被强制登出
        const baseUrl = getBaseUrl() || (typeof window !== 'undefined'
          ? `${window.location.protocol}//${window.location.hostname}:8000`
          : 'http://localhost:8000')
        await new Promise((resolve, reject) => {
          uni.request({
            url: baseUrl + '/api/auth/login',
            method: 'POST',
            data: { username: user.username, password: this.exitPassword },
            header: { 'Content-Type': 'application/json' },
            timeout: 10000,
            success: (res) => {
              if (res.statusCode >= 200 && res.statusCode < 300) {
                resolve(res.data)
              } else {
                reject(new Error('密码错误'))
              }
            },
            fail: (err) => reject(err),
          })
        })
        // 验证通过
        this.showExitModal = false
        this.exitPassword = ''
        // 用 reLaunch 跳回家长端首页（儿童端是通过 reLaunch 进入的，页面栈无上一页）
        uni.reLaunch({ url: '/pages/parent/home/index' })
      } catch (e) {
        this.exitError = '密码错误，请重试'
      } finally {
        this.exitLoading = false
      }
    },
  },
}
</script>

<style scoped>
.page-container {
  height: 100vh;
  width: 100%;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

/* ── 顶部栏 ── */
.top-bar {
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.user-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.avatar {
  width: 60rpx; height: 60rpx; min-width: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 3rpx solid #FFFFFF;
  display: flex; align-items: center; justify-content: center;
  font-size: 26rpx; font-weight: 700; color: #4F9EF8;
  box-shadow: 0 4rpx 12rpx rgba(79, 158, 248, 0.2);
  flex-shrink: 0; margin-right: 14rpx;
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }

.user-text { flex: 1; min-width: 0; overflow: hidden; }
.user-text .hello { font-size: 30rpx; font-weight: 700; color: #2D3748; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-text .welcome { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; white-space: nowrap; overflow: hidden; }

.top-right {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
  margin-left: 12rpx;
}

.stars-badge {
  display: flex; flex-direction: row; align-items: center;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  padding: 10rpx 18rpx; border-radius: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.3);
}
.stars-badge .ph { font-size: 26rpx; color: #F57F17; margin-right: 6rpx; }
.stars-count { font-size: 22rpx; font-weight: 700; color: #E65100; }

/* 退出按钮 */
.exit-btn {
  width: 60rpx; height: 60rpx;
  border-radius: 50%;
  background: rgba(255, 107, 107, 0.1);
  border: 2rpx solid rgba(255, 107, 107, 0.2);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.exit-btn:active { background: rgba(255, 107, 107, 0.2); transform: scale(0.92); }
.exit-btn .ph { font-size: 28rpx; color: #FF6B6B; }

/* ── 内容区 ── */
.content-area {
  flex: 1;
  min-height: 0;
  padding: 24rpx 32rpx 16rpx;
  box-sizing: border-box;
  width: 100%;
}

/* 插画 */
.illustration {
  width: 100%;
  height: 160rpx;
  margin-bottom: 16rpx;
  position: relative;
  background: #FFFFFF;
  border-radius: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  overflow: hidden;
}
.illustration-bg {
  position: absolute; top: -50%; right: -50%; width: 200%; height: 200%;
  background: radial-gradient(circle, rgba(79, 158, 248, 0.06) 0%, transparent 70%);
}
.illustration-main { position: relative; z-index: 1; display: flex; flex-direction: row; align-items: center; gap: 20rpx; }
.illustration-main .ph { font-size: 56rpx; color: #4F9EF8; display: block; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6rpx); } }
.dots { display: flex; flex-direction: row; }
.dot { width: 10rpx; height: 10rpx; border-radius: 50%; margin: 0 5rpx; animation: pulse 1.5s ease-in-out infinite; }
.dot.red { background: #FF6B6B; animation-delay: 0s; }
.dot.green { background: #22C55E; animation-delay: 0.2s; }
.dot.blue { background: #4F9EF8; animation-delay: 0.4s; }
@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.3); opacity: 0.7; } }

.title { font-size: 28rpx; font-weight: 800; color: #2D3748; margin-bottom: 2rpx; text-align: center; }
.subtitle { font-size: 20rpx; color: #A0AEC0; text-align: center; margin-bottom: 16rpx; font-weight: 500; }

/* ── 游戏卡片网格 ── */
.game-grid {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  margin-bottom: 24rpx;
  width: 100%;
}

.game-card {
  width: 100%;
  background: #FFFFFF;
  border-radius: 18rpx;
  padding: 18rpx 20rpx;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16rpx;
  position: relative;
  border: 2rpx solid transparent;
  transition: all 0.2s;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  box-sizing: border-box;
}
.game-card:active { transform: scale(0.98); }
.game-card.active {
  background: var(--bg);
  border-color: var(--c);
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.08);
}

.game-card-icon {
  width: 52rpx; height: 52rpx;
  border-radius: 14rpx;
  background: var(--bg);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.game-card.active .game-card-icon {
  background: rgba(255, 255, 255, 0.7);
}
.game-card-icon .ph { font-size: 26rpx; color: var(--c); }

.game-card-body { flex: 1; min-width: 0; }
.game-card-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.game-card-desc { font-size: 20rpx; color: #A0AEC0; font-weight: 500; margin-top: 2rpx; }

/* 选中勾 */
.game-card-check {
  margin-left: auto;
  flex-shrink: 0;
}
.game-card-check .ph { font-size: 28rpx; color: var(--c); }

/* ── 开始按钮 ── */
.start-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 18rpx;
  padding: 24rpx;
  font-size: 30rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3);
  display: flex; flex-direction: row; align-items: center; justify-content: center;
  box-sizing: border-box;
  margin-bottom: 12rpx;
}
.start-btn .ph { font-size: 30rpx; margin-right: 10rpx; }

.parent-tip {
  font-size: 20rpx; color: #CBD5E0;
  display: flex; flex-direction: row; align-items: center; justify-content: center;
  font-weight: 500;
}
.parent-tip .ph { font-size: 20rpx; margin-right: 6rpx; }

/* ── 底部导航 ── */
.child-tab-bar {
  position: fixed; bottom: 16rpx; left: 16rpx; right: 16rpx;
  display: flex; flex-direction: row; justify-content: space-around; align-items: center;
  padding: 12rpx 40rpx; padding-bottom: calc(12rpx + env(safe-area-inset-bottom));
  background: rgba(255,255,255,0.95); border-radius: 28rpx; z-index: 999;
  box-shadow: 0 8rpx 32rpx rgba(0,0,0,0.08), 0 0 0 1rpx rgba(0,0,0,0.04);
}
.child-tab-item {
  display: flex; flex-direction: column; align-items: center; gap: 4rpx;
  color: #9CA3AF; padding: 10rpx 32rpx; border-radius: 16rpx;
}
.child-tab-item.active { color: #4F9EF8; }
.child-tab-item .ph { font-size: 40rpx; }
.child-tab-label { font-size: 20rpx; font-weight: 600; }

/* ── 退出弹窗 ── */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.exit-modal {
  background: #FFFFFF;
  width: 88%;
  max-width: 620rpx;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn { from { opacity: 0; transform: scale(0.85); } to { opacity: 1; transform: scale(1); } }

.exit-modal-icon {
  width: 100rpx; height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 24rpx;
}
.exit-modal-icon .ph { font-size: 48rpx; color: #FF6B6B; }

.exit-modal-title { font-size: 34rpx; font-weight: 800; color: #2D3748; margin-bottom: 10rpx; }
.exit-modal-desc { font-size: 24rpx; color: #A0AEC0; margin-bottom: 32rpx; font-weight: 500; text-align: center; }

/* 密码输入框 */
.pwd-input-wrap {
  width: 100%;
  display: flex; align-items: center;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 16rpx;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.pwd-input-wrap:focus-within { border-color: #4F9EF8; }
.pwd-icon { font-size: 32rpx; color: #A0AEC0; margin-right: 16rpx; flex-shrink: 0; }
.pwd-input { flex: 1; font-size: 28rpx; color: #2D3748; background: transparent; }
.pwd-eye { padding: 0 4rpx; flex-shrink: 0; }
.pwd-eye .ph { font-size: 30rpx; color: #A0AEC0; }

/* 错误提示 */
.exit-error {
  width: 100%;
  display: flex; align-items: center; gap: 8rpx;
  font-size: 22rpx; color: #FF6B6B; font-weight: 600;
  margin-bottom: 16rpx;
  padding: 0 4rpx;
}
.exit-error .ph { font-size: 24rpx; }

/* 确认/取消按钮 */
.exit-confirm-btn {
  width: 100%;
  background: linear-gradient(135deg, #FF6B6B, #EF4444);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 28rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(255, 107, 107, 0.3);
  margin-bottom: 16rpx;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.exit-confirm-btn:active { transform: scale(0.97); }
.exit-confirm-btn.loading { opacity: 0.7; }

.exit-cancel-btn {
  width: 100%;
  background: #F5F5F5;
  color: #718096;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 28rpx; font-weight: 700;
  transition: all 0.2s;
}
.exit-cancel-btn:active { background: #EFF6FF; color: #4F9EF8; }

/* 旋转动画（加载中） */
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
