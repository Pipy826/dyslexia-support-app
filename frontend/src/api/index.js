import { getToken, clearAuth, isTokenExpired } from '../utils/auth.js';

// 后端地址配置
// - 开发（H5/Vite 5173端口）：走 Vite 代理，留空即可
// - 生产 H5：同域部署时留空（Nginx 反向代理 /api/）
// - App / 小程序：通过环境变量 VUE_APP_API_BASE_URL 注入真实地址
//
// 配置方式（推荐）：
//   在 HBuilderX 项目根目录创建 .env.production 文件：
//   VUE_APP_API_BASE_URL=https://your-domain.com
//
// 注意：不要在代码中硬编码真实服务器 IP，避免泄露服务器信息

export const getBaseUrl = () => {
  // 1. 编译时注入的环境变量（优先级最高）
  const configured =
    (typeof process !== 'undefined' && process.env && process.env.VUE_APP_API_BASE_URL) || '';
  if (configured) return configured;

  // 2. H5 环境（浏览器）
  // #ifndef APP-PLUS || MP-WEIXIN
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    const port = window.location.port;
    if (host === 'localhost' || host === '127.0.0.1') {
      // 本地开发环境：所有端口都直连后端（避免 Vite 代理不稳定的问题）
      return 'http://localhost:8000';
    }
    // 生产环境：同域部署，留空（Nginx 反向代理 /api/）
    return '';
  }
  // #endif

  // 3. App / 小程序环境：必须通过环境变量配置，此处返回空字符串作为安全兜底
  // #ifdef APP-PLUS || MP-WEIXIN
  // 如果未配置环境变量，请在上方第1步设置 VUE_APP_API_BASE_URL
  console.warn('[API] 未配置 VUE_APP_API_BASE_URL，请在 .env.production 中设置后端地址');
  return '';
  // #endif
};


/**
 * 统一请求封装
 * @param {object} options
 * @param {boolean} [options.silent] - 为 true 时，错误不弹 toast（用于后台静默请求）
 * @param {number} [options.timeout] - 超时时间（毫秒），默认 60000
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = getToken();
    const silent = options.silent || false;
    // 每次请求时动态获取 BASE_URL，避免 HBuilderX 热重载时缓存旧值
    const baseUrl = getBaseUrl();

    // 请求前检查 token 是否过期，避免发出注定失败的请求
    if (token && isTokenExpired()) {
      clearAuth();
      uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
      setTimeout(() => {
        uni.reLaunch({ url: '/pages/parent/auth/login' });
      }, 1500);
      reject(new Error('未授权'));
      return;
    }

    uni.request({
      ...options,
      timeout: options.timeout || 60000,
      url: options.url.startsWith('http') ? options.url : baseUrl + options.url,
      header: {
        'Content-Type': 'application/json',
        ...options.header,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      success: (res) => {
        if (res.statusCode === 401) {
          // 401：清除认证信息并跳转登录
          clearAuth();
          if (!silent) {
            uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          }
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/parent/auth/login' });
          }, silent ? 0 : 1500);
          reject(new Error('未授权'));
        } else if (res.statusCode === 429) {
          // 429：速率限制
          if (!silent) {
            const msg = res.data?.detail || '请求过于频繁，请稍后再试';
            uni.showToast({ title: String(msg), icon: 'none' });
          }
          reject({ ...res.data, _statusCode: res.statusCode });
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          if (!silent) {
            // detail 可能是字符串或数组（Pydantic 验证错误）
            let errorMsg = res.data?.detail || res.data?.message || '请求失败';
            if (Array.isArray(errorMsg)) {
              errorMsg = errorMsg.map(e => e.msg).join('；') || '请求失败';
            }
            uni.showToast({ title: String(errorMsg), icon: 'none' });
          }
          reject({ ...res.data, _statusCode: res.statusCode });
        }
      },
      fail: (err) => {
        // HBuilderX H5 模式下，CORS 预检失败或 4xx 响应有时会走 fail 回调
        const errMsg = err?.errMsg || '';
        const isCorsOrNetworkFail = errMsg.includes('ERR_FAILED') || errMsg.includes('request:fail');

        if (isCorsOrNetworkFail) {
          // 没有 token 时直接跳登录
          if (!getToken()) {
            uni.reLaunch({ url: '/pages/parent/auth/login' });
            reject(new Error('未授权'));
            return;
          }
          // 有 token 但 CORS/网络失败：静默处理，不弹 toast
          // 这通常是后端刚启动或 HBuilderX 内置浏览器的 CORS 处理差异
          reject(err);
          return;
        }

        if (!silent) {
          uni.showToast({ title: '网络请求失败，请检查后端是否启动', icon: 'none', duration: 3000 });
        }
        reject(err);
      }
    });
  });
};

// 封装常用 HTTP 方法
export const get = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'GET', data, header, silent, ...(timeout ? { timeout } : {}) });
};

export const post = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'POST', data, header, silent, ...(timeout ? { timeout } : {}) });
};

export const put = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'PUT', data, header, silent, ...(timeout ? { timeout } : {}) });
};

export const del = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'DELETE', data, header, silent, ...(timeout ? { timeout } : {}) });
};

export default request;
