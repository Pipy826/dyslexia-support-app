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
          <view class="child-name">
            {{ currentChild ? currentChild.name : '未选择' }}
            <text class="child-meta" v-if="currentChild">{{ getAge(currentChild.birth_date) }}岁 / {{ currentChild.grade || '' }}</text>
          </view>
        </view>
        <view class="switch-btn" @click="showChildPicker" v-if="children.length > 1">切换</view>
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
            <view class="history-title">{{ gameTypeName(item.game_type) }}筛查</view>
            <view class="history-time">{{ formatDate(item.created_at) }}</view>
          </view>
          <view class="history-score" v-if="item.score !== undefined">{{ item.score }}分</view>
          <view class="history-badge" :class="item.risk_level">{{ riskLabel(item.risk_level) }}</view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <view class="empty-icon">
          <text class="ph ph-clock"></text>
        </view>
        <view class="empty-text">暂无历史筛查记录</view>
        <view class="empty-hint">完成初筛后将在这里生成成长报告</view>
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
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import { getChildren } from '../../../api/child.js'
import { getScreeningHistory } from '../../../api/screening.js'
import { getReportByScreening } from '../../../api/report.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      children: [],
      showModal: false,
      showPicker: false,
      screeningHistory: []
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
    getAge(birthDate) {
      if (!birthDate) return '?'
      return new Date().getFullYear() - new Date(birthDate).getFullYear()
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
    },
    gameTypeName(type) {
      return { visual: '视觉辨识', spelling: '拼字识别', comprehension: '文字理解' }[type] || type
    },
    riskLabel(level) {
      return { low: '低风险', medium: '中风险', high: '高风险' }[level] || '未知'
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
        // 报告不存在时跳到报告列表页
        uni.navigateTo({ url: `/pages/parent/report/index?child_id=${this.currentChild.id}` })
      }
    },
    showHandoverModal() {
      if (!this.currentChild) {
        uni.showToast({ title: '请先添加孩子档案', icon: 'none' })
        return
      }
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
/* 创意筛查页面 */
.page-container { min-height: 100vh; background: #F5F7FA; padding-bottom: 160rpx; }

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(20rpx);
  padding: 56rpx 32rpx 20rpx; display: flex; justify-content: space-between; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}
.header-title { font-size: 36rpx; font-weight: 800; color: #2D3748; }
.header-action .ph { font-size: 32rpx; color: #A0AEC0; }

.page-content { padding: 24rpx 32rpx; }

.child-info-card {
  display: flex; align-items: center; gap: 20rpx; background: #FFFFFF;
  border-radius: 20rpx; padding: 24rpx; margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
.child-avatar {
  width: 80rpx; height: 80rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(79, 158, 248, 0.15);
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

.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
  display: flex; align-items: center; gap: 8rpx;
}
.section-title::before {
  content: ''; display: inline-block; width: 4rpx; height: 22rpx;
  background: linear-gradient(180deg, #4F9EF8, #A78BFA); border-radius: 2rpx;
}

.screening-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 32rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}
.screening-header { display: flex; gap: 20rpx; margin-bottom: 28rpx; }
.screening-icon { width: 80rpx; height: 80rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.screening-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.screening-icon.blue .ph { font-size: 40rpx; color: #4F9EF8; }
.screening-info { flex: 1; }
.screening-name { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 6rpx; }
.screening-desc { font-size: 22rpx; color: #718096; line-height: 1.5; font-weight: 500; }

.notice-box { background: #F8FAFF; border-radius: 16rpx; padding: 24rpx; margin-bottom: 28rpx; border: 1rpx solid #E5E7EB; }
.notice-title { font-size: 20rpx; font-weight: 700; color: #718096; margin-bottom: 12rpx; display: flex; align-items: center; gap: 6rpx; }
.notice-title .ph { color: #F57F17; font-size: 24rpx; }
.notice-list { list-style: none; padding: 0; margin: 0; }
.notice-list li { font-size: 22rpx; color: #718096; line-height: 1.8; display: flex; align-items: flex-start; gap: 12rpx; font-weight: 500; }
.notice-list li::before { content: ''; width: 6rpx; height: 6rpx; border-radius: 50%; background: #A0AEC0; margin-top: 14rpx; flex-shrink: 0; }
.notice-list li.highlight { color: #F57F17; font-weight: 600; }
.notice-list li.highlight::before { background: #F57F17; }

.start-btn {
  width: 100%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2); transition: all 0.2s;
}
.start-btn:active { transform: scale(0.97); }

.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 64rpx 40rpx; opacity: 0.7; }
.empty-icon { width: 100rpx; height: 100rpx; border-radius: 50%; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-bottom: 20rpx; }
.empty-icon .ph { font-size: 48rpx; color: #D1D5DB; }
.empty-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
.empty-hint { font-size: 22rpx; color: #D1D5DB; margin-top: 6rpx; font-weight: 500; }

.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(4rpx); z-index: 9999;
  display: flex; justify-content: center; align-items: flex-end; padding-bottom: 48rpx;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-content {
  background: #FFFFFF; width: 90%; max-width: 600rpx; border-radius: 32rpx; padding: 40rpx;
  display: flex; flex-direction: column; align-items: center;
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes slideUp { from { opacity: 0; transform: translateY(40rpx); } to { opacity: 1; transform: translateY(0); } }

.modal-icon {
  width: 100rpx; height: 100rpx; border-radius: 24rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center; margin-bottom: 24rpx;
}
.modal-icon .ph { font-size: 52rpx; color: #4F9EF8; }
.modal-title { font-size: 32rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; text-align: center; }
.modal-desc { font-size: 24rpx; color: #718096; text-align: center; line-height: 1.6; margin-bottom: 32rpx; font-weight: 500; }
.modal-btn { width: 100%; border-radius: 16rpx; padding: 26rpx; font-size: 26rpx; font-weight: 700; margin-bottom: 16rpx; transition: all 0.2s; }
.modal-btn:active { transform: scale(0.97); }
.modal-btn.primary { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2); }
.modal-btn.secondary { background: #F5F5F5; color: #718096; }

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

.picker-sheet {
  background: #FFFFFF; width: 100%; border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx 32rpx calc(32rpx + env(safe-area-inset-bottom));
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.picker-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 24rpx; text-align: center; }
.picker-item { display: flex; align-items: center; gap: 20rpx; padding: 20rpx; border-radius: 16rpx; margin-bottom: 12rpx; transition: all 0.2s; }
.picker-item.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.picker-avatar { width: 64rpx; height: 64rpx; border-radius: 50%; background: linear-gradient(135deg, #DBEAFE, #BFDBFE); display: flex; align-items: center; justify-content: center; font-size: 26rpx; font-weight: 700; color: #4F9EF8; }
.picker-info { flex: 1; }
.picker-name { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.picker-meta { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.picker-check { font-size: 28rpx; color: #4F9EF8; }
</style>
