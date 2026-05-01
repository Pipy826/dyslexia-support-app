/**
 * 能力标签映射工具
 * 将专业维度分数映射为儿童友好的能力标签，隐藏医疗化表达
 *
 * 设计原则：
 * - 所有标签使用正向或中性表达，不含负面词汇
 * - 低分段使用"成长中"等鼓励性表达，而非"差"、"弱"等负面词
 * - 与游戏主题色系统（gameThemes.js）保持一致的游戏类型键名
 */

export const ABILITY_LABELS = {
  visual: {
    high: {
      label: '眼力小达人',
      emoji: '👁️',
      desc: '你的眼睛很厉害，能快速找到不同！',
      starRating: 5,
    },
    mid: {
      label: '眼力不错哦',
      emoji: '😊',
      desc: '再多练练，眼力会更强！',
      starRating: 3,
    },
    low: {
      label: '眼力在成长',
      emoji: '💪',
      desc: '没关系，多玩几次就会进步！',
      starRating: 2,
    },
  },
  spelling: {
    high: {
      label: '文字小魔法师',
      emoji: '✨',
      desc: '你认识好多字，真厉害！',
      starRating: 5,
    },
    mid: {
      label: '文字小学徒',
      emoji: '📚',
      desc: '继续加油，你会认识更多字！',
      starRating: 3,
    },
    low: {
      label: '文字探险家',
      emoji: '🔍',
      desc: '每个字都是新朋友，慢慢认识它们！',
      starRating: 2,
    },
  },
  comprehension: {
    high: {
      label: '故事小达人',
      emoji: '📖',
      desc: '你理解故事的能力超强！',
      starRating: 5,
    },
    mid: {
      label: '故事小读者',
      emoji: '🌱',
      desc: '多读故事，理解力会越来越好！',
      starRating: 3,
    },
    low: {
      label: '故事小探索者',
      emoji: '🗺️',
      desc: '每个故事都有宝藏，慢慢发现！',
      starRating: 2,
    },
  },
  working_memory: {
    high: {
      label: '记忆小冠军',
      emoji: '🧠',
      desc: '你的记忆力超级棒！',
      starRating: 5,
    },
    mid: {
      label: '记忆小能手',
      emoji: '💡',
      desc: '记忆力不错，继续练习会更强！',
      starRating: 3,
    },
    low: {
      label: '记忆小训练师',
      emoji: '🎯',
      desc: '记忆力是可以练出来的，加油！',
      starRating: 2,
    },
  },
  rapid_naming: {
    high: {
      label: '反应小闪电',
      emoji: '⚡',
      desc: '你的反应速度超快！',
      starRating: 5,
    },
    mid: {
      label: '反应小能手',
      emoji: '🏃',
      desc: '反应不错，多练练会更快！',
      starRating: 3,
    },
    low: {
      label: '反应小学员',
      emoji: '🌟',
      desc: '慢慢来，速度会越来越快的！',
      starRating: 2,
    },
  },
  motor_coordination: {
    high: {
      label: '手眼协调王',
      emoji: '🎯',
      desc: '你的手眼配合超级棒！',
      starRating: 5,
    },
    mid: {
      label: '手眼小能手',
      emoji: '✋',
      desc: '配合不错，继续练习！',
      starRating: 3,
    },
    low: {
      label: '手眼小训练师',
      emoji: '💪',
      desc: '多做手工游戏，会越来越好！',
      starRating: 2,
    },
  },
}

/**
 * 根据游戏类型和分数获取能力标签
 * @param {string} gameType - 游戏类型（visual/spelling/comprehension/working_memory/rapid_naming/motor_coordination）
 * @param {number} score - 分数（0-100）
 * @returns {{ label: string, emoji: string, desc: string, starRating: number } | null}
 *
 * 属性保证：
 * - 完备性：对任意合法 gameType 和 score（0-100），始终返回非空对象
 * - 非负性：所有标签不含负面词汇（差、弱、障碍、风险、问题）
 */
export function getAbilityLabel(gameType, score) {
  const labels = ABILITY_LABELS[gameType]
  if (!labels) {
    // 未知游戏类型，返回通用标签
    return {
      label: '小小探险家',
      emoji: '🌟',
      desc: '你完成了挑战，真棒！',
      starRating: 3,
    }
  }

  const numScore = Number(score) || 0
  if (numScore >= 75) return labels.high
  if (numScore >= 55) return labels.mid
  return labels.low
}

/**
 * 将分数转换为1-5星评级
 * @param {number} score - 分数（0-100）
 * @returns {number} - 1-5的整数
 */
export function scoreToStars(score) {
  const numScore = Number(score) || 0
  if (numScore >= 90) return 5
  if (numScore >= 75) return 4
  if (numScore >= 60) return 3
  if (numScore >= 40) return 2
  return 1
}

/**
 * 获取游戏类型的中文名称
 * @param {string} gameType
 * @returns {string}
 */
export function getGameTypeName(gameType) {
  const names = {
    visual: '视觉辨识',
    spelling: '拼字识别',
    comprehension: '文字理解',
    working_memory: '工作记忆',
    rapid_naming: '快速命名',
    motor_coordination: '精细动作',
  }
  return names[gameType] || gameType
}

/**
 * 获取所有游戏类型的能力标签（用于能力地图展示）
 * @param {object} scores - { gameType: score } 格式的分数对象
 * @returns {Array<{ gameType, name, label, emoji, desc, starRating, score }>}
 */
export function getAllAbilityLabels(scores) {
  const gameTypes = ['visual', 'spelling', 'comprehension', 'working_memory', 'rapid_naming', 'motor_coordination']
  return gameTypes
    .filter(type => scores[type] !== undefined)
    .map(type => ({
      gameType: type,
      name: getGameTypeName(type),
      score: scores[type],
      ...getAbilityLabel(type, scores[type]),
    }))
}
