# 工作日志

## 2026-04-24

- **变更摘要**：添加API参考手册、知识发现协议和Fork开发规范
  - `docs/api-reference.md`：渐进式API参考手册（三层：模块总览→接口列表→请求/响应详情），覆盖132个接口
  - `docs/openapi-schema.json`：OpenAPI 3 完整 Schema 导出（可通过 `python manage.py spectacular` 重新生成）
  - `CLAUDE.md`：增加知识发现协议章节（定义AI查阅优先级：API手册→在线文档→Schema→源码）
  - `CLAUDE.md`：增加 Fork 开发工作流规范（分支策略、upstream同步流程）
  - `.gitattributes`：统一换行符配置（.sh/.py 强制 LF）
  - `.gitignore`：排除 openapi-schema.json

- **环境配置**：使用 conda 创建 django37 环境（Python 3.7.16），安装项目依赖，验证 spectacular 命令可用

- **PR**：#30 已合并到 upstream（Mmmai/hz-manage）
