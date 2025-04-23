export const redirects = JSON.parse("{}")

export const routes = Object.fromEntries([
  ["/", { loader: () => import(/* webpackChunkName: "index.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/index.html.js"), meta: {"title":"Home"} }],
  ["/manage/install.html", { loader: () => import(/* webpackChunkName: "manage_install.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/manage/install.html.js"), meta: {"title":"安装"} }],
  ["/manage/", { loader: () => import(/* webpackChunkName: "manage_index.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/manage/index.html.js"), meta: {"title":"介绍"} }],
  ["/manage/version.html", { loader: () => import(/* webpackChunkName: "manage_version.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/manage/version.html.js"), meta: {"title":""} }],
  ["/manage/basic/menu.html", { loader: () => import(/* webpackChunkName: "manage_basic_menu.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/manage/basic/menu.html.js"), meta: {"title":"菜单管理"} }],
  ["/manage/basic/rbac.html", { loader: () => import(/* webpackChunkName: "manage_basic_rbac.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/manage/basic/rbac.html.js"), meta: {"title":"用户管理"} }],
  ["/404.html", { loader: () => import(/* webpackChunkName: "404.html" */"C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/404.html.js"), meta: {"title":""} }],
]);

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updateRoutes) {
    __VUE_HMR_RUNTIME__.updateRoutes(routes)
  }
  if (__VUE_HMR_RUNTIME__.updateRedirects) {
    __VUE_HMR_RUNTIME__.updateRedirects(redirects)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ routes, redirects }) => {
    __VUE_HMR_RUNTIME__.updateRoutes(routes)
    __VUE_HMR_RUNTIME__.updateRedirects(redirects)
  })
}
