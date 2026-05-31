import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@shared': path.resolve(__dirname, '../shared')
    }
  },
  css: {
    preprocessorOptions: {
      css: {
        additionalData: `@import "@shared/style_sample.css";`
      }
    }
  }
});