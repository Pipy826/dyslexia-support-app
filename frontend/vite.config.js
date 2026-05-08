import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { resolve } from 'path'

export default defineConfig({
  plugins: [uni()],
  publicDir: resolve(__dirname, 'public'),
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    }
  },
  optimizeDeps: {
    // 让 Vite 预构建时统一使用同一个 vue-router 实例
    include: ['vue-router'],
  },
  // H5开发模式代理，解决跨域问题
  server: {
    port: 5173,
    host: '0.0.0.0',           // 监听所有网卡，手机扫码可访问
    strictPort: false,
    headers: {
      'Cache-Control': 'no-store',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        timeout: 120000,
        proxyTimeout: 120000,
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  // 确保输出文件使用 UTF-8 编码
  css: {
    preprocessorOptions: {
      scss: {
        api: 'modern-compiler',
        additionalData: '',
        charset: false,
        includePaths: [resolve(__dirname, 'node_modules'), resolve(__dirname, 'src')]
      }
    }
  },
  // 确保构建时正确处理中文
  build: {
    charset: 'utf8',
    rollupOptions: {
      output: {
        // 确保输出文件名正确处理中文
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) {
            return `images/[name]-[hash].${ext}`
          }
          if (/\.(css|scss|sass|less)$/.test(assetInfo.name)) {
            return `css/[name]-[hash].${ext}`
          }
          return `[name]-[hash].${ext}`
        }
      }
    }
  }
})