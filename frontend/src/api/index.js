import { getToken, clearAuth } from '../utils/auth.js';

// 后端地址配置
// - 开发（H5）：走 Vite 代理，留空即可
// - 生产 H5 / App / 小程序：填写真实后端地址
// 优先级：环境变量 > 编译时常量 > 自动推断
export const getBaseUrl = () => {
  // 1. 编译时注入的环境变量（.env 文件或 HBuilderX 自定义基座）
  const configured = (typeof process !== 'undefined' && process.env && process.env.VUE_APP_API_BASE_URL) || '';
  if (configured) return configured;

  // 2. App / 小程序环境：必须填写真实地址
  // #ifdef APP-PLUS || MP-WEIXIN
  return 'https://your-api-domain.com';  // ← 云打包前替换为真实后端地址
  // #endif

  // 3. H5 生产环境：同域部署时留空（Nginx 反向代理 /api/）
  // H5 开发环境：Vite 代理到 localhost:8000
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') {
      // 同域部署：前端和后端在同一域名下，Nginx 代理 /api/
      return '';
    }
  }
  return '';
};

const BASE_URL = getBaseUrl();

/**
 * 统一请求封装
 * @param {object} options
 * @param {boolean} [options.silent] - 为 true 时，错误不弹 toast（用于后台静默请求）
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = getToken();
    const silent = options.silent || false;

    uni.request({
      ...options,
      timeout: options.timeout || 60000,  // 支持自定义超时，默认60秒
      url: options.url.startsWith('http') ? options.url : BASE_URL + options.url,
      header: {
        'Content-Type': 'application/json',
        ...options.header,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      success: (res) => {
        if (res.statusCode === 401) {
          // 401 错误：无论 silent 与否，都清除认证信息并跳转登录
          clearAuth();
          if (!silent) {
            uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          }
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/parent/auth/login' });
          }, silent ? 0 : 1500);
          reject(new Error('未授权'));
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          if (!silent) {
            const errorMsg = res.data?.detail || res.data?.message || '请求失败';
            uni.showToast({ title: errorMsg, icon: 'none' });
          }
          reject({ ...res.data, _statusCode: res.statusCode });
        }
      },
      fail: (err) => {
        if (!silent) {
          uni.showToast({ title: '网络请求失败', icon: 'none' });
        }
        reject(err);
      }
    });
  });
};

// 封装常用 HTTP 方法
export const get = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'GET', data, header, silent, timeout });
};

export const post = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'POST', data, header, silent, timeout });
};

export const put = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'PUT', data, header, silent, timeout });
};

export const del = (url, data = {}, header = {}, silent = false, timeout = null) => {
  return request({ url, method: 'DELETE', data, header, silent, timeout });
};

export default request;
