<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-center">
        <view class="header-title">智能解答助手</view>
        <view class="header-sub">由 AI 大模型驱动</view>
      </view>
      <view class="clear-btn" @click="confirmClear">
        <text class="ph ph-trash"></text>
      </view>
    </view>

    <!-- 聊天消息区域 -->
    <scroll-view
      class="chat-messages"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-with-animation="true"
      @scrolltoupper="onScrollTop"
    >
      <!-- 欢迎提示 -->
      <view class="welcome-tip" v-if="messages.length === 0">
        👋 你好！我是AI助手，可以帮你解读孩子的筛查报告、解答读写障碍相关问题，或者给出家庭训练建议。
      </view>

      <!-- 快捷问题（无历史时显示） -->
      <view class="quick-cards" v-if="messages.length === 0">
        <view
          class="quick-card"
          v-for="q in quickQuestions"
          :key="q.text"
          @click="sendQuick(q.text)"
        >
          <text :class="q.icon"></text>
          <view class="quick-card-text">{{ q.text }}</view>
        </view>
      </view>

      <!-- 消息列表 -->
      <view
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <view class="message-avatar">
          <text :class="msg.role === 'assistant' ? 'ph-fill ph-robot' : 'ph ph-user'"></text>
        </view>
        <view class="message-content">
          <view class="message-text">
            {{ msg.message }}
            <!-- 流式光标 -->
            <text class="cursor" v-if="msg.streaming">▋</text>
          </view>
          <view class="message-time" v-if="msg.created_at && !msg.streaming">
            {{ formatTime(msg.created_at) }}
          </view>
        </view>
      </view>

      <!-- AI 思考中 -->
      <view class="message assistant" v-if="isThinking">
        <view class="message-avatar">
          <text class="ph-fill ph-robot"></text>
        </view>
        <view class="message-content">
          <view class="message-text thinking">
            <view class="dot-flashing"></view>
          </view>
        </view>
      </view>

      <!-- 底部占位 -->
      <view style="height: 32rpx;"></view>
    </scroll-view>

    <!-- 底部输入区域 -->
    <view class="input-section">
      <!-- 快捷问题（有消息时显示） -->
      <view class="quick-questions" v-if="messages.length > 0">
        <view
          class="quick-btn"
          v-for="q in quickQuestions.slice(0, 2)"
          :key="q.text"
          @click="sendQuick(q.text)"
        >{{ q.text }}</view>
      </view>
      <view class="input-row">
        <input
          class="input"
          v-model="inputMessage"
          placeholder="输入你想问的问题..."
          :disabled="isStreaming"
          @confirm="sendMessage"
          confirm-type="send"
        />
        <view
          :class="['send-btn', { disabled: isStreaming || !inputMessage.trim() }]"
          @click="sendMessage"
        >
          <text v-if="!isStreaming" class="ph ph-paper-plane-tilt"></text>
          <text v-else class="ph ph-stop-circle" @click.stop="abortStream"></text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { chat, chatStream, getChatHistory, clearChatHistory } from '../../../api/ai.js';
import { getCurrentChild } from '../../../utils/auth.js';

export default {
  data() {
    return {
      messages: [],
      inputMessage: '',
      currentChild: null,
      isThinking: false,
      isStreaming: false,
      scrollTop: 0,
      _abortStream: null,

      quickQuestions: [
        { text: '什么是视觉加工速度慢？', icon: 'ph ph-eye' },
        { text: '在家应该怎么陪他练？', icon: 'ph ph-house' },
        { text: '读写障碍会影响智力吗？', icon: 'ph ph-brain' },
        { text: '孩子的风险等级怎么理解？', icon: 'ph ph-chart-bar' },
      ],
    };
  },

  onLoad(options) {
    if (options.child_id) {
      this.currentChild = { id: parseInt(options.child_id) };
    } else {
      this.currentChild = getCurrentChild();
    }
    this.loadHistory();
  },

  onUnload() {
    // 页面卸载时中断流式请求
    if (this._abortStream) this._abortStream();
  },

  methods: {
    async loadHistory() {
      try {
        const history = await getChatHistory(this.currentChild?.id);
        this.messages = history.map((h) => ({
          role: h.role,
          message: h.message,
          created_at: h.created_at,
        }));
        this.scrollToBottom();
      } catch (e) {
        console.error('加载历史失败', e);
      }
    },

    async sendMessage() {
      const text = this.inputMessage.trim();
      if (!text || this.isStreaming) return;

      this.inputMessage = '';

      // 添加用户消息
      this.messages.push({
        role: 'user',
        message: text,
        created_at: new Date().toISOString(),
      });
      this.scrollToBottom();

      // 尝试流式，降级到普通
      if (typeof fetch !== 'undefined') {
        await this.sendStream(text);
      } else {
        await this.sendNormal(text);
      }
    },

    async sendStream(text) {
      this.isStreaming = true;
      this.isThinking = true;

      // 预先插入一条空的 AI 消息
      const aiMsgIndex = this.messages.length;
      this.messages.push({
        role: 'assistant',
        message: '',
        streaming: true,
        created_at: null,
      });

      this._abortStream = chatStream(
        { child_id: this.currentChild?.id, message: text },
        // onChunk
        (chunk) => {
          if (this.isThinking) {
            this.isThinking = false;
          }
          this.messages[aiMsgIndex].message += chunk;
          this.scrollToBottom();
        },
        // onDone
        () => {
          this.messages[aiMsgIndex].streaming = false;
          this.messages[aiMsgIndex].created_at = new Date().toISOString();
          this.isStreaming = false;
          this.isThinking = false;
          this._abortStream = null;
        },
        // onError
        (err) => {
          console.error('流式失败，降级到普通模式', err);
          this.messages.splice(aiMsgIndex, 1);
          this.isStreaming = false;
          this.isThinking = false;
          this.sendNormal(text);
        }
      );
    },

    async sendNormal(text) {
      this.isThinking = true;
      try {
        const res = await chat({
          child_id: this.currentChild?.id,
          message: text,
        });
        this.messages.push({
          role: 'assistant',
          message: res.reply,
          created_at: new Date().toISOString(),
        });
        this.scrollToBottom();
      } catch (e) {
        uni.showToast({ title: '发送失败，请重试', icon: 'none' });
      } finally {
        this.isThinking = false;
      }
    },

    abortStream() {
      if (this._abortStream) {
        this._abortStream();
        this._abortStream = null;
        this.isStreaming = false;
        this.isThinking = false;
        // 标记最后一条消息为已完成
        const last = this.messages[this.messages.length - 1];
        if (last && last.streaming) {
          last.streaming = false;
          last.message += '（已停止）';
          last.created_at = new Date().toISOString();
        }
      }
    },

    sendQuick(question) {
      this.inputMessage = question;
      this.sendMessage();
    },

    confirmClear() {
      uni.showModal({
        title: '清空对话',
        content: '确定要清空所有对话记录吗？',
        success: async (res) => {
          if (res.confirm) {
            await clearChatHistory(this.currentChild?.id);
            this.messages = [];
          }
        },
      });
    },

    onScrollTop() {
      // 可扩展：加载更多历史
    },

    scrollToBottom() {
      this.$nextTick(() => {
        this.scrollTop = 999999;
      });
    },

    goBack() {
      uni.navigateBack();
    },

    formatTime(timeStr) {
      if (!timeStr) return '';
      const date = new Date(timeStr);
      return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
    },
  },
};
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

.back-btn, .clear-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.back-btn .ph { font-size: 40rpx; color: #6B7280; }
.clear-btn .ph { font-size: 36rpx; color: #9CA3AF; }

.header-center {
  flex: 1;
}

.header-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #1F2937;
  line-height: 1.2;
}

.header-sub {
  font-size: 20rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

/* 聊天区域 */
.chat-messages {
  flex: 1;
  padding: 32rpx 48rpx;
  overflow-y: auto;
}

.welcome-tip {
  background: #FFFFFF;
  padding: 32rpx;
  border-radius: 32rpx;
  font-size: 28rpx;
  color: #4B5563;
  line-height: 1.7;
  margin-bottom: 32rpx;
  border: 1rpx solid #F3F4F6;
}

/* 快捷卡片（首屏） */
.quick-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.quick-card {
  background: #FFFFFF;
  border: 1rpx solid #E5E7EB;
  border-radius: 24rpx;
  padding: 28rpx 24rpx;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.quick-card .ph {
  font-size: 36rpx;
  color: #7C3AED;
}

.quick-card-text {
  font-size: 24rpx;
  color: #374151;
  line-height: 1.4;
}

/* 消息 */
.message {
  display: flex;
  margin-bottom: 32rpx;
  gap: 20rpx;
  align-items: flex-start;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 72rpx;
  height: 72rpx;
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
  font-size: 36rpx;
  color: #8B5CF6;
}

.message.user .message-avatar {
  background: #EFF6FF;
}

.message.user .message-avatar .ph {
  font-size: 36rpx;
  color: #3B82F6;
}

.message-content {
  max-width: 72%;
}

.message-text {
  padding: 24rpx 28rpx;
  border-radius: 32rpx;
  font-size: 28rpx;
  line-height: 1.7;
  word-break: break-all;
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

.cursor {
  animation: blink 1s step-end infinite;
  color: #7C3AED;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
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

/* 思考动画 */
.thinking {
  padding: 28rpx 36rpx !important;
}

.dot-flashing {
  position: relative;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background-color: #9CA3AF;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0.5s;
}

.dot-flashing::before,
.dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background-color: #9CA3AF;
}

.dot-flashing::before {
  left: -28rpx;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 0s;
}

.dot-flashing::after {
  left: 28rpx;
  animation: dot-flashing 1s infinite alternate;
  animation-delay: 1s;
}

@keyframes dot-flashing {
  0% { background-color: #9CA3AF; }
  100% { background-color: #E5E7EB; }
}

/* 输入区域 */
.input-section {
  background: #FFFFFF;
  padding: 24rpx 48rpx;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #F3F4F6;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
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
  gap: 20rpx;
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

.send-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #3B82F6;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 0.2s;
}

.send-btn.disabled {
  opacity: 0.5;
}

.send-btn .ph {
  font-size: 32rpx;
  color: #FFFFFF;
}
</style>
