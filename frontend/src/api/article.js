import { get, post, put, del } from './index.js';

/**
 * 获取科普文章/视频列表
 * @param {object} params - { content_type, tag, featured_only, page, page_size }
 */
export const getArticles = (params = {}) => get('/api/articles', params);

/**
 * 获取文章详情（同时增加浏览量）
 */
export const getArticle = (id) => get(`/api/articles/${id}`);

/**
 * 发布文章（需登录）
 */
export const createArticle = (data) => post('/api/articles', data);

/**
 * 更新文章（需登录）
 */
export const updateArticle = (id, data) => put(`/api/articles/${id}`, data);

/**
 * 删除文章（需登录）
 */
export const deleteArticle = (id) => del(`/api/articles/${id}`);
