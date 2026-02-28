---
title: API 文档
---

## 接口文档

后端采用 Django REST Framework + drf-spectacular 自动生成 API 文档。

### 在线文档

- **[Swagger UI](/api/docs/)** - 交互式 API 文档，支持在线调试
- **[ReDoc](/api/redoc/)** - 格式化 API 参考文档

::: tip 说明
以上链接通过前端服务代理访问后端 API 文档：
- **开发环境**：由 Vite 代理到 `http://localhost:8000`
- **生产环境**：由 Nginx 代理到后端服务

如果代理不可用，请直接访问后端地址（需根据环境调整端口号）。
:::

### 认证方式

所有 API 请求都需要携带 Token 进行认证：

```
GET /api/v1/cmdb/model_instance/?token=your_jwt_token
```

或者使用 HTTP Header：

```
Authorization: Bearer your_jwt_token
```

### 分页参数

大部分列表接口支持分页：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| page | 页码（从1开始） | 1 |
| page_size | 每页数量（最大100） | 10 |

### 模块说明

| 模块 | 前缀 | 说明 |
|------|------|------|
| CMDB | `/api/v1/cmdb/` | 配置管理数据库 |
| 用户管理 | `/api/v1/mapi/` | 用户、角色、权限 |
| 节点管理 | `/api/v1/node_mg/` | 服务器、设备管理 |
| 访问控制 | `/api/v1/access/` | 访问控制 |
| 审计 | `/api/v1/audit/` | 操作审计日志 |
