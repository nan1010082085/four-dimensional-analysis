import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: '/stock-analysis/',
  plugins: [vue()],
  server: {
    proxy: {
      '/stock-analysis/api': {
        target: 'http://localhost:5080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/stock-analysis/, ''),
      },
    },
  },
})
