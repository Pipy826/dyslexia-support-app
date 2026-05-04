<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">能力探索</view>
      <view class="header-action">
        <text class="ph ph-question"></text>
      </view>
    </view>

    <view class="page-content">
      <!-- 探索对象信息区 -->
      <view class="child-info-card">
        <view class="child-avatar">
          <text class="ph ph-user"></text>
        </view>
        <view class="child-details">
          <view class="child-label">当前评测对象</view>
          <view class="child-name">
            {{ currentChild ? currentChild.name : '未选择' }}
            <text class="child-meta" v-if="currentChild">{{ getAge(currentChild.birth_date) }}岁 / {{ currentChild.grade || '' }}</text>
          </view>
        </view>
        <view class="switch-btn" @click="showChildPicker" v-if="children.length > 1">切换</view>
      </view>

      <!-- 无孩子档案提示 -->
      <view class="no-child-tip" v-if="!currentChild">
        <text class="ph ph-info"></text>
        <text>请先添加孩子档案，以开始能力探索</text>
      </view>

      <!-- 进入儿童模式入口 -->
      <view class="handover-card" v-if="currentChild" @click="enterChildMode">
        <view class="handover-decoration"></view>
        <view class="handover-left">
          <view class="handover-icon">
            <text class="ph ph-game-controller"></text>
          </view>
          <view class="handover-text">
            <view class="handover-title">进入儿童模式</view>
            <view class="handover-desc">将设备交给 {{ currentChild.name }}，由孩子自主选择游戏开始能力探索</view>
          </view>
        </view>
        <view class="handover-arrow">
          <text class="ph ph-arrow-right"></text>
        </view>
      </view>

      <!-- 读写能力风险筛查入口（二维码） -->
      <view class="screening-qr-card" v-if="currentChild">
        <view class="qr-card-header">
          <view class="qr-badge">专业筛查</view>
          <view class="qr-title">读写能力风险筛查</view>
          <view class="qr-desc">由星萌乐学专业团队提供，扫码即可完成专业筛查，结果由专业老师解读</view>
        </view>
        <view class="qr-body">
          <view class="qr-image-wrap">
            <image
              class="qr-image"
              src="/static/images/screening_qr.png"
              mode="aspectFit"
              @error="qrLoadError = true"
            />
            <view class="qr-placeholder" v-if="qrLoadError">
              <text class="ph ph-qr-code"></text>
              <text class="qr-placeholder-text">筛查二维码</text>
            </view>
          </view>
          <view class="qr-tips">
            <view class="qr-tip-row">
              <text class="ph ph-check-circle qr-tip-icon"></text>
              <text class="qr-tip-text">专业团队设计，科学可靠</text>
            </view>
            <view class="qr-tip-row">
              <text class="ph ph-check-circle qr-tip-icon"></text>
              <text class="qr-tip-text">筛查数据由专业老师查看</text>
            </view>
            <view class="qr-tip-row">
              <text class="ph ph-check-circle qr-tip-icon"></text>
              <text class="qr-tip-text">高风险可联系专业导师</text>
            </view>
          </view>
        </view>
        <view class="qr-footer">
          <text class="ph ph-info"></text>
          游戏成绩偏低时，建议扫码做专业筛查
        </view>
      </view>

      <!-- 说明卡片 -->
      <view class="tips-card" v-if="currentChild">
        <view class="tips-row">
          <view class="tips-icon blue"><text class="ph ph-headphones"></text></view>
          <view class="tips-text">请在安静环境下进行，避免干扰</view>
        </view>
        <view class="tips-row">
          <view class="tips-icon green"><text class="ph ph-shield-check"></text></view>
          <view class="tips-text">游戏结束后报告将自动生成并发送给您</view>
        </view>
        <view class="tips-row">
          <view class="tips-icon orange"><text class="ph ph-lock"></text></view>
          <view class="tips-text">退出儿童模式需要输入您的登录密码</view>
        </view>
      </view>

      <!-- 历史记录区 -->
      <view class="section-header">
        <view class="section-title">历史探索记录</view>
      </view>

      <!-- 历史列表 -->
      <view v-if="screeningHistory.length > 0">
        <view
          class="history-card"
          v-for="item in screeningHistory"
          :key="item.id"
          @click="viewReport(item)"
        >
          <view class="history-icon" :class="item.risk_level">
            <text class="ph ph-file-text"></text>
          </view>
          <view class="history-info">
            <view class="history-title">{{ gameTypeName(item.game_type) }}能力探索</view>
            <view class="history-time">{{ formatDate(item.created_at) }}</view>
          </view>
          <view class="history-score" v-if="item.score > 0">{{ item.score }}分</view>
          <view class="history-badge" :class="item.risk_level">{{ riskLabel(item.risk_level) }}</view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <view class="empty-icon">
          <text class="ph ph-clock"></text>
        </view>
        <view class="empty-text">暂无历史探索记录</view>
        <view class="empty-hint">完成能力探索后将在这里生成成长报告</view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/screening/index"></tab-bar>

    <!-- 儿童切换弹窗 -->
    <view class="modal-overlay" v-if="showPicker" @click="showPicker = false">
      <view class="picker-sheet" @click.stop>
        <view class="picker-title">选择评测对象</view>
        <view
          v-for="child in children"
          :key="child.id"
          :class="['picker-item', { active: currentChild?.id === child.id }]"
          @click="selectChild(child)"
        >
          <view class="picker-avatar">{{ child.name.charAt(0) }}</view>
          <view class="picker-info">
            <view class="picker-name">{{ child.name }}</view>
            <view class="picker-meta">{{ getAge(child.birth_date) }}岁 / {{ child.grade || '' }}</view>
          </view>
          <text v-if="currentChild?.id === child.id" class="ph ph-check picker-check"></text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import { getChildren } from '../../../api/child.js'
import { getScreeningHistory } from '../../../api/screening.js'
import { getReportByScreening } from '../../../api/report.js'
import TabBar from '../../../components/tab-bar/index.vue'
import { friendlyRiskLevel } from '../../../utils/terminology.js'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      children: [],
      showPicker: false,
      screeningHistory: [],
      qrLoadError: false,
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        this.children = await getChildren()
        const saved = getCurrentChild()
        if (saved) {
          this.currentChild = this.children.find(c => c.id === saved.id) || this.children[0]
        } else if (this.children.length > 0) {
          this.currentChild = this.children[0]
        }
        if (this.currentChild) {
          setCurrentChild(this.currentChild)
          await this.loadHistory()
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadHistory() {
      if (!this.currentChild) return
      try {
        this.screeningHistory = await getScreeningHistory(this.currentChild.id)
      } catch (e) {
        console.error('加载历史失败', e)
      }
    },
    enterChildMode() {
      if (!this.currentChild) {
        uni.showToast({ title: '请先添加孩子档案', icon: 'none' })
        return
      }
      // 确保当前孩子信息已持久化，儿童端可以读取
      setCurrentChild(this.currentChild)
      uni.navigateTo({ url: '/pages/child/child-training/index' })
    },
    getAge(birthDate) {
      if (!birthDate) return '?'
      const birth = new Date(birthDate)
      if (isNaN(birth.getTime())) return '?'
      const today = new Date()
      let age = today.getFullYear() - birth.getFullYear()
      // 如果今年还没过生日，减1
      if (
        today.getMonth() < birth.getMonth() ||
        (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())
      ) {
        age--
      }
      return age < 0 ? '?' : age
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
    },
    gameTypeName(type) {
      if (!type) return '未知'
      const map = {
        visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解',
        working_memory: '工作记忆', rapid_naming: '快速命名', motor_coordination: '精细动作',
        handwriting: '手写汉字', flip_card: '翻牌记忆', connect_game: '连一连',
      }
      return map[type] || type
    },
    riskLabel(level) {
      return friendlyRiskLevel(level)
    },
    showChildPicker() {
      this.showPicker = true
    },
    selectChild(child) {
      this.currentChild = child
      setCurrentChild(child)
      this.showPicker = false
      this.screeningHistory = []
      this.loadHistory()
    },
    async viewReport(screening) {
      try {
        const report = await getReportByScreening(screening.id)
        uni.navigateTo({ url: `/pages/parent/report/detail?id=${report.id}` })
      } catch (e) {
        uni.navigateTo({ url: `/pages/parent/report/index?child_id=${this.currentChild.id}` })
      }
    },
  }
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; padding-bottom: 160rpx; overflow-x: hidden; }

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255, 255, 255, 0.95); padding: 56rpx 32rpx 20rpx; display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}
.header-title { font-size: 36rpx; font-weight: 800; color: #2D3748; }
.header-action .ph { font-size: 32rpx; color: #A0AEC0; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

/* 孩子信息卡 */
.child-info-card {
  display: flex; align-items: center; gap: 20rpx; background: #FFFFFF;
  border-radius: 20rpx; padding: 24rpx; margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
.child-avatar {
  width: 80rpx; height: 80rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
}
.child-avatar .ph { font-size: 40rpx; color: #4F9EF8; }
.child-details { flex: 1; }
.child-label { font-size: 20rpx; color: #A0AEC0; margin-bottom: 4rpx; font-weight: 500; }
.child-name { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.child-meta { font-size: 20rpx; font-weight: 500; color: #A0AEC0; margin-left: 12rpx; }
.switch-btn {
  font-size: 24rpx; font-weight: 700; color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE); padding: 8rpx 20rpx; border-radius: 12rpx;
}

/* 无孩子提示 */
.no-child-tip {
  display: flex; align-items: center; gap: 12rpx;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border-radius: 16rpx; padding: 20rpx 24rpx; margin-bottom: 24rpx;
  font-size: 22rpx; color: #92400E; font-weight: 500;
}
.no-child-tip .ph { font-size: 28rpx; color: #F59E0B; flex-shrink: 0; }

/* 进入儿童模式大卡片 */
.handover-card {
  background: linear-gradient(135deg, #3B82F6, #4F9EF8);
  border-radius: 24rpx;
  padding: 36rpx 32rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.35);
  transition: all 0.2s;
}
.handover-card:active { transform: scale(0.98); }

.handover-decoration {
  position: absolute;
  right: -40rpx; top: -40rpx;
  width: 200rpx; height: 200rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
}

.handover-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
  flex: 1;
  position: relative;
  z-index: 1;
}

.handover-icon {
  width: 88rpx; height: 88rpx;
  border-radius: 22rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.handover-icon .ph { font-size: 44rpx; color: #FFFFFF; }

.handover-text { flex: 1; }
.handover-title { font-size: 32rpx; font-weight: 800; color: #FFFFFF; margin-bottom: 8rpx; }
.handover-desc { font-size: 22rpx; color: rgba(255, 255, 255, 0.8); line-height: 1.5; font-weight: 500; }

.handover-arrow {
  position: relative; z-index: 1;
  width: 56rpx; height: 56rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.handover-arrow .ph { font-size: 28rpx; color: #FFFFFF; }

/* 说明卡片 */
.tips-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}
.tips-row {
  display: flex; align-items: center; gap: 16rpx;
}
.tips-icon {
  width: 52rpx; height: 52rpx; border-radius: 14rpx;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.tips-icon .ph { font-size: 26rpx; }
.tips-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.tips-icon.blue .ph { color: #4F9EF8; }
.tips-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.tips-icon.green .ph { color: #22C55E; }
.tips-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.tips-icon.orange .ph { color: #F57F17; }
.tips-text { font-size: 24rpx; color: #718096; font-weight: 500; line-height: 1.5; }

/* 读写能力风险筛查二维码卡片 */
.screening-qr-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.05);
  border: 2rpx solid #EDE9FE;
}

.qr-card-header { margin-bottom: 20rpx; }

.qr-badge {
  display: inline-block;
  background: linear-gradient(135deg, #7C3AED, #A78BFA);
  color: #FFFFFF;
  font-size: 18rpx;
  font-weight: 700;
  padding: 4rpx 16rpx;
  border-radius: 9999rpx;
  margin-bottom: 10rpx;
  letter-spacing: 1rpx;
}

.qr-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
}

.qr-desc {
  font-size: 22rpx;
  color: #718096;
  line-height: 1.6;
  font-weight: 500;
}

.qr-body {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-bottom: 16rpx;
}

.qr-image-wrap {
  width: 180rpx;
  height: 180rpx;
  flex-shrink: 0;
  border-radius: 16rpx;
  overflow: hidden;
  background: #F5F7FA;
  border: 2rpx solid #E5E7EB;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.qr-image {
  width: 100%;
  height: 100%;
}

.qr-placeholder {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.qr-placeholder .ph {
  font-size: 60rpx;
  color: #A78BFA;
}

.qr-placeholder-text {
  font-size: 18rpx;
  color: #A0AEC0;
  font-weight: 600;
}

.qr-tips {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 14rpx;
}

.qr-tip-row {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.qr-tip-icon {
  font-size: 24rpx;
  color: #7C3AED;
  flex-shrink: 0;
}

.qr-tip-text {
  font-size: 22rpx;
  color: #4A5568;
  font-weight: 500;
}

.qr-footer {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
  background: #F9FAFB;
  border-radius: 12rpx;
  padding: 12rpx 16rpx;
}

.qr-footer .ph {
  font-size: 22rpx;
  color: #A78BFA;
  flex-shrink: 0;
}

/* 区域标题 */
.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
}
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }

/* 历史记录 */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 64rpx 40rpx; opacity: 0.7; }
.empty-icon { width: 100rpx; height: 100rpx; border-radius: 50%; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-bottom: 20rpx; }
.empty-icon .ph { font-size: 48rpx; color: #D1D5DB; }
.empty-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
.empty-hint { font-size: 22rpx; color: #D1D5DB; margin-top: 6rpx; font-weight: 500; }

.history-card {
  background: #FFFFFF; border-radius: 20rpx; padding: 24rpx; margin-bottom: 12rpx;
  display: flex; align-items: center; gap: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03); transition: all 0.2s;
}
.history-card:active { transform: scale(0.98); }
.history-icon { width: 64rpx; height: 64rpx; border-radius: 16rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.history-icon.low { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.history-icon.low .ph { color: #22C55E; }
.history-icon.medium { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.history-icon.medium .ph { color: #F57F17; }
.history-icon.high { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); }
.history-icon.high .ph { color: #FF6B6B; }
.history-icon .ph { font-size: 30rpx; }
.history-info { flex: 1; }
.history-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.history-time { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.history-score { font-size: 26rpx; font-weight: 700; color: #2D3748; margin-right: 8rpx; }
.history-badge { font-size: 20rpx; font-weight: 700; padding: 6rpx 16rpx; border-radius: 10rpx; }
.history-badge.low { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); color: #22C55E; }
.history-badge.medium { background: linear-gradient(135deg, #FFF9C4, #FFE082); color: #F57F17; }
.history-badge.high { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); color: #FF6B6B; }

/* 儿童切换弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4); z-index: 9999;
  display: flex; justify-content: center; align-items: flex-end;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.picker-sheet {
  background: #FFFFFF; width: 100%; border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx 32rpx calc(32rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
.picker-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 24rpx; text-align: center; }
.picker-item { display: flex; align-items: center; gap: 20rpx; padding: 20rpx; border-radius: 16rpx; margin-bottom: 12rpx; transition: all 0.2s; }
.picker-item.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.picker-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: linear-gradient(135deg, #DBEAFE, #BFDBFE); display: flex; align-items: center; justify-content: center; font-size: 26rpx; font-weight: 700; color: #4F9EF8; }
.picker-info { flex: 1; }
.picker-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.picker-meta { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.picker-check { font-size: 28rpx; color: #4F9EF8; }
</style>
