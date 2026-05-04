/**
 * 游戏评分与奖励计算纯函数
 * gameScoring.js
 */

/**
 * 计算两组笔迹的形态相似度（0–1）
 * 通过对比归一化后的点分布来估算相似度
 * @param {Array} strokes1 - 笔迹点序列数组，每笔为 [{x, y, t}, ...]
 * @param {Array} strokes2 - 参考笔迹点序列数组
 * @returns {number} 0–1 的相似度
 */
function calcShapeSimilarity(strokes1, strokes2) {
  // 将所有笔迹展平为点集
  const flatPoints = (strokes) =>
    strokes.reduce((acc, stroke) => acc.concat(stroke), []);

  const pts1 = flatPoints(strokes1);
  const pts2 = flatPoints(strokes2);

  if (pts1.length === 0 || pts2.length === 0) return 0;

  // 计算边界框并归一化
  const normalize = (points) => {
    const xs = points.map((p) => p.x);
    const ys = points.map((p) => p.y);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;
    return points.map((p) => ({
      x: (p.x - minX) / rangeX,
      y: (p.y - minY) / rangeY,
    }));
  };

  const norm1 = normalize(pts1);
  const norm2 = normalize(pts2);

  // 对两组点进行均匀重采样到相同数量，再计算平均距离
  const resample = (points, n) => {
    if (points.length === 0) return [];
    if (points.length === 1) return Array(n).fill(points[0]);
    const result = [];
    for (let i = 0; i < n; i++) {
      const idx = (i / (n - 1)) * (points.length - 1);
      const lo = Math.floor(idx);
      const hi = Math.min(lo + 1, points.length - 1);
      const t = idx - lo;
      result.push({
        x: points[lo].x * (1 - t) + points[hi].x * t,
        y: points[lo].y * (1 - t) + points[hi].y * t,
      });
    }
    return result;
  };

  const N = 32;
  const r1 = resample(norm1, N);
  const r2 = resample(norm2, N);

  // 计算平均欧氏距离，转换为相似度
  let totalDist = 0;
  for (let i = 0; i < N; i++) {
    const dx = r1[i].x - r2[i].x;
    const dy = r1[i].y - r2[i].y;
    totalDist += Math.sqrt(dx * dx + dy * dy);
  }
  const avgDist = totalDist / N;

  // avgDist 范围约 [0, sqrt(2)]，映射到相似度 [0, 1]
  const maxDist = Math.SQRT2;
  return Math.max(0, 1 - avgDist / maxDist);
}

/**
 * 手写汉字评分
 * 评分逻辑：笔画数量匹配度（50%权重）+ 形态相似度（50%权重），结果 clamp 至 [0, 100]
 * 空笔迹或单点笔迹返回 0
 * @param {Array} strokeData - 笔迹点序列数组，每笔为 [{x, y, t}, ...]
 * @param {Array} referenceData - 参考笔迹数据（同格式）
 * @returns {number} 0-100 整数评分
 */
export function evaluateHandwriting(strokeData, referenceData) {
  // 空笔迹检查
  if (!strokeData || strokeData.length === 0) return 0;

  // 过滤掉空笔画
  const validStrokes = strokeData.filter(
    (stroke) => Array.isArray(stroke) && stroke.length > 0
  );
  if (validStrokes.length === 0) return 0;

  // 单点笔迹检查（所有笔画合计只有 1 个点）
  const totalPoints = validStrokes.reduce(
    (sum, stroke) => sum + stroke.length,
    0
  );
  if (totalPoints <= 1) return 0;

  // 参考数据为空时，仅基于笔迹是否存在给基础分
  const refStrokes =
    referenceData && referenceData.length > 0
      ? referenceData.filter(
          (stroke) => Array.isArray(stroke) && stroke.length > 0
        )
      : [];

  if (refStrokes.length === 0) {
    // 无参考数据，给予基础分 50
    return 50;
  }

  // 笔画数量匹配度（50% 权重）
  const strokeCountScore = (() => {
    const ratio =
      Math.min(validStrokes.length, refStrokes.length) /
      Math.max(validStrokes.length, refStrokes.length);
    return ratio * 100;
  })();

  // 形态相似度（50% 权重）
  const shapeScore = calcShapeSimilarity(validStrokes, refStrokes) * 100;

  // 加权平均
  const rawScore = strokeCountScore * 0.5 + shapeScore * 0.5;

  // clamp 至 [0, 100] 并取整
  return Math.round(Math.min(100, Math.max(0, rawScore)));
}

/**
 * 根据手写评分计算星星奖励
 * score >= 60 返回 1，score < 60 返回 0
 * @param {number} score - 0-100 的评分
 * @returns {number} 0 或 1 颗星
 */
export function calcHandwritingStars(score) {
  return score >= 60 ? 1 : 0;
}

/**
 * 根据翻牌次数计算星星奖励
 * flipCount <= totalPairs → 3星
 * flipCount <= totalPairs * 1.5 → 2星
 * 其余 → 1星
 * 返回值始终在 [1, 3] 整数范围内
 * @param {number} flipCount - 实际翻牌次数
 * @param {number} totalPairs - 总配对数
 * @returns {number} 1-3 颗星
 */
export function calcFlipCardStars(flipCount, totalPairs) {
  if (flipCount <= totalPairs) {
    return 3;
  } else if (flipCount <= totalPairs * 1.5) {
    return 2;
  } else {
    return 1;
  }
}

/**
 * 根据连一连正确率计算星星奖励
 * accuracyRate = 1.0 → 3星
 * [0.8, 1.0) → 2星
 * [0.6, 0.8) → 1星
 * < 0.6 → 0星
 * @param {number} accuracyRate - 正确率 [0, 1]
 * @returns {number} 0-3 颗星
 */
export function calcConnectGameStars(accuracyRate) {
  if (accuracyRate >= 1.0) {
    return 3;
  } else if (accuracyRate >= 0.8) {
    return 2;
  } else if (accuracyRate >= 0.6) {
    return 1;
  } else {
    return 0;
  }
}

/**
 * 根据星星数量获取结果页表情图标识符
 * stars=1 → 'emoji_ok'
 * stars=2 → 'emoji_happy'
 * stars=3 → 'emoji_super'
 * @param {number} stars - 1-3 颗星
 * @returns {string} 表情图标识符
 */
export function getResultEmoji(stars) {
  if (stars === 3) return 'emoji_super';
  if (stars === 2) return 'emoji_happy';
  return 'emoji_ok';
}

/**
 * 从连线列表中移除指定 id 的连线，返回新数组
 * id 不存在时列表不变（幂等）
 * @param {Array} connections - [{id, leftId, rightId, isCorrect}, ...]
 * @param {string} connectionId
 * @returns {Array}
 */
export function removeConnection(connections, connectionId) {
  if (!Array.isArray(connections)) return [];
  return connections.filter((conn) => conn.id !== connectionId);
}
