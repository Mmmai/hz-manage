# hz-manage

企业级运维管理平台，配置管理 + 节点管理 + 任务调度 + 监控告警

## 技术栈

- 前端: Node 20+ LTS + Vue 3.5 + Vite 5 + Element Plus + Ant Design Vue
- 后端: Python 3.7-3.8 + Django 3.2 + DRF + Channels (WebSocket)
- 缓存/队列: Redis + django-cacheops + Celery
- 图表/图形: ECharts + AntV X6 (建模)

## 目录结构

```
hz-manage/
├── django/              # Django 后端
│   ├── vuedjango/       # 主项目配置
│   ├── mapi/            # 用户管理
│   ├── cmdb/            # 配置管理数据库 (核心)
│   ├── node_mg/         # 节点管理
│   ├── jobflow/         # 任务流程
│   ├── monitor/         # 监控模块
│   ├── audit/           # 审计模块
│   ├── access/          # 访问控制
│   └── mlog/            # 日志模块
└── hz-ui/               # Vue 前端
    └── src/
        ├── api/         # API 封装
        ├── composables/ # 组合式函数
        └── views/       # 页面视图
```

## 项目特有配置

### 环境变量
后端数据库/Redis连接通过环境变量配置：
- `DATABASE_HOST/NAME/USER/PASSWORD/PORT` - MySQL 连接
- `REDIS_HOST/PORT` - Redis 连接
- `ZABBIX_URL` - Zabbix API 地址 (django/.env)

### 开发代理
hz-ui/vite.config.js 已配置代理：
- `/api` → `http://127.0.0.1:8000`
- `/ws`, `/jobflow/ws` → WebSocket

### WebSocket 支持
使用 ASGI (uvicorn) 而非 WSGI：
```bash
uvicorn --host 0.0.0.0 --port 8000 vuedjango.asgi:application --workers 5
```

### Celery 启动
```bash
# Windows (需 eventlet)
celery -A vuedjango worker -l info -P eventlet -B
# Linux
celery -A vuedjango worker -l info -B
```

## 核心模块关系

```
mapi (用户/权限)
    ├─> access (访问控制)
    ├─> audit (审计日志)
    └─> 所有业务模块

cmdb (配置管理) <─> node_mg (节点管理)
    ↓                    ↓
jobflow (任务流程) ←─ monitor (监控)
```

## 开发注意事项

**本项目暂不需要测试验证，只需保证代码能够编译通过。**

## Claude 任务与记忆管理规范

为确保项目连续性和防止上下文丢失，所有多步骤任务需遵循以下结构化流程：

### 1. 规划阶段（执行前）
- **目录**: `.claude/plans/`
- **操作**: 创建 Markdown 文件（如 `YYYY-MM-DD_task-name.md`），详细说明预期方案、受影响的文件和成功标准
- **目标**: 在进行重大代码更改前获得用户确认

### 2. 归档与总结（执行后）
- **归档目录**: `.claude/plans_archive/` - 存放已完成的原始计划文件
- **总结目录**: `.claude/completed/` - 存放执行总结文件
- **操作**: 任务完成后，将 `.claude/plans/` 中的原始计划文件移动到 `.claude/plans_archive/`，并生成执行总结（如 `YYYY-MM-DD_task-name.md`）到 `.claude/completed/`
- **内容要求**:
    - **完成内容**: 最终实现的高级概述
    - **关键决策**: 为何选择特定路径而非其他替代方案
    - **偏差**: 初始计划与实际实现之间的差异
    - **遗留与风险**: 未解决的问题、技术债务或需要未来关注的领域
    - **后续步骤**: 下一迭代的建议起点

### 3. 版本控制集成
- **提交策略**: 始终将 `.claude/completed/` 总结文件与代码更改包含在同一个 Git 提交中
- **提交消息**: 引用总结文件（如 `feat: user-auth (详情见 .claude/completed/...)`）

## 部署脚本

- `rebuild.sh` - 完整重建 (Docker)
- `restart.sh` - Docker Compose 重启
