import { post, get, del } from './index.js';
import { getToken } from '../utils/auth.js';

// ── 基础 URL（与 index.js 保持一致） ─────────────────────────────────────────
const getBaseUrl = () => {
  const configured = import.meta.env.VITE_API_BASE_URL || '';
  if (configured) return configured;
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') {
      return `http://${host}:8000`;
    }
  }
  return '';
};

// ── 1. 普通对话 ───────────────────────────────────────────────────────────────
export const chat = (data) => post('/api/ai/chat', data);

// ── 2. 流式对话（SSE） ────────────────────────────────────────────────────────
/**
 * 流式对话
 * @param {Object} data - { child_id, message }
 * @param {Function} onChunk - 每收到一个文字片段时的回调 (chunk: string) => void
 * @param {Function} onDone  - 流结束时的回调 () => void
 * @param {Function} onError - 出错时的回调 (err) => void
 * @returns {Function} abort - 调用可中断请求
 */
export const chatStream = (data, onChunk, onDone, onError) => {
  const token = getToken();
  const baseUrl = getBaseUrl();
  const url = `${baseUrl}/api/ai/chat/stream`;

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
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const reader = resp.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // 保留未完整的行

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr) continue;
          try {
            const parsed = JSON.parse(jsonStr);
            if (parsed.chunk) {
              onChunk(parsed.chunk);
            }
            if (parsed.done) {
              onDone && onDone();
            }
          } catch (_) {
            // 忽略解析错误
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError && onError(err);
      }
    });

  return () => controller.abort();
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
export const getGrowthAnalysis = (childId) =>
  get(`/api/ai/growth-analysis/${childId}`);

// ── 8. 每日学习贴士 ───────────────────────────────────────────────────────────
export const getDailyTip = (childId) =>
  get(`/api/ai/daily-tip/${childId}`);

// ── 9. 家长情绪支持 ───────────────────────────────────────────────────────────
export const getEmotionalSupport = (reportId) =>
  post('/api/ai/emotional-support', { report_id: reportId });

// ── 10. 自适应难度评估 ────────────────────────────────────────────────────────
export const evaluateAdaptiveDifficulty = (data) =>
  post('/api/ai/adaptive-difficulty', data);
