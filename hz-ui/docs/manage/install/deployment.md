---
title: 部署步骤
icon: download
order: 4
---

## 部署准备

### 1. 上传部署包

```bash
# 方式一：SCP 上传
scp teligen-ui_v1.3.3.tar.gz root@your-server:/opt/

# 方式二：直接下载
wget https://your-repo/teligen-ui_v1.3.3.tar.gz -O /opt/teligen-ui_v1.3.3.tar.gz
```

### 2. 解压部署包

```bash
cd /opt
tar xzf teligen-ui_v1.3.3.tar.gz
cd teligen-ui
```

### 3. 检查文件结构

```bash
ls -la

# 应该包含以下内容
# docker-compose.yaml
# .env
# nginx/
# build/
# etc/
```

---

## 配置修改

### 1. 编辑环境变量

```bash
vim .env
```

### 2. 必须修改的参数

```bash
# 数据库密码（必须修改）
DATABASE_PASSWORD=YourStrongPassword123!

# Web 端口（如有冲突）
WEB_PORT=8843

# 数据目录（建议使用绝对路径）
DATA_DIR=/data/teligen-ui
```

### 3. 可选修改

```bash
# Zabbix 配置（如果使用监控）
ZABBIX_URL=http://your-zabbix/api_jsonrpc.php
ZABBIX_SERVER=your-zabbix-ip
ZABBIX_INTERVAL=300
```

### 4. 创建数据目录

```bash
mkdir -p /data/teligen-ui
```

---

## 启动服务

### 1. 启动所有服务

```bash
docker-compose up -d
```

### 2. 查看启动状态

```bash
docker-compose ps

# 输出示例：
# NAME              STATUS    PORTS
# web-ui            Up        0.0.0.0:8843->443/tcp
# manage-django     Up        0.0.0.0:8000->8000/tcp
# mysql             Up        0.0.0.0:3306->3306/tcp
# redis             Up        6379/tcp
# celery-worker     Up
# celery-beat       Up
```

### 3. 查看启动日志

```bash
# 查看所有服务日志
docker-compose logs

# 实时跟踪日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f service
```

---

## 初始化检查

### 1. 检查容器状态

```bash
docker ps

# 确认所有容器状态为 "Up"
```

### 2. 检查网络连接

```bash
docker network inspect teligen-ui_backend

# 确认所有容器都在 backend 网络中
```

### 3. 检查数据库初始化

```bash
# 进入 MySQL 容器
docker exec -it mysql mysql -uroot -p

# 查看数据库
SHOW DATABASES;

# 应该包含：
# - manage
# - cmdb
```

### 4. 检查后端 API

```bash
curl http://localhost:8000/api/v1/mapi/user/

# 返回 JSON 数据表示后端正常
```

---

## 防火墙配置

### 1. 开放 Web 端口

```bash
# firewalld
firewall-cmd --permanent --add-port=8843/tcp
firewall-cmd --reload

# ufw (Ubuntu)
ufw allow 8843/tcp
```

### 2. 验证端口

```bash
netstat -tunlp | grep 8843

# 应该看到 docker-proxy 监听 8843
```

---

## 访问系统

### 1. 浏览器访问

```
https://your-server-ip:8843
```

### 2. 首次登录

```
用户名: admin
密码: thinker
```

::: warning 安全提醒
首次登录后请立即修改默认密码！
:::

### 3. 验证功能

- 登录系统
- 查看首页
- 访问文档 (点击右上角文档图标)
- 测试基础功能

---

## 部署后配置

### 1. 修改默认密码

```
登录系统 → 系统管理 → 用户管理 → admin → 修改密码
```

### 2. 配置角色权限

```
系统管理 → 角色管理 → 创建角色 → 分配权限
```

### 3. 添加用户

```
系统管理 → 用户管理 → 新增用户 → 分配角色
```

### 4. 配置门户收藏夹

```
点击任意页面右上角"收藏"按钮 → 添加到门户
```

---

## 升级部署

### 1. 备份数据

```bash
# 停止服务
docker-compose down

# 备份数据目录
cp -r /data/teligen-ui /data/teligen-ui.backup
```

### 2. 上传新版本

```bash
# 上传新部署包
scp teligen-ui_v1.4.0.tar.gz root@server:/opt/

# 解压
cd /opt
tar xzf teligen-ui_v1.4.0.tar.gz
cd teligen-ui
```

### 3. 复制配置

```bash
# 复制旧版本的 .env 和数据
cp ../teligen-ui.old/.env .
```

### 4. 更新镜像

```bash
# 构建新镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 5. 数据迁移

```bash
# 进入后端容器
docker exec -it manage-django bash

# 执行数据库迁移
python manage.py migrate
```

---

## 回滚部署

### 1. 停止服务

```bash
docker-compose down
```

### 2. 恢复备份

```bash
# 恢复数据目录
rm -rf /data/teligen-ui
mv /data/teligen-ui.backup /data/teligen-ui
```

### 3. 重启服务

```bash
cd /opt/teligen-ui.old
docker-compose up -d
```
