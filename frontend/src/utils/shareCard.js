/**
 * 分享卡片生成工具
 * 生成科普化的游戏结果分享内容，用于朋友圈传播
 */

/**
 * 生成8位字母数字混合分享码
 * 碰撞概率 < 1/百万（36^8 ≈ 2.8万亿种组合）
 * @returns {string}
 */
export function generateShareCode() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  let code = ''
  for (let i = 0; i < 8; i++) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

/**
 * 生成分享卡片配置
 * @param {object} gameResult - 游戏结果
 * @param {string} gameResult.gameType - 游戏类型
 * @param {number} gameResult.score - 分数
 * @param {string} gameResult.abilityLabel - 能力标签
 * @param {string} gameResult.abilityEmoji - 能力emoji
 * @param {string} gameResult.childName - 孩子名字（可选）
 * @returns {{ title, desc, path, imageUrl }}
 */
export function generateShareCard(gameResult) {
  const { gameType, score, abilityLabel, abilityEmoji, childName } = gameResult
  const shareCode = generateShareCode()
  const gameName = getGameName(gameType)
  const namePrefix = childName ? `${childName}的` : '我家孩子的'

  const title = `${abilityEmoji || '🌟'} ${namePrefix}${gameName}能力：${abilityLabel || '小小探险家'}！`
  const desc = `得了${score}分！快来测测你家孩子的读写能力～悦读灯塔，趣味游戏发现成长潜力`

  return {
    title,
    desc,
    path: `/pages/guest/play/index?ref=${shareCode}`,
    shareCode,
    imageUrl: '', // 可扩展为动态生成的卡片图片URL
  }
}

/**
 * 调用 UniApp 分享 API
 * @param {object} shareConfig - 分享配置（来自 generateShareCard）
 */
export function triggerShare(shareConfig) {
  const { title, desc, path } = shareConfig

  // #ifdef MP-WEIXIN
  uni.showShareMenu({
    withShareTicket: true,
    menus: ['shareAppMessage', 'shareTimeline'],
  })
  // 微信小程序通过 onShareAppMessage 生命周期钩子处理分享
  // #endif

  // #ifdef H5
  if (typeof navigator !== 'undefined' && navigator.share) {
    navigator.share({
      title,
      text: desc,
      url: typeof window !== 'undefined' ? window.location.origin + path : path,
    }).catch(() => {
      // 用户取消分享，静默处理
    })
  } else {
    // 降级：复制链接
    const url = typeof window !== 'undefined' ? window.location.origin + path : path
    if (typeof uni !== 'undefined') {
      uni.setClipboardData({
        data: `${title}\n${desc}\n${url}`,
        success: () => {
          uni.showToast({ title: '分享内容已复制！', icon: 'none' })
        },
      })
    }
  }
  // #endif
}

/**
 * 获取游戏类型中文名
 * @param {string} gameType
 * @returns {string}
 */
function getGameName(gameType) {
  const names = {
    visual: '视觉辨识',
    spelling: '拼字识别',
    comprehension: '文字理解',
    working_memory: '工作记忆',
    rapid_naming: '快速命名',
    motor_coordination: '精细动作',
  }
  return names[gameType] || '读写能力'
}
