

export default {
  navbar: [
    // 嵌套 Group - 最大深度为 2
    {
      text: 'Group',
      prefix: '/group/',
      children: [
        {
          text: 'SubGroup1',
          prefix: 'sub1/',
          children: [
            'foo.md', // 解析为 `/guide/group/sub1/bar.md`
            'bar.md', // 解析为 `/guide/group/sub1/bar.md`

            // 一个外部链接
            {
              text: 'Example',
              link: 'https://example.com',
            },
          ],
        },
        {
          text: 'SubGroup2',
          prefix: 'sub2/',
          // 项目内链接的 .md 或 .html 后缀是可以省略的
          children: [
            'foo', // 解析为 `/guide/group/sub2/foo.md`
            'bar', // 解析为 `/guide/group/sub2/bar.md`

            // 不在 SubGroup2 内的链接
            '/baz/', // 解析为 `/baz/README.md`
          ],
        },
      ],
    },
    // 控制元素何时被激活
    {
      text: 'Group 2',
      children: [
        {
          text: 'Always active',
          link: '/',
          // 该元素将一直处于激活状态
          activeMatch: '/',
        },
        {
          text: 'Active on /foo/',
          link: '/not-foo/',
          // 该元素在当前路由路径是 /foo/ 开头时激活
          // 支持正则表达式
          activeMatch: '^/foo/',
        },
      ],
    },
  ]
}

