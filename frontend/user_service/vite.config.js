import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const AUTH_TARGET = process.env.VITE_AUTH_PROXY_TARGET || "http://localhost:8000";
const USER_TARGET = process.env.VITE_USER_PROXY_TARGET || "http://localhost:8001";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/v1/auth/sync": {
        target: USER_TARGET,
        changeOrigin: true,
      },
      "/api/v1/auth/decode": {
        target: USER_TARGET,
        changeOrigin: true,
      },
      "/api/v1/auth": {
        target: AUTH_TARGET,
        changeOrigin: true,
      },
      "/api": {
        target: USER_TARGET,
        changeOrigin: true,
      },
    },
  },
});
