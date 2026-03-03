# CMDB 模块 API 文档完善任务

## Part 1: 已完成的工作（需要 commit）

### 自定义 Action Schema 补充

已为 10 个自定义 action 添加了 drf-spectacular Schema 定义：

| ViewSet | Action | 方法 | 功能 |
|---------|--------|------|------|
| `ModelGroupsViewSet` | `rename_instances` | POST | 批量重命名模型实例 |
| `ModelGroupsViewSet` | `rename_status` | GET | 查看重命名任务状态 |
| `ModelFieldsViewSet` | `bulk_update_fields` | PATCH | 批量更新实例字段 |
| `ModelInstanceViewSet` | `import_status_sse` | GET | SSE 实时导入状态 |
| `ModelInstanceViewSet` | `quick_search` | GET | 快速搜索实例 |
| `ModelInstanceViewSet` | `tree` | GET | 获取实例分组树 |
| `ModelInstanceGroupRelationViewSet` | `bulk_associate` | POST | 批量创建多对一/一对多关联 |
| `ModelInstanceGroupRelationViewSet` | `bulk_create` | POST | 批量创建关联关系 |
| `ModelInstanceGroupRelationViewSet` | `bulk_delete` | POST | 批量删除关联关系 |
| `RelationsViewSet` | `get_topology` | POST | 获取实例关系拓扑图 |

**修改文件**：`/opt/workpool/hz-manage-api-docs/django/cmdb/schemas.py`

**后续操作**：
1. 将计划文件移至 `.claude/plans_archive/`
2. 创建执行总结至 `.claude/completed/`
3. Git commit 并 push

---

## Part 2: 新任务 - 标准 CRUD 方法描述显示问题

### Context

Swagger UI 中标准 CRUD 方法显示的是 **ViewSet 类的 docstring** 而不是 schemas.py 中定义的 `summary`。

**问题示例**：
- 接口：`POST /api/v1/cmdb/model_instance/`
- schemas.py 设置：`summary='创建模型实例'`
- 实际显示：`"实例视图集，用于管理模型实例的增删改查操作"`（ViewSet 类 docstring）

**原因分析**：
drf-spectacular 可能会使用 ViewSet 的 docstring 作为 `description`，需要为所有标准 CRUD 方法添加 `description` 参数来明确覆盖。

---

## Implementation Plan

### 修改文件

- **`/opt/workpool/hz-manage-api-docs/django/cmdb/schemas.py`**

### 解决方案

为所有标准 CRUD 方法添加 `description` 参数。

#### 修改模式

```python
# 修改前
create=extend_schema(
    summary='创建模型实例',
    tags=['实例管理'],
    # ...
)

# 修改后
create=extend_schema(
    summary='创建模型实例',
    description='创建模型实例，支持指定实例名称、字段值、分组等信息。',
    tags=['实例管理'],
    # ...
)
```

### 需要修改的 Schema 定义

1. `model_groups_schema` - 模型分组 CRUD
2. `models_schema` - 模型 CRUD
3. `model_field_groups_schema` - 字段分组 CRUD
4. `validation_rules_schema` - 校验规则 CRUD
5. `model_fields_schema` - 字段 CRUD
6. `model_field_preference_schema` - 字段展示 CRUD
7. `unique_constraint_schema` - 唯一约束 CRUD
8. `model_instance_schema` - 实例 CRUD
9. `model_ref_schema` - 模型引用 CRUD
10. `model_field_meta_schema` - 字段元数据 CRUD
11. `model_instance_group_schema` - 实例分组 CRUD
12. `model_instance_group_relation_schema` - 实例分组关联 CRUD
13. `relations_schema` - 关联 CRUD
14. `relation_definition_schema` - 引用定义 CRUD
15. `password_manage_schema` - 密码管理 actions

---

## Verification

1. **重启服务**清除缓存
2. **访问** `/api/docs/` 检查所有接口的描述
3. **确认**显示的是 `description` 而非 ViewSet docstring
