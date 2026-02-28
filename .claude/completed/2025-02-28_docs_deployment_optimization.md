# 2025-02-28 文档部署优化 - 完成总结

## 完成内容

### 1. 安装部署文档拆分重构

将原本冗长的 `install.md` 拆分为结构化的多文件文档体系：

**新建目录结构**：
```
docs/manage/install/
├── README.md              # 安装概述、快速开始
├── docker-compose.md      # Docker Compose 原理、架构
├── env-config.md          # 环境变量配置详解
├── services.md            # 6个服务的配置说明
├── deployment.md          # 完整部署步骤
├── backup.md              # 备份与恢复（新增）
└── operations.md          # 运维管理
```

### 2. 备份恢复文档（新增）

创建了 `install/backup.md`，包含：

- **重要数据识别**：明确哪些数据必须备份（数据库、日志、配置）
- **备份策略**：
  - 逻辑备份（mysqldump）
  - 物理备份（文件系统快照）
  - 自动备份脚本（完整 shell 脚本 + crontab 配置）
- **恢复流程**：数据库恢复、配置恢复、物理备份恢复
- **灾难恢复**：三种典型场景的恢复方案
  - 数据损坏场景
  - 误删除场景
  - 完全重建场景
- **数据安全建议**：
  - 3-2-1 备份原则
  - 备份验证
  - 异地备份
  - 加密敏感备份
- **常见问题**：强调 `docker-compose down -v` 的危险性

### 3. 侧边栏结构优化

- 将"安装部署"和"安装文档"合并为**"部署运维"**可折叠菜单
- 按逻辑顺序组织子文档：
  1. 快速开始
  2. Docker Compose 原理
  3. 环境变量配置
  4. 服务配置说明
  5. 部署步骤
  6. 备份与恢复 ← 新增
  7. 运维管理

### 4. 其他优化

- 删除旧的 `install.md` 和 `basic/` 目录
- 将原有 rbac.md 和 menu.md 内容优化后合并到 `guide/system/`

## 关键决策

### 为什么拆分文档？

原 `install.md` 文件过长（约500行），包含：
- Docker Compose 原理
- 环境变量说明
- 服务配置详解
- 部署步骤
- 运维命令

拆分后：
- 每个文件职责单一，便于查阅
- 支持侧边栏独立导航
- 便于后续维护更新

### 为什么强调备份？

生产环境中，数据丢失是灾难性风险：
- **数据库数据**是核心资产（CMDB、用户、业务数据）
- **配置文件**决定系统行为
- **日志**用于审计和故障排查

文档中明确警告：
::: danger 重要
永远不要使用 `docker-compose down -v`，这会删除所有数据卷！
:::

## 遗留问题

1. **备份脚本测试**：自动备份脚本未在真实环境测试
2. **监控告警**：备份检查脚本需要配置邮件或告警通道
3. **异地同步**：rsync/scp 配置需要根据实际环境调整

## 后续建议

1. **补充截图**：为部署步骤添加实际操作截图
2. **视频教程**：录制快速开始视频教程
3. **FAQ 扩充**：根据实际使用反馈补充常见问题
4. **多语言支持**：考虑提供英文版文档

## 文件变更清单

**新增文件**：
- `docs/manage/install/README.md`
- `docs/manage/install/docker-compose.md`
- `docs/manage/install/env-config.md`
- `docs/manage/install/services.md`
- `docs/manage/install/deployment.md`
- `docs/manage/install/operations.md`
- `docs/manage/install/backup.md`
- `docs/manage/guide/system/rbac.md`（优化合并）
- `docs/manage/guide/system/menu.md`（优化合并）
- `docs/manage/guide/home.md`
- `docs/manage/guide/favorites.md`
- `docs/manage/guide/cmdb/*.md`（6个文件）
- `docs/manage/guide/node/*.md`（2个文件）
- `docs/manage/guide/job/*.md`（1个文件）
- `docs/manage/guide/log/*.md`（3个文件）

**删除文件**：
- `docs/manage/install.md`
- `docs/manage/basic/`（整个目录）
- `docs/manage/guide/system/role.md`

**修改文件**：
- `docs/.vuepress/sidebar.ts`
- `docs/manage/README.md`（概览页面）
- `docs/manage/deploy.md`
- `docs/manage/api.md`
- `docs/manage/version.md`

## 影响范围

- **文档访问**：侧边栏导航结构变化
- **用户体验**：文档查找更便捷
- **维护成本**：模块化后更易于维护
