/**
 * 关卡评分工具模块
 * 所有函数均为纯函数，无副作用，可独立测试
 */

/**
 * 多选题评分（圈出所有错字）
 * @param {Set|Array} selectedPositions - 用户选中的字符位置集合
 * @param {Array} errorPositions - 正确错字位置数组（非空）
 * @returns {number} 得分，范围 [0, 1]
 */
export function scoreMultiSelect(selectedPositions, errorPositions) {
  if (!errorPositions || errorPositions.length === 0) return 0

  const selectedSet = selectedPositions instanceof Set
    ? selectedPositions
    : new Set(selectedPositions)

  const errorSet = new Set(errorPositions)
  const total = errorPositions.length

  // 正确选中数 = 交集大小
  let correctCount = 0
  for (const pos of selectedSet) {
    if (errorSet.has(pos)) correctCount++
  }

  // 误选数 = 选中但不在错字位置中的数量
  const wrongCount = selectedSet.size - correctCount

  return Math.max(0, (correctCount - wrongCount) / total)
}

/**
 * 拼音拼写评分
 * @param {Array} selectedBlocks - 用户选择的字母块数组（有序）
 * @param {string} correctPinyin - 正确拼音字符串（含声调）
 * @returns {number} 0.0 或 1.0
 */
export function scorePinyinSpelling(selectedBlocks, correctPinyin) {
  if (!selectedBlocks || !correctPinyin) return 0.0
  const assembled = selectedBlocks.join('')
  return assembled === correctPinyin ? 1.0 : 0.0
}

/**
 * 点击序列复现评分
 * @param {Array} clickedSequence - 用户点击的格子索引数组
 * @param {Array} correctSequence - 正确序列数组
 * @returns {number} 0.0 或 1.0
 */
export function scoreSequenceClick(clickedSequence, correctSequence) {
  if (!clickedSequence || !correctSequence) return 0.0
  if (clickedSequence.length !== correctSequence.length) return 0.0
  const allCorrect = clickedSequence.every((v, i) => v === correctSequence[i])
  return allCorrect ? 1.0 : 0.0
}

/**
 * 计时点击评分
 * @param {Set} clickedIds - 已点击项目 ID 的 Set
 * @param {Array} items - 项目数组，每项含 id 和 is_target
 * @returns {number} 得分，范围 [0, 1]
 */
export function scoreTimedClick(clickedIds, items) {
  if (!items || items.length === 0) return 0

  const targets = items.filter(i => i.is_target)
  if (targets.length === 0) return 0

  const clickedSet = clickedIds instanceof Set ? clickedIds : new Set(clickedIds)

  const correctClicks = targets.filter(t => clickedSet.has(t.id)).length
  const wrongClicks = items.filter(i => !i.is_target && clickedSet.has(i.id)).length

  return Math.max(0, (correctClicks - wrongClicks) / targets.length)
}

/**
 * 计算参考路径上被用户轨迹覆盖的比例
 * @param {Array} userPath - 用户轨迹点数组 [{x, y}]
 * @param {Array} referencePath - 参考路径点数组 [{x, y}]
 * @param {number} tolerance - 容差（归一化单位）
 * @returns {number} 覆盖比例 [0, 1]
 */
function calcPathCoverage(userPath, referencePath, tolerance) {
  if (!userPath || userPath.length === 0 || !referencePath || referencePath.length === 0) return 0

  // 对参考路径进行插值，生成均匀采样点
  const samplePoints = interpolatePath(referencePath, 50)
  let coveredCount = 0

  for (const refPt of samplePoints) {
    // 检查用户轨迹中是否有点在容差范围内
    const covered = userPath.some(userPt => {
      const dx = userPt.x - refPt.x
      const dy = userPt.y - refPt.y
      return Math.sqrt(dx * dx + dy * dy) <= tolerance
    })
    if (covered) coveredCount++
  }

  return coveredCount / samplePoints.length
}

/**
 * 计算用户轨迹到参考路径的平均最近距离
 * @param {Array} userPath - 用户轨迹点数组 [{x, y}]
 * @param {Array} referencePath - 参考路径点数组 [{x, y}]
 * @returns {number} 平均偏差
 */
function calcAverageDeviation(userPath, referencePath) {
  if (!userPath || userPath.length === 0 || !referencePath || referencePath.length === 0) return Infinity

  const samplePoints = interpolatePath(referencePath, 50)
  let totalDist = 0

  for (const userPt of userPath) {
    let minDist = Infinity
    for (const refPt of samplePoints) {
      const dx = userPt.x - refPt.x
      const dy = userPt.y - refPt.y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < minDist) minDist = dist
    }
    totalDist += minDist
  }

  return totalDist / userPath.length
}

/**
 * 对路径进行均匀插值，生成 n 个采样点
 * @param {Array} path - 路径点数组 [{x, y}]
 * @param {number} n - 采样点数量
 * @returns {Array} 插值后的点数组
 */
function interpolatePath(path, n) {
  if (path.length === 1) return [path[0]]
  if (path.length === 0) return []

  // 计算总路径长度
  let totalLength = 0
  const segments = []
  for (let i = 1; i < path.length; i++) {
    const dx = path[i].x - path[i - 1].x
    const dy = path[i].y - path[i - 1].y
    const len = Math.sqrt(dx * dx + dy * dy)
    segments.push(len)
    totalLength += len
  }

  if (totalLength === 0) return [path[0]]

  const result = []
  const step = totalLength / (n - 1)
  let accumulated = 0
  let segIdx = 0
  let segAccum = 0

  result.push({ x: path[0].x, y: path[0].y })

  for (let i = 1; i < n - 1; i++) {
    const target = i * step
    while (segIdx < segments.length && segAccum + segments[segIdx] < target) {
      segAccum += segments[segIdx]
      segIdx++
    }
    if (segIdx >= segments.length) break
    const t = (target - segAccum) / segments[segIdx]
    const p0 = path[segIdx]
    const p1 = path[segIdx + 1]
    result.push({
      x: p0.x + t * (p1.x - p0.x),
      y: p0.y + t * (p1.y - p0.y)
    })
  }

  result.push({ x: path[path.length - 1].x, y: path[path.length - 1].y })
  return result
}

/**
 * 路径描绘评分
 * @param {Array} userPath - 用户轨迹点数组 [{x, y}]
 * @param {Array} referencePath - 参考路径点数组 [{x, y}]
 * @param {number} tolerance - 容差（正数，归一化单位）
 * @param {number} minCoverage - 最小覆盖率 [0, 1]
 * @returns {number} 得分，范围 [0, 1]
 */
export function scorePathDraw(userPath, referencePath, tolerance, minCoverage) {
  if (!userPath || userPath.length === 0) return 0
  if (!referencePath || referencePath.length === 0) return 0
  if (tolerance <= 0) return 0

  const coverage = calcPathCoverage(userPath, referencePath, tolerance)

  if (coverage < minCoverage) return 0

  const avgDeviation = calcAverageDeviation(userPath, referencePath)
  const accuracyScore = Math.max(0, 1 - avgDeviation / tolerance)

  return Math.min(1, coverage * 0.6 + accuracyScore * 0.4)
}

/**
 * 构建关卡完成后的 extra_data 对象
 * @param {Object} params
 * @param {string} params.gameType - 游戏类型
 * @param {string} params.difficulty - 难度
 * @param {string} params.levelId - 关卡 ID
 * @param {number} params.levelNum - 关卡编号
 * @param {number} params.accuracy - 正确率 [0, 1]
 * @param {number} params.correctCount - 答对题数
 * @param {number} params.totalCount - 总题数
 * @param {number} params.durationSeconds - 用时秒数
 * @param {Object} params.passCondition - 通关条件 { min_accuracy: number }
 * @returns {Object} extra_data 对象（含10个必要字段）
 */
export function buildLevelExtraData(params) {
  const {
    gameType,
    difficulty,
    levelId,
    levelNum,
    accuracy,
    correctCount,
    totalCount,
    durationSeconds,
    passCondition
  } = params

  const passed = accuracy >= passCondition.min_accuracy

  let starsEarned = 0
  if (passed) {
    if (accuracy >= 0.95) {
      starsEarned = 3
    } else if (accuracy >= 0.8) {
      starsEarned = 2
    } else {
      starsEarned = 1
    }
  }

  return {
    game_type: gameType,
    difficulty: difficulty,
    level_id: levelId,
    level_num: levelNum,
    passed: passed,
    accuracy: accuracy,
    correct_count: correctCount,
    total_count: totalCount,
    duration_seconds: durationSeconds,
    stars_earned: starsEarned
  }
}
