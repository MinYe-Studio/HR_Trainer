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
  build: {
    // iOS 单机版：禁用代码分割，产出单一 JS 包，便于内联进 index.html
    // （解决 WKWebView 对外部 JS 文件中文编码识别错误的问题）
    rolldownOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
      },
    },
  },
})
