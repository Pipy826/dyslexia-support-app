import { request } from './index.js'

// 获取通知列表
export const getNotifications = (unreadOnly = false) =>
  request('/api/notifications' + (unreadOnly ? '?unread_only=true' : ''), 'GET')

// 获取未读数量
export const getUnreadCount = () =>
  request('/api/notifications/unread-count', 'GET')

// 标记单条已读
export const markAsRead = (id) =>
  request(`/api/notifications/${id}/read`, 'PUT')

// 全部标记已读
export const markAllRead = () =>
  request('/api/notifications/read-all', 'PUT')

// 删除通知
export const deleteNotification = (id) =>
  request(`/api/notifications/${id}`, 'DELETE')

// 注册推送 token（H5 Web Push / 微信小程序 openid）
export const registerPushToken = (platform, token) =>
  request('/api/notifications/token', 'POST', { platform, token })
