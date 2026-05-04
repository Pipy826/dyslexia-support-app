import { get } from './index.js';

export const getReports = (childId, limit = 20, offset = 0) => {
  const params = { limit, offset };
  if (childId) params.child_id = childId;
  return get('/api/reports/', params);
};

export const getReport = (id) => get(`/api/reports/${id}`);

export const getReportDimensions = (id) => get(`/api/reports/${id}/dimensions`);

export const getReportByScreening = (screeningId) => get(`/api/reports/by-screening/${screeningId}`);

/**
 * 获取孩子所有筛查报告的合并维度（综合能力图谱）
 */
export const getMergedDimensions = (childId) => get(`/api/reports/child/${childId}/merged-dimensions`);

/**
 * 服务端导出报告文字内容
 */
export const exportReportText = (id) => get(`/api/reports/${id}/export-text`)

/**
 * 获取孩子的成长日记数据
 */
export const getGrowthDiary = (childId) => get(`/api/reports/growth-diary/${childId}`)

/**
 * 获取孩子的游戏活动情况报告（家长端）
 */
export const getGameActivityReport = (childId, days = 30) =>
  get(`/api/reports/game-activity/${childId}`, { days })
