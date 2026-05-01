<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">专业支持引导</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <view class="loading-spinner"></view>
        <view class="loading-text">正在分析孩子情况...</view>
      </view>

      <template v-else-if="guidance">
        <!-- 是否需要专业支持 -->
        <view class="status-card" :class="urgencyClass">
          <view class="status-icon">
            <text :class="['ph', urgencyIcon]"></text>
          </view>
          <view class="status-info">
            <view class="status-title">{{ urgencyTitle }}</view>
            <view class="status-desc">{{ urgencyDesc }}</view>
          </view>
        </view>

        <!-- AI 引导内容 -->
        <view class="section-title">专业建议</view>
        <view class="guidance-card">
          <view class="guidance-header">
            <view class="guidance-avatar">
              <text class="ph-fill ph-robot"></text>
            </view>
            <view class="guidance-title">AI 专业引导</view>
          </view>
          <view class="guidance-text">{{ guidance.guidance }}</view>
        </view>

        <!-- 家长准备清单 -->
        <view class="section-title" v-if="guidance.checklist && guidance.checklist.length > 0">
          就诊前准备清单
        </view>
        <view class="checklist-card" v-if="guidance.checklist && guidance.checklist.length > 0">
          <view
            class="checklist-item"
            v-for="(item, i) in guidance.checklist"
            :key="i"
            @click="toggleCheck(i)"
          >
            <view :class="['check-box', { checked: checkedItems[i] }]">
              <text class="ph ph-check" v-if="checkedItems[i]"></text>
            </view>
            <view class="check-text" :class="{ done: checkedItems[i] }">{{ item }}</view>
          </view>
          <view class="checklist-progress">
            已准备 {{ checkedCount }}/{{ guidance.checklist.length }} 项
          </view>
        </view>

        <!-- 推荐机构类型 -->
        <view class="section-title" v-if="guidance.suggested_institutions && guidance.suggested_institutions.length > 0">
          可寻求的专业机构
        </view>
        <view class="institutions-card" v-if="guidance.suggested_institutions && guidance.suggested_institutions.length > 0">
          <view
            class="institution-item"
            v-for="(inst, i) in guidance.suggested_institutions"
            :key="i"
          >
            <view class="inst-icon">
              <text class="ph ph-hospital"></text>
            </view>
            <view class="inst-name">{{ inst }}</view>
          </view>
        </view>

        <!-- 继续家庭训练提示（低紧迫度时） -->
        <view class="continue-card" v-if="guidance.urgency === 'low'">
          <text class="ph ph-heart continue-icon"></text>
          <view class="continue-text">
            目前可以继续家庭训练，坚持每天完成任务，定期复评观察变化。如有疑问，随时可以咨询 AI 助手。
          </view>
        </view>

        <!-- 底部操作 -->
        <view class="bottom-actions">
          <button class="ai-chat-btn" @click="goToAiChat">
            <text class="ph ph-chat-circle-dots"></text> 继续咨询 AI
          </button>
          <button class="screening-btn" @click="goToScreening">
            <text class="ph ph-play"></text> 发起复评
          </button>
        </view>
      </template>

      <!-- 无报告 -->
      <view class="empty-state" v-else-if="!loading">
        <text class="ph ph-file-text empty-icon"></text>
        <view class="empty-title">暂无探索数据</view>
        <view class="empty-desc">请先完成一次能力探索，系统将根据结果为您提供专业支持建议。</view>
        <button class="empty-btn" @click="goToScreening">开始能力探索</button>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { getProfessionalGuidance } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      childId: null,
      guidance: null,
      loading: false,
      checkedItems: {},
    }
  },
  onLoad(options) {
    if (options.child_id) {
      this.childId = parseInt(options.child_id)
    } else {
      const child = getCurrentChild()
      this.childId = child?.id
    }
    if (this.childId) this.loadGuidance()
  },
  computed: {
    urgencyClass() {
      const map = { high: 'red', medium: 'orange', low: 'green' }
      return map[this.guidance?.urgency] || 'blue'
    },
    urgencyIcon() {
      const map = { high: 'ph-warning-circle', medium: 'ph-info', low: 'ph-check-circle' }
      return map[this.guidance?.urgency] || 'ph-info'
    },
    urgencyTitle() {
      const map = {
        high: '建议尽快寻求专业支持',
        medium: '建议考虑专业评估',
        low: '目前可继续家庭训练',
      }
      return map[this.guidance?.urgency] || ''
    },
    urgencyDesc() {
      const map = {
        high: '根据当前评估结果，建议尽快联系专业机构进行全面评估',
        medium: '训练一段时间后改善不明显，可考虑寻求专业支持',
        low: '孩子情况稳定，继续坚持家庭训练即可',
      }
      return map[this.guidance?.urgency] || ''
    },
    checkedCount() {
      return Object.values(this.checkedItems).filter(Boolean).length
    },
  },
  methods: {
    async loadGuidance() {
      this.loading = true
      try {
        this.guidance = await getProfessionalGuidance(this.childId)
      } catch (e) {
        console.error('加载专业引导失败', e)
      } finally {
        this.loading = false
      }
    },
    toggleCheck(index) {
      this.checkedItems = { ...this.checkedItems, [index]: !this.checkedItems[index] }
    },
    goBack() { uni.navigateBack() },
    goToAiChat() {
      uni.navigateTo({ url: `/pages/parent/ai-chat/index?child_id=${this.childId}` })
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center;
  box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

/* 加载 */
.loading-state {
  display: flex; flex-direction: column; align-items: center; padding: 100rpx 0; gap: 20rpx;
}
.loading-spinner {
  width: 64rpx; height: 64rpx; border: 5rpx solid #DBEAFE; border-top-color: #4F9EF8;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-size: 26rpx; color: #4F9EF8; font-weight: 600; }

/* 状态卡片 */
.status-card {
  border-radius: 24rpx; padding: 28rpx;
  display: flex; align-items: center; gap: 20rpx;
  margin-bottom: 24rpx;
}
.status-card.red { background: linear-gradient(135deg, #FFF5F5, #FFE4E4); border: 2rpx solid #FECACA; }
.status-card.orange { background: linear-gradient(135deg, #FFFBEB, #FEF3C7); border: 2rpx solid #FDE68A; }
.status-card.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); border: 2rpx solid #BBF7D0; }
.status-card.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border: 1rpx solid #BFDBFE; }

.status-icon {
  width: 80rpx; height: 80rpx; border-radius: 20rpx;
  background: rgba(255,255,255,0.7);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.status-card.red .status-icon .ph { font-size: 40rpx; color: #FF6B6B; }
.status-card.orange .status-icon .ph { font-size: 40rpx; color: #F57F17; }
.status-card.green .status-icon .ph { font-size: 40rpx; color: #22C55E; }
.status-card.blue .status-icon .ph { font-size: 40rpx; color: #4F9EF8; }

.status-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 6rpx; }
.status-desc { font-size: 22rpx; color: #718096; line-height: 1.5; font-weight: 500; }

/* 区域标题 */
.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
}

/* AI 引导卡片 */
.guidance-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 24rpx; padding: 28rpx; margin-bottom: 24rpx; border: 1rpx solid #BFDBFE;
}
.guidance-header { display: flex; align-items: center; gap: 14rpx; margin-bottom: 20rpx; }
.guidance-avatar {
  width: 52rpx; height: 52rpx; border-radius: 14rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex; align-items: center; justify-content: center;
}
.guidance-avatar .ph { font-size: 26rpx; color: #FFFFFF; }
.guidance-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.guidance-text { font-size: 26rpx; color: #2D3748; line-height: 1.8; font-weight: 500; }

/* 准备清单 */
.checklist-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 28rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}
.checklist-item {
  display: flex; align-items: flex-start; gap: 16rpx;
  padding: 16rpx 0; border-bottom: 1rpx solid #F5F5F5;
}
.checklist-item:last-of-type { border-bottom: none; }
.check-box {
  width: 36rpx; height: 36rpx; border-radius: 10rpx; border: 2rpx solid #D1D5DB;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2rpx;
  transition: all 0.2s;
}
.check-box.checked { background: #4F9EF8; border-color: #4F9EF8; }
.check-box .ph { font-size: 20rpx; color: #FFFFFF; }
.check-text { font-size: 26rpx; color: #2D3748; line-height: 1.6; font-weight: 500; }
.check-text.done { color: #A0AEC0; text-decoration: line-through; }
.checklist-progress {
  font-size: 22rpx; color: #4F9EF8; font-weight: 700; text-align: right; margin-top: 16rpx;
}

/* 机构列表 */
.institutions-card {
  background: #FFFFFF; border-radius: 24rpx; padding: 24rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
  display: flex; flex-direction: column; gap: 16rpx;
}
.institution-item { display: flex; align-items: center; gap: 16rpx; }
.inst-icon {
  width: 52rpx; height: 52rpx; border-radius: 14rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.inst-icon .ph { font-size: 26rpx; color: #4F9EF8; }
.inst-name { font-size: 26rpx; font-weight: 600; color: #2D3748; }

/* 继续训练提示 */
.continue-card {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  border-radius: 24rpx; padding: 28rpx; margin-bottom: 24rpx;
  border: 1rpx solid #BBF7D0;
  display: flex; align-items: flex-start; gap: 16rpx;
}
.continue-icon { font-size: 32rpx; color: #22C55E; flex-shrink: 0; margin-top: 2rpx; }
.continue-text { font-size: 26rpx; color: #2D3748; line-height: 1.7; font-weight: 500; }

/* 底部操作 */
.bottom-actions { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.ai-chat-btn {
  flex: 1; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; padding: 24rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.2);
}
.ai-chat-btn .ph { font-size: 24rpx; }
.screening-btn {
  flex: 1; background: #FFFFFF; border: 2rpx solid #BFDBFE; color: #4F9EF8;
  border-radius: 16rpx; padding: 24rpx; font-size: 24rpx; font-weight: 700;
  display: flex; align-items: center; justify-content: center; gap: 8rpx;
}
.screening-btn .ph { font-size: 24rpx; }

/* 空状态 */
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 100rpx 40rpx; }
.empty-icon { font-size: 80rpx; color: #D1D5DB; margin-bottom: 24rpx; }
.empty-title { font-size: 32rpx; font-weight: 700; color: #2D3748; margin-bottom: 12rpx; }
.empty-desc { font-size: 24rpx; color: #A0AEC0; text-align: center; line-height: 1.6; margin-bottom: 40rpx; }
.empty-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 16rpx; padding: 22rpx 56rpx; font-size: 26rpx; font-weight: 700;
}

/* 训练页专业引导卡片样式 */
.professional-card {
  background: linear-gradient(135deg, #FFF5F5, #FFE4E4);
  border-radius: 20rpx; padding: 24rpx 28rpx; margin-bottom: 24rpx;
  display: flex; align-items: center; justify-content: space-between;
  border: 1rpx solid #FECACA; transition: all 0.2s;
}
.professional-card:active { transform: scale(0.98); }
.professional-left { display: flex; align-items: center; gap: 20rpx; }
.professional-icon {
  width: 68rpx; height: 68rpx; border-radius: 16rpx;
  background: rgba(255,255,255,0.7);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.professional-icon .ph { font-size: 36rpx; color: #FF6B6B; }
.professional-title { font-size: 28rpx; font-weight: 700; color: #2D3748; }
.professional-sub { font-size: 20rpx; color: #A0AEC0; margin-top: 3rpx; font-weight: 500; }
.professional-arrow { font-size: 32rpx; color: #FF6B6B; }
</style>
