---
title: 服务配置说明
icon: server
order: 3
---

## 服务列表

本系统由 6 个服务组成：

| 服务名 | 容器名 | 镜像 | 端口 | 说明 |
|--------|--------|------|------|------|
| web | web-ui | nginx:latest | 8843 | Web 服务器 |
| service | manage-django | manage-django:版本 | 8000 | Django 后端 |
| db | mysql | mysql:8.3 | 3306 | MySQL 数据库 |
| redis | redis | redis:latest | - | Redis 缓存 |
| celery | celery-worker | manage-django:版本 | - | Celery 任务消费者 |
| celery-beat | celery-beat | manage-django:版本 | - | Celery 定时任务 |

---

## web (Nginx)

### 配置说明

```yaml
web:
  image: nginx:latest
  container_name: web-ui
  restart: always
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    - ./nginx/server.key:/etc/nginx/server.key
    - ./nginx/server.crt:/etc/nginx/server.crt
    - ./nginx/dist:/usr/share/nginx/html
    - ./nginx/docs:/usr/share/nginx/docs
  environment:
    - APP_VERSION=${APP_VERSION:-latest}
  ports:
    - ${WEB_PORT:-443}:443
  depends_on:
    - service
    - db
    - redis
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| HTTPS 服务 | 提供 SSL/TLS 加密访问 |
| 静态文件 | 托管前端 (dist/) 和文档 (docs/) |
| API 代理 | `/api/*` 代理到 `service:8000` |
| WebSocket | 支持 WebSocket 连接转发 |

### 目录挂载

| 宿主机 | 容器内 | 说明 |
|--------|--------|------|
| `./nginx/nginx.conf` | `/etc/nginx/nginx.conf` | Nginx 配置文件 |
| `./nginx/server.key` | `/etc/nginx/server.key` | SSL 私钥 |
| `./nginx/server.crt` | `/etc/nginx/server.crt` | SSL 证书 |
| `./nginx/dist` | `/usr/share/nginx/html` | 前端静态文件 |
| `./nginx/docs` | `/usr/share/nginx/docs` | 文档静态文件 |

---

## service (Django 后端)

### 配置说明

```yaml
service:
  build: ./build
  image: manage-django:${APP_VERSION}
  container_name: manage-django
  restart: always
  privileged: true
  environment:
    - DATABASE_HOST=${DATABASE_HOST:-mysql}
    - DATABASE_PORT=${DATABASE_PORT:-3306}
    - DATABASE_USER=${DATABASE_USER:-root}
    - DATABASE_PASS=${DATABASE_PASS:-thinker}
    - MANAGE_DATABASE=${MANAGE_DATABASE:-manage}
    - CMDB_DATABASE=${CMDB_DATABASE:-cmdb}
    - REDIS_HOST=${REDIS_HOST:-redis}
    - REDIS_PORT=${REDIS_PORT:-6379}
    - ZABBIX_URL=${ZABBIX_URL}
    - ZABBIX_SERVER=${ZABBIX_SERVER}
    - ZABBIX_USER=${ZABBIX_USR:-Admin}
    - ZABBIX_PASSWORD=${ZABBIX_PASSWORD:-zabbix}
    - ZABBIX_INTERVAL=${ZABBIX_INTERVAL:-0}
  volumes:
    - /etc/localtime:/etc/localtime:ro
    - ./logs:/opt/teligen-ui/logs
    - ./zabbix_agent:/opt/zabbix_agent
    - ./etc/ansible.cfg:/etc/ansible/ansible.cfg
  ports:
    - 8000:8000
  depends_on:
    - db
    - redis
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| REST API | 提供所有后端 API 接口 |
| 业务逻辑 | CMDB、日志、作业等业务处理 |
| WebSocket | 实时消息推送 |
| Ansible 集成 | 远程执行命令和脚本 |
| Zabbix 集成 | 监控数据采集 |

### 特权模式

`privileged: true` 用于 Ansible 操作，需要：
- 读写宿主机文件
- 执行系统命令
- 连接到远程节点

---

## db (MySQL 数据库)

### 配置说明

```yaml
db:
  image: mysql:8.3
  container_name: mysql
  restart: always
  environment:
    - MYSQL_ROOT_PASSWORD=${DATABASE_PASSWORD:-thinker}
    - MANAGE_DATABASE=${MANAGE_DATABASE:-manage}
    - CMDB_DATABASE=${CMDB_DATABASE:-cmdb}
  volumes:
    - ${DATA_DIR}/mysql:/var/lib/mysql
    - ./etc/my.cnf:/etc/mysql/conf.d/my.cnf
    - ./etc/init.sql:/docker-entrypoint-initdb.d/init.sql
  ports:
    - "3306:3306"
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| 数据存储 | CMDB、用户、业务数据 |
| 自动初始化 | 首次启动执行 `init.sql` |
| 配置管理 | 支持自定义 `my.cnf` |

### 数据库列表

| 数据库 | 说明 |
|--------|------|
| `manage` | 业务数据（用户、角色、权限等） |
| `cmdb` | CMDB 配置和资产数据 |

### 数据持久化

```bash
# 数据文件位置
${DATA_DIR}/mysql/

# 包含内容
- ibdata1        # 系统表空间
- ib_logfile0     # 日志文件
- manage/         # manage 数据库
- cmdb/           # cmdb 数据库
```

::: warning 备份建议
定期备份 `${DATA_DIR}/mysql/` 目录，或使用 `mysqldump` 导出数据。
:::

---

## redis (缓存服务)

### 配置说明

```yaml
redis:
  image: redis:latest
  container_name: redis
  restart: always
  volumes:
    - ${DATA_DIR}/redis-data:/data
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| 数据缓存 | 热点数据缓存，提高响应速度 |
| 会话存储 | 用户会话信息 |
| 消息队列 | Celery 任务队列 |

---

## celery (任务消费者)

### 配置说明

```yaml
celery:
  build: ./build
  restart: always
  container_name: celery-worker
  privileged: true
  volumes:
    - .:/app
  depends_on:
    - service
    - redis
  entrypoint: /bin/bash -c "sleep 30 && celery -A vuedjango worker --loglevel=info"
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| 异步任务 | 执行耗时的后台任务 |
| 日志分析 | 流程日志分析任务 |
| 批量操作 | 批量导入导出 |

### 启动延迟

`sleep 30` 确保：
- Django 后端完全启动
- 数据库迁移完成
- Redis 连接就绪

---

## celery-beat (定时任务)

### 配置说明

```yaml
celery-beat:
  build: ./build
  restart: always
  container_name: celery-beat
  privileged: true
  depends_on:
    - service
    - redis
  entrypoint: /bin/bash -c "sleep 30 && celery -A vuedjango beat --loglevel=info"
  networks:
    - backend
```

### 功能职责

| 功能 | 说明 |
|------|------|
| 定时任务 | 按配置触发周期性任务 |
| 任务调度 | 向 Celery 发送定时任务 |
| 监控巡检 | 定期采集监控数据 |

---

## 服务通信

### 内部网络通信

```
web → service → db
                → redis

celery → redis → service → db
celery-beat → redis
```

### 端口说明

| 端口 | 服务 | 暴露范围 | 用途 |
|------|------|---------|------|
| 8843 | web | 外部 | HTTPS 访问 |
| 8000 | service | 内部 | API 调用 |
| 3306 | db | 内部 | 数据库连接 |
| 6379 | redis | 内部 | 缓存/队列 |

::: tip 安全建议
只有 `web` 服务的端口需要暴露到外部，其他服务通过内部网络访问，提高安全性。
:::
