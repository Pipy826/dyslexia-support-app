import { post, get } from './index.js';
import { setToken, setUser } from '../utils/auth.js';

export const register = (data) => post('/api/auth/register', data);

export const login = (data) => post('/api/auth/login', data);

export const loginByCode = (phone, code) =>
  post('/api/auth/login-by-code', { phone, code });

export const getCurrentUser = () => get('/api/auth/me', {}, {}, true);

/**
 * 登录成功后统一处理：保存 token 和用户信息
 * 同时异步刷新用户信息，确保本地缓存与服务端一致
 */
export const handleLoginSuccess = (res) => {
  setToken(res.access_token);
  setUser(res.user);
  // 后台静默刷新用户信息，不 await、不抛异常、不弹 toast
  getCurrentUser()
    .then(freshUser => setUser(freshUser))
    .catch(() => { /* 静默失败，使用登录响应中的用户信息即可 */ });
};

export const sendVerifyCode = (phone) => post('/api/auth/send-code', { phone });

/**
 * 实时校验验证码（不消耗验证码）
 */
export const checkVerifyCode = (phone, code) =>
  get('/api/auth/verify-code', { phone, code });

/**
 * 验证当前登录用户的密码（用于儿童模式退出验证）
 * 使用 silent=true 避免密码错误时弹出全局 toast
 */
export const verifyPassword = (password) =>
  post('/api/auth/verify-password', { password }, {}, true);

/**
 * 微信小程序登录
 * 调用 wx.login() 获取 code，发送给后端换取 JWT
 */
export const wxLogin = () => {
  return new Promise((resolve, reject) => {
    // #ifdef MP-WEIXIN
    wx.login({
      success(res) {
        if (!res.code) {
          reject(new Error('wx.login 失败'))
          return
        }
        post('/api/auth/wx-login', { code: res.code })
          .then(resolve)
          .catch(reject)
      },
      fail(err) {
        reject(err)
      },
    })
    // #endif
    // #ifndef MP-WEIXIN
    reject(new Error('微信登录仅支持微信小程序环境'))
    // #endif
  })
}
