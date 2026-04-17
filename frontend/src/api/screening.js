import { get, post } from './index.js';

/**
 * 获取游戏题目
 * @param {string} gameType - 游戏类型
 * @param {object} options  - { difficulty, grade, count }
 *   - difficulty: 显式指定难度（自适应调难时传入），传了则忽略 grade 映射
 *   - grade: 孩子学龄（首次加载时传入，后端自动映射难度）
 *   - count: 题目数量，默认 10
 */
export const getQuestions = (gameType, options = {}) => {
  const { difficulty, grade, count = 10 } = typeof options === 'string'
    ? { difficulty: options }   // 兼容旧的字符串调用方式
    : options
  const params = { count }
  if (difficulty) params.difficulty = difficulty
  if (grade) params.grade = grade
  return get(`/api/screenings/questions/${gameType}`, params)
};

export const startScreening = (data) => post('/api/screenings/start', data);

export const submitScreening = (data) => post('/api/screenings/submit', data);

export const getScreeningHistory = (childId) => {
  const params = childId ? { child_id: childId } : {};
  return get('/api/screenings/history', params);
};
