import { get, post, put } from './index.js';

export const getTasks = (childId, status) => {
  const params = {};
  if (childId) params.child_id = childId;
  if (status) params.status = status;
  return get('/api/training/tasks', params);
};

export const createTask = (data) => post('/api/training/tasks', data);

export const updateTaskProgress = (taskId, data) => put(`/api/training/tasks/${taskId}/progress`, data);

export const completeTask = (taskId, data = null) => post(`/api/training/tasks/${taskId}/complete`, data || {});

export const getGrowthRecords = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/training/growth', params);
};

export const createGrowthRecord = (data) => post('/api/training/growth', data);

export const getRewards = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/training/rewards', params);
};

export const getTotalStars = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/training/stars', params);
};

export const getLeaderboard = (childId, scope = 'global', limit = 20) => {
  return get('/api/training/leaderboard', { child_id: childId, scope, limit });
};
