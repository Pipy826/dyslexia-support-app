<template>
  <view class="page-container">
    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="user-info">
        <view class="avatar">
          <image v-if="childAvatar" :src="childAvatar" class="avatar-img" mode="aspectFill" />
          <text v-else class="avatar-initial">{{ childInitial }}</text>
        </view>
        <view class="user-text">
          <view class="hello">你好，{{ childName }}！</view>
          <view class="welcome">今天也要加油哦 🌟</view>
        </view>
      </view>
      <view class="top-right">
        <view class="stars-badge">
          <text class="ph ph-star"></text>
          <text class="stars-count">{{ totalStars }}</text>
        </view>
        <view class="rank-btn" @click="goToRanking">
          <text class="ph ph-ranking"></text>
        </view>
        <view class="bgm-btn" @click="toggleBGM">
          <text class="bgm-icon">{{ bgmEnabled ? '🎵' : '🔇' }}</text>
        </view>
        <view class="exit-btn" @click="showExitModal = true">
          <text class="ph ph-sign-out"></text>
        </view>
      </view>
    </view>

    <!-- Tab 导航 -->
    <view class="tab-nav">
      <view
        v-for="tab in tabs"
        :key="tab.id"
        :class="['tab-item', { active: activeTab === tab.id }]"
        @click="switchTab(tab.id)"
      >
        <text class="tab-label">{{ tab.label }}</text>
        <view class="tab-indicator" v-if="activeTab === tab.id"></view>
      </view>
    </view>

    <!-- Tab 内容区（v-show 切换，不销毁组件，保持 BGM） -->
    <view class="tab-content">
      <view v-show="activeTab === 'challenge'" class="tab-pane">
        <challenge-tab
          :child-grade="childGrade"
          :initial-game-type="initialGameType"
          :initial-level-mode="initialLevelMode"
          style="height: 100%;"
        ></challenge-tab>
      </view>
      <view v-show="activeTab === 'training'" class="tab-pane">
        <training-tab :child-id="childId" :total-stars="totalStars" style="height: 100%;"></training-tab>
      </view>
      <view v-show="activeTab === 'today'" class="tab-pane">
        <today-task-tab :child-id="childId" @go-challenge="switchTab('challenge')" style="height: 100%;"></today-task-tab>
      </view>
    </view>

    <!-- 退出验证弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click.self="cancelExit">
      <view class="exit-modal">
        <view class="exit-modal-icon">
          <text :class="isGuest ? 'ph ph-sign-out' : 'ph ph-lock'"></text>
        </view>
        <view class="exit-modal-title">退出儿童模式</view>
        <view class="exit-modal-desc" v-if="isGuest">确认退出儿童模式？</view>
        <view class="exit-modal-desc" v-else>请输入家长登录密码以退出</view>
        <view class="pwd-input-wrap" v-if="!isGuest">
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
        <button class="exit-confirm-btn" :class="{ loading: exitLoading }" @click="confirmExit" :disabled="exitLoading">
          <text class="ph ph-circle-notch spin" v-if="exitLoading"></text>
          <text v-else>确认退出</text>
        </button>
        <button class="exit-cancel-btn" @click="cancelExit">继续游戏</button>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild, isGuestUser } from '../../../utils/auth.js'
import { getTotalStars } from '../../../api/training.js'
import { verifyPassword } from '../../../api/auth.js'
import { getBaseUrl } from '../../../api/index.js'
import AudioManager from '../../../utils/audio.js'
import ChallengeTab from '../../../components/child/ChallengeTab.vue'
import TrainingTab from '../../../components/child/TrainingTab.vue'
import TodayTaskTab from '../../../components/child/TodayTaskTab.vue'

export default {
  name: 'ChildTraining',
  components: { ChallengeTab, TrainingTab, TodayTaskTab },

  data() {
    return {
      activeTab: 'challenge',
      tabs: [
        { id: 'challenge', label: '挑战' },
        { id: 'training', label: '训练' },
        { id: 'today', label: '今日任务' },
      ],
      child: null,
      totalStars: 0,
      bgmEnabled: true,
      // 从家长端任务跳转时传入的参数
      initialGameType: '',
      initialLevelMode: false,
      // 退出弹窗
      showExitModal: false,
      exitPassword: '',
      exitError: '',
      exitLoading: false,
      showPwd: false,
      isGuest: false,
      showPwd: false,
    }
  },

  computed: {
    childName() { return this.child?.name || '小朋友' },
    childInitial() { return this.child?.name?.charAt(0) || '🌟' },
    childId() { return this.child?.id || null },
    childGrade() { return this.child?.grade || '' },
    childAvatar() {
      if (!this.child?.avatar_url) return null
      const url = this.child.avatar_url
      if (url.startsWith('http')) return url
      return getBaseUrl() + url
    },
  },

  onLoad(options) {
    if (options.tab && ['challenge', 'training', 'today'].includes(options.tab)) {
      this.activeTab = options.tab
    }
    if (options.game_type) {
      this.initialGameType = options.game_type
    }
    if (options.level_mode === 'true' || options.level_mode === true) {
      this.initialLevelMode = true
    }
  },

  onShow() {
    this.child = getCurrentChild()
    this.isGuest = isGuestUser()
    if (!this.child) {
      uni.showToast({ title: '请先在家长端添加档案', icon: 'none' })
      return
    }
    if (!this._checkAllowedTime()) return

    this.loadStars()

    // 加载音频偏好（不自动播放，等待用户交互）
    const prefs = AudioManager.loadPreferences()
    this.bgmEnabled = prefs.bgmEnabled
    // H5 环境下浏览器禁止自动播放，监听首次用户交互后再播放
    if (this.bgmEnabled) {
      this._tryPlayBGM()
    }
  },

  onBackPress() {
    this.showExitModal = true
    return true
  },

  methods: {
    switchTab(tabId) {
      this.activeTab = tabId
    },

    goToRanking() {
      uni.navigateTo({ url: '/pages/child/ranking/index' })
    },

    toggleBGM() {
      AudioManager.toggleBGM()
      this.bgmEnabled = AudioManager.bgmEnabled
    },

    // 尝试播放 BGM，处理浏览器自动播放限制
    _tryPlayBGM() {
      if (!this.bgmEnabled) return

      // H5 环境：不主动播放，只注册首次用户交互监听
      // 浏览器策略要求必须有用户交互才能播放音频
      if (typeof document !== 'undefined') {
        const onFirstInteraction = () => {
          if (this.bgmEnabled) {
            AudioManager.playBGM(0)
          }
          document.removeEventListener('touchstart', onFirstInteraction)
          document.removeEventListener('click', onFirstInteraction)
          document.removeEventListener('keydown', onFirstInteraction)
        }
        document.addEventListener('touchstart', onFirstInteraction, { once: true })
        document.addEventListener('click', onFirstInteraction, { once: true })
        document.addEventListener('keydown', onFirstInteraction, { once: true })
        return
      }

      // 非 H5 环境（小程序）直接播放
      AudioManager.playBGM(0)
    },

    async loadStars() {
      try {
        const res = await getTotalStars(this.child.id)
        this.totalStars = res.total_stars || 0
      } catch (e) {
        console.warn('加载星星失败', e)
      }
    },

    _checkAllowedTime() {
      const settings = uni.getStorageSync('reminder_settings') || {}
      if (!settings.timeControlEnabled) return true
      const { allowStart, allowEnd } = settings
      if (!allowStart || !allowEnd) return true
      const now = new Date()
      const [sh, sm] = allowStart.split(':').map(Number)
      const [eh, em] = allowEnd.split(':').map(Number)
      const nowMin = now.getHours() * 60 + now.getMinutes()
      const startMin = sh * 60 + sm
      const endMin = eh * 60 + em
      const allowed = startMin <= endMin
        ? nowMin >= startMin && nowMin <= endMin
        : nowMin >= startMin || nowMin <= endMin
      if (!allowed) {
        uni.showModal({
          title: '暂时不能玩哦',
          content: `家长设置了允许使用时间：${allowStart} - ${allowEnd}，现在还不到时间呢！`,
          showCancel: false,
          confirmText: '好的',
          success: () => { uni.reLaunch({ url: '/pages/parent/home/index' }) },
        })
        return false
      }
      return true
    },

    cancelExit() {
      this.showExitModal = false
      this.exitPassword = ''
      this.exitError = ''
      this.showPwd = false
    },

    async confirmExit() {
      // 游客账号无密码，直接退出
      if (this.isGuest) {
        AudioManager.stopBGM()
        uni.reLaunch({ url: '/pages/parent/home/index' })
        return
      }
      if (!this.exitPassword) { this.exitError = '请输入密码'; return }
      this.exitLoading = true
      this.exitError = ''
      try {
        await verifyPassword(this.exitPassword)
        AudioManager.stopBGM()
        this.showExitModal = false
        this.exitPassword = ''
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
  background: #FFF8F0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部栏 */
.top-bar {
  padding: 56rpx 32rpx 20rpx;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 2rpx 12rpx rgba(245, 127, 23, 0.08);
}
.user-info { display: flex; flex-direction: row; align-items: center; flex: 1; min-width: 0; overflow: hidden; }
.avatar {
  width: 72rpx; height: 72rpx; min-width: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFF3E0, #FFE0B2);
  border: 3rpx solid #FFE0B2;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; margin-right: 16rpx; overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-initial { font-size: 30rpx; font-weight: 700; color: #F57F17; }
.user-text { flex: 1; min-width: 0; }
.hello { font-size: 30rpx; font-weight: 700; color: #3E2723; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.welcome { font-size: 22rpx; color: #8D6E63; margin-top: 2rpx; font-weight: 500; }

.top-right { display: flex; flex-direction: row; align-items: center; gap: 12rpx; flex-shrink: 0; margin-left: 12rpx; }
.stars-badge {
  display: flex; flex-direction: row; align-items: center; gap: 6rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  padding: 10rpx 18rpx; border-radius: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(255, 213, 79, 0.3);
}
.stars-badge .ph { font-size: 26rpx; color: #F57F17; }
.stars-count { font-size: 22rpx; font-weight: 700; color: #E65100; }

.bgm-btn {
  width: 60rpx; height: 60rpx; border-radius: 50%;
  background: #FFF3E0; border: 2rpx solid #FFE0B2;
  display: flex; align-items: center; justify-content: center;
}
.bgm-btn:active { transform: scale(0.92); }
.bgm-icon { font-size: 28rpx; }

.rank-btn {
  width: 60rpx; height: 60rpx; border-radius: 50%;
  background: rgba(251,191,36,0.12); border: 2rpx solid rgba(251,191,36,0.3);
  display: flex; align-items: center; justify-content: center;
}
.rank-btn:active { transform: scale(0.92); }
.rank-btn .ph { font-size: 28rpx; color: #D97706; }

.exit-btn {
  width: 60rpx; height: 60rpx; border-radius: 50%;
  background: rgba(255, 107, 107, 0.1); border: 2rpx solid rgba(255, 107, 107, 0.2);
  display: flex; align-items: center; justify-content: center;
}
.exit-btn:active { transform: scale(0.92); }
.exit-btn .ph { font-size: 28rpx; color: #FF6B6B; }

/* Tab 导航 */
.tab-nav {
  display: flex;
  flex-direction: row;
  background: rgba(255, 255, 255, 0.95);
  padding: 0 28rpx;
  border-bottom: 2rpx solid #FFE0B2;
  flex-shrink: 0;
}
.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0 16rpx;
  position: relative;
  cursor: pointer;
}
.tab-item:active { opacity: 0.7; }
.tab-label {
  font-size: 28rpx;
  font-weight: 600;
  color: #A0AEC0;
  transition: all 0.2s;
}
.tab-item.active .tab-label {
  color: #F57F17;
  font-weight: 800;
}
.tab-indicator {
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 4rpx;
  background: linear-gradient(90deg, #FF8F00, #F57F17);
  border-radius: 2rpx;
  animation: slideIn 0.2s ease;
}
@keyframes slideIn { from { opacity: 0; transform: scaleX(0); } to { opacity: 1; transform: scaleX(1); } }

/* Tab 内容区 */
.tab-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
}
.tab-pane {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
}

/* 退出弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.exit-modal {
  background: #FFFFFF; width: 88%; max-width: 620rpx;
  border-radius: 32rpx; padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn { from { opacity: 0; transform: scale(0.85); } to { opacity: 1; transform: scale(1); } }
.exit-modal-icon {
  width: 100rpx; height: 100rpx; border-radius: 50%;
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  display: flex; align-items: center; justify-content: center; margin-bottom: 24rpx;
}
.exit-modal-icon .ph { font-size: 48rpx; color: #FF6B6B; }
.exit-modal-title { font-size: 34rpx; font-weight: 800; color: #2D3748; margin-bottom: 10rpx; }
.exit-modal-desc { font-size: 24rpx; color: #A0AEC0; margin-bottom: 32rpx; font-weight: 500; text-align: center; }
.pwd-input-wrap {
  width: 100%; display: flex; align-items: center;
  background: #F9FAFB; border: 2rpx solid #E5E7EB; border-radius: 20rpx;
  padding: 24rpx 28rpx; margin-bottom: 16rpx; box-sizing: border-box;
}
.pwd-input-wrap:focus-within { border-color: #F57F17; }
.pwd-icon { font-size: 32rpx; color: #A0AEC0; margin-right: 16rpx; flex-shrink: 0; }
.pwd-input { flex: 1; font-size: 28rpx; color: #2D3748; background: transparent; }
.pwd-eye { padding: 0 4rpx; flex-shrink: 0; }
.pwd-eye .ph { font-size: 30rpx; color: #A0AEC0; }
.exit-error {
  width: 100%; display: flex; align-items: center; gap: 8rpx;
  font-size: 22rpx; color: #FF6B6B; font-weight: 600; margin-bottom: 16rpx; padding: 0 4rpx;
}
.exit-error .ph { font-size: 24rpx; }
.exit-confirm-btn {
  width: 100%; background: linear-gradient(135deg, #FF6B6B, #EF4444); color: #FFFFFF;
  border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(255,107,107,0.3); margin-bottom: 16rpx;
  display: flex; align-items: center; justify-content: center; box-sizing: border-box;
}
.exit-confirm-btn:active { transform: scale(0.97); }
.exit-confirm-btn.loading { opacity: 0.7; }
.exit-cancel-btn {
  width: 100%; background: #F5F5F5; color: #718096;
  border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; box-sizing: border-box;
}
.exit-cancel-btn:active { background: #FFF3E0; color: #F57F17; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
