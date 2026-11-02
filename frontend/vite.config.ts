import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // 面试可讲：开发期用 proxy 把 /api 转发到后端，
    // 这样前端代码里写相对路径就行，不需要处理跨域。
    proxy: {
      '/api': { target: 'http://127.0.0.1:8011', changeOrigin: true },
      '/media': { target: 'http://127.0.0.1:8011', changeOrigin: true },
    },
  },
})
