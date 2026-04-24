# 工作日志

## 2026-04-25

- **变更摘要**：为 CMDB 模块补全完整测试套件（132 个测试全部通过）
  - `django/vuedjango/test_settings.py`：新建测试配置，SQLite 内存数据库 + 禁用 cacheops/Redis
  - `django/cmdb/tests/__init__.py`：重写为 `CmdbAPITestCase` 基类，封装认证/权限 mock + 8 个信号断开
  - `django/cmdb/tests/test_model_groups.py`：新建，14 个测试覆盖 ModelGroups CRUD + 权限 + 过滤
  - `django/cmdb/tests/test_model_field_groups.py`：新建，12 个测试覆盖 ModelFieldGroups
  - `django/cmdb/tests/test_validation_rules.py`：新建，14 个测试覆盖 ValidationRules + 枚举规则
  - `django/cmdb/tests/test_unique_constraint.py`：新建，10 个测试覆盖 UniqueConstraint
  - `django/cmdb/tests/test_model_instance.py`：新建，18 个测试覆盖 ModelInstance CRUD + 批量操作 + 导出
  - `django/cmdb/tests/test_model_instance_group.py`：新建，14 个测试覆盖树形分组 + 关联关系
  - `django/cmdb/tests/test_relation.py`：新建，11 个测试覆盖 RelationDefinition + Relations
  - `django/cmdb/tests/test_serializers.py`：新建，15 个测试覆盖 Serializer 级别验证逻辑
  - `django/cmdb/tests/test_models.py`：修复数据模型（去除不存在的 type 字段，添加 verbose_name）
  - `django/cmdb/tests/test_model_fields.py`：修复 create/delete 测试数据
  - `CLAUDE.md`：更新开发注意事项，添加 CMDB 测试运行说明

## 2026-04-24

- **变更摘要**：添加API参考手册、知识发现协议和Fork开发规范
  - `docs/api-reference.md`：渐进式API参考手册（三层：模块总览→接口列表→请求/响应详情），覆盖132个接口
  - `docs/openapi-schema.json`：OpenAPI 3 完整 Schema 导出（可通过 `python manage.py spectacular` 重新生成）
  - `CLAUDE.md`：增加知识发现协议章节（定义AI查阅优先级：API手册→在线文档→Schema→源码）
  - `CLAUDE.md`：增加 Fork 开发工作流规范（分支策略、upstream同步流程）
  - `.gitattributes`：统一换行符配置（.sh/.py 强制 LF）
  - `.gitignore`：排除 openapi-schema.json

- **环境配置**：使用 conda 创建 django37 环境（Python 3.7.16），安装项目依赖，验证 spectacular 命令可用

- **PR**：#30 已合并到 upstream（Mmmai/hz-manage）
