//import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus, { ariaProps } from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import api from './api/index'
import store from './store'
import './icons/iconfont.js'
import iconfontSvg from "./icons/iconFont.vue";
import commonFunc from './utils/common'
import 'element-plus/theme-chalk/dark/css-vars.css'
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import myCommand from "./utils/myCommand"
import VueCountdown from '@chenfengyuan/vue-countdown';
// 导入自定义样式
import "@/styles/comm.scss";
// 导入ant
import Antd from 'ant-design-vue';
// import 'ant-design-vue/dist/reset.css';

//main.js
import '@imengyu/vue3-context-menu/lib/vue3-context-menu.css'

// 设置中文
import locale from "element-plus/es/locale/lang/zh-cn";
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate)
const app = createApp(App)
app.component("iconfont-svg", iconfontSvg)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.config.globalProperties.$api = api
app.config.globalProperties.$commonFunc = commonFunc
app.use(store)
app.use(pinia)
app.use(router)
app.use(Antd)
// 自定义指令
myCommand(app)
app.component(VueCountdown.name, VueCountdown);
app.use(ElementPlus, { locale })
app.mount('#app')
