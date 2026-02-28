---
title: 安装部署
icon: laptop-code
order: 2
---

## 系统要求

### 硬件配置

| 资源 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 内存 | 8 GB | 32 GB+ |
| CPU | 4 核 | 8 核+ |
| 磁盘 | 100 GB | 500 GB+ |

### 软件环境

| 软件 | 版本要求 |
|------|---------|
| 操作系统 | 内核 > 3（RedHat 7.5+ / openEuler 20+ / Ubuntu 20+） |
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

### 网络要求

- 关闭防火墙或开放必要端口（8843、8000、3306）
- 确保容器间网络互通

---

## 快速开始

### 1. 上传并解压

```bash
# 上传部署包
scp teligen-ui_v1.3.3.tar.gz root@your-server:/opt/

# 解压
cd /opt
tar xzf teligen-ui_v1.3.3.tar.gz
cd teligen-ui
```

### 2. 修改配置

```bash
# 编辑环境变量
vim .env

# 必须修改
DATABASE_PASSWORD=your_strong_password    # 数据库密码
WEB_PORT=8843                            # Web 访问端口
```

### 3. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看状态
docker-compose ps
```

### 4. 访问系统

```
https://your-server-ip:8843
```

默认账号：`admin / thinker`

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [Docker Compose 原理](./docker-compose.md) | 了解 Docker Compose 和系统架构 |
| [环境变量配置](./env-config.md) | .env 文件参数详解 |
| [服务配置说明](./services.md) | 各服务配置详解 |
| [部署步骤](./deployment.md) | 完整部署流程 |
| [运维管理](./operations.md) | 运维命令和故障排查 |
