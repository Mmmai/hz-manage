// vite.config.js
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/node_modules/.store/vite@5.4.21/node_modules/vite/dist/node/index.js";
import vue from "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/node_modules/.store/@vitejs+plugin-vue@4.6.2/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import Icons from "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/node_modules/.store/unplugin-icons@0.22.0/node_modules/unplugin-icons/dist/vite.js";
import IconsResolver from "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/node_modules/.store/unplugin-icons@0.22.0/node_modules/unplugin-icons/dist/resolver.js";
import Components from "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/node_modules/.store/unplugin-vue-components@0.28.0/node_modules/unplugin-vue-components/dist/vite.js";
var __vite_injected_original_import_meta_url = "file:///mnt/c/Users/78712/Desktop/teligen-ui/vue/hz-ui/vite.config.js";
var vite_config_default = defineConfig({
  plugins: [
    Components({
      resolvers: [IconsResolver({ prefix: "icon" })]
    }),
    Icons(),
    vue({
      script: {
        defineModel: true
      }
    })
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", __vite_injected_original_import_meta_url))
    }
  },
  server: {
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        // target: 'http://teligen-ui:8000',
        changeOrigin: true
        // rewrite: path => path.replace(/^\/api/, '')
      },
      "/ws": {
        target: "ws://127.0.0.1:8000"
      },
      "/jobflow/ws": {
        target: "ws://127.0.0.1:8000"
      }
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/globalVar.scss" as *;`
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCIvbW50L2MvVXNlcnMvNzg3MTIvRGVza3RvcC90ZWxpZ2VuLXVpL3Z1ZS9oei11aVwiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9maWxlbmFtZSA9IFwiL21udC9jL1VzZXJzLzc4NzEyL0Rlc2t0b3AvdGVsaWdlbi11aS92dWUvaHotdWkvdml0ZS5jb25maWcuanNcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfaW1wb3J0X21ldGFfdXJsID0gXCJmaWxlOi8vL21udC9jL1VzZXJzLzc4NzEyL0Rlc2t0b3AvdGVsaWdlbi11aS92dWUvaHotdWkvdml0ZS5jb25maWcuanNcIjtpbXBvcnQgeyBmaWxlVVJMVG9QYXRoLCBVUkwgfSBmcm9tIFwibm9kZTp1cmxcIjtcclxuXHJcbmltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gXCJ2aXRlXCI7XHJcbmltcG9ydCB2dWUgZnJvbSBcIkB2aXRlanMvcGx1Z2luLXZ1ZVwiO1xyXG5pbXBvcnQgSWNvbnMgZnJvbSBcInVucGx1Z2luLWljb25zL3ZpdGVcIjtcclxuaW1wb3J0IEljb25zUmVzb2x2ZXIgZnJvbSBcInVucGx1Z2luLWljb25zL3Jlc29sdmVyXCI7XHJcbmltcG9ydCBDb21wb25lbnRzIGZyb20gXCJ1bnBsdWdpbi12dWUtY29tcG9uZW50cy92aXRlXCI7XHJcbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XHJcbiAgcGx1Z2luczogW1xyXG4gICAgQ29tcG9uZW50cyh7XHJcbiAgICAgIHJlc29sdmVyczogW0ljb25zUmVzb2x2ZXIoeyBwcmVmaXg6IFwiaWNvblwiIH0pXSxcclxuICAgIH0pLFxyXG4gICAgSWNvbnMoKSxcclxuICAgIHZ1ZSh7XHJcbiAgICAgIHNjcmlwdDoge1xyXG4gICAgICAgIGRlZmluZU1vZGVsOiB0cnVlLFxyXG4gICAgICB9LFxyXG4gICAgfSksXHJcbiAgXSxcclxuICByZXNvbHZlOiB7XHJcbiAgICBhbGlhczoge1xyXG4gICAgICBcIkBcIjogZmlsZVVSTFRvUGF0aChuZXcgVVJMKFwiLi9zcmNcIiwgaW1wb3J0Lm1ldGEudXJsKSksXHJcbiAgICB9LFxyXG4gIH0sXHJcbiAgc2VydmVyOiB7XHJcbiAgICBwcm94eToge1xyXG4gICAgICBcIi9hcGlcIjoge1xyXG4gICAgICAgIHRhcmdldDogXCJodHRwOi8vMTI3LjAuMC4xOjgwMDBcIixcclxuICAgICAgICAvLyB0YXJnZXQ6ICdodHRwOi8vdGVsaWdlbi11aTo4MDAwJyxcclxuXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxyXG4gICAgICAgIC8vIHJld3JpdGU6IHBhdGggPT4gcGF0aC5yZXBsYWNlKC9eXFwvYXBpLywgJycpXHJcbiAgICAgIH0sXHJcbiAgICAgIFwiL3dzXCI6IHtcclxuICAgICAgICB0YXJnZXQ6IFwid3M6Ly8xMjcuMC4wLjE6ODAwMFwiLFxyXG4gICAgICB9LFxyXG4gICAgICBcIi9qb2JmbG93L3dzXCI6IHtcclxuICAgICAgICB0YXJnZXQ6IFwid3M6Ly8xMjcuMC4wLjE6ODAwMFwiLFxyXG4gICAgICB9LFxyXG4gICAgfSxcclxuICB9LFxyXG4gIGNzczoge1xyXG4gICAgcHJlcHJvY2Vzc29yT3B0aW9uczoge1xyXG4gICAgICBzY3NzOiB7XHJcbiAgICAgICAgYWRkaXRpb25hbERhdGE6IGBAdXNlIFwiQC9zdHlsZXMvZ2xvYmFsVmFyLnNjc3NcIiBhcyAqO2AsXHJcbiAgICAgIH0sXHJcbiAgICB9LFxyXG4gIH0sXHJcbn0pO1xyXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQStULFNBQVMsZUFBZSxXQUFXO0FBRWxXLFNBQVMsb0JBQW9CO0FBQzdCLE9BQU8sU0FBUztBQUNoQixPQUFPLFdBQVc7QUFDbEIsT0FBTyxtQkFBbUI7QUFDMUIsT0FBTyxnQkFBZ0I7QUFOK0ssSUFBTSwyQ0FBMkM7QUFRdlAsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUztBQUFBLElBQ1AsV0FBVztBQUFBLE1BQ1QsV0FBVyxDQUFDLGNBQWMsRUFBRSxRQUFRLE9BQU8sQ0FBQyxDQUFDO0FBQUEsSUFDL0MsQ0FBQztBQUFBLElBQ0QsTUFBTTtBQUFBLElBQ04sSUFBSTtBQUFBLE1BQ0YsUUFBUTtBQUFBLFFBQ04sYUFBYTtBQUFBLE1BQ2Y7QUFBQSxJQUNGLENBQUM7QUFBQSxFQUNIO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCxLQUFLLGNBQWMsSUFBSSxJQUFJLFNBQVMsd0NBQWUsQ0FBQztBQUFBLElBQ3REO0FBQUEsRUFDRjtBQUFBLEVBQ0EsUUFBUTtBQUFBLElBQ04sT0FBTztBQUFBLE1BQ0wsUUFBUTtBQUFBLFFBQ04sUUFBUTtBQUFBO0FBQUEsUUFHUixjQUFjO0FBQUE7QUFBQSxNQUVoQjtBQUFBLE1BQ0EsT0FBTztBQUFBLFFBQ0wsUUFBUTtBQUFBLE1BQ1Y7QUFBQSxNQUNBLGVBQWU7QUFBQSxRQUNiLFFBQVE7QUFBQSxNQUNWO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLEtBQUs7QUFBQSxJQUNILHFCQUFxQjtBQUFBLE1BQ25CLE1BQU07QUFBQSxRQUNKLGdCQUFnQjtBQUFBLE1BQ2xCO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
