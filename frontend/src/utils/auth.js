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
