import { get } from './index.js';

export const getReports = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/reports/', params);
};

export const getReport = (id) => get(`/api/reports/${id}`);

export const getReportDimensions = (id) => get(`/api/reports/${id}/dimensions`);
