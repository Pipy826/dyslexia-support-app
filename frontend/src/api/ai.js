import { post, get, del } from './index.js';
import { getToken } from '../utils/auth.js';
import { getBaseUrl } from './index.js';

// ── 1. 普通对话 ───────────────────────────────────────────────────────────────
export const chat = (data) => post('/api/ai/chat', data);
// ── 2. 流式对话（SSE）────────────────────────────────────────────────────────
/**
 * 流式对话 - 兼容微信小程序和H5
 * 微信小程序使用 wx.request enableChunked 模式
 * H5 使用 fetch + ReadableStream
 */
export const chatStream = (data, onChunk, onDone, onError) => {
  const token = getToken();
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}/api/ai/chat/stream`;

  // #ifdef MP-WEIXIN
  // 微信小程序：使用 enableChunked 分块接收
  let buffer = '';
  const task = wx.request({
    url,
    method: 'POST',
    header: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    data: JSON.stringify(data),
    enableChunked: true,
    success() {
      onDone && onDone();
    },
    fail(err) {
      onError && onError(err);
    },
  });

  task.onChunkReceived((res) => {
    try {
      const decoder = new TextDecoder('utf-8');
      const chunk = decoder.decode(new Uint8Array(res.data));
      buffer += chunk;
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;
        try {
          const parsed = JSON.parse(jsonStr);
          if (parsed.chunk) onChunk(parsed.chunk);
          if (parsed.done) onDone && onDone(parsed);
        } catch (e) {}
      }
    } catch (e) {}
  });

  return () => task.abort();
  // #endif

  // #ifndef MP-WEIXIN
  // H5 / App：使用 fetch + ReadableStream
  const controller = new AbortController();
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(data),
    signal: controller.signal,
  })
    .then(async (resp) => {
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const reader = resp.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buf = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const lines = buf.split('\n');
        buf = lines.pop();
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          try {
            const parsed = JSON.parse(jsonStr);
            if (parsed.chunk) onChunk(parsed.chunk);
            if (parsed.done) onDone && onDone(parsed);
          } catch (e) {}
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') onError && onError(err);
    });
  return () => controller.abort();
  // #endif
};

// ── 3. 对话历史 ───────────────────────────────────────────────────────────────
export const getChatHistory = (childId, limit = 20) => {
  const params = { limit };
  if (childId) params.child_id = childId;
  return get('/api/ai/history', params);
};

export const clearChatHistory = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return del('/api/ai/history', params);
};

// ── 4. AI 报告解读 ────────────────────────────────────────────────────────────
export const getReportInterpretation = (reportId) =>
  post('/api/ai/report-interpretation', { report_id: reportId });

// ── 5. AI 生成训练计划 ────────────────────────────────────────────────────────
export const generateTrainingPlan = (childId, reportId = null) =>
  post('/api/ai/training-plan', { child_id: childId, report_id: reportId });

// ── 6. 儿童鼓励话语 ───────────────────────────────────────────────────────────
export const getEncouragement = (data) =>
  post('/api/ai/encouragement', data);

// ── 7. 成长趋势分析 ───────────────────────────────────────────────────────────
// AI 分析接口耗时较长，通过 request 的 timeout 参数设置 120 秒
export const getGrowthAnalysis = (childId) =>
  get(`/api/ai/growth-analysis/${childId}`, {}, {}, false, 120000);

// ── 8. 每日学习贴士 ───────────────────────────────────────────────────────────
export const getDailyTip = (childId) =>
  get(`/api/ai/daily-tip/${childId}`);

// ── 9. 家长情绪支持 ───────────────────────────────────────────────────────────
export const getEmotionalSupport = (reportId) =>
  post('/api/ai/emotional-support', { report_id: reportId });

// ── 10. 自适应难度评估 ────────────────────────────────────────────────────────
export const evaluateAdaptiveDifficulty = (data) =>
  post('/api/ai/adaptive-difficulty', data);

// ── 11. 专业支持引导 ──────────────────────────────────────────────────────────
export const getProfessionalGuidance = (childId) =>
  get(`/api/ai/professional-guidance/${childId}`);

// ── 12. AI 回复收藏 ───────────────────────────────────────────────────────────
export const saveMessage = (data) => post('/api/ai/saved-messages', data);
export const getSavedMessages = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/ai/saved-messages', params);
};
export const deleteSavedMessage = (id) => del(`/api/ai/saved-messages/${id}`);

// ── 13. 联系方式 ──────────────────────────────────────────────────────────────
export const getContactInfo = () => get('/api/ai/contact-info');
