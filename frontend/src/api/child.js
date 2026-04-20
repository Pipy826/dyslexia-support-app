import { get, post, put, del } from './index.js';
import { getToken } from '../utils/auth.js';
import { getBaseUrl } from './index.js';

export const getChildren = () => get('/api/children/');

export const getChild = (id) => get(`/api/children/${id}`);

export const createChild = (data) => post('/api/children/', data);

export const updateChild = (id, data) => put(`/api/children/${id}`, data);

export const deleteChild = (id) => del(`/api/children/${id}`);

/**
 * 上传头像，返回 { url, filename }
 */
export const uploadAvatar = (filePath) => {
  return new Promise((resolve, reject) => {
    const token = getToken();
    const baseUrl = getBaseUrl();
    uni.uploadFile({
      url: baseUrl + '/api/upload/avatar',
      filePath,
      name: 'file',
      header: token ? { Authorization: `Bearer ${token}` } : {},
      success: (res) => {
        try {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            uni.showToast({ title: data?.detail || '上传失败', icon: 'none' });
            reject(data);
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => {
        uni.showToast({ title: '上传失败', icon: 'none' });
        reject(err);
      }
    });
  });
};

export const getAvatarUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return getBaseUrl() + path;
};
