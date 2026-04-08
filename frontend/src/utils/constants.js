// 常量定义

export const GAME_TYPES = {
  VISUAL: 'visual',
  SPELLING: 'spelling',
  COMPREHENSION: 'comprehension'
};

export const GAME_NAMES = {
  [GAME_TYPES.VISUAL]: '视觉辨识',
  [GAME_TYPES.SPELLING]: '拼字识别',
  [GAME_TYPES.COMPREHENSION]: '文字理解'
};

export const DIFFICULTY_LEVELS = ['L1', 'L2', 'L3'];

export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high'
};

export const RISK_LABELS = {
  [RISK_LEVELS.LOW]: '低风险',
  [RISK_LEVELS.MEDIUM]: '中风险',
  [RISK_LEVELS.HIGH]: '高风险'
};

export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed'
};

// 家长端 tab 列表
export const PARENT_TABS = [
  { id: 'home', label: '首页', icon: 'home' },
  { id: 'screening', label: '筛查', icon: 'search' },
  { id: 'report', label: '报告', icon: 'file-text' },
  { id: 'training', label: '训练', icon: 'clipboard' },
  { id: 'profile', label: '我的', icon: 'user' }
];

// 儿童端 tab 列表
export const CHILD_TABS = [
  { id: 'challenge', label: '挑战', icon: 'rocket' },
  { id: 'training', label: '训练乐园', icon: 'star' }
];
