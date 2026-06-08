import { defineConfig } from 'vite'
import React from '@vitejs/plugin-react'

const API_HOST = process.env.VITE_API_HOST || 'host.docker.internal'
const PLAYER_API_TARGET = process.env.VITE_PLAYER_API_TARGET || `http://${API_HOST}:8004`
const USER_API_TARGET = process.env.VITE_USER_API_TARGET || `http://${API_HOST}:8000`

export default defineConfig({
  plugins: [React()],
  server: {
    port: 5173,
    proxy: {
      '/api/v1/users': {
        target: USER_API_TARGET,
        changeOrigin: true,
      },
      '/api': {
        target: PLAYER_API_TARGET,
        changeOrigin: true,
      },
    },
  },
})
