import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    hmr: {
      clientPort: 80
    },
    proxy: {
      '/api': { target: 'http://backend:8000', changeOrigin: true },
      '/admin': { target: 'http://backend:8000', changeOrigin: true },
      '/static': { target: 'http://backend:8000', changeOrigin: true },
      '/media': { target: 'http://backend:8000', changeOrigin: true },
    }
  }
})