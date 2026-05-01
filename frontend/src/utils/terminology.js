/**
 * 词汇映射工具 — 将医学化/标签化词汇替换为更温和、积极的表达
 * 设计原则：温和引导，避免家长产生焦虑感
 */

export const TERM_MAP = {
  '发起筛查': '开始能力探索',
  '筛查报告': '能力观察报告',
  '筛查历史': '探索记录',
  '历史报告': '成长记录',
  '筛查': '能力探索',
  '风险等级': '关注等级',
  '高风险': '需要更多关注',
  '中风险': '有些地方可以加强',
  '低风险': '表现良好',
  '读写障碍': '读写学习特点',
  '读写障碍筛查': '文字游戏挑战',
  '干预建议': '成长建议',
  '干预训练': '成长练习',
  '干预': '成长建议',
  '风险报告': '成长报告',
  '诊断': '观察',
  '风险': '关注',
  '专业评估': '趣味探索',
  '评估报告': '能力地图',
  '维度分数': '能力星级',
}

/**
 * 将词汇转换为友好表达
 * @param {string} term - 原始词汇
 * @returns {string} - 友好词汇，若不在映射表中则原样返回
 *
 * 属性保证：
 * - 幂等性：friendlyTerm(friendlyTerm(term)) === friendlyTerm(term)
 * - 完备性：对映射表中的词汇返回对应友好词汇，否则原样返回
 * - 非空性：任意输入的返回值不为空字符串
 */
export function friendlyTerm(term) {
  if (term === null || term === undefined) return ''
  const str = String(term)
  return TERM_MAP[str] || str
}

/**
 * 将风险等级代码转换为友好显示文本
 * @param {string} riskLevel - 'high' | 'medium' | 'low'
 * @returns {string}
 */
export function friendlyRiskLevel(riskLevel) {
  const map = {
    high: '需要更多关注',
    medium: '有些地方可以加强',
    low: '表现良好',
  }
  return map[riskLevel] || riskLevel
}

/**
 * 获取关注等级对应的颜色类名（温暖色调，非警告色调）
 * @param {string} riskLevel - 'high' | 'medium' | 'low'
 * @returns {string}
 */
export function attentionLevelClass(riskLevel) {
  const map = {
    high: 'attention-high',
    medium: 'attention-medium',
    low: 'attention-low',
  }
  return map[riskLevel] || 'attention-low'
}

/**
 * 批量替换文本中的医疗化词汇为友好词汇
 * 遍历 TERM_MAP 中所有映射关系，将文本中出现的医疗词汇替换为对应的友好词汇
 * 注意：按词汇长度从长到短替换，避免短词替换破坏长词（如"筛查"不应先于"读写障碍筛查"替换）
 * @param {string} text - 原始文本
 * @returns {string} - 替换后的友好文本
 *
 * 属性保证：
 * - 幂等性：sanitizeText(sanitizeText(text)) === sanitizeText(text)
 * - 完备性：文本中所有在 TERM_MAP 中的词汇均被替换
 * - 非空性：任意输入的返回值不为 null/undefined
 */
export function sanitizeText(text) {
  let result = String(text == null ? '' : text)
  // 按词汇长度从长到短排序，确保长词优先替换，避免短词破坏长词
  const sortedEntries = Object.entries(TERM_MAP).sort((a, b) => b[0].length - a[0].length)
  for (const [medical, friendly] of sortedEntries) {
    result = result.replaceAll(medical, friendly)
  }
  return result
}
