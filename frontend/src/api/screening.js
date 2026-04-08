import { get, post } from './index.js';

export const getQuestions = (gameType, difficulty = 'L1', count = 10) => {
  return get(`/api/screenings/questions/${gameType}`, { difficulty, count });
};

export const startScreening = (data) => post('/api/screenings/start', data);

export const submitScreening = (data) => post('/api/screenings/submit', data);

export const getScreeningHistory = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/screenings/history', params);
};
