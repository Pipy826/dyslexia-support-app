/**
 * 游客会话管理工具
 * 支持无需注册即可试玩游戏，本地存储游戏结果，注册后可迁移数据
 */

const GUEST_KEY = 'guest_session'
const GUEST_TTL = 7 * 24 * 60 * 60 * 1000 // 7天有效期（毫秒）

/**
 * 生成 UUID v4
 * @returns {string}
 */
function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
}

/**
 * 获取或创建游客会话
 * - 有效期内复用现有 guest_id
 * - 过期或不存在时创建新会话
 * @returns {{ guest_id: string, game_results: Array, created_at: number, expires_at: number }}
 */
export function getOrCreateGuestSession() {
  try {
    const stored = uni.getStorageSync(GUEST_KEY)
    if (stored && stored.guest_id && Date.now() < stored.expires_at) {
      return stored
    }
  } catch (e) {
    // 读取失败，创建新会话
  }

  const session = {
    guest_id: generateUUID(),
    game_results: [],
    created_at: Date.now(),
    expires_at: Date.now() + GUEST_TTL,
  }
  try {
    uni.setStorageSync(GUEST_KEY, session)
  } catch (e) {
    console.warn('游客会话保存失败', e)
  }
  return session
}

/**
 * 保存游客游戏结果到本地会话
 * @param {object} result - 游戏结果对象
 */
export function saveGuestGameResult(result) {
  const session = getOrCreateGuestSession()
  session.game_results = session.game_results || []
  session.game_results.push({
    ...result,
    saved_at: Date.now(),
  })
  try {
    uni.setStorageSync(GUEST_KEY, session)
  } catch (e) {
    console.warn('游客游戏结果保存失败', e)
  }
}

/**
 * 获取游客所有游戏结果
 * @returns {Array}
 */
export function getGuestGameResults() {
  const session = getOrCreateGuestSession()
  return session.game_results || []
}

/**
 * 判断当前是否为游客模式（未登录）
 * @returns {boolean}
 */
export function isGuestMode() {
  try {
    const token = uni.getStorageSync('token')
    return !token
  } catch (e) {
    return true
  }
}

/**
 * 清除游客会话（注册/登录后调用）
 */
export function clearGuestSession() {
  try {
    uni.removeStorageSync(GUEST_KEY)
  } catch (e) {
    console.warn('清除游客会话失败', e)
  }
}

/**
 * 获取当前游客 ID（不存在则创建）
 * @returns {string}
 */
export function getGuestId() {
  return getOrCreateGuestSession().guest_id
}
