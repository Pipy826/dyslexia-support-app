import { getToken, clearAuth } from '../utils/auth.js';

// H5开发模式走vite代理（空字符串），生产环境改为实际后端地址
// 当用局域网IP访问时，代理不生效，需要直接指向后端
const getBaseUrl = () => {
  const configured = import.meta.env.VITE_API_BASE_URL || '';
  if (configured) return configured;
  // 浏览器环境：如果当前不是localhost，直接用同主机的8000端口
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') {
      return `http://${host}:8000`;
    }
  }
  return '';
};

const BASE_URL = getBaseUrl();

/**
 * 统一请求封装
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = getToken();

    uni.request({
      ...options,
      url: options.url.startsWith('http') ? options.url : BASE_URL + options.url,
      header: {
        'Content-Type': 'application/json',
        ...options.header,
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      success: (res) => {
        if (res.statusCode === 401) {
          clearAuth();
          uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' });
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/parent/auth/login' });
          }, 1500);
          reject(new Error('未授权'));
        } else if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          const errorMsg = res.data?.detail || res.data?.message || '请求失败';
          uni.showToast({ title: errorMsg, icon: 'none' });
          reject({ ...res.data, _statusCode: res.statusCode });
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络请求失败', icon: 'none' });
        reject(err);
      }
    });
  });
};

// 封装常用 HTTP 方法
export const get = (url, data = {}, header = {}) => {
  return request({ url, method: 'GET', data, header });
};

export const post = (url, data = {}, header = {}) => {
  return request({ url, method: 'POST', data, header });
};

export const put = (url, data = {}, header = {}) => {
  return request({ url, method: 'PUT', data, header });
};

export const del = (url, data = {}, header = {}) => {
  return request({ url, method: 'DELETE', data, header });
};

export default request;
