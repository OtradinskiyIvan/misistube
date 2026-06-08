import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const INTERACTION_TARGET = process.env.VITE_INTERACTION_PROXY_TARGET || "http://localhost:8002";

export default defineConfig({
  plugins: [react()],
  base: '/interaction/',
  server: {
    port: 5175,
    proxy: {
      "/api": {
        target: INTERACTION_TARGET,
        changeOrigin: true,
      },
    },
  },
});
