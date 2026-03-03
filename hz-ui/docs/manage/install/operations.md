---
title: 运维管理
icon: wrench
order: 5
---

## 服务管理

### 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 启动指定服务
docker-compose up -d service
```

### 停止服务

```bash
# 停止所有服务
docker-compose stop

# 停止指定服务
docker-compose stop service

# 停止并删除容器
docker-compose down
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启指定服务
docker-compose restart service
```

### 查看状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看详细信息
docker ps -a
```

---

## 日志管理

### 查看日志

```bash
# 查看所有日志
docker-compose logs

# 查看指定服务日志
docker-compose logs service

# 实时跟踪日志
docker-compose logs -f service

# 查看最近 N 行
docker-compose logs --tail=100 service

# 查看指定时间日志
docker-compose logs --since 1h service
```

### 日志文件位置

| 服务 | 日志路径 | 说明 |
|------|---------|------|
| Django | `./logs/django.log` | 应用日志 |
| Nginx | 容器内 `/var/log/nginx/` | 访问日志 |
| Celery | `./logs/celery.log` | 任务日志 |

### 清理日志

```bash
# 清理 Django 日志
> ./logs/django.log

# 清理 Celery 日志
> ./logs/celery.log

# 或者使用 logrotate 配置自动轮转
```

---

## 容器操作

### 进入容器

```bash
# 进入 Django 容器
docker exec -it manage-django bash

# 进入 MySQL 容器
docker exec -it mysql bash

# 进入 Redis 容器
docker exec -it redis bash
```

### 执行命令

```bash
# 在容器中执行单条命令
docker exec manage-django python manage.py migrate

# 在容器中执行数据库操作
docker exec mysql mysql -uroot -p -e "SHOW DATABASES;"
```

### 查看资源占用

```bash
# 查看所有容器资源使用
docker stats

# 查看指定容器
docker stats manage-django
```

---

## 数据库管理

### 备份数据库

```bash
# 备份所有数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --all-databases > backup_$(date +%Y%m%d).sql

# 备份指定数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  manage > backup_manage_$(date +%Y%m%d).sql

# 备份 CMDB 数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  cmdb > backup_cmdb_$(date +%Y%m%d).sql
```

### 恢复数据库

```bash
# 恢复数据库
docker exec -i mysql mysql -uroot -p${DATABASE_PASSWORD} \
  < backup_20250128.sql
```

### 进入数据库

```bash
# 进入 MySQL
docker exec -it mysql mysql -uroot -p

# 执行 SQL
mysql> USE manage;
mysql> SHOW TABLES;
mysql> SELECT * FROM auth_user;
```

---

## 数据目录管理

### 查看数据目录大小

```bash
# 查看总大小
du -sh ${DATA_DIR}

# 查看各子目录
du -sh ${DATA_DIR}/*
```

### 清理数据

```bash
# 清理 Docker 未使用的资源
docker system prune -a

# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune
```

---

## 性能监控

### 查看服务健康状态

```bash
# 检查所有容器状态
docker ps

# 检查容器健康检查日志
docker inspect --format='{{.State.Health.Status}}' manage-django
```

### 监控资源使用

```bash
# 实时监控
docker stats

# 查看磁盘使用
df -h

# 查看内存使用
free -h
```

### 性能优化建议

| 项目 | 优化建议 |
|------|---------|
| 数据库 | 定期清理日志，优化索引 |
| Redis | 配置最大内存限制 |
| 日志 | 配置日志轮转，避免磁盘占满 |
| 容器 | 限制容器资源使用 |

---

## 故障排查

### 服务启动失败

```bash
# 1. 查看详细日志
docker-compose logs service

# 2. 检查配置文件
docker-compose config

# 3. 检查端口占用
netstat -tunlp | grep 8843

# 4. 检查磁盘空间
df -h
```

### 数据库连接失败

```bash
# 1. 检查 MySQL 容器状态
docker ps | grep mysql

# 2. 检查数据库日志
docker logs mysql

# 3. 测试数据库连接
docker exec manage-django python manage.py dbshell

# 4. 检查网络连通性
docker exec web-ui ping mysql
```

### 无法访问 Web

```bash
# 1. 检查 Nginx 容器
docker ps | grep web-ui

# 2. 检查 Nginx 配置
docker exec web-ui nginx -t

# 3. 查看 Nginx 日志
docker logs web-ui

# 4. 检查防火墙
firewall-cmd --list-all
```

### 容器频繁重启

```bash
# 1. 查看重启次数
docker ps -a

# 2. 查看重启日志
docker logs --tail=50 service

# 3. 检查容器资源
docker stats service

# 4. 检查系统日志
dmesg | tail
```

---

## 常见问题

### Q: 忘记数据库密码？

A: 查看 `.env` 文件或重置密码：

```bash
# 查看当前密码
grep DATABASE_PASSWORD .env

# 重置密码
docker exec -it mysql mysql -uroot -p
mysql> ALTER USER 'root'@'%' IDENTIFIED BY 'new_password';
```

### Q: 如何修改 Web 端口？

A: 修改 `.env` 中的 `WEB_PORT` 并重启：

```bash
vim .env
# WEB_PORT=9443

docker-compose up -d web
```

### Q: 如何扩容 Celery Worker？

A: 修改 `docker-compose.yaml` 中的 scale：

```bash
docker-compose up -d --scale celery=3
```

### Q: 数据库文件太大怎么办？

A: 定期清理日志和备份数据：

```bash
# 清理 Django 日志
> ./logs/django.log

# 备份并清理旧数据
docker exec mysql mysqldump -uroot -p manage > backup.sql
docker exec -it mysql mysql -uroot -p -e "DELETE FROM audit_log WHERE created < '2024-01-01';"
```

### Q: 如何查看容器内部网络？

A: 使用 `docker network inspect`：

```bash
docker network inspect teligen-ui_backend
```
