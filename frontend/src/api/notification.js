import { get, post, put, del } from './index.js'

// 获取通知列表
export const getNotifications = (unreadOnly = false) =>
  get('/api/notifications', unreadOnly ? { unread_only: true } : {})

// 获取未读数量（静默请求，不弹 toast）
export const getUnreadCount = () =>
  get('/api/notifications/unread-count', {}, {}, true)

// 标记单条已读
export const markAsRead = (id) =>
  put(`/api/notifications/${id}/read`)

// 全部标记已读
export const markAllRead = () =>
  put('/api/notifications/read-all')

// 删除通知
export const deleteNotification = (id) =>
  del(`/api/notifications/${id}`)

// 注册推送 token（H5 Web Push / 微信小程序 openid）
export const registerPushToken = (platform, token) =>
  post('/api/notifications/token', { platform, token })
