import { post, get } from './index.js';
import { setToken, setUser } from '../utils/auth.js';

export const register = (data) => post('/api/auth/register', data);

export const login = (data) => post('/api/auth/login', data);

export const loginByCode = (phone, code) =>
  post('/api/auth/login-by-code', { phone, code });

export const getCurrentUser = () => get('/api/auth/me');

/**
 * 登录成功后统一处理：保存 token 和用户信息
 * 同时异步刷新用户信息，确保本地缓存与服务端一致
 */
export const handleLoginSuccess = async (res) => {
  setToken(res.access_token);
  setUser(res.user);
  // 异步刷新用户信息（不阻塞主流程）
  try {
    const freshUser = await getCurrentUser();
    setUser(freshUser);
  } catch (e) {
    // 静默失败，使用 token 响应中的用户信息
  }
};

export const sendVerifyCode = (phone) => post('/api/auth/send-code', { phone });

/**
 * 实时校验验证码（不消耗验证码）
 */
export const checkVerifyCode = (phone, code) =>
  get('/api/auth/verify-code', { phone, code });
