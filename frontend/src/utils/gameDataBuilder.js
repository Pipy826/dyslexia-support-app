/**
 * 游戏数据构建纯函数 & 重试队列工具
 * gameDataBuilder.js
 *
 * CompleteTaskPayload 结构：
 * {
 *   correct_count: number,
 *   total_count: number,
 *   accuracy: number,        // 0-100 整数
 *   extra_data: string,      // JSON.stringify 后的字符串，包含游戏特有字段
 * }
 */

// ─────────────────────────────────────────────
// Payload 构建函数
// ─────────────────────────────────────────────

/**
 * 构建手写汉字游戏提交 payload
 * @param {Object} result - {
 *   taskId, difficulty, score, starsEarned, durationSeconds,
 *   charactersAttempted, charactersPasssed
 * }
 * @returns {Object} CompleteTaskPayload
 */
export function buildHandwritingPayload(result) {
  const {
    taskId,
    difficulty,
    score,
    starsEarned,
    durationSeconds,
    charactersAttempted,
    charactersPasssed, // 保留原拼写（与接口约定一致）
  } = result;

  const correctCount =
    typeof charactersPasssed === 'number' ? charactersPasssed : 0;
  const totalCount =
    typeof charactersAttempted === 'number' ? charactersAttempted : 0;
  const accuracy = Math.round(Math.min(100, Math.max(0, score || 0)));

  const extraData = {
    game_type: 'handwriting',
    difficulty: difficulty || 'L1',
    stars_earned: starsEarned || 0,
    duration_seconds: durationSeconds || 0,
    score: accuracy,
    characters_attempted: totalCount,
    characters_passed: correctCount,
  };

  return {
    correct_count: correctCount,
    total_count: totalCount,
    accuracy,
    extra_data: JSON.stringify(extraData),
  };
}

/**
 * 构建翻牌记忆游戏提交 payload
 * @param {Object} result - {
 *   taskId, difficulty, starsEarned, durationSeconds,
 *   totalPairs, flipCount, matchCount
 * }
 * @returns {Object} CompleteTaskPayload
 */
export function buildFlipCardPayload(result) {
  const {
    taskId,
    difficulty,
    starsEarned,
    durationSeconds,
    totalPairs,
    flipCount,
    matchCount,
  } = result;

  const correctCount = typeof matchCount === 'number' ? matchCount : 0;
  const totalCount = typeof totalPairs === 'number' ? totalPairs : 0;
  const accuracy =
    totalCount > 0
      ? Math.round((correctCount / totalCount) * 100)
      : 0;

  const extraData = {
    game_type: 'flip_card',
    difficulty: difficulty || 'L1',
    stars_earned: starsEarned || 0,
    duration_seconds: durationSeconds || 0,
    total_pairs: totalCount,
    flip_count: typeof flipCount === 'number' ? flipCount : 0,
    match_count: correctCount,
  };

  return {
    correct_count: correctCount,
    total_count: totalCount,
    accuracy,
    extra_data: JSON.stringify(extraData),
  };
}

/**
 * 构建连一连游戏提交 payload
 * @param {Object} result - {
 *   taskId, difficulty, starsEarned, durationSeconds,
 *   totalPairs, correctPairs, accuracyRate
 * }
 * @returns {Object} CompleteTaskPayload
 */
export function buildConnectGamePayload(result) {
  const {
    taskId,
    difficulty,
    starsEarned,
    durationSeconds,
    totalPairs,
    correctPairs,
    accuracyRate,
  } = result;

  const correctCount = typeof correctPairs === 'number' ? correctPairs : 0;
  const totalCount = typeof totalPairs === 'number' ? totalPairs : 0;
  const accuracy = Math.round(
    Math.min(100, Math.max(0, (accuracyRate || 0) * 100))
  );

  const extraData = {
    game_type: 'connect_game',
    difficulty: difficulty || 'L1',
    stars_earned: starsEarned || 0,
    duration_seconds: durationSeconds || 0,
    total_pairs: totalCount,
    correct_pairs: correctCount,
    accuracy_rate: typeof accuracyRate === 'number' ? accuracyRate : 0,
  };

  return {
    correct_count: correctCount,
    total_count: totalCount,
    accuracy,
    extra_data: JSON.stringify(extraData),
  };
}

// ─────────────────────────────────────────────
// 重试队列工具函数
// 使用 uni.setStorageSync / uni.getStorageSync
// key: 'pending_game_records'
// ─────────────────────────────────────────────

const QUEUE_KEY = 'pending_game_records';

/**
 * 读取本地队列，若不存在则返回空数组
 * @returns {Array}
 */
function readQueue() {
  try {
    const data = uni.getStorageSync(QUEUE_KEY);
    return Array.isArray(data) ? data : [];
  } catch (e) {
    return [];
  }
}

/**
 * 将队列写入本地存储
 * @param {Array} queue
 */
function writeQueue(queue) {
  try {
    uni.setStorageSync(QUEUE_KEY, queue);
  } catch (e) {
    // 静默失败，不影响游戏流程
  }
}

/**
 * 将记录加入本地缓存队列
 * @param {Object} record - { taskId, payload, retryCount, createdAt }
 */
export function enqueueRecord(record) {
  const queue = readQueue();
  const newRecord = {
    retryCount: 0,
    createdAt: new Date().toISOString(),
    ...record,
  };
  queue.push(newRecord);
  writeQueue(queue);
}

/**
 * 取出并移除队列第一条记录
 * 队列为空时返回 null
 * @returns {Object|null}
 */
export function dequeueRecord() {
  const queue = readQueue();
  if (queue.length === 0) return null;
  const [first, ...rest] = queue;
  writeQueue(rest);
  return first;
}

/**
 * retryCount + 1，返回新记录对象（不修改原对象）
 * @param {Object} record
 * @returns {Object}
 */
export function incrementRetryCount(record) {
  return {
    ...record,
    retryCount: (record.retryCount || 0) + 1,
  };
}

/**
 * retryCount < 3 时返回 true
 * @param {Object} record
 * @returns {boolean}
 */
export function shouldRetry(record) {
  return (record.retryCount || 0) < 3;
}
