import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api/v1/auth/login": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/api/v1/auth/register": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/api/v1/auth/confirm": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/api/v1/auth/refresh": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/api/v1/auth/me": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
    },
  },
});
