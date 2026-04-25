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

## 知识发现协议

理解本项目时应按以下优先级查阅信息，避免直接翻源码：

1. **API 参考手册** → `docs/api-reference.md`（静态导出，无需启动后端）
2. **在线 API 文档**（需启动后端）→ `/api/docs/`(Swagger) | `/api/redoc/`(ReDoc)
3. **Schema 定义** → 各模块 `schemas.py`（请求/响应结构、示例）
4. **源码** → `views.py` → `serializers.py` → `models.py`（仅当文档不足以解答时）

### 各模块 Schema 文件
- `django/mapi/schemas.py` — 用户/权限管理
- `django/cmdb/schemas.py` — CMDB 核心（模型、字段、实例）
- `django/node_mg/schemas.py` — 节点管理
- `django/access/schemas.py` — 访问控制
- `django/audit/schemas.py` — 审计日志

### 全局配置
- `django/vuedjango/settings.py` — SPECTACULAR_SETTINGS
- `django/vuedjango/drf_spectacular_hooks.py` — Schema 后处理钩子

## Fork 开发工作流

本项目 fork 自 `Mmmai/hz-manage`，开发时必须遵循以下流程：

### 远程仓库
- `origin` → `lakeland1990/hz-manage`（自己的 fork）
- `upstream` → `Mmmai/hz-manage`（原仓库）

### 核心规则
- **永远不要在 main 分支上直接改代码**，main 只用来同步 upstream
- **一个分支只做一件事**，有新想法就基于最新 main 另开分支

### 标准开发循环
```
1. 同步 upstream
   git checkout main
   git pull upstream main

2. 创建功能分支
   git checkout -b feature/xxx

3. 开发完成后，rebase 到最新 main
   git rebase main

4. 推送到 origin 并提 PR
   git push origin feature/xxx
   → GitHub 页面提 PR 到 upstream/main

5. PR 合并后清理
   git checkout main && git pull upstream main
   git branch -d feature/xxx
   git push origin --delete feature/xxx
```

## 开发注意事项

### CMDB 测试

测试套件位于 `django/cmdb/tests/`，使用 SQLite 内存数据库（`vuedjango/test_settings.py`）。

```bash
cd django
conda activate django37
python manage.py test cmdb.tests --settings=vuedjango.test_settings --verbosity=1
```

测试基类 `CmdbAPITestCase`（`cmdb/tests/__init__.py`）自动处理：
- 认证模拟（`force_authenticate`）
- 数据权限过滤器 mock（`get_scope_query`、`PermissionManager`）
- 信号断开（CMDB 初始化、字段元数据、审计、node_mg 同步）
- SQLite 不支持 JSONField `contains` 查询，涉及此查询的 service 方法需 mock

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
