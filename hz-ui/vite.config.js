import { fileURLToPath, URL } from "node:url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import Components from "unplugin-vue-components/vite";
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    Components({
      resolvers: [IconsResolver({ prefix: "icon" })],
    }),
    Icons(),
    vue({
      script: {
        defineModel: true,
      },
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        // target: 'http://teligen-ui:8000',

        changeOrigin: true,
        // rewrite: path => path.replace(/^\/api/, '')
      },
      "/ws": {
        target: "ws://127.0.0.1:8001"
      }
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/globalVar.scss" as *;`,
      },
    },
  },
});
