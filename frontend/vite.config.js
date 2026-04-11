import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  // În development: proxy cererile /api la API-ul local
  // În producție: VITE_API_URL e setat la URL-ul Fly.io (ex: https://shopping-bot-app.fly.dev)
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
