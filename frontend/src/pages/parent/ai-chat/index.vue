<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">智能解答助手</view>
      <view class="header-action" @click="showSaved = true">
        <text class="ph ph-bookmark-simple"></text>
        <view class="saved-dot" v-if="savedMessages.length > 0"></view>
      </view>
    </view>

    <!-- 聊天消息区域 -->
    <scroll-view class="chat-messages" scroll-y :scroll-top="scrollTop" scroll-with-animation>
      <view class="welcome-tip">👋 你好！关于{{ currentChild ? currentChild.name : '孩子' }}的报告或者平时的训练，您有任何疑问都可以问我哦。</view>

      <view v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
        <view class="message-avatar">
          <text :class="msg.role === 'assistant' ? 'ph-fill ph-robot' : 'ph ph-user'"></text>
        </view>
        <view class="message-content">
          <view class="message-text">{{ msg.message }}</view>
          <view class="message-footer">
            <view class="message-time" v-if="msg.created_at">{{ formatTime(msg.created_at) }}</view>
            <!-- 收藏按钮：仅 assistant 消息且有 id 时显示 -->
            <view
              v-if="msg.role === 'assistant' && msg.id"
              class="save-btn"
              :class="{ saved: savedIds.has(msg.id) }"
              @click="toggleSave(msg)"
            >
              <text :class="savedIds.has(msg.id) ? 'ph-fill ph-bookmark-simple' : 'ph ph-bookmark-simple'"></text>
            </view>
          </view>
        </view>
      </view>

      <!-- 正在输入指示 -->
      <view class="message assistant" v-if="loading">
        <view class="message-avatar">
          <text class="ph-fill ph-robot"></text>
        </view>
        <view class="message-content">
          <view class="message-text typing">
            <view class="dot"></view><view class="dot"></view><view class="dot"></view>
          </view>
        </view>
      </view>
    </scroll-view>

    <!-- 底部输入区域 -->
    <view class="input-section">
      <view class="quick-questions">
        <view class="quick-btn" v-for="(q, i) in dynamicQuickQuestions" :key="i" @click="sendQuick(q)">{{ q }}</view>
      </view>
      <view class="input-row">
        <input
          class="input"
          v-model="inputMessage"
          placeholder="输入你想问的问题..."
          @confirm="sendMessage"
          :disabled="loading"
        />
        <view class="send-btn" :class="{ active: inputMessage.trim() && !loading }" @click="sendMessage">
          <text class="ph ph-paper-plane-tilt"></text>
        </view>
      </view>
    </view>

    <!-- 收藏列表弹窗 -->
    <view class="modal-overlay" v-if="showSaved" @click="showSaved = false">
      <view class="saved-sheet" @click.stop>
        <view class="saved-header">
          <view class="saved-title">已收藏的建议</view>
          <view class="saved-close" @click="showSaved = false">
            <text class="ph ph-x"></text>
          </view>
        </view>
        <scroll-view class="saved-list" scroll-y>
          <view v-if="savedMessages.length === 0" class="saved-empty">
            <text class="ph ph-bookmark-simple saved-empty-icon"></text>
            <view>还没有收藏任何建议</view>
            <view class="saved-empty-hint">长按 AI 回复右下角的书签图标即可收藏</view>
          </view>
          <view
            v-for="item in savedMessages"
            :key="item.id"
            class="saved-item"
          >
            <view class="saved-content">{{ item.content }}</view>
            <view class="saved-meta">
              <view class="saved-date">{{ formatDate(item.created_at) }}</view>
              <view class="saved-del" @click="removeSaved(item)">
                <text class="ph ph-trash"></text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import { chat, getChatHistory, saveMessage, unsaveMessage, getSavedMessages } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'
import { getReports } from '../../../api/report.js'

export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      currentChild: null,
      latestReport: null,
      parsedDimensions: {},
      loading: false,
      scrollTop: 0,
      _scrollCounter: 0,
      showSaved: false,
      savedMessages: [],
      savedIds: new Set()
    }
  },
  computed: {
    dynamicQuickQuestions() {
      if (!this.latestReport) {
        return ['什么是读写障碍？', '如何帮助孩子提高阅读？', '训练多久能看到效果？']
      }
      const level = this.latestReport.risk_level
      let questions = []
      if (level === 'high') {
        questions = ['需要去医院吗？', '高风险意味着什么？', '如何尽快干预？']
      } else if (level === 'medium') {
        questions = ['在家怎么练？', '多久能改善？', '需要专业机构吗？']
      } else {
        questions = ['如何保持现状？', '还需要继续训练吗？', '低风险还需要关注吗？']
      }
      const dimNames = {
        visual_discrimination: '视觉辨识', phonological: '音形映射',
        character_order: '字序组织', spelling: '拼写输出',
        reading_comprehension: '阅读理解', semantic_integration: '语义整合',
        information_extraction: '信息提取', attention: '任务注意力'
      }
      const weakDims = Object.entries(this.parsedDimensions)
        .filter(([, score]) => score < 60)
        .map(([dim]) => dim)
      if (weakDims.length > 0) {
        const name = dimNames[weakDims[0]] || weakDims[0]
        questions.push(`${name}弱怎么训练？`)
      }
      return questions.slice(0, 4)
    }
  },
  onLoad(options) {
    if (options.child_id) {
      this.currentChild = { id: parseInt(options.child_id) }
    } else {
      this.currentChild = getCurrentChild()
    }
    this.loadHistory()
    this.loadReport()
    this.loadSaved()
  },
  methods: {
    async loadReport() {
      if (!this.currentChild?.id) return
      try {
        const reports = await getReports(this.currentChild.id)
        if (reports && reports.length > 0) {
          this.latestReport = reports[0]
          if (this.latestReport.dimensions) {
            try { this.parsedDimensions = JSON.parse(this.latestReport.dimensions) } catch (e) {}
          }
        }
      } catch (e) {
        console.warn('加载报告失败', e)
      }
    },
    async loadHistory() {
      try {
        const history = await getChatHistory(this.currentChild?.id)
        this.messages = history.map(h => ({
          id: h.id,
          role: h.role,
          message: h.message,
          created_at: h.created_at
        }))
        const childName = this.currentChild?.name || '孩子'
        if (this.messages.length === 0) {
          this.messages.push({
            role: 'assistant',
            message: `家长您好！我是AI助手。关于${childName}的报告或者平时的训练，您有任何疑问都可以问我哦。`
          })
        }
        this.scrollToBottom()
      } catch (e) {
        const childName = this.currentChild?.name || '孩子'
        this.messages.push({
          role: 'assistant',
          message: `家长您好！我是AI助手。关于${childName}的报告或者平时的训练，您有任何疑问都可以问我哦。`
        })
      }
    },
    async loadSaved() {
      try {
        const items = await getSavedMessages(this.currentChild?.id)
        this.savedMessages = items
        this.savedIds = new Set(items.map(i => i.conversation_id))
      } catch (e) {
        console.warn('加载收藏失败', e)
      }
    },
    async sendMessage() {
      if (!this.inputMessage.trim() || this.loading) return
      const userMsg = this.inputMessage
      this.inputMessage = ''
      this.messages.push({ role: 'user', message: userMsg, created_at: new Date().toISOString() })
      this.loading = true
      this.scrollToBottom()
      try {
        const res = await chat({ child_id: this.currentChild?.id, message: userMsg })
        this.messages.push({
          id: res.conversation_id,
          role: 'assistant',
          message: res.reply,
          created_at: new Date().toISOString()
        })
        this.scrollToBottom()
      } catch (e) {
        uni.showToast({ title: '发送失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    sendQuick(question) {
      this.inputMessage = question
      this.sendMessage()
    },
    async toggleSave(msg) {
      if (!msg.id) return
      try {
        if (this.savedIds.has(msg.id)) {
          await unsaveMessage(msg.id)
          this.savedIds.delete(msg.id)
          this.savedMessages = this.savedMessages.filter(s => s.conversation_id !== msg.id)
          uni.showToast({ title: '已取消收藏', icon: 'none' })
        } else {
          await saveMessage(msg.id)
          this.savedIds.add(msg.id)
          this.savedMessages.unshift({ conversation_id: msg.id, content: msg.message, created_at: new Date().toISOString() })
          uni.showToast({ title: '已收藏', icon: 'success' })
        }
        // 触发响应式更新
        this.savedIds = new Set(this.savedIds)
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    async removeSaved(item) {
      try {
        await unsaveMessage(item.conversation_id)
        this.savedIds.delete(item.conversation_id)
        this.savedIds = new Set(this.savedIds)
        this.savedMessages = this.savedMessages.filter(s => s.id !== item.id)
        uni.showToast({ title: '已取消收藏', icon: 'none' })
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        this._scrollCounter += 1
        this.scrollTop = 999999 + this._scrollCounter
      })
    },
    goBack() { uni.navigateBack() },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
    },
    formatDate(timeStr) {
      if (!timeStr) return ''
      const d = new Date(timeStr)
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.page-container { height: 100vh; display: flex; flex-direction: column; background: #F9FAFB; }

/* 头部 */
.page-header {
  position: sticky; top: 0; z-index: 30; background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex; align-items: center; gap: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
}
.back-btn { width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center; }
.back-btn .ph { font-size: 40rpx; color: #6B7280; }
.header-title { flex: 1; font-size: 36rpx; font-weight: 700; color: #1F2937; }
.header-action {
  width: 64rpx; height: 64rpx; display: flex; align-items: center; justify-content: center;
  position: relative;
}
.header-action .ph { font-size: 40rpx; color: #6B7280; }
.saved-dot {
  position: absolute; top: 12rpx; right: 12rpx;
  width: 14rpx; height: 14rpx; border-radius: 50%;
  background: #3B82F6; border: 2rpx solid #FFFFFF;
}

/* 聊天区域 */
.chat-messages { flex: 1; padding: 32rpx 48rpx; overflow-y: auto; }
.welcome-tip {
  background: #FFFFFF; padding: 24rpx; border-radius: 24rpx;
  font-size: 26rpx; color: #4B5563; line-height: 1.6;
  margin-bottom: 32rpx; border: 1rpx solid #F3F4F6;
}

.message { display: flex; margin-bottom: 32rpx; gap: 24rpx; }
.message.user { flex-direction: row-reverse; }
.message-avatar {
  width: 80rpx; height: 80rpx; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.message.assistant .message-avatar { background: #F3E8FF; }
.message.assistant .message-avatar .ph { font-size: 40rpx; color: #8B5CF6; }
.message.user .message-avatar { background: #EFF6FF; }
.message.user .message-avatar .ph { font-size: 40rpx; color: #3B82F6; }
.message-content { max-width: 75%; }
.message-text {
  padding: 24rpx; border-radius: 32rpx;
  font-size: 28rpx; line-height: 1.6;
}
.message.assistant .message-text {
  background: #FFFFFF; color: #374151;
  border-bottom-left-radius: 8rpx; border: 1rpx solid #F3F4F6;
}
.message.user .message-text {
  background: #3B82F6; color: #FFFFFF; border-bottom-right-radius: 8rpx;
}

/* 消息底部：时间 + 收藏 */
.message-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8rpx 4rpx 0;
}
.message-time { font-size: 20rpx; color: #9CA3AF; }
.message.user .message-footer { flex-direction: row-reverse; }
.save-btn {
  width: 48rpx; height: 48rpx; display: flex; align-items: center; justify-content: center;
  border-radius: 50%; transition: background 0.2s;
}
.save-btn .ph { font-size: 28rpx; color: #9CA3AF; }
.save-btn.saved .ph { color: #3B82F6; }
.save-btn:active { background: #F3F4F6; }

/* 正在输入 */
.typing { display: flex; align-items: center; gap: 8rpx; padding: 28rpx 32rpx !important; }
.dot {
  width: 12rpx; height: 12rpx; border-radius: 50%; background: #9CA3AF;
  animation: blink 1.2s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0.3; } 40% { opacity: 1; } }

/* 输入区域 */
.input-section {
  background: #FFFFFF; padding: 32rpx 48rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #F3F4F6;
}
.quick-questions { display: flex; flex-wrap: wrap; gap: 16rpx; margin-bottom: 24rpx; }
.quick-btn {
  background: #F3E8FF; color: #7C3AED;
  padding: 12rpx 24rpx; border-radius: 50rpx;
  font-size: 22rpx; font-weight: 500;
}
.input-row {
  display: flex; align-items: center; gap: 24rpx;
  background: #F9FAFB; border: 2rpx solid #E5E7EB;
  border-radius: 50rpx; padding: 16rpx 24rpx;
}
.input { flex: 1; border: none; background: transparent; font-size: 28rpx; color: #374151; }
.send-btn {
  width: 64rpx; height: 64rpx; border-radius: 50%;
  background: #D1D5DB; display: flex; align-items: center; justify-content: center;
  transition: background 0.2s;
}
.send-btn.active { background: #3B82F6; }
.send-btn .ph { font-size: 32rpx; color: #FFFFFF; }

/* 收藏弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4); z-index: 9999;
  display: flex; align-items: flex-end;
}
.saved-sheet {
  background: #FFFFFF; width: 100%;
  border-radius: 48rpx 48rpx 0 0;
  padding: 48rpx 48rpx calc(48rpx + env(safe-area-inset-bottom));
  max-height: 70vh; display: flex; flex-direction: column;
}
.saved-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 32rpx;
}
.saved-title { font-size: 36rpx; font-weight: 700; color: #1F2937; }
.saved-close .ph { font-size: 40rpx; color: #9CA3AF; }
.saved-list { flex: 1; overflow-y: auto; }
.saved-empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 80rpx 0; color: #9CA3AF; font-size: 26rpx; gap: 16rpx;
}
.saved-empty-icon { font-size: 80rpx; color: #D1D5DB; }
.saved-empty-hint { font-size: 22rpx; color: #D1D5DB; }
.saved-item {
  background: #F9FAFB; border-radius: 24rpx; padding: 32rpx;
  margin-bottom: 24rpx; border: 1rpx solid #F3F4F6;
}
.saved-content { font-size: 26rpx; color: #374151; line-height: 1.7; margin-bottom: 16rpx; }
.saved-meta { display: flex; justify-content: space-between; align-items: center; }
.saved-date { font-size: 22rpx; color: #9CA3AF; }
.saved-del .ph { font-size: 32rpx; color: #EF4444; }
</style>
