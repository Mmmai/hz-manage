---
title: 备份与恢复
icon: shield
order: 6
---

## 重要数据识别

### 必须备份的数据

| 数据 | 位置 | 说明 | 重要性 |
|------|------|------|--------|
| 数据库 | `${DATA_DIR}/mysql/` | 所有业务数据、CMDB 数据 | ⭐⭐⭐ |
| 应用日志 | `./logs/` | 操作审计、故障排查 | ⭐⭐ |
| 配置文件 | `.env`、`./nginx/`、`./etc/` | 系统配置 | ⭐⭐⭐ |
| Docker 镜像 | 本地镜像仓库 | 自定义构建的镜像 | ⭐ |

### 可选备份的数据

| 数据 | 位置 | 说明 |
|------|------|------|
| Redis 数据 | `${DATA_DIR}/redis-data/` | 缓存数据（可重建） |
| Ansible 配置 | `./etc/ansible.cfg` | Ansible 配置 |
| Zabbix Agent | `./zabbix_agent/` | 监控代理配置 |

---

## 数据库备份

### 逻辑备份（mysqldump）

#### 完整备份

```bash
# 备份所有数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --all-databases > backup_all_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --single-transaction \
  --all-databases | gzip > backup_all_$(date +%Y%m%d).sql.gz
```

#### 单库备份

```bash
# 备份业务数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --single-transaction \
  manage > backup_manage_$(date +%Y%m%d).sql

# 备份 CMDB 数据库
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --single-transaction \
  cmdb > backup_cmdb_$(date +%Y%m%d).sql
```

#### 仅备份表结构

```bash
# 备份表结构（不含数据）
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --no-data \
  --all-databases > backup_schema_$(date +%Y%m%d).sql
```

### 物理备份

#### 文件系统快照

```bash
# 停止数据库
docker-compose stop mysql

# 复制数据目录
cp -r ${DATA_DIR}/mysql ${DATA_DIR}/backup/mysql_$(date +%Y%m%d)

# 重启数据库
docker-compose start mysql
```

#### 使用 tar 打包

```bash
# 停止数据库
docker-compose stop mysql

# 打包数据目录
tar czf mysql_backup_$(date +%Y%m%d).tar.gz -C ${DATA_DIR} mysql

# 重启数据库
docker-compose start mysql
```

---

## 自动备份脚本

### 完整备份脚本

创建 `backup.sh`：

```bash
#!/bin/bash

# 配置
BACKUP_DIR="/data/backup"
DATA_DIR="/data/teligen-ui"
RETENTION_DAYS=7

# 读取密码
source .env
DATABASE_PASSWORD=${DATABASE_PASSWORD}

# 创建备份目录
mkdir -p ${BACKUP_DIR}

# 备份日期
DATE=$(date +%Y%m%d_%H%M%S)

# 1. 数据库逻辑备份
echo "开始备份数据库..."
docker exec mysql mysqldump -uroot -p${DATABASE_PASSWORD} \
  --single-transaction \
  --routines \
  --triggers \
  --events \
  --all-databases | gzip > ${BACKUP_DIR}/database_${DATE}.sql.gz

# 2. 配置文件备份
echo "备份配置文件..."
tar czf ${BACKUP_DIR}/config_${DATE}.tar.gz \
  .env \
  nginx/ \
  etc/

# 3. 日志备份（最近7天）
echo "备份日志文件..."
find ./logs -name "*.log" -mtime -7 -exec tar rvf ${BACKUP_DIR}/logs_${DATE}.tar {} \;

# 4. 清理旧备份
echo "清理 ${RETENTION_DAYS} 天前的备份..."
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "备份完成: ${BACKUP_DIR}/database_${DATE}.sql.gz"
```

### 设置定时任务

```bash
# 1. 赋予执行权限
chmod +x backup.sh

# 2. 测试运行
./backup.sh

# 3. 添加到 crontab（每天凌晨 2 点执行）
crontab -e

# 添加以下行
0 2 * * * cd /usr/teligen-ui/teligen-ui && ./backup.sh >> ./logs/backup.log 2>&1
```

---

## 恢复流程

### 恢复数据库

#### 从逻辑备份恢复

```bash
# 1. 解压备份文件（如果是压缩的）
gunzip backup_all_20250128.sql.gz

# 2. 停止应用服务
docker-compose stop service celery celery-beat

# 3. 恢复数据库
docker exec -i mysql mysql -uroot -p${DATABASE_PASSWORD} < backup_all_20250128.sql

# 4. 重启服务
docker-compose start service celery celery-beat
```

#### 恢复单个数据库

```bash
# 恢复 CMDB 数据库
docker exec -i mysql mysql -uroot -p${DATABASE_PASSWORD} cmdb < backup_cmdb_20250128.sql
```

### 恢复配置文件

```bash
# 1. 停止所有服务
docker-compose down

# 2. 恢复配置
tar xzf config_20250128.tar.gz -C /

# 3. 启动服务
docker-compose up -d
```

### 恢复物理备份

```bash
# 1. 停止数据库
docker-compose stop mysql

# 2. 备份当前数据（以防万一）
mv ${DATA_DIR}/mysql ${DATA_DIR}/mysql.failed

# 3. 恢复数据
tar xzf mysql_backup_20250128.tar.gz -C ${DATA_DIR}

# 4. 启动数据库
docker-compose start mysql
```

---

## 灾难恢复

### 场景一：数据损坏

**症状**：数据库无法启动，表损坏

```bash
# 1. 停止数据库
docker-compose stop mysql

# 2. 查看错误日志
docker logs mysql --tail 100

# 3. 尝试修复
docker-compose start mysql
docker exec mysql mysqlcheck -uroot -p --repair --all-databases

# 4. 如果无法修复，从备份恢复
docker exec -i mysql mysql -uroot -p < backup_all_latest.sql.gz
```

### 场景二：误删除数据

**症状**：用户误删除重要数据

```bash
# 1. 立即停止应用服务（防止继续写入）
docker-compose stop service

# 2. 确定需要恢复的时间点
# 查看最近的备份
ls -lt ${BACKUP_DIR}/database_*.sql.gz

# 3. 恢复到指定时间点的备份
gunzip -c backup_all_20250128_020000.sql.gz | \
  docker exec -i mysql mysql -uroot -p

# 4. 重启服务
docker-compose start service
```

### 场景三：完全重建

**症状**：服务器宕机，需要在新服务器重建

```bash
# 1. 在新服务器安装 Docker 和 Docker Compose

# 2. 上传部署包和备份文件
scp teligen-ui.tar.gz root@new-server:/opt/
scp -r /data/backup root@new-server:/data/

# 3. 解压部署包
cd /opt
tar xzf teligen-ui.tar.gz
cd teligen-ui

# 4. 复制配置文件
tar xzf /data/backup/config_latest.tar.gz

# 5. 启动服务
docker-compose up -d db redis
sleep 30
docker-compose up -d

# 6. 恢复数据库
docker exec -i mysql mysql -uroot -p${DATABASE_PASSWORD} < \
  /data/backup/database_latest.sql.gz

# 7. 重启所有服务
docker-compose restart
```

---

## 数据安全建议

### 1. 3-2-1 备份原则

```
3 份备份（1 份原始 + 2 份备份）
2 种不同介质（本地磁盘 + 远程存储）
1 份异地备份（防止灾难性故障）
```

### 2. 备份验证

```bash
# 定期测试备份恢复（建议每月一次）
# 1. 恢复到测试环境
# 2. 验证数据完整性
# 3. 确认备份文件可用
```

### 3. 异地备份

```bash
# 使用 rsync 同步到远程服务器
rsync -avz --delete \
  /data/backup/ \
  backup-server:/remote-backup/teligen-ui/

# 或使用 scp 定期上传
scp backup_all_$(date +%Y%m%d).sql.gz \
  user@backup-server:/remote-backup/
```

### 4. 加密敏感备份

```bash
# 加密备份文件
gzip backup_all_20250128.sql
openssl enc -aes-256-cbc -salt -in backup_all_20250128.sql.gz \
  -out backup_all_20250128.sql.gz.enc

# 解密备份文件
openssl enc -aes-256-cbc -d -in backup_all_20250128.sql.gz.enc \
  -out backup_all_20250128.sql.gz
```

---

## 监控备份状态

### 备份检查脚本

```bash
#!/bin/bash

# 检查备份是否存在且可恢复

BACKUP_DIR="/data/backup"
ALERT_EMAIL="admin@example.com"

# 检查最新备份
LATEST_BACKUP=$(ls -t ${BACKUP_DIR}/database_*.sql.gz | head -1)

if [ -z "$LATEST_BACKUP" ]; then
  echo "警告：没有找到备份文件！" | mail -s "备份失败" $ALERT_EMAIL
  exit 1
fi

# 检查备份文件大小
SIZE=$(stat -f%z "$LATEST_BACKUP" 2>/dev/null || stat -c%s "$LATEST_BACKUP")
if [ $SIZE -lt 1000 ]; then
  echo "警告：备份文件过小 ($SIZE bytes)" | mail -s "备份异常" $ALERT_EMAIL
  exit 1
fi

# 测试备份可解压
if ! gunzip -t "$LATEST_BACKUP" 2>/dev/null; then
  echo "警告：备份文件损坏" | mail -s "备份损坏" $ALERT_EMAIL
  exit 1
fi

echo "备份检查完成：$LATEST_BACKUP ($SIZE bytes)"
```

---

## 常见问题

### Q: 数据库数据会丢失吗？

A: 可能导致数据丢失的场景：
- **硬件故障**：磁盘损坏 → 通过备份恢复
- **误操作**：DROP TABLE、DELETE → 从备份恢复
- **容器删除**：docker-compose down -v → **数据永久丢失**

::: danger 重要
永远不要使用 `docker-compose down -v`，这会删除所有数据卷！
:::

### Q: 如何避免数据丢失？

A:
1. **定期备份**：每天自动备份数据库
2. **异地备份**：备份文件同步到远程服务器
3. **测试恢复**：定期验证备份可用性
4. **监控告警**：备份失败时及时通知
5. **权限控制**：限制数据库操作权限

### Q: Redis 数据需要备份吗？

A: 一般不需要。Redis 数据是缓存，可以从数据库重建。如果需要持久化：
- 启用 Redis AOF 模式
- 定期保存 `${DATA_DIR}/redis-data/`

### Q: 备份文件保留多久？

A: 建议策略：
- **每日备份**：保留 7 天
- **每周备份**：保留 4 周
- **每月备份**：保留 12 个月
