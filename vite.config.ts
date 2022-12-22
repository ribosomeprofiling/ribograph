import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  root: "./ribograph/browser/",
  plugins: [vue()],
  server: {
    watch: {
      usePolling: true
    }
  },
  build: {
    manifest: true,
    rollupOptions: {
      // overwrite default .html entry
      input: './ribograph/browser/src/main.ts'
    },
    outDir: 'static/browser/vuefiles',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
