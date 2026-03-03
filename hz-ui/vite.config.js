/**
 * Vite 配置文件
 *
 * 环境变量配置说明：
 * - VITE_API_URL: 后端 API 地址（可选，用于 Vite 代理）
 *   - 本地开发：默认使用 http://127.0.0.1:8000
 *   - Docker 环境：在 docker-compose.yml 中设置，如 http://backend:8000
 *
 * - VITE_BACKEND_URL: 后端外部可访问地址（可选，用于浏览器直接访问后端）
 *   - 生产环境需要配置，如 http://localhost:8000 或 http://your-domain.com
 *   - 未配置时使用当前域名（依赖反向代理）
 *
 * 使用示例：
 * 1. 本地开发（默认）：npm run dev
 * 2. Docker 环境：
 *    environment:
 *      - VITE_API_URL=http://backend:8000
 *      - VITE_BACKEND_URL=http://localhost:8000
 * 3. 自定义环境文件：创建 .env.local 或 .env.docker
 */

import { fileURLToPath, URL } from "node:url";
import { loadEnv } from "vite";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import Icons from "unplugin-icons/vite";
import IconsResolver from "unplugin-icons/resolver";
import Components from "unplugin-vue-components/vite";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量，支持通过 VITE_API_URL 动态配置后端地址
  // 本地开发：使用默认的 http://127.0.0.1:8000
  // Docker 环境：通过环境变量 VITE_API_URL 指定，如 http://backend:8000
  const env = loadEnv(mode, process.cwd(), "");
  const target = env.VITE_API_URL || "http://127.0.0.1:8000";

  return {
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
      // API 请求代理
      "/api": {
        target,
        changeOrigin: true,
      },
      // drf-spectacular Swagger UI 静态文件代理
      "/static/drf_spectacular_sidecar": {
        target,
        changeOrigin: true,
      },
      // VuePress 文档代理（同一容器内的 5173 端口）
      "/docs": {
        target: "http://localhost:5173",
        changeOrigin: true,
        ws: true,
      },
      // WebSocket 连接代理（通用）
      "/ws": {
        // 自动将 http:// 协议转换为 ws://
        target: target.replace("http://", "ws://"),
      },
      // JobFlow WebSocket 连接代理
      "/jobflow/ws": {
        target: target.replace("http://", "ws://"),
      },
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/globalVar.scss" as *;`,
      },
    },
  },
  };
});
