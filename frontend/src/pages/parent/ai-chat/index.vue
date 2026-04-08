<template>
  <view class="page-container">
    <!-- 极简头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">智能解答助手</view>
    </view>

    <!-- 聊天消息区域 -->
    <view class="chat-messages">
      <view class="welcome-tip">👋 你好！关于小明的报告或者平时的训练，您有任何疑问都可以问我哦。</view>

      <view
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <view class="message-avatar">
          <text :class="msg.role === 'assistant' ? 'ph-fill ph-robot' : 'ph ph-user'"></text>
        </view>
        <view class="message-content">
          <view class="message-text">{{ msg.message }}</view>
          <view class="message-time" v-if="msg.created_at">{{ formatTime(msg.created_at) }}</view>
        </view>
      </view>
    </view>

    <!-- 底部输入区域 -->
    <view class="input-section">
      <view class="quick-questions">
        <view class="quick-btn" @click="sendQuick('什么是视觉加工速度慢？')">什么是视觉加工速度慢？</view>
        <view class="quick-btn" @click="sendQuick('在家应该怎么陪他练？')">在家应该怎么陪他练？</view>
      </view>
      <view class="input-row">
        <input
          class="input"
          v-model="inputMessage"
          placeholder="输入你想问的问题..."
          @confirm="sendMessage"
        />
        <view class="send-btn" @click="sendMessage">
          <text class="ph ph-paper-plane-tilt"></text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { chat, getChatHistory } from '../../../api/ai.js'
import { getCurrentChild } from '../../../utils/auth.js'

export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      currentChild: null
    }
  },
  onLoad(options) {
    if (options.child_id) {
      this.currentChild = { id: options.child_id }
    } else {
      this.currentChild = getCurrentChild()
    }
    this.loadHistory()
  },
  methods: {
    async loadHistory() {
      try {
        const history = await getChatHistory(this.currentChild?.id)
        this.messages = history.map(h => ({
          role: h.role,
          message: h.message,
          created_at: h.created_at
        }))

        if (this.messages.length === 0) {
          this.messages.push({
            role: 'assistant',
            message: '家长您好！我是AI助手。关于小明的报告或者平时的训练，您有任何疑问都可以问我哦。'
          })
        }
      } catch (e) {
        console.error('加载历史失败', e)
        this.messages.push({
          role: 'assistant',
          message: '家长您好！我是AI助手。关于小明的报告或者平时的训练，您有任何疑问都可以问我哦。'
        })
      }
    },
    async sendMessage() {
      if (!this.inputMessage.trim()) return

      const userMsg = this.inputMessage
      this.inputMessage = ''

      this.messages.push({
        role: 'user',
        message: userMsg,
        created_at: new Date().toISOString()
      })

      try {
        const res = await chat({
          child_id: this.currentChild?.id,
          message: userMsg
        })

        this.messages.push({
          role: 'assistant',
          message: res.reply,
          created_at: new Date().toISOString()
        })
      } catch (e) {
        console.error('发送失败', e)
        uni.showToast({ title: '发送失败', icon: 'none' })
      }
    },
    sendQuick(question) {
      this.inputMessage = question
      this.sendMessage()
    },
    goBack() {
      uni.navigateBack()
    },
    formatTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.page-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #F9FAFB;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: #FFFFFF;
  padding: 96rpx 48rpx 32rpx;
  display: flex;
  align-items: center;
  gap: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
}

.back-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-btn .ph {
  font-size: 40rpx;
  color: #6B7280;
}

.header-title {
  flex: 1;
  font-size: 36rpx;
  font-weight: 700;
  color: #1F2937;
}

/* 聊天区域 */
.chat-messages {
  flex: 1;
  padding: 32rpx 48rpx;
  overflow-y: auto;
}

.welcome-tip {
  background: #FFFFFF;
  padding: 24rpx;
  border-radius: 24rpx;
  font-size: 26rpx;
  color: #4B5563;
  line-height: 1.6;
  margin-bottom: 32rpx;
  border: 1rpx solid #F3F4F6;
}

.message {
  display: flex;
  margin-bottom: 32rpx;
  gap: 24rpx;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: #F3E8FF;
}

.message.assistant .message-avatar .ph {
  font-size: 40rpx;
  color: #8B5CF6;
}

.message.user .message-avatar {
  background: #EFF6FF;
}

.message.user .message-avatar .ph {
  font-size: 40rpx;
  color: #3B82F6;
}

.message-content {
  max-width: 70%;
}

.message-text {
  padding: 24rpx;
  border-radius: 32rpx;
  font-size: 28rpx;
  line-height: 1.6;
}

.message.assistant .message-text {
  background: #FFFFFF;
  color: #374151;
  border-bottom-left-radius: 8rpx;
  border: 1rpx solid #F3F4F6;
}

.message.user .message-text {
  background: #3B82F6;
  color: #FFFFFF;
  border-bottom-right-radius: 8rpx;
}

.message-time {
  font-size: 20rpx;
  color: #9CA3AF;
  margin-top: 8rpx;
  padding-left: 12rpx;
}

.message.user .message-time {
  text-align: right;
  padding-right: 12rpx;
}

/* 输入区域 */
.input-section {
  background: #FFFFFF;
  padding: 32rpx 48rpx;
  padding-bottom: calc(32rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #F3F4F6;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.quick-btn {
  background: #F3E8FF;
  color: #7C3AED;
  padding: 12rpx 24rpx;
  border-radius: 50rpx;
  font-size: 22rpx;
  font-weight: 500;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  background: #F9FAFB;
  border: 2rpx solid #E5E7EB;
  border-radius: 50rpx;
  padding: 16rpx 24rpx;
}

.input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 28rpx;
  color: #374151;
}

.input::placeholder {
  color: #9CA3AF;
}

.send-btn {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: #3B82F6;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn .ph {
  font-size: 32rpx;
  color: #FFFFFF;
}
</style>
