import App from './App.vue'
import { createSSRApp } from 'vue'

export function createApp() {
  const app = createSSRApp(App)

  // 静默处理 uni-app H5 onBackPress 拦截时产生的 navigateBack 错误
  // 这是 uni-app 的已知行为，不影响功能
  // #ifdef H5
  if (typeof window !== 'undefined') {
    window.addEventListener('unhandledrejection', (event) => {
      const msg = event?.reason?.errMsg || ''
      if (msg.includes('navigateBack:fail')) {
        event.preventDefault()
      }
    })
  }
  // #endif

  return { app }
}
