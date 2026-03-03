import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'
import { viteBundler } from '@vuepress/bundler-vite'
import navbar from './navbar'
import sidebar from './sidebar'
export default defineUserConfig({
  base: '/docs',
  title: 'HZ-MANAGE',
  bundler: viteBundler(),
  theme: defaultTheme({
    sidebarDepth: 1,
    logo: '/logos--godot-icon.svg',
    // ...navbar,
    ...sidebar,



  }),
})