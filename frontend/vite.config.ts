import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: true,
    hmr: {
      host: 'localhost'
    }
  },
  plugins: [
    vue({
      template: {
        transformAssetUrls: {
          base: null,
          includeAbsolute: false,
        },
      },
    }),
    vueDevTools(),
  ],
  build: {
    outDir: fileURLToPath(new URL('../public', import.meta.url)),
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      // エイリアス'@'はjsやvueのimportでのみ有効。htmlでは`/src/...`と書くこと。
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
