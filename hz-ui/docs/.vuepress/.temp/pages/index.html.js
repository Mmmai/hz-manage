import comp from "C:/Users/78712/Desktop/teligen-ui/vue/hz-ui/docs/.vuepress/.temp/pages/index.html.vue"
const data = JSON.parse("{\"path\":\"/\",\"title\":\"Home\",\"lang\":\"en-US\",\"frontmatter\":{\"home\":true,\"title\":\"Home\",\"heroImage\":\"/hero.png\",\"heroText\":\"HZ-MANAGE\",\"tagline\":\"中心自研运维平台\",\"actions\":[{\"text\":\"开始使用\",\"link\":\"/manage/\",\"type\":\"primary\"}],\"features\":null,\"footer\":\"工程售后服务中心-技术管理室 | Copyright © 2024-present\"},\"headers\":[],\"git\":{\"updatedTime\":1736824175000,\"contributors\":[{\"name\":\"maish\",\"username\":\"maish\",\"email\":\"787121533@qq.com\",\"commits\":2,\"url\":\"https://github.com/maish\"}]},\"filePathRelative\":\"README.md\"}")
export { comp, data }

if (import.meta.webpackHot) {
  import.meta.webpackHot.accept()
  if (__VUE_HMR_RUNTIME__.updatePageData) {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(({ data }) => {
    __VUE_HMR_RUNTIME__.updatePageData(data)
  })
}
