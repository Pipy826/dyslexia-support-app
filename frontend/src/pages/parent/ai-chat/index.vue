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
          <view class="message-footer" v-if="msg.created_at && !msg.streaming">
            <view class="message-time">{{ formatTime(msg.created_at) }}</view>
            <!-- 收藏按钮（仅 AI 回复） -->
            <view
              v-if="msg.role === 'assistant' && msg.id"
              class="save-btn"
              :class="{ saved: savedIds.includes(msg.id) }"
              @click="toggleSave(msg)"
            >
              <text :class="savedIds.includes(msg.id) ? 'ph-fill ph-bookmark-simple' : 'ph ph-bookmark-simple'"></text>
            </view>
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
import { chat, chatStream, getChatHistory, clearChatHistory, saveMessage, getSavedMessages, deleteSavedMessage } from '../../../api/ai.js';
import { getCurrentChild } from '../../../utils/auth.js';
import { getReports } from '../../../api/report.js';

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
      reportContext: null,
      savedIds: [],  // 已收藏的 conversation_id 数组（Set 在 Vue 响应式中不可靠）
    };  },

  onLoad(options) {
    if (options.child_id) {
      this.currentChild = { id: parseInt(options.child_id) };
    } else {
      this.currentChild = getCurrentChild();
    }
    this.loadHistory();
    this.loadReportContext();
    this.loadSavedIds();
  },
  onUnload() {
    // 页面卸载时中断流式请求
    if (this._abortStream) this._abortStream();
  },

  methods: {
    async loadHistory() {      try {
        const history = await getChatHistory(this.currentChild?.id);
        this.messages = history.map((h) => ({
          role: h.role,
          message: h.message,
          created_at: h.created_at,
          id: h.id,
        }));
        this.scrollToBottom();
      } catch (e) {
        console.error('加载历史失败', e);
      }
    },

    async loadReportContext() {
      if (!this.currentChild?.id) return
      try {
        const reports = await getReports(this.currentChild.id)
        if (!reports || reports.length === 0) return
        const latest = reports[0]
        this.reportContext = latest
        const level = latest.risk_level
        const dynamicQuestions = []
        if (level === 'high') {
          dynamicQuestions.push({ text: '高风险意味着什么？需要去医院吗？', icon: 'ph ph-warning-circle' })
          dynamicQuestions.push({ text: '孩子高风险，我该怎么办？', icon: 'ph ph-heart' })
        } else if (level === 'medium') {
          dynamicQuestions.push({ text: '中风险需要担心吗？', icon: 'ph ph-info' })
          dynamicQuestions.push({ text: '如何通过家庭训练改善？', icon: 'ph ph-house' })
        } else {
          dynamicQuestions.push({ text: '低风险还需要训练吗？', icon: 'ph ph-check-circle' })
        }
        dynamicQuestions.push({ text: '报告里的维度评分怎么理解？', icon: 'ph ph-chart-bar' })
        dynamicQuestions.push({ text: '读写障碍会影响智力吗？', icon: 'ph ph-brain' })
        this.quickQuestions = dynamicQuestions
      } catch (e) {
        // 静默失败，保留默认问题
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
      // #ifdef MP-WEIXIN
      await this.sendStream(text);
      // #endif
      // #ifndef MP-WEIXIN
      if (typeof fetch !== 'undefined') {
        await this.sendStream(text);
      } else {
        await this.sendNormal(text);
      }
      // #endif
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
        // onError：流式失败时提示用户重试（用户消息已入库，不重复调用避免重复入库）
        (err) => {
          console.error('流式请求失败', err);
          // 移除空的 AI 占位消息
          this.messages.splice(aiMsgIndex, 1);
          this.isStreaming = false;
          this.isThinking = false;
          this._abortStream = null;
          uni.showToast({ title: '网络异常，请重试', icon: 'none' });
        }
      );
    },

    // 仅获取 AI 回复（流式降级时使用）
    async fetchNormalReply(text) {
      await this.sendNormal(text)
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

    // ── 收藏功能 ──────────────────────────────────────────────────────────────
    async loadSavedIds() {
      try {
        const items = await getSavedMessages(this.currentChild?.id);
        this.savedIds = items.map(m => m.conversation_id);
      } catch (e) {}
    },

    async toggleSave(msg) {
      if (!msg.id) return;
      if (this.savedIds.includes(msg.id)) {
        // 取消收藏
        try {
          const items = await getSavedMessages(this.currentChild?.id);
          const saved = items.find(m => m.conversation_id === msg.id);
          if (saved) {
            await deleteSavedMessage(saved.id);
            this.savedIds = this.savedIds.filter(id => id !== msg.id);
            uni.showToast({ title: '已取消收藏', icon: 'none' });
          }
        } catch (e) {}
      } else {
        try {
          await saveMessage({ conversation_id: msg.id, child_id: this.currentChild?.id });
          this.savedIds = [...this.savedIds, msg.id];
          uni.showToast({ title: '已收藏', icon: 'success' });
        } catch (e) {}
      }
    },
  },
};
</script>




<style scoped>
/* AI问答 - 小程序兼容布局，避免flex子元素分离 */

/* 整页用固定高度 + flex列布局 */
.page-container {
  height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 头部固定高度，不参与flex伸缩 */
.page-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.06);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.back-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }

.header-center { flex: 1; min-width: 0; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }
.header-sub { font-size: 18rpx; color: #A0AEC0; margin-top: 2rpx; }

.clear-btn {
  width: 56rpx;
  height: 56rpx;
  border-radius: 14rpx;
  background: #F0F0F0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-left: 8rpx;
}
.clear-btn .ph { font-size: 26rpx; color: #A0AEC0; }

/* scroll-view 必须有明确高度才能滚动 */
.chat-messages {
  flex: 1;
  overflow: hidden;
  padding: 20rpx 24rpx;
  box-sizing: border-box;
}

.welcome-tip {
  background: #FFFFFF;
  padding: 20rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  color: #718096;
  line-height: 1.7;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

/* 快捷卡片 - 用 overflow:hidden + float 或直接 inline-block 避免gap问题 */
.quick-cards {
  margin-bottom: 20rpx;
  font-size: 0; /* 消除inline-block间距 */
}

.quick-card {
  display: inline-block;
  width: calc(50% - 8rpx);
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 18rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
  margin-bottom: 12rpx;
  vertical-align: top;
  box-sizing: border-box;
}

.quick-card:nth-child(odd) { margin-right: 16rpx; }

.quick-card .ph {
  font-size: 30rpx;
  color: #4F9EF8;
  display: block;
  margin-bottom: 8rpx;
}

.quick-card-text {
  font-size: 22rpx;
  color: #2D3748;
  line-height: 1.4;
  font-weight: 600;
}

/* 消息行 - 关键：用 overflow:hidden 清除浮动，避免flex子元素分离 */
.message {
  overflow: hidden; /* 清除浮动 */
  margin-bottom: 20rpx;
}

/* AI消息：头像左浮动 */
.message.assistant .message-avatar {
  float: left;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12rpx;
  flex-shrink: 0;
}

.message.assistant .message-avatar .ph {
  font-size: 28rpx;
  color: #4F9EF8;
}

/* 用户消息：头像右浮动 */
.message.user .message-avatar {
  float: right;
  width: 56rpx;
  height: 56rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #F0FDF4, #DCFCE7);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 12rpx;
  flex-shrink: 0;
}

.message.user .message-avatar .ph {
  font-size: 28rpx;
  color: #22C55E;
}

/* 消息内容：overflow:hidden 让它自动填充剩余宽度 */
.message-content {
  overflow: hidden;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  display: inline-block;
  max-width: 100%;
  padding: 18rpx 20rpx;
  border-radius: 16rpx;
  font-size: 26rpx;
  line-height: 1.7;
  word-break: break-all;
  word-wrap: break-word;
  text-align: left;
}

.message.assistant .message-text {
  background: #FFFFFF;
  color: #2D3748;
  border-bottom-left-radius: 4rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.message.user .message-text {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  border-bottom-right-radius: 4rpx;
  box-shadow: 0 4rpx 12rpx rgba(59, 130, 246, 0.2);
}

.cursor { color: #4F9EF8; animation: blink 1s step-end infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

.message-time {
  font-size: 18rpx;
  color: #A0AEC0;
  margin-top: 6rpx;
  display: block;
}

.message.user .message-time { text-align: right; }

.message-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6rpx;
}
.message.user .message-footer { flex-direction: row-reverse; }

.save-btn {
  width: 40rpx; height: 40rpx;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}
.save-btn .ph { font-size: 26rpx; color: #A0AEC0; }
.save-btn.saved .ph { color: #F57F17; }
.save-btn:active { transform: scale(0.85); }

/* 思考动画 */
.thinking { padding: 20rpx 24rpx !important; }

.dot-flashing {
  position: relative;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background-color: #A0AEC0;
  animation: dot-flashing 1s infinite linear alternate;
  animation-delay: 0.5s;
  display: inline-block;
}

.dot-flashing::before,
.dot-flashing::after {
  content: '';
  display: inline-block;
  position: absolute;
  top: 0;
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background-color: #A0AEC0;
}

.dot-flashing::before { left: -22rpx; animation: dot-flashing 1s infinite alternate; animation-delay: 0s; }
.dot-flashing::after { left: 22rpx; animation: dot-flashing 1s infinite alternate; animation-delay: 1s; }

@keyframes dot-flashing {
  0% { background-color: #A0AEC0; }
  100% { background-color: #E5E7EB; }
}

/* 输入区域 - 固定在底部 */
.input-section {
  background: #FFFFFF;
  padding: 14rpx 20rpx;
  padding-bottom: calc(14rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid #F0F0F0;
  flex-shrink: 0;
}

/* 快捷问题 - inline-block 避免gap */
.quick-questions {
  margin-bottom: 12rpx;
  font-size: 0;
}

.quick-btn {
  display: inline-block;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  color: #4F9EF8;
  padding: 8rpx 18rpx;
  border-radius: 9999rpx;
  font-size: 20rpx;
  font-weight: 600;
  margin-right: 10rpx;
  margin-bottom: 8rpx;
}

/* 输入行 - 用 table 布局确保兼容性 */
.input-row {
  display: flex;
  align-items: center;
  background: #F5F7FA;
  border: 2rpx solid #E5E7EB;
  border-radius: 9999rpx;
  padding: 10rpx 10rpx 10rpx 20rpx;
  box-sizing: border-box;
}

.input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-size: 26rpx;
  color: #2D3748;
  height: 60rpx;
  line-height: 60rpx;
}

.send-btn {
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2rpx 8rpx rgba(59, 130, 246, 0.25);
}

.send-btn.disabled { opacity: 0.4; box-shadow: none; }
.send-btn .ph { font-size: 26rpx; color: #FFFFFF; }
</style>
