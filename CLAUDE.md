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

## 部署脚本

- `rebuild.sh` - 完整重建 (Docker)
- `restart.sh` - Docker Compose 重启
