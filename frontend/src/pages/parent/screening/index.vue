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

      <!-- 无孩子档案提示 -->
      <view class="no-child-tip" v-if="!currentChild">
        <text class="ph ph-info"></text>
        <text>请先添加孩子档案，以获取个性化推荐筛查项目</text>
      </view>

      <!-- 推荐筛查项目区 -->
      <view class="section-title">推荐筛查项目</view>
      <view class="recommended-grid">
        <view
          class="game-card"
          v-for="gameType in getRecommendedGames(currentChild ? currentChild.grade : null)"
          :key="gameType"
          @click="showHandoverModal(gameType)"
          :style="{ '--card-color': gameTypeColor(gameType) }"
        >
          <view class="game-card-icon" :style="{ background: gameTypeColorBg(gameType) }">
            <text :class="['ph', gameTypeIcon(gameType)]" :style="{ color: gameTypeColor(gameType) }"></text>
          </view>
          <view class="game-card-body">
            <view class="game-card-name">{{ gameTypeName(gameType) }}</view>
            <view class="game-card-desc">{{ gameTypeDesc(gameType) }}</view>
          </view>
          <view class="game-card-arrow">
            <text class="ph ph-caret-right" :style="{ color: gameTypeColor(gameType) }"></text>
          </view>
        </view>
      </view>

      <!-- 自定义筛查折叠区 -->
      <view class="custom-section">
        <view class="custom-header" @click="showCustomPicker = !showCustomPicker">
          <view class="section-title" style="margin-bottom: 0;">自定义筛查</view>
          <view class="custom-toggle">
            <text :class="['ph', showCustomPicker ? 'ph-caret-up' : 'ph-caret-down']"></text>
          </view>
        </view>

        <view class="custom-grid" v-if="showCustomPicker">
          <template v-for="gameType in ALL_GAME_TYPES" :key="gameType">
            <view
              class="game-card custom-card"
              v-if="!(getGradeGroup(currentChild ? currentChild.grade : null) === 'preschool' && gameType === 'spelling')"
              @click="showHandoverModal(gameType)"
              :style="{ '--card-color': gameTypeColor(gameType) }"
            >
              <view class="game-card-icon" :style="{ background: gameTypeColorBg(gameType) }">
                <text :class="['ph', gameTypeIcon(gameType)]" :style="{ color: gameTypeColor(gameType) }"></text>
              </view>
              <view class="game-card-body">
                <view class="game-card-name">{{ gameTypeName(gameType) }}</view>
                <view class="game-card-desc">{{ gameTypeDesc(gameType) }}</view>
              </view>
              <view class="game-card-arrow">
                <text class="ph ph-caret-right" :style="{ color: gameTypeColor(gameType) }"></text>
              </view>
            </view>
          </template>
        </view>
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
          <view class="history-score" v-if="item.score > 0">{{ item.score }}分</view>
          <view class="history-badge" :class="item.risk_level">{{ riskLabel(item.risk_level) }}</view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-else>
        <view class="empty-icon">
          <text class="ph ph-clock"></text>
        </view>
        <view class="empty-text">暂无历史筛查记录</view>
        <view class="empty-hint">完成筛查后将在这里生成成长报告</view>
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
        <view class="modal-icon" :style="{ background: gameTypeColorBg(selectedGameType) }">
          <text :class="['ph', gameTypeIcon(selectedGameType)]" :style="{ color: gameTypeColor(selectedGameType), fontSize: '52rpx' }"></text>
        </view>
        <view class="modal-title">请把手机交给孩子</view>
        <view class="modal-game-tag" :style="{ background: gameTypeColorBg(selectedGameType), color: gameTypeColor(selectedGameType) }">
          {{ gameTypeName(selectedGameType) }}
        </view>
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

const RECOMMENDED_GAMES = {
  preschool:     ['visual', 'working_memory', 'motor_coordination'],
  lower_primary: ['visual', 'spelling', 'comprehension', 'rapid_naming'],
  upper_primary: ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming'],
}

const ALL_GAME_TYPES = ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      children: [],
      showModal: false,
      showPicker: false,
      showCustomPicker: false,
      screeningHistory: [],
      selectedGameType: null,
      ALL_GAME_TYPES,
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
    getGradeGroup(grade) {
      if (!grade) return 'lower_primary'
      const preschool = ['幼儿园', '学前', 'preschool']
      const lower = ['一年级', '二年级', 'grade_1', 'grade_2']
      const upper = ['三年级', '四年级', '五年级', '六年级', 'grade_3', 'grade_4', 'grade_5', 'grade_6']
      if (preschool.includes(grade)) return 'preschool'
      if (lower.includes(grade)) return 'lower_primary'
      if (upper.includes(grade)) return 'upper_primary'
      return 'lower_primary'
    },
    getRecommendedGames(grade) {
      const group = this.getGradeGroup(grade)
      return RECOMMENDED_GAMES[group] || RECOMMENDED_GAMES.lower_primary
    },
    gameTypeName(type) {
      const map = {
        visual: '视觉辨识',
        spelling: '拼字识别',
        comprehension: '文字理解',
        working_memory: '工作记忆',
        rapid_naming: '快速命名',
        motor_coordination: '精细动作',
      }
      return map[type] || type
    },
    gameTypeIcon(type) {
      const map = {
        visual: 'ph-eye',
        spelling: 'ph-text-aa',
        comprehension: 'ph-book-open',
        working_memory: 'ph-brain',
        rapid_naming: 'ph-lightning',
        motor_coordination: 'ph-hand',
      }
      return map[type] || 'ph-game-controller'
    },
    gameTypeDesc(type) {
      const map = {
        visual: '通过图形辨别训练，评估视觉感知与注意力集中能力',
        spelling: '识别汉字笔画与字形，评估拼写与字形记忆能力',
        comprehension: '阅读短文并回答问题，评估语义理解与信息提取能力',
        working_memory: '记忆并复现序列信息，评估短时记忆与工作记忆容量',
        rapid_naming: '快速识别并命名图形或文字，评估命名速度与音韵意识',
        motor_coordination: '判断图形线条整齐度，评估精细动作控制与视动整合',
      }
      return map[type] || ''
    },
    gameTypeColor(type) {
      const map = {
        visual: '#4F9EF8',
        spelling: '#A78BFA',
        comprehension: '#22C55E',
        working_memory: '#F97316',
        rapid_naming: '#EAB308',
        motor_coordination: '#EC4899',
      }
      return map[type] || '#4F9EF8'
    },
    gameTypeColorBg(type) {
      const map = {
        visual: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)',
        spelling: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)',
        comprehension: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)',
        working_memory: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)',
        rapid_naming: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)',
        motor_coordination: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)',
      }
      return map[type] || 'linear-gradient(135deg, #EFF6FF, #DBEAFE)'
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
        uni.navigateTo({ url: `/pages/parent/report/index?child_id=${this.currentChild.id}` })
      }
    },
    showHandoverModal(gameType) {
      if (!this.currentChild) {
        uni.showToast({ title: '请先添加孩子档案', icon: 'none' })
        return
      }
      this.selectedGameType = gameType
      this.showModal = true
    },
    hideModal() {
      this.showModal = false
    },
    transferToChild() {
      this.showModal = false
      const gradeParam = this.currentChild?.grade ? `&grade=${encodeURIComponent(this.currentChild.grade)}` : ''
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${this.selectedGameType}${gradeParam}`
      })
    }
  }
}
</script>

<style scoped>
/* 筛查页面 */
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

/* 无孩子提示 */
.no-child-tip {
  display: flex; align-items: center; gap: 12rpx;
  background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
  border-radius: 16rpx; padding: 20rpx 24rpx; margin-bottom: 24rpx;
  font-size: 22rpx; color: #92400E; font-weight: 500;
}
.no-child-tip .ph { font-size: 28rpx; color: #F59E0B; flex-shrink: 0; }

/* 区域标题 */
.section-title {
  font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx;
  display: flex; align-items: center; gap: 8rpx;
}
.section-title::before {
  content: ''; display: inline-block; width: 4rpx; height: 22rpx;
  background: linear-gradient(180deg, #4F9EF8, #A78BFA); border-radius: 2rpx;
}

/* 推荐游戏卡片列表 */
.recommended-grid { display: flex; flex-direction: column; gap: 12rpx; margin-bottom: 24rpx; }

.game-card {
  background: #FFFFFF; border-radius: 20rpx; padding: 24rpx;
  display: flex; align-items: center; gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
  border-left: 4rpx solid var(--card-color, #4F9EF8);
}
.game-card:active { transform: scale(0.98); box-shadow: 0 1rpx 6rpx rgba(0, 0, 0, 0.06); }

.game-card-icon {
  width: 80rpx; height: 80rpx; border-radius: 20rpx;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.game-card-icon .ph { font-size: 40rpx; }

.game-card-body { flex: 1; min-width: 0; }
.game-card-name { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 6rpx; }
.game-card-desc { font-size: 22rpx; color: #718096; line-height: 1.5; font-weight: 500; }

.game-card-arrow .ph { font-size: 28rpx; }

/* 自定义筛查区 */
.custom-section {
  background: #FFFFFF; border-radius: 20rpx; padding: 24rpx;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}
.custom-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0;
}
.custom-toggle .ph { font-size: 28rpx; color: #A0AEC0; }

.custom-grid {
  display: flex; flex-direction: column; gap: 12rpx;
  margin-top: 16rpx; padding-top: 16rpx;
  border-top: 1rpx solid #F0F0F0;
}
.custom-card {
  box-shadow: none;
  background: #FAFAFA;
  border-radius: 16rpx;
}

/* 历史记录 */
.section-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16rpx; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 64rpx 40rpx; opacity: 0.7; }
.empty-icon { width: 100rpx; height: 100rpx; border-radius: 50%; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-bottom: 20rpx; }
.empty-icon .ph { font-size: 48rpx; color: #D1D5DB; }
.empty-text { font-size: 26rpx; color: #A0AEC0; font-weight: 600; }
.empty-hint { font-size: 22rpx; color: #D1D5DB; margin-top: 6rpx; font-weight: 500; }

/* 弹窗 */
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
  display: flex; align-items: center; justify-content: center; margin-bottom: 20rpx;
}
.modal-title { font-size: 32rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; text-align: center; }
.modal-game-tag {
  font-size: 22rpx; font-weight: 700; padding: 8rpx 24rpx; border-radius: 20rpx;
  margin-bottom: 16rpx;
}
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

/* 儿童切换弹窗 */
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
