// Token 存储 key
export const TOKEN_KEY = 'auth_token';
export const USER_KEY = 'user_info';
export const CHILD_KEY = 'current_child';

// Token 操作
export const setToken = (token) => {
  uni.setStorageSync(TOKEN_KEY, token);
};

export const getToken = () => {
  return uni.getStorageSync(TOKEN_KEY) || '';
};

export const removeToken = () => {
  uni.removeStorageSync(TOKEN_KEY);
};

/**
 * 检查 token 是否已过期（解析 JWT payload 中的 exp 字段）
 * 提前 60 秒判定为过期，避免边界情况
 * @returns {boolean} true = 已过期或无效
 */
export const isTokenExpired = () => {
  const token = getToken();
  if (!token) return true;
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    // Base64url 解码 payload
    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
    if (!payload.exp) return false; // 没有 exp 字段，视为永不过期
    // 提前 60 秒判定过期
    return Date.now() / 1000 > payload.exp - 60;
  } catch (e) {
    return true; // 解析失败视为过期
  }
};

// 用户信息操作
export const setUser = (user) => {
  if (user) {
    uni.setStorageSync(USER_KEY, JSON.stringify(user));
  } else {
    uni.removeStorageSync(USER_KEY);
  }
};

export const getUser = () => {
  try {
    const user = uni.getStorageSync(USER_KEY);
    if (!user) return null;
    const parsed = JSON.parse(user);
    return (parsed && Object.keys(parsed).length > 0) ? parsed : null;
  } catch (e) {
    uni.removeStorageSync(USER_KEY);
    return null;
  }
};

export const removeUser = () => {
  uni.removeStorageSync(USER_KEY);
};

// 当前选中儿童
export const setCurrentChild = (child) => {
  if (child) {
    uni.setStorageSync(CHILD_KEY, JSON.stringify(child));
  } else {
    uni.removeStorageSync(CHILD_KEY);
  }
};

export const getCurrentChild = () => {
  try {
    const child = uni.getStorageSync(CHILD_KEY);
    if (!child) return null;
    const parsed = JSON.parse(child);
    return (parsed && Object.keys(parsed).length > 0) ? parsed : null;
  } catch (e) {
    uni.removeStorageSync(CHILD_KEY);
    return null;
  }
};

export const removeCurrentChild = () => {
  uni.removeStorageSync(CHILD_KEY);
};

// 清除所有认证信息
export const clearAuth = () => {
  removeToken();
  removeUser();
  removeCurrentChild();
};
