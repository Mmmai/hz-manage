---
title: Docker Compose 原理
icon: container
order: 1
---

## 什么是 Docker Compose

Docker Compose 是用于定义和运行多容器 Docker 应用程序的工具。通过 YAML 配置文件，可以一次性启动多个相关联的容器。

### 核心价值

- **统一编排**：一个文件管理所有服务
- **依赖管理**：自动处理服务启动顺序
- **网络隔离**：容器间独立网络通信
- **快速部署**：一条命令启动整套系统

---

## 基本概念

### YAML 配置文件

```yaml
version: '3'              # Compose 文件版本
services:                 # 定义服务
  web:                    # 服务名称
    image: nginx:latest   # 使用的镜像
    ports:                # 端口映射
      - "80:80"
networks:                # 定义网络
  frontend:
volumes:                 # 定义数据卷
  data:
```

### 常用命令

| 命令 | 说明 |
|------|------|
| `docker-compose up -d` | 启动所有服务（后台运行） |
| `docker-compose down` | 停止并删除所有容器 |
| `docker-compose ps` | 查看服务状态 |
| `docker-compose logs` | 查看所有日志 |
| `docker-compose restart` | 重启服务 |
| `docker-compose exec` | 进入容器执行命令 |

---

## 系统架构

### 整体架构图

```
┌────────────────────────────────────────────────────────────────┐
│                         浏览器客户端                            │
└────────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS :8843
                            ▼
┌────────────────────────────────────────────────────────────────┐
│  web (Nginx)                                                    │
│  - 静态文件服务 (前端 + 文档)                                   │
│  - SSL/TLS 加密                                                │
│  - API 请求代理 → service:8000                                 │
└────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   service    │  │  db (MySQL)  │  │   redis      │
│  Django:8000 │  │   Port:3306  │  │   Port:6379  │
│              │  │              │  │              │
│ - REST API   │  │ - 数据存储   │  │ - 缓存       │
│ - WebSocket  │  │ - 持久化     │  │ - 消息队列   │
│ - 业务逻辑   │  │              │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
       │
       ├──────────┬──────────┐
       ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐
  │ celery │ │ celery │ │ Zabbix │
  │ worker │ │  beat  │ │  API   │
  │        │ │        │ │        │
  │ 异步   │ │ 定时   │ │ 监控   │
  │ 任务   │ │ 任务   │ │ 对接   │
  └────────┘ └────────┘ └────────┘
```

### 数据流向

#### 1. 用户访问前端

```
浏览器 → Nginx:8843 → 静态文件 (dist/)
```

#### 2. API 请求

```
浏览器 → Nginx:8843 → proxy_pass → Django:8000 → MySQL/Redis
```

#### 3. WebSocket 连接

```
前端 → Nginx → Django:8000 (WebSocket)
```

#### 4. 异步任务

```
Django → Redis (消息队列) → Celery Worker → 执行任务
```

---

## 容器网络

### backend 网络

所有服务连接到 `backend` 网络，容器间可以通过**服务名**相互访问：

```yaml
networks:
  backend:        # 网络名称
```

### 服务发现

容器内部使用服务名进行通信：

| 源 | 目标 | 地址 |
|----|------|------|
| web | service | `http://service:8000` |
| service | mysql | `mysql:3306` |
| service | redis | `redis:6379` |

### 网络隔离

- `backend` 网络：内部服务通信
- 只有 `web` 服务暴露端口到宿主机
- 其他服务仅内部访问，提高安全性

---

## 服务依赖

### depends_on 配置

```yaml
service:
  depends_on:
    - db
    - redis
```

### 启动顺序

```
1. db (MySQL)    ← 基础服务
2. redis         ← 基础服务
3. service       ← 依赖 db、redis
4. web           ← 依赖 service
5. celery        ← 依赖 service、redis
6. celery-beat   ← 依赖 service、redis
```

::: tip 注意
`depends_on` 仅控制启动顺序，不等待服务就绪。Celery 使用 `sleep 30` 确保后端完全启动。
:::

---

## 数据持久化

### volumes 配置

```yaml
volumes:
  - ./data/mysql:/var/lib/mysql    # 数据库数据
  - ./logs:/opt/teligen-ui/logs    # 应用日志
```

### 持久化策略

| 数据类型 | 存储位置 | 说明 |
|---------|---------|------|
| 数据库 | `./data/mysql/` | MySQL 数据文件 |
| Redis | `./data/redis-data/` | Redis 持久化 |
| 日志 | `./logs/` | 应用和访问日志 |
| 配置 | `./nginx/`、`./etc/` | 配置文件 |

::: warning 重要
确保数据目录有足够的磁盘空间，并定期备份。
:::
