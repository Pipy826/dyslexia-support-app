<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="header-title">干预与训练</view>
      <view class="header-subtitle">已为{{ currentChild ? currentChild.name : '孩子' }}定制专属的家庭提升计划</view>
    </view>

    <view class="page-content">
      <!-- AI 生成训练计划入口 -->
      <view class="ai-plan-banner" @click="showAiPlanModal">
        <view class="ai-plan-left">
          <view class="ai-plan-icon">
            <text class="ph-fill ph-robot"></text>
          </view>
          <view class="ai-plan-text">
            <view class="ai-plan-title">AI 智能训练计划</view>
            <view class="ai-plan-sub">根据筛查报告，一键生成专属方案</view>
          </view>
        </view>
        <text class="ph ph-arrow-right ai-plan-arrow"></text>
      </view>

      <!-- 今日进度概览 -->
      <view class="today-card">
        <view class="today-decoration"></view>
        <view class="today-header">
          <view class="today-info">
            <view class="today-title">今日任务表</view>
            <view class="today-meta">预计用时 15 分钟</view>
          </view>
          <view class="today-count">
            <view class="count-ring">{{ completedCount }}/{{ totalCount }}</view>
          </view>
        </view>

        <!-- 家长陪伴贴士 -->
        <view class="tips-box">
          <text class="ph ph-heart"></text>
          <view class="tips-text">家长请在旁陪伴，当孩子遇到困难时多给予鼓励，<text class="bold">切勿直接给出答案或指责</text>。</view>
        </view>
      </view>

      <!-- 任务列表 -->
      <view class="section-title">待完成的任务</view>
      <view class="task-list" v-if="pendingTasks.length > 0">
        <view
          class="task-card"
          v-for="task in pendingTasks"
          :key="task.id"
          :class="{ completed: task.status === 'completed' }"
        >
          <view class="task-icon" :class="taskColor(task.task_type)">
            <text :class="'ph ' + taskIcon(task.task_type)"></text>
          </view>
          <view class="task-info">
            <view class="task-name">{{ task.task_name || task.task_type }}</view>
            <view class="task-desc">{{ taskDesc(task.task_type) }}</view>
          </view>
          <button
            class="task-btn"
            :class="{ done: task.status === 'completed' }"
            @click="startTask(task)"
            :disabled="task.status === 'completed'"
          >{{ task.status === 'completed' ? '已完成' : '去完成' }}</button>
        </view>
      </view>
      <view class="task-list" v-else>
        <view class="task-card">
          <view class="task-icon orange"><text class="ph ph-eye"></text></view>
          <view class="task-info">
            <view class="task-name">火眼金睛 (视觉训练)</view>
            <view class="task-desc">提升形近字辨识能力</view>
          </view>
          <button class="task-btn" @click="startTask({ task_type: 'visual', status: 'pending' })">去完成</button>
        </view>
        <view class="task-card">
          <view class="task-icon blue"><text class="ph ph-puzzle-piece"></text></view>
          <view class="task-info">
            <view class="task-name">字形保卫战</view>
            <view class="task-desc">强化汉字结构记忆</view>
          </view>
          <button class="task-btn" @click="startTask({ task_type: 'spelling', status: 'pending' })">去完成</button>
        </view>
        <view class="task-card">
          <view class="task-icon green"><text class="ph ph-book-open"></text></view>
          <view class="task-info">
            <view class="task-name">亲子共读打卡</view>
            <view class="task-desc">培养语感与阅读兴趣</view>
          </view>
          <button class="task-btn" @click="startTask({ task_type: 'reading', status: 'pending' })">去完成</button>
        </view>
      </view>

      <!-- 阶段小结预告 -->
      <view class="milestone-card" :class="{ active: showReassessReminder }">
        <text class="ph ph-flag"></text>
        <view class="milestone-info">
          <view class="milestone-title">
            {{ showReassessReminder ? '🎉 可以复评了！' : '阶段复评预告' }}
          </view>
          <view class="milestone-desc" v-if="!showReassessReminder">
            连续坚持训练 <text class="highlight">14天</text> 后，系统将提示进行下一轮效果复评。
            <text v-if="continuousDays > 0">（当前已连续 <text class="highlight">{{ continuousDays }}</text> 天）</text>
          </view>
          <view class="milestone-desc" v-else>
            已连续训练 <text class="highlight">{{ continuousDays }}</text> 天，建议发起复评检验训练效果！
          </view>
        </view>
        <button v-if="showReassessReminder" class="reassess-mini-btn" @click="goToScreening">去复评</button>
      </view>

      <!-- 本周重点 -->
      <view class="section-title">本周训练重点</view>
      <view class="week-card">
        <view class="week-item" v-for="(item, i) in weekFocus" :key="i">
          <view class="week-dot" :class="item.color"></view>
          <view class="week-text">{{ item.text }}</view>
        </view>
      </view>
    </view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/training/index"></tab-bar>

    <!-- AI 训练计划弹窗 -->
    <view class="modal-overlay" v-if="showAiModal" @click="showAiModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-header">
          <view class="modal-avatar">
            <text class="ph-fill ph-robot"></text>
          </view>
          <view class="modal-title">AI 专属训练计划</view>
          <view class="modal-close" @click="showAiModal = false">
            <text class="ph ph-x"></text>
          </view>
        </view>

        <!-- 加载中 -->
        <view class="modal-loading" v-if="aiPlanLoading">
          <view class="loading-spinner"></view>
          <view class="loading-text">AI 正在分析报告，生成专属计划...</view>
        </view>

        <!-- 计划内容 -->
        <view class="modal-plan" v-else-if="aiPlan">
          <view class="plan-summary">{{ aiPlan.plan_summary }}</view>
          <view class="plan-duration">计划周期：{{ aiPlan.duration_weeks }} 周</view>

          <view class="plan-tasks">
            <view
              class="plan-task-item"
              v-for="(task, i) in aiPlan.tasks"
              :key="i"
            >
              <view class="plan-task-header">
                <view class="plan-task-icon" :class="taskColor(task.task_type)">
                  <text :class="'ph ' + taskIcon(task.task_type)"></text>
                </view>
                <view class="plan-task-info">
                  <view class="plan-task-name">{{ task.task_name }}</view>
                  <view class="plan-task-meta">{{ task.frequency }} · {{ task.duration_minutes }}分钟</view>
                </view>
              </view>
              <view class="plan-task-desc">{{ task.description }}</view>
              <view class="plan-task-tip" v-if="task.tips">
                <text class="ph ph-lightbulb"></text> {{ task.tips }}
              </view>
            </view>
          </view>

          <button class="apply-plan-btn" @click="applyAiPlan">
            <text class="ph ph-check-circle"></text> 应用此计划
          </button>
        </view>

        <!-- 未生成 -->
        <view class="modal-empty" v-else>
          <view class="modal-empty-text">AI 将根据孩子的最新筛查报告，生成个性化的家庭训练计划。</view>
          <button class="generate-btn" @click="generateAiPlan">
            <text class="ph ph-sparkle"></text> 立即生成
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { getChildren } from '../../../api/child.js'
import { getCurrentChild, setCurrentChild } from '../../../utils/auth.js'
import { getTasks, completeTask, createTask } from '../../../api/training.js'
import { getReports } from '../../../api/report.js'
import { generateTrainingPlan } from '../../../api/ai.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      currentChild: null,
      pendingTasks: [],
      completedCount: 0,
      totalCount: 3,
      weekFocus: [
        { text: '每天完成今日任务，保持训练节奏', color: 'blue' },
        { text: '重点练习弱项维度，每次10-15分钟', color: 'orange' },
        { text: '家长陪伴，多鼓励，不催促', color: 'green' }
      ],
      showReassessReminder: false,
      continuousDays: 0,
      // AI 训练计划
      showAiModal: false,
      aiPlanLoading: false,
      aiPlan: null,
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
          await Promise.all([this.loadTasks(), this.loadWeekFocus()])
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    async loadWeekFocus() {
      // 根据最新报告的弱项维度动态生成本周重点
      try {
        const reports = await getReports(this.currentChild.id)
        if (!reports || reports.length === 0) return
        const latest = reports[0]
        let dims = {}
        try {
          // 后端 dimensions 可能是字符串（JSON）或已解析的对象
          const raw = latest.dimensions
          dims = typeof raw === 'string' ? JSON.parse(raw || '{}') : (raw || {})
        } catch (e) { dims = {} }
        const dimAdvice = {
          visual_discrimination: { text: '重点：每天5分钟形近字辨别练习', color: 'orange' },
          attention:             { text: '重点：训练时使用计时器，控制在15分钟内', color: 'orange' },
          phonological:          { text: '重点：拼音与汉字对应卡片游戏', color: 'orange' },
          character_order:       { text: '重点：描红练习，强化笔顺记忆', color: 'orange' },
          spelling:              { text: '重点：每日听写5个词语，错词重复3遍', color: 'orange' },
          reading_comprehension: { text: '重点：亲子共读后提问，引导复述', color: 'orange' },
          semantic_integration:  { text: '重点：多做造句练习，理解词语用法', color: 'orange' },
          information_extraction:{ text: '重点：阅读后找出时间/地点/人物', color: 'orange' },
        }
        const weakDims = Object.entries(dims).filter(([, s]) => s < 70).map(([d]) => d)
        const focus = [{ text: '每天完成今日任务，保持训练节奏', color: 'blue' }]
        for (const d of weakDims.slice(0, 2)) {
          if (dimAdvice[d]) focus.push(dimAdvice[d])
        }
        focus.push({ text: '家长陪伴，多鼓励，不催促', color: 'green' })
        this.weekFocus = focus

        // 计算连续训练天数，判断是否触发复评提醒
        const allTasks = await getTasks(this.currentChild.id, 'completed')
        this.continuousDays = this._calcContinuousDays(allTasks)
        if (this.continuousDays >= 14) {
          this.showReassessReminder = true
        }
      } catch (e) {
        console.warn('加载报告失败', e)
      }
    },
    _calcContinuousDays(completedTasks) {
      if (!completedTasks || completedTasks.length === 0) return 0
      const days = new Set(completedTasks.map(t => {
        const d = t.completed_at || t.created_at
        return d ? d.split('T')[0] : null
      }).filter(Boolean))
      const sorted = [...days].sort().reverse()
      let count = 0
      let prev = null
      for (const day of sorted) {
        if (!prev) { count = 1; prev = day; continue }
        const diff = (new Date(prev) - new Date(day)) / 86400000
        if (diff === 1) { count++; prev = day }
        else break
      }
      return count
    },
    async loadTasks() {
      if (!this.currentChild) return
      try {
        const allTasks = await getTasks(this.currentChild.id)
        // 今日任务：取最近3条
        const today = new Date().toISOString().split('T')[0]
        let todayTasks = allTasks.filter(t => {
          const d = t.scheduled_date || t.created_at?.split('T')[0]
          return d === today
        })
        // 如果没有今日任务，自动创建默认任务
        if (todayTasks.length === 0 && allTasks.length === 0) {
          await this.createDefaultTasks()
          const refreshed = await getTasks(this.currentChild.id)
          todayTasks = refreshed.slice(0, 3)
        } else if (todayTasks.length === 0) {
          todayTasks = allTasks.slice(0, 3)
        }
        this.pendingTasks = todayTasks
        this.completedCount = todayTasks.filter(t => t.status === 'completed').length
        this.totalCount = todayTasks.length || 3
      } catch (e) {
        console.error('加载任务失败', e)
      }
    },
    async createDefaultTasks() {
      const today = new Date().toISOString().split('T')[0]
      const defaults = [
        { task_type: 'visual',        task_name: '火眼金睛 (视觉训练)',  child_id: this.currentChild.id, scheduled_date: today },
        { task_type: 'spelling',      task_name: '字形保卫战',           child_id: this.currentChild.id, scheduled_date: today },
        { task_type: 'comprehension', task_name: '亲子共读打卡',         child_id: this.currentChild.id, scheduled_date: today }
      ]
      for (const t of defaults) {
        try { await createTask(t) } catch (e) { /* ignore */ }
      }
    },
    async doCompleteTask(task) {
      if (task.status === 'completed') return
      try {
        await completeTask(task.id)
        task.status = 'completed'
        this.completedCount = this.pendingTasks.filter(t => t.status === 'completed').length
        uni.showToast({ title: '太棒了！获得一颗星星 ⭐', icon: 'none' })
      } catch (e) {
        console.error('完成任务失败', e)
      }
    },
    startTask(task) {
      if (task.status === 'completed') return
      if (task.id) uni.setStorageSync('pending_task_id', task.id)
      // reading 映射到 comprehension（后端不支持 reading 类型）
      const typeMap = { reading: 'comprehension' }
      const gameType = typeMap[task.task_type] || task.task_type || 'visual'
      uni.navigateTo({
        url: `/pages/child/prep/index?game_type=${gameType}`
      })
    },
    taskIcon(type) {
      return { visual: 'ph-eye', spelling: 'ph-puzzle-piece', comprehension: 'ph-book-open', reading: 'ph-book-open' }[type] || 'ph-star'
    },
    taskColor(type) {
      return { visual: 'orange', spelling: 'blue', comprehension: 'green', reading: 'green' }[type] || 'blue'
    },
    taskDesc(type) {
      return { visual: '提升形近字辨识能力', spelling: '强化汉字结构记忆', comprehension: '培养语感与阅读兴趣', reading: '培养语感与阅读兴趣' }[type] || ''
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },

    // ── AI 训练计划 ──────────────────────────────────────────────────────────
    showAiPlanModal() {
      this.showAiModal = true
    },
    async generateAiPlan() {
      if (!this.currentChild) {
        uni.showToast({ title: '请先选择孩子', icon: 'none' })
        return
      }
      this.aiPlanLoading = true
      this.aiPlan = null
      try {
        const res = await generateTrainingPlan(this.currentChild.id)
        this.aiPlan = res.plan
      } catch (e) {
        uni.showToast({ title: 'AI生成失败，请先完成筛查', icon: 'none' })
      } finally {
        this.aiPlanLoading = false
      }
    },
    async applyAiPlan() {
      if (!this.aiPlan || !this.currentChild) return
      const today = new Date().toISOString().split('T')[0]
      let created = 0
      for (const task of this.aiPlan.tasks) {
        try {
          await createTask({
            child_id: this.currentChild.id,
            task_type: task.task_type,
            task_name: task.task_name,
            scheduled_date: today,
          })
          created++
        } catch (e) { /* ignore */ }
      }
      this.showAiModal = false
      uni.showToast({ title: `已添加 ${created} 个训练任务 ✅`, icon: 'none' })
      await this.loadTasks()
    },
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  padding-bottom: 196rpx;
}

/* AI 训练计划入口 Banner */
.ai-plan-banner {
  background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%);
  border-radius: 40rpx;
  padding: 32rpx 40rpx;
  margin-bottom: 32rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ai-plan-left {
  display: flex;
  align-items: center;
  gap: 24rpx;
}

.ai-plan-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-plan-icon .ph {
  font-size: 40rpx;
  color: #FFFFFF;
}

.ai-plan-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.ai-plan-sub {
  font-size: 22rpx;
  color: rgba(255,255,255,0.75);
  margin-top: 4rpx;
}

.ai-plan-arrow {
  font-size: 36rpx;
  color: rgba(255,255,255,0.7);
}

/* AI 计划弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  background: #FFFFFF;
  width: 100%;
  border-radius: 64rpx 64rpx 0 0;
  padding: 48rpx;
  max-height: 85vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 40rpx;
}

.modal-avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #7C3AED;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-avatar .ph {
  font-size: 36rpx;
  color: #FFFFFF;
}

.modal-title {
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

.modal-close .ph {
  font-size: 40rpx;
  color: #9CA3AF;
}

.modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
  gap: 32rpx;
}

.loading-spinner {
  width: 80rpx;
  height: 80rpx;
  border: 6rpx solid #EDE9FE;
  border-top-color: #7C3AED;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 26rpx;
  color: #7C3AED;
}

.plan-summary {
  font-size: 28rpx;
  color: #374151;
  line-height: 1.7;
  background: #F5F3FF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 16rpx;
}

.plan-duration {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 32rpx;
}

.plan-tasks {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  margin-bottom: 40rpx;
}

.plan-task-item {
  background: #F9FAFB;
  border-radius: 32rpx;
  padding: 32rpx;
  border: 1rpx solid #F3F4F6;
}

.plan-task-header {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.plan-task-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.plan-task-icon .ph { font-size: 36rpx; }
.plan-task-icon.orange { background: #FEF3C7; }
.plan-task-icon.orange .ph { color: #F59E0B; }
.plan-task-icon.blue { background: #EFF6FF; }
.plan-task-icon.blue .ph { color: #3B82F6; }
.plan-task-icon.green { background: #ECFDF5; }
.plan-task-icon.green .ph { color: #10B981; }

.plan-task-name {
  font-size: 28rpx;
  font-weight: 700;
  color: #1F2937;
}

.plan-task-meta {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.plan-task-desc {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.6;
  margin-bottom: 12rpx;
}

.plan-task-tip {
  font-size: 22rpx;
  color: #7C3AED;
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.plan-task-tip .ph { font-size: 24rpx; }

.apply-plan-btn {
  width: 100%;
  background: #7C3AED;
  color: #FFFFFF;
  border-radius: 40rpx;
  padding: 32rpx;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
}

.apply-plan-btn .ph { font-size: 32rpx; }

.modal-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0;
  gap: 32rpx;
}

.modal-empty-text {
  font-size: 28rpx;
  color: #6B7280;
  text-align: center;
  line-height: 1.7;
}

.generate-btn {
  background: #7C3AED;
  color: #FFFFFF;
  border-radius: 40rpx;
  padding: 28rpx 64rpx;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.generate-btn .ph { font-size: 32rpx; }

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

.task-btn.done {
  background: #F3F4F6;
  color: #9CA3AF;
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
  margin-bottom: 48rpx;
}

.milestone-card.active {
  background: #ECFDF5;
  border-color: #6EE7B7;
}

.milestone-card .ph {
  font-size: 64rpx;
  color: #D1D5DB;
  flex-shrink: 0;
}

.milestone-card.active .ph {
  color: #10B981;
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

.reassess-mini-btn {
  padding: 16rpx 28rpx;
  background: #10B981;
  color: #FFFFFF;
  border-radius: 24rpx;
  font-size: 22rpx;
  font-weight: 700;
  flex-shrink: 0;
}

/* 本周重点 */
.week-card {
  background: #F9FAFB;
  border-radius: 32rpx;
  padding: 32rpx 40rpx;
  border: 1rpx solid #F3F4F6;
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.week-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
}
.week-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  flex-shrink: 0;
}
.week-dot.blue { background: #3B82F6; }
.week-dot.orange { background: #F59E0B; }
.week-dot.green { background: #10B981; }
.week-text {
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.5;
}
</style>
