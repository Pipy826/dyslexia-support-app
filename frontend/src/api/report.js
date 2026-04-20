import { get } from './index.js';

export const getReports = (childId) => {
  const params = childId ? { child_id: childId } : {};
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
