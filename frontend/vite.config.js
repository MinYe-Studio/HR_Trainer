import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: true,      // 同时监听 IPv4/IPv6，避免 localhost 解析差异
    port: 5174,
    strictPort: true,
    proxy: {
      // 开发期代理到 FastAPI 后端
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
