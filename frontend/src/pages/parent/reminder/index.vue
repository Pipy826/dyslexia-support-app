<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack"><text class="ph ph-arrow-left"></text></view>
      <view class="header-title">任务与提醒设置</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 每日训练提醒 -->
      <view class="section-title">每日训练提醒</view>
      <view class="setting-card">
        <view class="setting-row">
          <view class="setting-left">
            <view class="setting-icon green"><text class="ph ph-bell"></text></view>
            <view class="setting-info">
              <view class="setting-label">开启每日提醒</view>
              <view class="setting-desc">每天定时提醒孩子完成训练任务</view>
            </view>
          </view>
          <view class="toggle" :class="{ on: reminderEnabled }" @click="toggleReminder">
            <view class="toggle-thumb"></view>
          </view>
        </view>

        <view class="setting-row" v-if="reminderEnabled">
          <view class="setting-left">
            <view class="setting-icon blue"><text class="ph ph-clock"></text></view>
            <view class="setting-info">
              <view class="setting-label">提醒时间</view>
              <view class="setting-desc">{{ reminderTime }}</view>
            </view>
          </view>
          <picker mode="time" :value="reminderTime" @change="onTimeChange">
            <view class="setting-action">修改 ›</view>
          </picker>
        </view>
      </view>

      <!-- 复评提醒 -->
      <view class="section-title">复评提醒</view>
      <view class="setting-card">
        <view class="setting-row">
          <view class="setting-left">
            <view class="setting-icon orange"><text class="ph ph-calendar-check"></text></view>
            <view class="setting-info">
              <view class="setting-label">阶段复评提醒</view>
              <view class="setting-desc">训练满{{ reassessDays }}天后提醒复评</view>
            </view>
          </view>
          <view class="toggle" :class="{ on: reassessEnabled }" @click="reassessEnabled = !reassessEnabled; saveSettings()">
            <view class="toggle-thumb"></view>
          </view>
        </view>

        <view class="setting-row" v-if="reassessEnabled">
          <view class="setting-left">
            <view class="setting-icon orange"><text class="ph ph-timer"></text></view>
            <view class="setting-info">
              <view class="setting-label">复评周期</view>
              <view class="setting-desc">每隔多少天提醒一次</view>
            </view>
          </view>
          <view class="days-picker">
            <view
              v-for="d in [7, 14, 21, 30]"
              :key="d"
              :class="['day-option', { active: reassessDays === d }]"
              @click="reassessDays = d; saveSettings()"
            >{{ d }}天</view>
          </view>
        </view>
      </view>

      <!-- 儿童使用时段控制 -->
      <view class="section-title">儿童使用时段控制</view>
      <view class="setting-card">
        <view class="setting-row">
          <view class="setting-left">
            <view class="setting-icon blue"><text class="ph ph-clock-countdown"></text></view>
            <view class="setting-info">
              <view class="setting-label">限制使用时段</view>
              <view class="setting-desc">仅允许在指定时间段内进入儿童模式</view>
            </view>
          </view>
          <view class="toggle" :class="{ on: timeControlEnabled }" @click="timeControlEnabled = !timeControlEnabled; saveSettings()">
            <view class="toggle-thumb"></view>
          </view>
        </view>

        <view v-if="timeControlEnabled">
          <view class="setting-row">
            <view class="setting-left">
              <view class="setting-icon green"><text class="ph ph-play-circle"></text></view>
              <view class="setting-info">
                <view class="setting-label">开始时间</view>
                <view class="setting-desc">{{ allowStart }}</view>
              </view>
            </view>
            <picker mode="time" :value="allowStart" @change="e => { allowStart = e.detail.value; saveSettings() }">
              <view class="setting-action">修改 ›</view>
            </picker>
          </view>
          <view class="setting-row">
            <view class="setting-left">
              <view class="setting-icon orange"><text class="ph ph-stop-circle"></text></view>
              <view class="setting-info">
                <view class="setting-label">结束时间</view>
                <view class="setting-desc">{{ allowEnd }}</view>
              </view>
            </view>
            <picker mode="time" :value="allowEnd" @change="e => { allowEnd = e.detail.value; saveSettings() }">
              <view class="setting-action">修改 ›</view>
            </picker>
          </view>
          <view class="time-range-tip">
            <text class="ph ph-info"></text>
            孩子只能在 {{ allowStart }} ~ {{ allowEnd }} 之间进入儿童模式
          </view>
        </view>
      </view>

      <!-- 训练时长建议 -->
      <view class="section-title">训练时长建议</view>      <view class="setting-card">
        <view class="setting-row">
          <view class="setting-left">
            <view class="setting-icon purple"><text class="ph ph-hourglass"></text></view>
            <view class="setting-info">
              <view class="setting-label">每日训练时长</view>
              <view class="setting-desc">建议每次 {{ dailyMinutes }} 分钟</view>
            </view>
          </view>
          <view class="minutes-picker">
            <view
              v-for="m in [10, 15, 20, 30]"
              :key="m"
              :class="['minute-option', { active: dailyMinutes === m }]"
              @click="dailyMinutes = m; saveSettings()"
            >{{ m }}分</view>
          </view>
        </view>
      </view>

      <!-- 提示说明 -->
      <view class="tip-card">
        <text class="ph ph-lightbulb tip-icon"></text>
        <view class="tip-text">
          研究表明，每天坚持 10-15 分钟的针对性训练，比偶尔长时间训练效果更好。建议选择孩子状态最好的时间段（如放学后休息片刻后）进行训练。
        </view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      reminderEnabled: false,
      reminderTime: '19:00',
      reassessEnabled: true,
      reassessDays: 14,
      dailyMinutes: 15,
      // 时段控制
      timeControlEnabled: false,
      allowStart: '15:00',
      allowEnd: '20:00',
    }
  },
  onLoad() {
    this.loadSettings()
  },
  methods: {
    loadSettings() {
      const s = uni.getStorageSync('reminder_settings') || {}
      this.reminderEnabled = s.reminderEnabled ?? false
      this.reminderTime = s.reminderTime ?? '19:00'
      this.reassessEnabled = s.reassessEnabled ?? true
      this.reassessDays = s.reassessDays ?? 14
      this.dailyMinutes = s.dailyMinutes ?? 15
      this.timeControlEnabled = s.timeControlEnabled ?? false
      this.allowStart = s.allowStart ?? '15:00'
      this.allowEnd = s.allowEnd ?? '20:00'
    },
    saveSettings() {
      uni.setStorageSync('reminder_settings', {
        reminderEnabled: this.reminderEnabled,
        reminderTime: this.reminderTime,
        reassessEnabled: this.reassessEnabled,
        reassessDays: this.reassessDays,
        dailyMinutes: this.dailyMinutes,
        timeControlEnabled: this.timeControlEnabled,
        allowStart: this.allowStart,
        allowEnd: this.allowEnd,
      })
      uni.showToast({ title: '设置已保存', icon: 'success', duration: 1000 })
    },
    toggleReminder() {
      this.reminderEnabled = !this.reminderEnabled
      this.saveSettings()
      if (this.reminderEnabled) {
        // #ifdef MP-WEIXIN
        // 微信小程序：请求订阅消息权限
        wx.requestSubscribeMessage({
          tmplIds: ['training_reminder_template_id'], // 需在微信公众平台申请模板ID
          success(res) {
            console.log('订阅消息授权结果', res)
          },
          fail() {},
        })
        // #endif
        // #ifdef H5
        if (typeof Notification !== 'undefined' && Notification.permission === 'default') {
          Notification.requestPermission()
        }
        // #endif
        uni.showToast({ title: `已设置 ${this.reminderTime} 提醒`, icon: 'none' })
      }
    },
    onTimeChange(e) {
      this.reminderTime = e.detail.value
      this.saveSettings()
    },
    goBack() { uni.navigateBack() },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx; display: flex; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; }

.setting-card { background: #FFFFFF; border-radius: 24rpx; padding: 8rpx 0; margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04); overflow: hidden; }

.setting-row { display: flex; align-items: center; justify-content: space-between; padding: 20rpx 28rpx; border-bottom: 1rpx solid #F5F5F5; }
.setting-row:last-child { border-bottom: none; }

.setting-left { display: flex; align-items: center; gap: 16rpx; flex: 1; }
.setting-icon { width: 56rpx; height: 56rpx; border-radius: 14rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.setting-icon .ph { font-size: 26rpx; }
.setting-icon.green { background: rgba(34,197,94,0.1); }
.setting-icon.green .ph { color: #22C55E; }
.setting-icon.blue { background: rgba(79,158,248,0.1); }
.setting-icon.blue .ph { color: #4F9EF8; }
.setting-icon.orange { background: rgba(245,127,23,0.1); }
.setting-icon.orange .ph { color: #F57F17; }
.setting-icon.purple { background: rgba(167,139,250,0.1); }
.setting-icon.purple .ph { color: #A78BFA; }

.setting-info { flex: 1; }
.setting-label { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.setting-desc { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }

.setting-action { font-size: 24rpx; color: #4F9EF8; font-weight: 700; }

/* 开关 */
.toggle { width: 80rpx; height: 44rpx; border-radius: 22rpx; background: #E5E7EB; position: relative; transition: all 0.3s; flex-shrink: 0; }
.toggle.on { background: #22C55E; }
.toggle-thumb { position: absolute; top: 4rpx; left: 4rpx; width: 36rpx; height: 36rpx; border-radius: 50%; background: #FFFFFF; box-shadow: 0 2rpx 6rpx rgba(0,0,0,0.15); transition: all 0.3s; }
.toggle.on .toggle-thumb { left: 40rpx; }

/* 天数/分钟选择 */
.days-picker, .minutes-picker { display: flex; gap: 8rpx; flex-wrap: wrap; justify-content: flex-end; }
.day-option, .minute-option { font-size: 20rpx; font-weight: 700; padding: 8rpx 16rpx; border-radius: 12rpx; background: #F5F5F5; color: #718096; transition: all 0.2s; }
.day-option.active, .minute-option.active { background: rgba(245,127,23,0.1); color: #F57F17; }

/* 提示卡片 */
.tip-card { background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border-radius: 20rpx; padding: 24rpx; border: 1rpx solid #FDE68A; display: flex; align-items: flex-start; gap: 12rpx; }
.tip-icon { font-size: 28rpx; color: #F57F17; flex-shrink: 0; margin-top: 2rpx; }
.tip-text { font-size: 24rpx; color: #92400E; line-height: 1.7; font-weight: 500; }

/* 时段控制提示 */
.time-range-tip {
  display: flex; align-items: center; gap: 8rpx;
  font-size: 22rpx; color: #4F9EF8; font-weight: 500;
  padding: 12rpx 28rpx 16rpx;
}
.time-range-tip .ph { font-size: 22rpx; }
</style>
