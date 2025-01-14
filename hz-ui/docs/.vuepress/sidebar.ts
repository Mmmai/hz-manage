import path from "path";

export default {
  sidebar: {
    '/manage/': [
      {
        text: "介绍",
        link: "/manage/"
      },
      {
        text: "安装部署",
        link: "/manage/install.md"
      },
      {
        text: '基础功能',
        collapsible: true,
        children: [
          {
            text: "用户管理",
            link: '/manage/basic/rbac.md',
          },
          {
            text: "菜单管理",
            link: '/manage/basic/menu.md',
          },
        ]
      }
    ]
  }
}