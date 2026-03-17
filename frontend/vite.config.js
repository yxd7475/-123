import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    server: {
  host: '0.0.0.0',
  port: 3000,
  allowedHosts: true,
  proxy: {
    '/api': {
      target: env.VITE_DEV_API_TARGET || 'http://127.0.0.1:5000',
      changeOrigin: true
        }
      }
    }
  }
})