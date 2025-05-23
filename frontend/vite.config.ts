import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: '/', // NOTE: Vue RouterのcreateWebHistoryで用いられるベースパスはここで設定する。(例: /app/ など)
  server: {
    host: true,
    hmr: {
      host: 'localhost',
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // NOTE: Dockerコンテナ内部のホスト名とポート番号を設定する
        changeOrigin: true,
        //rewrite: (path) => path.replace(/^\/api/, '/api'),
      },
    },
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
    chunkSizeWarningLimit: 1024 * 1024 * 10, // 10MiB
  },
  resolve: {
    alias: {
      // エイリアス'@'はjsやvueのimportでのみ有効。htmlでは`/src/...`と書くこと。
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
