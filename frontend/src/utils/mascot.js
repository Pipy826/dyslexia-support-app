/**
 * 吉祥物"灯塔小精灵"状态管理
 * 在游戏过程中陪伴引导儿童，提供即时情感反馈
 */

export const MASCOT_STATES = {
  idle: 'idle',           // 默认待机
  excited: 'excited',     // 答对时
  thinking: 'thinking',   // 答题中
  encouraging: 'encouraging', // 答错鼓励
  celebrating: 'celebrating', // 游戏结束
}

export const MASCOT_EMOJIS = {
  idle: '😊',
  excited: '🤩',
  thinking: '🤔',
  encouraging: '💪',
  celebrating: '🎉',
}

export const MASCOT_MESSAGES = {
  correct: [
    '太棒了！',
    '你真厉害！',
    '完美！',
    '继续加油！',
    '答对啦！🌟',
    '超级棒！',
    '你好聪明！',
  ],
  wrong: [
    '没关系，再试试！',
    '下一题会更好！',
    '你已经很努力了！',
    '加油，你能行！',
    '继续挑战！💪',
  ],
  start: [
    '准备好了吗？',
    '让我们开始吧！',
    '加油！',
    '你可以的！',
    '一起来挑战！',
  ],
  end: [
    '你完成了！🎉',
    '太厉害了！',
    '为你骄傲！',
    '挑战成功！',
    '你真的很棒！',
  ],
  thinking: [
    '想一想...',
    '认真思考中...',
    '你能做到的！',
  ],
}

/**
 * 随机获取某类话语
 * @param {'correct'|'wrong'|'start'|'end'|'thinking'} type
 * @returns {string}
 */
export function getRandomMessage(type) {
  const messages = MASCOT_MESSAGES[type] || MASCOT_MESSAGES.start
  return messages[Math.floor(Math.random() * messages.length)]
}
