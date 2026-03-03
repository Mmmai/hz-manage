---
title: 环境变量配置
icon: file-settings
order: 2
---

## .env 文件概述

`.env` 文件位于部署目录根目录，用于定义环境变量。Docker Compose 启动时会自动读取该文件，并替换 `docker-compose.yaml` 中的变量引用。

### 位置

```bash
/usr/teligen-ui/teligen-ui/.env
```

---

## 完整配置示例

```bash
# 版本配置
APP_VERSION=v1.3.3

# Web 服务配置
WEB_PORT=8843                    # Nginx HTTPS 访问端口

# 数据库配置
DATABASE_HOST=mysql              # 数据库主机（容器名）
DATABASE_PORT=3306               # 数据库端口
DATABASE_USER=root               # 数据库用户
DATABASE_PASSWORD=thinker        # 数据库密码（必须修改）
DATABASE_NAME=autoOps            # 统一数据库名

# Redis 配置
REDIS_HOST=redis                 # Redis 主机（容器名）
REDIS_PORT=6379                  # Redis 端口

# Zabbix 配置
ZABBIX_URL=http://192.168.163.160/api_jsonrpc.php
ZABBIX_SERVER=192.168.163.160
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
ZABBIX_INTERVAL=0                # 监控数据采集间隔（0=禁用）

# 数据持久化目录
DATA_DIR=./data                  # 数据存储根目录
```

---

## 参数详解

### 版本配置

| 参数 | 说明 | 示例 |
|------|------|------|
| `APP_VERSION` | 应用版本号，用于构建镜像标签 | `v1.3.3` |

### Web 服务配置

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `WEB_PORT` | Nginx HTTPS 端口 | `443` | 修改为 `8843` 等，避免冲突 |

::: tip 端口说明
- 宿主机访问：`https://ip:${WEB_PORT}`
- 容器内部始终使用 `443`
:::

### 数据库配置

| 参数 | 说明 | 默认值 | 安全建议 |
|------|------|--------|---------|
| `DATABASE_HOST` | 数据库主机 | `mysql` | **不要修改**（容器名） |
| `DATABASE_PORT` | 数据库端口 | `3306` | **不要修改**（容器内部端口） |
| `DATABASE_USER` | 数据库用户 | `root` | 保持默认 |
| `DATABASE_PASSWORD` | 数据库密码 | `thinker` | **必须修改为强密码** |
| `DATABASE_NAME` | 统一数据库 | `autoOps` | 按需修改 |

::: warning 安全警告
生产环境务必修改 `DATABASE_PASSWORD` 为强密码！建议使用大小写字母+数字+特殊字符，长度至少 12 位。
:::

### Redis 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `REDIS_HOST` | Redis 主机 | `redis` |
| `REDIS_PORT` | Redis 端口 | `6379` |

::: tip 说明
Redis 配置通常不需要修改，`redis` 是容器名。
:::

### Zabbix 配置

| 参数 | 说明 | 示例 |
|------|------|------|
| `ZABBIX_URL` | Zabbix API 地址 | `http://192.168.163.160/api_jsonrpc.php` |
| `ZABBIX_SERVER` | Zabbix 服务器地址 | `192.168.163.160` |
| `ZABBIX_USER` | Zabbix 用户名 | `Admin` |
| `ZABBIX_PASSWORD` | Zabbix 密码 | `zabbix` |
| `ZABBIX_INTERVAL` | 采集间隔（秒） | `0`（禁用） |

::: tip Zabbix 集成
如果不使用 Zabbix，保持 `ZABBIX_INTERVAL=0` 即可。
:::

### 数据持久化配置

| 参数 | 说明 | 建议 |
|------|------|------|
| `DATA_DIR` | 数据存储根目录 | 使用绝对路径，如 `/data/teligen-ui` |

---

## 环境变量替换

### 语法规则

在 `docker-compose.yaml` 中使用：

```yaml
environment:
  - DATABASE_HOST=${DATABASE_HOST:-mysql}
  - DATABASE_PASSWORD=${DATABASE_PASSWORD:-thinker}
```

**格式**：`${变量名:-默认值}`

- 如果 `.env` 中定义了该变量，使用 `.env` 中的值
- 如果未定义，使用冒号后的默认值

### 实际示例

| .env 配置 | docker-compose.yaml | 实际值 |
|-----------|---------------------|--------|
| `WEB_PORT=8843` | `${WEB_PORT:-443}` | `8843` |
| 未配置 | `${WEB_PORT:-443}` | `443` |
| `DATABASE_PASSWORD=abc123` | `${DATABASE_PASSWORD:-thinker}` | `abc123` |

---

## 修改配置

### 修改密码

```bash
# 1. 编辑 .env 文件
vim .env

# 2. 修改数据库密码
DATABASE_PASSWORD=YourStrongPassword123!

# 3. 重建数据库容器
docker-compose stop db
docker-compose rm -f db
docker-compose up -d db

# 4. 更新 service 配置
docker-compose up -d service
```

### 修改端口

```bash
# 1. 编辑 .env 文件
vim .env

# 2. 修改 Web 端口
WEB_PORT=9443

# 3. 重启 web 服务
docker-compose up -d web
```

### 修改数据目录

```bash
# 1. 停止所有服务
docker-compose down

# 2. 移动数据目录
mv ./data /data/teligen-ui

# 3. 编辑 .env 文件
vim .env
DATA_DIR=/data/teligen-ui

# 4. 启动服务
docker-compose up -d
```

---

## 常见问题

### Q: 修改 .env 后需要重启吗？

A: 是的。修改 `.env` 后需要重启受影响的服务：

```bash
docker-compose up -d
```

### Q: 如何验证环境变量是否生效？

A: 进入容器查看环境变量：

```bash
docker exec manage-django env | grep DATABASE
```

### Q: 忘记数据库密码怎么办？

A: 查看当前配置：

```bash
grep DATABASE_PASSWORD .env
```

或进入数据库重置：

```bash
docker exec -it mysql mysql -uroot -p
```
