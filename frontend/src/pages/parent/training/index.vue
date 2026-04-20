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
          <view class="task-icon" :class="task.task_type === 'visual' || task.task_type === 'working_memory' ? 'orange' : task.task_type === 'spelling' || task.task_type === 'rapid_naming' ? 'blue' : 'green'">
            <text :class="'ph ' + taskIcon(task.task_type)"></text>
          </view>
          <view class="task-info">
            <view class="task-name">{{ task.task_name || task.task_type }}</view>
            <view class="task-desc">{{ taskDesc(task.task_type) }}</view>
            <!-- 训练结果反馈 -->
            <view class="task-result" v-if="task.status === 'completed' && task.accuracy != null">
              <view class="result-tag" :class="task.accuracy >= 80 ? 'green' : task.accuracy >= 60 ? 'orange' : 'red'">
                正确率 {{ task.accuracy }}%
              </view>
              <view class="result-detail">答对 {{ task.correct_count }}/{{ task.total_count }} 题</view>
            </view>
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

      <!-- 本阶段目标 -->
      <view class="section-title">本阶段目标</view>
      <view class="goal-card">
        <view class="goal-header">
          <view class="goal-icon"><text class="ph ph-target"></text></view>
          <view class="goal-info">
            <view class="goal-title">{{ stageGoal.title }}</view>
            <view class="goal-period">{{ stageGoal.period }}</view>
          </view>
          <view class="goal-progress-ring">
            <view class="ring-val">{{ stageGoal.progress }}%</view>
          </view>
        </view>
        <view class="goal-items">
          <view class="goal-item" v-for="(g, i) in stageGoal.items" :key="i">
            <text :class="['ph', g.done ? 'ph-check-circle' : 'ph-circle', g.done ? 'done' : '']"></text>
            <view class="goal-item-text" :class="{ done: g.done }">{{ g.text }}</view>
          </view>
        </view>
      </view>

      <!-- 专业支持引导（高风险或长期无改善时显示） -->
      <view class="professional-card" v-if="showProfessionalGuide" @click="goToProfessionalGuide">
        <view class="professional-left">
          <view class="professional-icon">
            <text class="ph ph-hospital"></text>
          </view>
          <view class="professional-text">
            <view class="professional-title">需要专业支持？</view>
            <view class="professional-sub">了解何时应寻求专业机构评估</view>
          </view>
        </view>
        <text class="ph ph-arrow-right professional-arrow"></text>
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
                <view class="plan-task-icon" :class="task.task_type === 'visual' || task.task_type === 'working_memory' ? 'orange' : task.task_type === 'spelling' || task.task_type === 'rapid_naming' ? 'blue' : 'green'">
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
      // 专业支持引导
      showProfessionalGuide: false,
      // 阶段目标
      stageGoal: {
        title: '基础能力建立阶段',
        period: '第1-2周',
        progress: 0,
        items: [
          { text: '每天完成今日训练任务', done: false },
          { text: '坚持训练满7天', done: false },
          { text: '完成一次复评', done: false },
        ],
      },
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
          dims = (typeof raw === 'string' && raw.trim())
            ? JSON.parse(raw)
            : (raw && typeof raw === 'object' ? raw : {})
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
        // 高风险或长期训练无改善时显示专业支持引导
        if (latest.risk_level === 'high' || (this.continuousDays >= 30 && !this.showReassessReminder)) {
          this.showProfessionalGuide = true
        }
        // 更新阶段目标进度
        this._updateStageGoal(this.continuousDays, allTasks)
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
        // 今日任务：使用 UTC 日期与后端保持一致（后端 scheduled_date 存的是 UTC 日期）
        const today = new Date(new Date().toISOString().split('T')[0] + 'T00:00:00Z')
        const todayStr = today.toISOString().split('T')[0]
        let todayTasks = allTasks.filter(t => {
          // scheduled_date 是纯日期字符串（YYYY-MM-DD），直接比较
          if (t.scheduled_date) return t.scheduled_date === todayStr
          // 没有 scheduled_date 时，用 created_at 的 UTC 日期
          if (t.created_at) return t.created_at.split('T')[0] === todayStr
          return false
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
    },    async doCompleteTask(task) {
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
      // 将所有可能的 task_type 映射到后端支持的 game_type
      // 后端支持：visual / spelling / comprehension / working_memory / rapid_naming / motor_coordination
      const VALID_GAME_TYPES = new Set(['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination'])
      const typeMap = {
        reading:              'comprehension',
        reading_comprehension:'comprehension',
        phonological:         'spelling',
        character_order:      'spelling',
        attention:            'visual',
        visual_discrimination:'visual',
        short_term_memory:    'working_memory',
        working_memory_capacity: 'working_memory',
        rapid_naming_speed:   'rapid_naming',
        phonological_awareness: 'rapid_naming',
        fine_motor_control:   'motor_coordination',
        visual_motor_integration: 'motor_coordination',
      }
      const rawType = task.task_type || 'visual'
      const gameType = VALID_GAME_TYPES.has(rawType) ? rawType : (typeMap[rawType] || 'visual')
      const gradeParam = this.currentChild?.grade ? `&grade=${encodeURIComponent(this.currentChild.grade)}` : ''
      const taskIdParam = task.id ? `&task_id=${task.id}` : ''
      // 跳转到儿童端训练游戏页（独立训练模式，不走筛查流程）
      uni.navigateTo({
        url: `/pages/child/training-game/index?game_type=${gameType}${gradeParam}${taskIdParam}`
      })
    },
    taskIcon(type) {
      return { visual: 'ph-eye', spelling: 'ph-puzzle-piece', comprehension: 'ph-book-open', reading: 'ph-book-open', working_memory: 'ph-brain', rapid_naming: 'ph-lightning', motor_coordination: 'ph-hand' }[type] || 'ph-star'
    },
    taskColor(type) {
      return { visual: 'orange', spelling: 'blue', comprehension: 'green', reading: 'green', working_memory: 'orange', rapid_naming: 'blue', motor_coordination: 'green' }[type] || 'blue'
    },
    taskDesc(type) {
      return { visual: '提升形近字辨识能力', spelling: '强化汉字结构记忆', comprehension: '培养语感与阅读兴趣', reading: '培养语感与阅读兴趣', working_memory: '提升工作记忆容量', rapid_naming: '提高命名速度与音韵意识', motor_coordination: '训练精细动作协调能力' }[type] || ''
    },
    goToScreening() {
      uni.navigateTo({ url: '/pages/parent/screening/index' })
    },
    _updateStageGoal(days, allTasks) {
      const completedCount = allTasks ? allTasks.filter(t => t.status === 'completed').length : 0
      const done1 = completedCount > 0
      const done2 = days >= 7
      const done3 = this.showReassessReminder
      const doneCount = [done1, done2, done3].filter(Boolean).length
      const progress = Math.round((doneCount / 3) * 100)
      let title = '基础能力建立阶段'
      let period = '第1-2周'
      if (days >= 14) { title = '能力强化阶段'; period = '第3-4周' }
      if (days >= 28) { title = '巩固提升阶段'; period = '第5周+' }
      this.stageGoal = {
        title, period, progress,
        items: [
          { text: '每天完成今日训练任务', done: done1 },
          { text: `坚持训练满7天（当前${days}天）`, done: done2 },
          { text: '完成一次阶段复评', done: done3 },
        ],
      }
    },
    goToProfessionalGuide() {
      if (!this.currentChild) return
      uni.navigateTo({ url: `/pages/parent/professional-guide/index?child_id=${this.currentChild.id}` })
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
/* 训练页面 - 统一创意风格 */
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
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.header-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 4rpx;
}

.header-subtitle {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

/* 页面内容 */
.page-content {
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
  overflow-x: hidden;
}

/* AI 训练计划入口 Banner - 蓝色渐变替代紫色 */
.ai-plan-banner {
  background: linear-gradient(135deg, #4F9EF8 0%, #3B82F6 100%);
  border-radius: 20rpx;
  padding: 24rpx 28rpx;
  margin-bottom: 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.25);
  transition: all 0.2s;
}

.ai-plan-banner:active {
  transform: scale(0.98);
}

.ai-plan-left {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.ai-plan-icon {
  width: 68rpx;
  height: 68rpx;
  border-radius: 16rpx;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-plan-icon .ph {
  font-size: 36rpx;
  color: #FFFFFF;
}

.ai-plan-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #FFFFFF;
}

.ai-plan-sub {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 3rpx;
}

.ai-plan-arrow {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.7);
}

/* AI 计划弹窗 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 9999;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s;
}

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-content {
  background: #FFFFFF;
  width: 100%;
  border-radius: 32rpx 32rpx 0 0;
  padding: 32rpx;
  max-height: 85vh;
  overflow-y: auto;
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 28rpx;
}

.modal-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-avatar .ph {
  font-size: 32rpx;
  color: #FFFFFF;
}

.modal-title {
  flex: 1;
  font-size: 32rpx;
  font-weight: 700;
  color: #2D3748;
}

.modal-close .ph {
  font-size: 36rpx;
  color: #A0AEC0;
}

.modal-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 64rpx 0;
  gap: 24rpx;
}

.loading-spinner {
  width: 64rpx;
  height: 64rpx;
  border: 5rpx solid #DBEAFE;
  border-top-color: #4F9EF8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-size: 26rpx;
  color: #4F9EF8;
  font-weight: 600;
}

.plan-summary {
  font-size: 26rpx;
  color: #2D3748;
  line-height: 1.7;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.plan-duration {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-bottom: 24rpx;
  font-weight: 500;
}

.plan-tasks {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.plan-task-item {
  background: #F8FAFF;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
}

.plan-task-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.plan-task-icon {
  width: 60rpx;
  height: 60rpx;
  border-radius: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.plan-task-icon .ph { font-size: 30rpx; }
.plan-task-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.plan-task-icon.orange .ph { color: #F57F17; }
.plan-task-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.plan-task-icon.blue .ph { color: #4F9EF8; }
.plan-task-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.plan-task-icon.green .ph { color: #22C55E; }

.plan-task-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.plan-task-meta {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 2rpx;
  font-weight: 500;
}

.plan-task-desc {
  font-size: 24rpx;
  color: #718096;
  line-height: 1.6;
  margin-bottom: 10rpx;
  font-weight: 500;
}

.plan-task-tip {
  font-size: 20rpx;
  color: #4F9EF8;
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-weight: 600;
}

.plan-task-tip .ph { font-size: 22rpx; }

.apply-plan-btn {
  width: 100%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 28rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10rpx;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.25);
  transition: all 0.2s;
}

.apply-plan-btn:active { transform: scale(0.97); }
.apply-plan-btn .ph { font-size: 28rpx; }

.modal-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48rpx 0;
  gap: 24rpx;
}

.modal-empty-text {
  font-size: 26rpx;
  color: #718096;
  text-align: center;
  line-height: 1.7;
  font-weight: 500;
}

.generate-btn {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx 56rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10rpx;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.25);
  transition: all 0.2s;
}

.generate-btn:active { transform: scale(0.97); }
.generate-btn .ph { font-size: 28rpx; }

/* 今日卡片 */
.today-card {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

.today-decoration {
  position: absolute;
  right: -24rpx;
  top: -24rpx;
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  opacity: 0.6;
}

.today-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
  position: relative;
  z-index: 1;
}

.today-title {
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
}

.today-meta {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 3rpx;
  font-weight: 500;
}

.count-ring {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  border: 6rpx solid #22C55E;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #FFFFFF;
  font-size: 24rpx;
  font-weight: 700;
  color: #22C55E;
}

/* 贴士 */
.tips-box {
  background: #F8FAFF;
  border-radius: 16rpx;
  padding: 20rpx;
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
  position: relative;
  z-index: 1;
}

.tips-box .ph {
  font-size: 28rpx;
  color: #FF6B6B;
  flex-shrink: 0;
}

.tips-text {
  font-size: 22rpx;
  color: #718096;
  line-height: 1.7;
  font-weight: 500;
}

.tips-text .bold {
  font-weight: 700;
  color: #2D3748;
}

/* 区域标题 */
.section-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
}

/* 任务列表 */
.task-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.task-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  transition: all 0.2s;
}

.task-card:active { transform: scale(0.98); }

.task-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.task-icon .ph { font-size: 40rpx; }
.task-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.task-icon.orange .ph { color: #F57F17; }
.task-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.task-icon.blue .ph { color: #4F9EF8; }
.task-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.task-icon.green .ph { color: #22C55E; }

.task-info { flex: 1; }

.task-name {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.task-desc {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 3rpx;
  font-weight: 500;
}

/* 训练结果反馈 */
.task-result { display: flex; align-items: center; gap: 10rpx; margin-top: 8rpx; }
.result-tag { font-size: 18rpx; font-weight: 700; padding: 4rpx 12rpx; border-radius: 8rpx; }
.result-tag.green { background: rgba(34,197,94,0.1); color: #22C55E; }
.result-tag.orange { background: rgba(245,127,23,0.1); color: #F57F17; }
.result-tag.red { background: rgba(255,107,107,0.1); color: #FF6B6B; }
.result-detail { font-size: 18rpx; color: #A0AEC0; font-weight: 500; }

.task-btn {
  padding: 14rpx 28rpx;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-radius: 14rpx;
  font-size: 22rpx;
  font-weight: 700;
  box-shadow: 0 2rpx 8rpx rgba(59, 130, 246, 0.2);
  transition: all 0.2s;
}

.task-btn:active { transform: scale(0.95); }

.task-btn.done {
  background: #F5F5F5;
  color: #A0AEC0;
  box-shadow: none;
}

/* 里程碑卡片 */
.milestone-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.milestone-card.active {
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  box-shadow: 0 2rpx 12rpx rgba(34, 197, 94, 0.1);
}

.milestone-card .ph {
  font-size: 48rpx;
  color: #D1D5DB;
  flex-shrink: 0;
}

.milestone-card.active .ph { color: #22C55E; }

.milestone-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

.milestone-desc {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 3rpx;
  font-weight: 500;
}

.milestone-desc .highlight {
  font-weight: 700;
  color: #4F9EF8;
}

.reassess-mini-btn {
  padding: 12rpx 24rpx;
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: #FFFFFF;
  border-radius: 12rpx;
  font-size: 20rpx;
  font-weight: 700;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(34, 197, 94, 0.2);
}

/* 本周重点 */
.week-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.week-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.week-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  flex-shrink: 0;
}

.week-dot.blue { background: #4F9EF8; }
.week-dot.orange { background: #F57F17; }
.week-dot.green { background: #22C55E; }

.week-text {
  font-size: 24rpx;
  color: #718096;
  line-height: 1.5;
  font-weight: 500;
}

/* 阶段目标卡片 */
.goal-card { background: #FFFFFF; border-radius: 20rpx; padding: 24rpx; margin-bottom: 24rpx; box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04); }
.goal-header { display: flex; align-items: center; gap: 16rpx; margin-bottom: 20rpx; }
.goal-icon { width: 60rpx; height: 60rpx; border-radius: 14rpx; background: linear-gradient(135deg, #EFF6FF, #DBEAFE); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.goal-icon .ph { font-size: 30rpx; color: #4F9EF8; }
.goal-info { flex: 1; }
.goal-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.goal-period { font-size: 20rpx; color: #A0AEC0; margin-top: 2rpx; font-weight: 500; }
.goal-progress-ring { width: 72rpx; height: 72rpx; border-radius: 50%; border: 6rpx solid #4F9EF8; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ring-val { font-size: 20rpx; font-weight: 800; color: #4F9EF8; }
.goal-items { display: flex; flex-direction: column; gap: 14rpx; }
.goal-item { display: flex; align-items: center; gap: 12rpx; }
.goal-item .ph { font-size: 28rpx; color: #D1D5DB; flex-shrink: 0; }
.goal-item .ph.done { color: #22C55E; }
.goal-item-text { font-size: 24rpx; color: #718096; font-weight: 500; }
.goal-item-text.done { color: #22C55E; text-decoration: line-through; }

/* 专业支持引导卡片 */.professional-card {
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
