import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      script: {
        defineModel: true,
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        // target: 'http://teligen-ui:8000',

        changeOrigin: true,
        // rewrite: path => path.replace(/^\/api/, '')
      }
    }
  },
  css:{
    preprocessorOptions: {
      scss: {
      additionalData: `@use "src/styles/globalVar.scss" as *;`
      }
    }
    }
})
