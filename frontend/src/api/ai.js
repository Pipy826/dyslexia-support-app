import { post, get, del } from './index.js';

export const chat = (data) => post('/api/ai/chat', data);

export const getChatHistory = (childId, limit = 20) => {
  const params = { limit };
  if (childId) params.child_id = childId;
  return get('/api/ai/history', params);
};

export const clearChatHistory = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return del('/api/ai/history', params);
};
