export const themeData = JSON.parse("{\"sidebarDepth\":1,\"logo\":\"/logos--godot-icon.svg\",\"sidebar\":{\"/manage/\":[{\"text\":\"介绍\",\"link\":\"/manage/\"},{\"text\":\"安装部署\",\"link\":\"/manage/install.md\"},{\"text\":\"基础功能\",\"collapsible\":true,\"children\":[{\"text\":\"用户管理\",\"link\":\"/manage/basic/rbac.md\"},{\"text\":\"菜单管理\",\"link\":\"/manage/basic/menu.md\"}]}]},\"locales\":{\"/\":{\"selectLanguageName\":\"English\"}},\"colorMode\":\"auto\",\"colorModeSwitch\":true,\"navbar\":[],\"repo\":null,\"selectLanguageText\":\"Languages\",\"selectLanguageAriaLabel\":\"Select language\",\"editLink\":true,\"editLinkText\":\"Edit this page\",\"lastUpdated\":true,\"lastUpdatedText\":\"Last Updated\",\"contributors\":true,\"contributorsText\":\"Contributors\",\"notFound\":[\"There's nothing here.\",\"How did we get here?\",\"That's a Four-Oh-Four.\",\"Looks like we've got some broken links.\"],\"backToHome\":\"Take me home\",\"openInNewWindow\":\"open in new window\",\"toggleColorMode\":\"toggle color mode\",\"toggleSidebar\":\"toggle sidebar\"}")

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updateThemeData) {
    __VUE_HMR_RUNTIME__.updateThemeData(themeData)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ themeData }) => {
    __VUE_HMR_RUNTIME__.updateThemeData(themeData)
  })
}
