import { getToken, clearAuth } from '../utils/auth.js';

const BASE_URL = 'http://localhost:8000';

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
