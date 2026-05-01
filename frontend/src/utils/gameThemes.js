/**
 * 游戏主题色系统
 * 每种游戏类型对应独立的主题色配置，通过 CSS 变量注入页面
 */

export const GAME_THEMES = {
  visual: {
    primary: '#4F9EF8',
    gradient: 'linear-gradient(135deg, #667EEA 0%, #764BA2 100%)',
    bgPattern: 'eyes',
    name: '视觉辨识',
  },
  spelling: {
    primary: '#A78BFA',
    gradient: 'linear-gradient(135deg, #A78BFA 0%, #EC4899 100%)',
    bgPattern: 'letters',
    name: '拼字识别',
  },
  comprehension: {
    primary: '#22C55E',
    gradient: 'linear-gradient(135deg, #11998E 0%, #38EF7D 100%)',
    bgPattern: 'books',
    name: '文字理解',
  },
  working_memory: {
    primary: '#F97316',
    gradient: 'linear-gradient(135deg, #F97316 0%, #FBBF24 100%)',
    bgPattern: 'brain',
    name: '工作记忆',
  },
  rapid_naming: {
    primary: '#EAB308',
    gradient: 'linear-gradient(135deg, #EAB308 0%, #F97316 100%)',
    bgPattern: 'lightning',
    name: '快速命名',
  },
  motor_coordination: {
    primary: '#EC4899',
    gradient: 'linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%)',
    bgPattern: 'hands',
    name: '精细动作',
  },
}

/**
 * 获取游戏主题配置
 * @param {string} gameType
 * @returns {object}
 */
export function getGameTheme(gameType) {
  return GAME_THEMES[gameType] || GAME_THEMES.visual
}

/**
 * 将游戏主题色注入为 CSS 变量（用于 H5 端）
 * @param {string} gameType
 * @param {HTMLElement} el - 目标元素，默认为 document.documentElement
 */
export function injectGameTheme(gameType, el) {
  const theme = getGameTheme(gameType)
  const target = el || (typeof document !== 'undefined' ? document.documentElement : null)
  if (target && target.style) {
    target.style.setProperty('--game-primary', theme.primary)
    target.style.setProperty('--game-gradient', theme.gradient)
  }
  return theme
}
