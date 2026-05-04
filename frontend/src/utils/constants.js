// 常量定义

export const GAME_TYPES = {
  VISUAL: 'visual',
  SPELLING: 'spelling',
  COMPREHENSION: 'comprehension',
  WORKING_MEMORY: 'working_memory',
  RAPID_NAMING: 'rapid_naming',
  MOTOR_COORDINATION: 'motor_coordination',
  HANDWRITING: 'handwriting',
  FLIP_CARD: 'flip_card',
  CONNECT_GAME: 'connect_game',
};

export const GAME_NAMES = {
  [GAME_TYPES.VISUAL]: '视觉辨识',
  [GAME_TYPES.SPELLING]: '拼字识别',
  [GAME_TYPES.COMPREHENSION]: '文字理解',
  [GAME_TYPES.WORKING_MEMORY]: '工作记忆',
  [GAME_TYPES.RAPID_NAMING]: '快速命名',
  [GAME_TYPES.MOTOR_COORDINATION]: '精细动作',
  [GAME_TYPES.HANDWRITING]: '手写汉字',
  [GAME_TYPES.FLIP_CARD]: '翻牌记忆',
  [GAME_TYPES.CONNECT_GAME]: '连一连',
};

export const DIFFICULTY_LEVELS = ['L1', 'L2', 'L3'];

export const RISK_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high'
};

export const RISK_LABELS = {
  [RISK_LEVELS.LOW]: '表现良好',
  [RISK_LEVELS.MEDIUM]: '有些地方可以加强',
  [RISK_LEVELS.HIGH]: '需要更多关注'
};

export const TASK_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed'
};

// 家长端 tab 列表
export const PARENT_TABS = [
  { id: 'home', label: '首页', icon: 'home' },
  { id: 'screening', label: '探索', icon: 'search' },
  { id: 'report', label: '报告', icon: 'file-text' },
  { id: 'training', label: '训练', icon: 'clipboard' },
  { id: 'profile', label: '我的', icon: 'user' }
];

// 儿童端 tab 列表
export const CHILD_TABS = [
  { id: 'challenge', label: '挑战', icon: 'rocket' },
  { id: 'training', label: '训练', icon: 'tree' },
  { id: 'today', label: '今日任务', icon: 'calendar-check' },
];

// 训练任务图标映射
export const GAME_TASK_ICONS = {
  // 现有六种
  visual: 'ph-eye',
  spelling: 'ph-puzzle-piece',
  comprehension: 'ph-book-open',
  working_memory: 'ph-brain',
  rapid_naming: 'ph-lightning',
  motor_coordination: 'ph-hand',
  // 新增三种
  handwriting: 'ph-pencil-line',
  flip_card: 'ph-cards',
  connect_game: 'ph-link',
}

export const GAME_TASK_DEFAULT_NAMES = {
  visual: '火眼金睛',
  spelling: '拼字小达人',
  comprehension: '故事大王',
  working_memory: '记忆训练',
  rapid_naming: '快速命名',
  motor_coordination: '精细动作',
  handwriting: '汉字书写',
  flip_card: '翻牌记忆',
  connect_game: '连一连',
}

export const GAME_TASK_DESCS = {
  visual: '找出不一样的字',
  spelling: '把字拼完整',
  comprehension: '读句子选图片',
  working_memory: '记住序列顺序',
  rapid_naming: '快速说出名称',
  motor_coordination: '判断线条方向',
  handwriting: '练习汉字书写',
  flip_card: '翻牌找配对',
  connect_game: '连线找匹配',
}

export const GAME_THEME_ANIMALS = {
  visual: { emoji: '🦉', label: '猫头鹰' },
  spelling: { emoji: '🐝', label: '小蜜蜂' },
  comprehension: { emoji: '🐸', label: '青蛙' },
  working_memory: { emoji: '🐘', label: '大象' },
  rapid_naming: { emoji: '🐇', label: '小兔' },
  motor_coordination: { emoji: '🐼', label: '熊猫' },
  handwriting: { emoji: '🦊', label: '小狐狸' },
  flip_card: { emoji: '🐱', label: '小猫' },
  connect_game: { emoji: '🐶', label: '小狗' },
}

// 游戏卡片颜色配置（主色 + 背景渐变）
export const GAME_CARD_COLORS = {
  visual:             { color: '#4F9EF8', bg: 'linear-gradient(135deg, #EFF6FF, #DBEAFE)' },
  spelling:           { color: '#A78BFA', bg: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)' },
  comprehension:      { color: '#22C55E', bg: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)' },
  working_memory:     { color: '#F97316', bg: 'linear-gradient(135deg, #FFF7ED, #FFEDD5)' },
  rapid_naming:       { color: '#EAB308', bg: 'linear-gradient(135deg, #FEFCE8, #FEF9C3)' },
  motor_coordination: { color: '#EC4899', bg: 'linear-gradient(135deg, #FDF2F8, #FCE7F3)' },
  handwriting:        { color: '#F57F17', bg: 'linear-gradient(135deg, #FFF8F0, #FFF3E0)' },
  flip_card:          { color: '#7C3AED', bg: 'linear-gradient(135deg, #F5F3FF, #EDE9FE)' },
  connect_game:       { color: '#16A34A', bg: 'linear-gradient(135deg, #F0FDF4, #DCFCE7)' },
}

// 游戏路由映射（所有游戏都先经过引导页）
export const GAME_ROUTES = {
  visual: '/pages/child/prep/index',
  spelling: '/pages/child/prep/index',
  comprehension: '/pages/child/prep/index',
  working_memory: '/pages/child/prep/index',
  rapid_naming: '/pages/child/prep/index',
  motor_coordination: '/pages/child/prep/index',
  handwriting: '/pages/child/prep/index',
  flip_card: '/pages/child/prep/index',
  connect_game: '/pages/child/prep/index',
}

// 引导页跳转到的实际游戏路由
export const GAME_PLAY_ROUTES = {
  visual: '/pages/child/game/index',
  spelling: '/pages/child/game/index',
  comprehension: '/pages/child/game/index',
  working_memory: '/pages/child/game/index',
  rapid_naming: '/pages/child/game/index',
  motor_coordination: '/pages/child/game/index',
  handwriting: '/pages/child/handwriting-game/index',
  flip_card: '/pages/child/flip-card-game/index',
  connect_game: '/pages/child/connect-game/index',
}
