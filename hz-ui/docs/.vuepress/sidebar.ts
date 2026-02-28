import path from "path";

export default {
  sidebar: {
    '/manage/': [
      {
        text: "概览",
        link: "/manage/",
      },
      {
        text: "部署运维",
        collapsible: true,
        children: [
          {
            text: "快速开始",
            link: "/manage/install/README.md",
          },
          {
            text: "Docker Compose 原理",
            link: "/manage/install/docker-compose.md",
          },
          {
            text: "环境变量配置",
            link: "/manage/install/env-config.md",
          },
          {
            text: "服务配置说明",
            link: "/manage/install/services.md",
          },
          {
            text: "部署步骤",
            link: "/manage/install/deployment.md",
          },
          {
            text: "备份与恢复",
            link: "/manage/install/backup.md",
          },
          {
            text: "运维管理",
            link: "/manage/install/operations.md",
          },
        ],
      },
      {
        text: "用户指南",
        collapsible: true,
        children: [
          {
            text: "首页",
            link: "/manage/guide/home.md",
          },
          {
            text: "门户收藏夹",
            link: "/manage/guide/favorites.md",
          },
          {
            text: "资产配置",
            collapsible: true,
            children: [
              {
                text: "资源检索",
                link: "/manage/guide/cmdb/search.md",
              },
              {
                text: "资源实例",
                link: "/manage/guide/cmdb/instance.md",
              },
              {
                text: "模型管理",
                link: "/manage/guide/cmdb/model.md",
              },
              {
                text: "校验配置",
                link: "/manage/guide/cmdb/validation.md",
              },
              {
                text: "关联关系",
                link: "/manage/guide/cmdb/relation.md",
              },
              {
                text: "资产审计",
                link: "/manage/guide/cmdb/audit.md",
              },
            ],
          },
          {
            text: "管控平台",
            collapsible: true,
            children: [
              {
                text: "节点管理",
                link: "/manage/guide/node/node.md",
              },
              {
                text: "代理配置",
                link: "/manage/guide/node/proxy.md",
              },
            ],
          },
          {
            text: "作业平台",
            collapsible: true,
            children: [
              {
                text: "批量执行",
                link: "/manage/guide/job/ansible.md",
              },
            ],
          },
          {
            text: "日志应用",
            collapsible: true,
            children: [
              {
                text: "日志检索",
                link: "/manage/guide/log/loki.md",
              },
              {
                text: "流程日志",
                link: "/manage/guide/log/analysis.md",
              },
              {
                text: "环节配置",
                link: "/manage/guide/log/module.md",
              },
            ],
          },
          {
            text: "系统管理",
            collapsible: true,
            children: [
              {
                text: "用户与权限",
                link: "/manage/guide/system/rbac.md",
              },
              {
                text: "菜单管理",
                link: "/manage/guide/system/menu.md",
              },
            ],
          },
        ],
      },
      {
        text: "开发指南",
        collapsible: true,
        children: [
          {
            text: "构建说明",
            link: "/manage/deploy.md",
          },
          {
            text: "API 文档",
            link: "/manage/api.md",
          },
          {
            text: "版本历史",
            link: "/manage/version.md",
          },
        ],
      },
    ],
  },
};