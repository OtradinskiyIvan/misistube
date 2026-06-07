import { defineConfig } from 'vite'
import React from '@vitejs/plugin-react'

const PLAYER_API_TARGET = process.env.VITE_PLAYER_API_TARGET || 'http://localhost:8001'

export default defineConfig({
  plugins: [React()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: PLAYER_API_TARGET,
        changeOrigin: true,
      },
    },
  },
})
