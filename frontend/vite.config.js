import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  // Base path: '/shopping-bot/' pentru GitHub Pages, '/' pentru dev/custom domain
  base: process.env.VITE_BASE || '/',

  // În development: proxy cererile /api la API-ul local
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    outDir: 'dist',
  },
})
