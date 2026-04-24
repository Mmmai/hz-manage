# API 参考手册

> 由 DRF Spectacular 自动导出，供 AI 快速理解项目接口。
> 完整 Schema 见 `docs/openapi-schema.json`，在线文档见 `/api/docs/`。

## 模块总览

| 模块 | 说明 | 接口数 |
|------|------|--------|
| mapi | 用户/组/角色/门户/数据源 | 42 |
| cmdb | 模型/字段/实例/引用/密码/缓存 | 83 |
| node_mg | 节点/代理/任务 | 24 |
| access | 菜单/按钮/权限/数据权限 | 22 |
| audit | 审计日志 | 2 |
| monitor | Zabbix 监控数据 | 0 |

## mapi — 用户/组/角色/门户/数据源

### 数据源管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/datasource/` | 获取数据源列表 |
| POST | `/api/v1/datasource/` | 创建数据源 |
| GET | `/api/v1/datasource/{id}/` | 获取数据源详情 |
| PUT | `/api/v1/datasource/{id}/` | 更新数据源 |
| DELETE | `/api/v1/datasource/{id}/` | 删除数据源 |
| GET | `/api/v1/sysconfig/` | 获取系统配置列表 |
| POST | `/api/v1/sysconfig/` | 创建系统配置 |
| GET | `/api/v1/sysconfig/{id}/` | 获取系统配置详情 |
| PUT | `/api/v1/sysconfig/{id}/` | 更新系统配置 |
| DELETE | `/api/v1/sysconfig/{id}/` | 删除系统配置 |

### 用户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/login/` | 用户登录 |
| GET | `/api/v1/userinfo/` | 获取用户列表 |
| POST | `/api/v1/userinfo/` | 创建用户 |
| GET | `/api/v1/userinfo/{id}/` | 获取用户详情 |
| PUT | `/api/v1/userinfo/{id}/` | 更新用户 |
| DELETE | `/api/v1/userinfo/{id}/` | 删除用户 |
| DELETE | `/api/v1/userinfo/multiple_delete/` | 批量删除用户 |

### 门户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/pgroup/` | 获取门户分组列表 |
| POST | `/api/v1/pgroup/` | 创建门户分组 |
| GET | `/api/v1/pgroup/{id}/` | 获取门户分组详情 |
| PUT | `/api/v1/pgroup/{id}/` | 更新门户分组 |
| DELETE | `/api/v1/pgroup/{id}/` | 删除门户分组 |
| GET | `/api/v1/portal/` | 获取门户列表 |
| POST | `/api/v1/portal/` | 创建门户 |
| GET | `/api/v1/portal/{id}/` | 获取门户详情 |
| PUT | `/api/v1/portal/{id}/` | 更新门户 |
| DELETE | `/api/v1/portal/{id}/` | 删除门户 |
| DELETE | `/api/v1/portal/multiple_delete/` | 批量删除门户 |
| GET | `/api/v1/portal_favorites/` | 获取门户收藏列表 |
| POST | `/api/v1/portal_favorites/` | 添加门户收藏 |
| GET | `/api/v1/portal_favorites/{id}/` | 获取门户收藏详情 |
| DELETE | `/api/v1/portal_favorites/{id}/` | 删除门户收藏 |

### 角色管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/role/` | 获取角色列表 |
| POST | `/api/v1/role/` | 创建角色 |
| GET | `/api/v1/role/{id}/` | 获取角色详情 |
| PUT | `/api/v1/role/{id}/` | 更新角色 |
| DELETE | `/api/v1/role/{id}/` | 删除角色 |

### 用户组管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/userGroup/` | 获取用户组列表 |
| POST | `/api/v1/userGroup/` | 创建用户组 |
| GET | `/api/v1/userGroup/{id}/` | 获取用户组详情 |
| PUT | `/api/v1/userGroup/{id}/` | 更新用户组 |
| DELETE | `/api/v1/userGroup/{id}/` | 删除用户组 |


## cmdb — 模型/字段/实例/引用/密码/缓存

### 字段分组管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_field_groups/` | 获取字段分组列表 |
| POST | `/api/v1/cmdb/model_field_groups/` | 创建字段分组 |
| GET | `/api/v1/cmdb/model_field_groups/{id}/` | 获取字段分组详情 |
| PUT | `/api/v1/cmdb/model_field_groups/{id}/` | 更新字段分组 |
| PATCH | `/api/v1/cmdb/model_field_groups/{id}/` | 部分更新字段分组 |
| DELETE | `/api/v1/cmdb/model_field_groups/{id}/` | 删除字段分组 |

### 字段展示管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_field_preference/` | 获取字段展示配置列表 |
| POST | `/api/v1/cmdb/model_field_preference/` | 创建字段展示配置 |
| GET | `/api/v1/cmdb/model_field_preference/{id}/` | 获取字段展示配置详情 |
| PUT | `/api/v1/cmdb/model_field_preference/{id}/` | 更新字段展示配置 |
| PATCH | `/api/v1/cmdb/model_field_preference/{id}/` | 部分更新字段展示配置 |
| DELETE | `/api/v1/cmdb/model_field_preference/{id}/` | 删除字段展示配置 |

### 字段管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_fields/` | 获取字段列表 |
| POST | `/api/v1/cmdb/model_fields/` | 创建字段 |
| GET | `/api/v1/cmdb/model_fields/{id}/` | 获取字段详情 |
| PUT | `/api/v1/cmdb/model_fields/{id}/` | 更新字段 |
| PATCH | `/api/v1/cmdb/model_fields/{id}/` | 部分更新字段 |
| DELETE | `/api/v1/cmdb/model_fields/{id}/` | 删除字段 |
| GET | `/api/v1/cmdb/model_fields/metadata/` | 获取字段配置选项 |

### 模型分组管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_groups/` | 获取模型分组列表 |
| POST | `/api/v1/cmdb/model_groups/` | 创建模型分组 |
| GET | `/api/v1/cmdb/model_groups/{id}/` | 获取模型分组详情 |
| PUT | `/api/v1/cmdb/model_groups/{id}/` | 更新模型分组 |
| PATCH | `/api/v1/cmdb/model_groups/{id}/` | 部分更新模型分组 |
| DELETE | `/api/v1/cmdb/model_groups/{id}/` | 删除模型分组 |

### 实例管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_instance/` | 获取模型实例列表 |
| POST | `/api/v1/cmdb/model_instance/` | 创建模型实例 |
| GET | `/api/v1/cmdb/model_instance/{id}/` | 获取模型实例详情 |
| PUT | `/api/v1/cmdb/model_instance/{id}/` | 更新模型实例 |
| PATCH | `/api/v1/cmdb/model_instance/{id}/` | 部分更新模型实例 |
| DELETE | `/api/v1/cmdb/model_instance/{id}/` | 删除模型实例 |
| POST | `/api/v1/cmdb/model_instance/bulk_delete/` | 批量删除模型实例 |
| PATCH | `/api/v1/cmdb/model_instance/bulk_update_fields/` | 批量更新模型实例字段 |
| POST | `/api/v1/cmdb/model_instance/download_error_records/` | 下载导入错误记录 |
| POST | `/api/v1/cmdb/model_instance/export_data/` | 导出模型实例数据 |
| POST | `/api/v1/cmdb/model_instance/export_template/` | 导出模型实例模板 |
| POST | `/api/v1/cmdb/model_instance/import_data/` | 导入模型实例数据 |
| GET | `/api/v1/cmdb/model_instance/import_status/` | 获取导入状态 |
| GET | `/api/v1/cmdb/model_instance/import_status_sse/` | 实时获取导入状态(SSE) |
| GET | `/api/v1/cmdb/model_instance/quick_search/` | 快速搜索实例 |
| GET | `/api/v1/cmdb/relations/` | 获取关联列表 |
| POST | `/api/v1/cmdb/relations/` | 创建关联 |
| GET | `/api/v1/cmdb/relations/{id}/` | 获取关联详情 |
| DELETE | `/api/v1/cmdb/relations/{id}/` | 删除关联 |
| POST | `/api/v1/cmdb/relations/get_topology/` | 获取实例关系拓扑图 |

### 实例分组管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_instance_group/` | 获取实例分组树 |
| POST | `/api/v1/cmdb/model_instance_group/` | 创建实例分组 |
| GET | `/api/v1/cmdb/model_instance_group/{id}/` | 获取实例分组详情 |
| PUT | `/api/v1/cmdb/model_instance_group/{id}/` | 更新实例分组 |
| PATCH | `/api/v1/cmdb/model_instance_group/{id}/` | 部分更新实例分组 |
| DELETE | `/api/v1/cmdb/model_instance_group/{id}/` | 删除实例分组 |

### 实例分组关联管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_instance_group_relation/` | 获取实例与分组的关联列表 |
| POST | `/api/v1/cmdb/model_instance_group_relation/` | 创建实例与分组的关联 |
| GET | `/api/v1/cmdb/model_instance_group_relation/{id}/` | 获取实例与分组的关联 |
| POST | `/api/v1/cmdb/model_instance_group_relation/create_relations/` | 批量创建实例与分组的关联 |

### 模型引用管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/model_ref/` | 获取模型关联列表 |
| GET | `/api/v1/cmdb/model_ref/{id}/` | 获取模型关联详情 |
| GET | `/api/v1/cmdb/relation_definition/` | 获取模型引用定义列表 |
| POST | `/api/v1/cmdb/relation_definition/` | 创建模型引用定义 |
| GET | `/api/v1/cmdb/relation_definition/{id}/` | 获取模型引用定义详情 |
| PUT | `/api/v1/cmdb/relation_definition/{id}/` | 更新模型引用定义 |
| DELETE | `/api/v1/cmdb/relation_definition/{id}/` | 删除模型引用定义 |

### 模型管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/models/` | 获取模型列表 |
| POST | `/api/v1/cmdb/models/` | 创建模型 |
| GET | `/api/v1/cmdb/models/{id}/` | 获取模型详情 |
| PUT | `/api/v1/cmdb/models/{id}/` | 更新模型 |
| PATCH | `/api/v1/cmdb/models/{id}/` | 部分更新模型 |
| DELETE | `/api/v1/cmdb/models/{id}/` | 删除模型 |

### 密码及密钥管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/cmdb/password_manage/re_encrypt/` | 重新加密密码 |
| POST | `/api/v1/cmdb/password_manage/reset_passwords/` | 重置密码 |

### 通用说明

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/cmdb/system_cache/clear_cache/` | 清理系统缓存 |

### 实例唯一性约束管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/unique_constraint/` | 获取唯一约束列表 |
| POST | `/api/v1/cmdb/unique_constraint/` | 创建唯一约束 |
| GET | `/api/v1/cmdb/unique_constraint/{id}/` | 获取唯一约束详情 |
| PUT | `/api/v1/cmdb/unique_constraint/{id}/` | 更新唯一约束 |
| PATCH | `/api/v1/cmdb/unique_constraint/{id}/` | 部分更新唯一约束 |
| DELETE | `/api/v1/cmdb/unique_constraint/{id}/` | 删除唯一约束 |

### 字段校验规则管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/cmdb/validation_rules/` | 获取校验规则列表 |
| POST | `/api/v1/cmdb/validation_rules/` | 创建字段校验规则 |
| GET | `/api/v1/cmdb/validation_rules/{id}/` | 获取校验规则详情 |
| PUT | `/api/v1/cmdb/validation_rules/{id}/` | 更新校验规则 |
| PATCH | `/api/v1/cmdb/validation_rules/{id}/` | 部分更新校验规则 |
| DELETE | `/api/v1/cmdb/validation_rules/{id}/` | 删除校验规则 |


## node_mg — 节点/代理/任务

### 节点管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/node_mg/modelConfig/` | 获取模型配置列表 |
| POST | `/api/v1/node_mg/modelConfig/` | 创建模型配置 |
| GET | `/api/v1/node_mg/modelConfig/{id}/` | 获取模型配置详情 |
| PUT | `/api/v1/node_mg/modelConfig/{id}/` | 更新模型配置 |
| DELETE | `/api/v1/node_mg/modelConfig/{id}/` | 删除模型配置 |
| GET | `/api/v1/node_mg/nodes/` | 获取节点列表 |
| POST | `/api/v1/node_mg/nodes/` | 创建节点 |
| GET | `/api/v1/node_mg/nodes/{id}/` | 获取节点详情 |
| PUT | `/api/v1/node_mg/nodes/{id}/` | 更新节点 |
| DELETE | `/api/v1/node_mg/nodes/{id}/` | 删除节点 |
| POST | `/api/v1/node_mg/nodes/associate_proxy/` | 关联代理 |
| POST | `/api/v1/node_mg/nodes/dissociate_proxy/` | 解除代理关联 |
| GET | `/api/v1/node_mg/nodes/get_info_by_instance/` | 根据实例ID获取节点信息 |
| POST | `/api/v1/node_mg/nodes/get_inventory/` | 获取资产信息 |
| POST | `/api/v1/node_mg/nodes/install_agent/` | 安装Agent |
| GET | `/api/v1/node_mg/nodes/list_all_nodes/` | 获取所有节点（不分页） |
| POST | `/api/v1/node_mg/nodes/sync_zabbix/` | 同步到Zabbix |

### 节点任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/node_mg/nodeTask/` | 获取节点任务列表 |
| GET | `/api/v1/node_mg/nodeTask/{id}/` | 获取节点任务详情 |

### 代理管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/node_mg/proxy/` | 获取代理列表 |
| POST | `/api/v1/node_mg/proxy/` | 创建代理 |
| GET | `/api/v1/node_mg/proxy/{id}/` | 获取代理详情 |
| PUT | `/api/v1/node_mg/proxy/{id}/` | 更新代理 |
| DELETE | `/api/v1/node_mg/proxy/{id}/` | 删除代理 |


## access — 菜单/按钮/权限/数据权限

### 菜单管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/access/button/` | 获取按钮列表 |
| POST | `/api/v1/access/button/` | 创建按钮 |
| GET | `/api/v1/access/button/{id}/` | 获取按钮详情 |
| PUT | `/api/v1/access/button/{id}/` | 更新按钮 |
| DELETE | `/api/v1/access/button/{id}/` | 删除按钮 |
| GET | `/api/v1/access/menu/` | 获取菜单列表 |
| POST | `/api/v1/access/menu/` | 创建菜单 |
| GET | `/api/v1/access/menu/{id}/` | 获取菜单详情 |
| PUT | `/api/v1/access/menu/{id}/` | 更新菜单 |
| DELETE | `/api/v1/access/menu/{id}/` | 删除菜单 |

### 数据权限

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/access/data_scope/` | 获取数据权限列表 |
| POST | `/api/v1/access/data_scope/` | 创建数据权限 |
| GET | `/api/v1/access/data_scope/{id}/` | 获取数据权限详情 |
| PUT | `/api/v1/access/data_scope/{id}/` | 更新数据权限 |
| DELETE | `/api/v1/access/data_scope/{id}/` | 删除数据权限 |
| GET | `/api/v1/access/data_scope/aggregated_permissions/` | 获取聚合权限 |
| GET | `/api/v1/access/data_scope/check-permission/` | 检查权限 |

### 权限管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/access/permission/` | 获取权限列表 |
| POST | `/api/v1/access/permission/` | 创建权限 |
| GET | `/api/v1/access/permission/{id}/` | 获取权限详情 |
| PUT | `/api/v1/access/permission/{id}/` | 更新权限 |
| DELETE | `/api/v1/access/permission/{id}/` | 删除权限 |


## audit — 审计日志

### 审计日志

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/audit/logs/` | 获取审计日志列表 |
| GET | `/api/v1/audit/logs/{id}/` | 获取审计日志详情 |


---

## 接口详情

> 以下为各接口的请求参数和响应结构。

### GET /api/v1/datasource/

获取数据源列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/datasource/

创建数据源

**请求体** (`application/json`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**响应** (`201`):
```
- **id** (string) 
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

---

### GET /api/v1/datasource/{id}/

获取数据源详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 数据源. |

**响应** (`200`):
```
- **id** (string) 
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

---

### PUT /api/v1/datasource/{id}/

更新数据源

**请求体** (`application/json`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 数据源. |

**响应** (`200`):
```
- **id** (string) 
- **source_name** (string) 
- **source_type** (string) 
- **username** (string) 
- **password** (string) 
- **url** (string) 
- **isUsed** (boolean) 
- **state** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
- **isAuth** (boolean) 
- **isDefault** (boolean) 
```

---

### DELETE /api/v1/datasource/{id}/

删除数据源

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 数据源. |

---

### GET /api/v1/sysconfig/

获取系统配置列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| param_name | query | string | 否 |  |
| param_value | query | string | 否 |  |

**响应** (`200`):
```
Array<- **id** (string) 
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) >
```

---

### POST /api/v1/sysconfig/

创建系统配置

**请求体** (`application/json`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**请求体** (`multipart/form-data`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

---

### GET /api/v1/sysconfig/{id}/

获取系统配置详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 系统参数配置表. |

**响应** (`200`):
```
- **id** (string) 
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

---

### PUT /api/v1/sysconfig/{id}/

更新系统配置

**请求体** (`application/json`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**请求体** (`multipart/form-data`):
```
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 系统参数配置表. |

**响应** (`200`):
```
- **id** (string) 
- **verbose_name** (string) 
- **system** (string) 
- **param_name** (string) 
- **param_value** (string) 
- **param_type** (string) * `string` - 字符串
* `int` - 整数
* `float` - 小数
- **description** (string) 
```

---

### DELETE /api/v1/sysconfig/{id}/

删除系统配置

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 系统参数配置表. |

---

### POST /api/v1/login/

用户登录

**请求体** (`application/json`):
```
- **username** (string) 用户名
- **password** (string) 密码
- **timeout** (integer) token超时时间(天)，默认3天
```

**响应** (`200`):
```
- **code** (integer) 
- **token** (string) JWT Token
- **userinfo** (object) 
- **permission** (array) 
```

---

### GET /api/v1/userinfo/

获取用户列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/userinfo/

创建用户

**请求体** (`application/json`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**请求体** (`multipart/form-data`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **roles** (array) 
- **groups** (array) 
- **username** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### GET /api/v1/userinfo/{id}/

获取用户详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户表. |

**响应** (`200`):
```
- **id** (string) 
- **roles** (array) 
- **groups** (array) 
- **username** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### PUT /api/v1/userinfo/{id}/

更新用户

**请求体** (`application/json`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**请求体** (`multipart/form-data`):
```
- **role_ids** (array) 
- **group_ids** (array) 
- **old_password** (string) 修改密码时需要提供旧密码
- **username** (string) 
- **password** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户表. |

**响应** (`200`):
```
- **id** (string) 
- **roles** (array) 
- **groups** (array) 
- **username** (string) 
- **password_salt** (string) 
- **real_name** (string) 
- **status** (boolean) 
- **built_in** (boolean) 
- **expire_time** (string) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### DELETE /api/v1/userinfo/{id}/

删除用户

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户表. |

---

### DELETE /api/v1/userinfo/multiple_delete/

批量删除用户

---

### GET /api/v1/pgroup/

获取门户分组列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/pgroup/

创建门户分组

**请求体** (`application/json`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**请求体** (`multipart/form-data`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**响应** (`201`):
```
- **id** (string) 
- **owner_name** (string) 
- **portals** (string) 
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### GET /api/v1/pgroup/{id}/

获取门户分组详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户分组表. |

**响应** (`200`):
```
- **id** (string) 
- **owner_name** (string) 
- **portals** (string) 
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### PUT /api/v1/pgroup/{id}/

更新门户分组

**请求体** (`application/json`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**请求体** (`multipart/form-data`):
```
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户分组表. |

**响应** (`200`):
```
- **id** (string) 
- **owner_name** (string) 
- **portals** (string) 
- **group** (string) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **sort_order** (integer) 
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### DELETE /api/v1/pgroup/{id}/

删除门户分组

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户分组表. |

---

### GET /api/v1/portal/

获取门户列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/portal/

创建门户

**请求体** (`application/json`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**请求体** (`multipart/form-data`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**响应** (`201`):
```
- **id** (string) 
- **groups** (array) 
- **is_favorite** (string) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### GET /api/v1/portal/{id}/

获取门户详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户表. |

**响应** (`200`):
```
- **id** (string) 
- **groups** (array) 
- **is_favorite** (string) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### PUT /api/v1/portal/{id}/

更新门户

**请求体** (`application/json`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**请求体** (`multipart/form-data`):
```
- **groups** (array) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户表. |

**响应** (`200`):
```
- **id** (string) 
- **groups** (array) 
- **is_favorite** (string) 
- **name** (string) 
- **url** (string) 
- **status** (boolean) 
- **username** (string) 
- **password** (string) 
- **target** (boolean) 
- **describe** (string) 
- **sort_order** (integer) 
- **sharing_type** (string) * `private` - 私人
* `public` - 公共
- **update_time** (string) 
- **create_time** (string) 
- **owner** (string) 
```

---

### DELETE /api/v1/portal/{id}/

删除门户

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 门户表. |

---

### DELETE /api/v1/portal/multiple_delete/

批量删除门户

---

### GET /api/v1/portal_favorites/

获取门户收藏列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/portal_favorites/

添加门户收藏

**请求体** (`application/json`):
```
- **portal** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **portal** (string) 
```

**请求体** (`multipart/form-data`):
```
- **portal** (string) 
```

**响应** (`201`):
```
- **id** (integer) 
- **portal** (string) 
- **create_time** (string) 
- **portal_info** (string) 
```

---

### GET /api/v1/portal_favorites/{id}/

获取门户收藏详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 |  |

**响应** (`200`):
```
- **id** (integer) 
- **portal** (string) 
- **create_time** (string) 
- **portal_info** (string) 
```

---

### DELETE /api/v1/portal_favorites/{id}/

删除门户收藏

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 |  |

---

### GET /api/v1/role/

获取角色列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| role | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/role/

创建角色

**请求体** (`application/json`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**响应** (`201`):
```
- **id** (string) 
- **user_count** (string) 
- **userGroup_count** (string) 
- **rolePermission** (string) 
- **associated_users** (string) 
- **associated_user_groups** (string) 
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### GET /api/v1/role/{id}/

获取角色详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 角色. |

**响应** (`200`):
```
- **id** (string) 
- **user_count** (string) 
- **userGroup_count** (string) 
- **rolePermission** (string) 
- **associated_users** (string) 
- **associated_user_groups** (string) 
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### PUT /api/v1/role/{id}/

更新角色

**请求体** (`application/json`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 角色. |

**响应** (`200`):
```
- **id** (string) 
- **user_count** (string) 
- **userGroup_count** (string) 
- **rolePermission** (string) 
- **associated_users** (string) 
- **associated_user_groups** (string) 
- **role** (string) 
- **role_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### DELETE /api/v1/role/{id}/

删除角色

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 角色. |

---

### GET /api/v1/userGroup/

获取用户组列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/userGroup/

创建用户组

**请求体** (`application/json`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**响应** (`201`):
```
- **id** (string) 
- **users** (array) 
- **roles** (array) 
- **user_count** (string) 
- **group_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### GET /api/v1/userGroup/{id}/

获取用户组详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户组表. |

**响应** (`200`):
```
- **id** (string) 
- **users** (array) 
- **roles** (array) 
- **user_count** (string) 
- **group_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### PUT /api/v1/userGroup/{id}/

更新用户组

**请求体** (`application/json`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**请求体** (`multipart/form-data`):
```
- **role_ids** (array) 
- **user_ids** (array) 
- **group_name** (string) 
- **built_in** (boolean) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户组表. |

**响应** (`200`):
```
- **id** (string) 
- **users** (array) 
- **roles** (array) 
- **user_count** (string) 
- **group_name** (string) 
- **built_in** (boolean) 
- **update_time** (string) 
- **create_time** (string) 
```

---

### DELETE /api/v1/userGroup/{id}/

删除用户组

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 用户组表. |

---

### GET /api/v1/cmdb/model_field_groups/

获取字段分组列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 | 根据是否内置字段分组查询 |
| description | query | string | 否 |  |
| editable | query | boolean | 否 |  |
| model | query | string | 否 | 根据模型ID查询 |
| name | query | string | 否 | 根据字段分组名称模糊查询 |
| verbose_name | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_field_groups/

创建字段分组

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 是 | 是否内置字段分组 |
| model | query | string | 是 | 所属模型ID |
| name | query | string | 是 | 字段分组名称 |
| order | query | integer | 否 | 排序 |
| verbose_name | query | string | 是 | 显示名称 |

**响应** (`201`):
```
- **id** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### GET /api/v1/cmdb/model_field_groups/{id}/

获取字段分组详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 字段分组ID |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### PUT /api/v1/cmdb/model_field_groups/{id}/

更新字段分组

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field groups. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PATCH /api/v1/cmdb/model_field_groups/{id}/

部分更新字段分组

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field groups. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### DELETE /api/v1/cmdb/model_field_groups/{id}/

删除字段分组

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field groups. |

---

### GET /api/v1/cmdb/model_field_preference/

获取字段展示配置列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| field | query | string | 否 | 根据字段ID查询 |
| model | query | string | 否 |  |
| user | query | string | 否 | 根据用户查询 |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_field_preference/

创建字段展示配置

**请求体** (`application/json`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| create_user | query | string | 是 | 创建用户 |
| fields_preferred | query | array | 是 | 字段ID |
| model | query | string | 是 | 模型ID |
| update_user | query | string | 是 | 更新用户 |

**响应** (`201`):
```
- **id** (string) 
- **fields_preferred** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### GET /api/v1/cmdb/model_field_preference/{id}/

获取字段展示配置详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 字段展示ID |

**响应** (`200`):
```
- **id** (string) 
- **fields_preferred** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### PUT /api/v1/cmdb/model_field_preference/{id}/

更新字段展示配置

**请求体** (`application/json`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field preference. |

**响应** (`200`):
```
- **id** (string) 
- **fields_preferred** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### PATCH /api/v1/cmdb/model_field_preference/{id}/

部分更新字段展示配置

**请求体** (`application/json`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields_preferred** (array) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field preference. |

**响应** (`200`):
```
- **id** (string) 
- **fields_preferred** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### DELETE /api/v1/cmdb/model_field_preference/{id}/

删除字段展示配置

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model field preference. |

---

### GET /api/v1/cmdb/model_fields/

获取字段列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 |  |
| description | query | string | 否 |  |
| editable | query | boolean | 否 |  |
| field_group | query | string | 否 | 根据字段分组ID查询 |
| field_type | query | string | 否 | 根据字段类型查询 |
| model | query | string | 否 | 根据模型ID查询 |
| model_field_group | query | string | 否 |  |
| name | query | string | 否 | 根据字段名称模糊查询 |
| order | query | integer | 否 |  |
| required | query | boolean | 否 |  |
| type | query | string | 否 |  |
| unit | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_fields/

创建字段

**请求体** (`application/json`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`multipart/form-data`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| create_user | query | string | 是 | 创建用户 |
| editable | query | boolean | 是 | 是否可编辑 |
| field_group | query | string | 否 | 所属字段分组ID |
| field_type | query | string | 是 | 字段类型 |
| model | query | string | 是 | 所属模型ID |
| name | query | string | 是 | 字段名称 |
| order | query | integer | 否 | 排序 |
| required | query | boolean | 是 | 是否必填 |
| update_user | query | string | 是 | 更新用户 |
| validation_rule | query | string | 否 | 校验规则ID |
| verbose_name | query | string | 是 | 显示名称 |

**响应** (`201`):
```
- **id** (string) 
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

---

### GET /api/v1/cmdb/model_fields/{id}/

获取字段详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 字段ID |

**响应** (`200`):
```
- **id** (string) 
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

---

### PUT /api/v1/cmdb/model_fields/{id}/

更新字段

**请求体** (`application/json`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`multipart/form-data`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model fields. |

**响应** (`200`):
```
- **id** (string) 
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

---

### PATCH /api/v1/cmdb/model_fields/{id}/

部分更新字段

**请求体** (`application/json`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**请求体** (`multipart/form-data`):
```
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model fields. |

**响应** (`200`):
```
- **id** (string) 
- **default** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **type** (string) 
- **unit** (string) 
- **built_in** (boolean) 
- **required** (boolean) 
- **editable** (boolean) 
- **description** (string) 
- **order** (integer) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_field_group** (string) 
- **ref_model** (string) 
- **validation_rule** (string) 
```

---

### DELETE /api/v1/cmdb/model_fields/{id}/

删除字段

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model fields. |

---

### GET /api/v1/cmdb/model_fields/metadata/

获取字段配置选项

**响应** (`200`):
```
object
```

---

### GET /api/v1/cmdb/model_groups/

获取模型分组列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 | 根据是否内置模型分组查询 |
| description | query | string | 否 | 根据模型分组描述模糊查询 |
| editable | query | boolean | 否 | 根据是否可编辑查询 |
| name | query | string | 否 | 根据模型分组名称模糊查询 |
| verbose_name | query | string | 否 | 根据显示名称模糊查询 |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_groups/

创建模型分组

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 是 | 是否内置模型分组 |
| create_user | query | string | 是 | 创建用户 |
| description | query | string | 否 | 模型分组描述 |
| editable | query | boolean | 是 | 是否可编辑 |
| name | query | string | 是 | 模型分组名称 |
| update_user | query | string | 是 | 更新用户 |
| verbose_name | query | string | 是 | 显示名称 |

**响应** (`201`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### GET /api/v1/cmdb/model_groups/{id}/

获取模型分组详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 模型分组ID |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PUT /api/v1/cmdb/model_groups/{id}/

更新模型分组

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model groups. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PATCH /api/v1/cmdb/model_groups/{id}/

部分更新模型分组

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model groups. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **editable** (boolean) 
- **verbose_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### DELETE /api/v1/cmdb/model_groups/{id}/

删除模型分组

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model groups. |

---

### GET /api/v1/cmdb/model_instance/

获取模型实例列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| field_query | query | object | 否 | 根据字段查询 |
| input_mode | query | string | 否 |  |
| instance_name | query | string | 否 | 根据实例名称模糊查询 |
| model | query | string | 否 | 根据模型ID查询 |
| model_instance_group | query | string | 否 | 根据实例分组ID查询 |
| page | query | integer | 否 | 页码 |
| page_size | query | integer | 否 | 每页数量 |
| using_template | query | boolean | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_instance/

创建模型实例

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| create_user | query | string | 是 | 创建用户 |
| fields | query | object | 是 | 字段键值对 |
| instance_group | query | array | 否 | 实例分组ID列表 |
| instance_name | query | string | 是 | 实例名称 |
| model | query | string | 是 | 模型ID |
| update_user | query | string | 是 | 更新用户 |

**响应** (`201`):
```
- **id** (string) 
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **field_values** (object) 
- **instance_group** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### GET /api/v1/cmdb/model_instance/{id}/

获取模型实例详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 实例ID |

**响应** (`200`):
```
- **id** (string) 
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **field_values** (object) 
- **instance_group** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PUT /api/v1/cmdb/model_instance/{id}/

更新模型实例

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| fields | query | object | 是 | 字段键值对 |
| id | path | string | 是 | A UUID string identifying this model instance. |
| instance_group | query | array | 否 | 实例分组ID列表 |
| instance_name | query | string | 是 | 实例名称 |
| model | query | string | 是 | 模型ID |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **id** (string) 
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **field_values** (object) 
- **instance_group** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PATCH /api/v1/cmdb/model_instance/{id}/

部分更新模型实例

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| fields | query | object | 是 | 字段键值对 |
| id | path | string | 是 | A UUID string identifying this model instance. |
| instance_group | query | array | 否 | 实例分组ID列表 |
| instance_name | query | string | 是 | 实例名称 |
| model | query | string | 是 | 模型ID |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **id** (string) 
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **field_values** (object) 
- **instance_group** (array) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### DELETE /api/v1/cmdb/model_instance/{id}/

删除模型实例

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model instance. |

---

### POST /api/v1/cmdb/model_instance/bulk_delete/

批量删除模型实例

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| instances | query | array | 是 | 实例ID列表 |

---

### PATCH /api/v1/cmdb/model_instance/bulk_update_fields/

批量更新模型实例字段

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| fields | query | object | 是 | 字段键值对 |
| instances | query | array | 是 | 实例ID列表 |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **status** (string) 更新结果
- **updated_instances_count** (integer) 更新实例数量
```

---

### POST /api/v1/cmdb/model_instance/download_error_records/

下载导入错误记录

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| cache_key | query | string | 是 | 错误记录文件ID |

**响应** (`200`):
```
string
```

---

### POST /api/v1/cmdb/model_instance/export_data/

导出模型实例数据

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| fields | query | array | 否 | 导出字段列表, 不填默认导出全部 |
| instances | query | array | 否 | 导出实例ID列表, 不填默认导出全部 |
| model | query | string | 是 | 模型ID |

**响应** (`200`):
```
string
```

---

### POST /api/v1/cmdb/model_instance/export_template/

导出模型实例模板

**请求体** (`application/json`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **model** (string) 
- **instance_name** (string) 
- **using_template** (boolean) 
- **input_mode** (string) * `manual` - 手动录入
* `import` - 表格导入
* `discover` - 自动发现
- **fields** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| model | query | string | 是 | 模型ID |

**响应** (`200`):
```
string
```

---

### POST /api/v1/cmdb/model_instance/import_data/

导入模型实例数据

**请求体** (`multipart/form-data`):
```
- **model** (string) 模型ID
- **file** (string) 导入的Excel文件(.xlsx)
```

**响应** (`200`):
```
- **cache_key** (string) 任务ID
```

---

### GET /api/v1/cmdb/model_instance/import_status/

获取导入状态

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| cache_key | query | string | 是 | 任务ID |

**响应** (`200`):
```
- **status** (string) 处理状态

* `pending` - pending
* `processing` - processing
* `completed` - completed
* `failed` - failed
- **total** (integer) 总记录数
- **progress** (integer) 当前进度
- **created** (integer) 创建数量
- **updated** (integer) 更新数量
- **skipped** (integer) 跳过数量
- **failed** (integer) 失败数量
- **errors** (array) 错误信息
- **error_file_key** (string) 错误文件标识
```

---

### GET /api/v1/cmdb/model_instance/import_status_sse/

实时获取导入状态(SSE)

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| cache_key | query | string | 是 | 导入任务ID |

**响应** (`200`):
```
string
```

---

### GET /api/v1/cmdb/model_instance/quick_search/

快速搜索实例

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| limit | query | integer | 否 | 返回数量限制(默认20,最大100) |
| model | query | string | 否 | 限制在指定模型中搜索 |
| query | query | string | 是 | 搜索关键词 |

**响应** (`200`):
```
- **results** (array) 搜索结果列表
- **total** (integer) 结果总数
- **query** (string) 搜索关键词
```

---

### GET /api/v1/cmdb/relations/

获取关联列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| instance_name | query | string | 否 |  |
| instances | query | string | 否 |  |
| model | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| relation | query | string | 否 |  |
| source_instance | query | string | 否 |  |
| target_instance | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/relations/

创建关联

**请求体** (`application/json`):
```
- **source_instance** (string) 
- **target_instance** (string) 
- **relation** (string) 
- **source_attributes** (object) 
- **target_attributes** (object) 
- **relation_attributes** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **source_instance** (string) 
- **target_instance** (string) 
- **relation** (string) 
- **source_attributes** (object) 
- **target_attributes** (object) 
- **relation_attributes** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **source_instance** (string) 
- **target_instance** (string) 
- **relation** (string) 
- **source_attributes** (object) 
- **target_attributes** (object) 
- **relation_attributes** (object) 
- **create_user** (string) 
- **update_user** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **source_instance** (string) 
- **target_instance** (string) 
- **relation** (string) 
- **source_attributes** (object) 
- **target_attributes** (object) 
- **relation_attributes** (object) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### GET /api/v1/cmdb/relations/{id}/

获取关联详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this relations. |

**响应** (`200`):
```
- **id** (string) 
- **source_instance** (string) 
- **target_instance** (string) 
- **relation** (string) 
- **source_attributes** (object) 
- **target_attributes** (object) 
- **relation_attributes** (object) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### DELETE /api/v1/cmdb/relations/{id}/

删除关联

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this relations. |

---

### POST /api/v1/cmdb/relations/get_topology/

获取实例关系拓扑图

**请求体** (`application/json`):
```
- **start_nodes** (array) 起始节点ID列表
- **end_nodes** (array) 结束节点ID列表(path模式时必填)
- **depth** (integer) 搜索深度(1-10)
- **direction** (string) 搜索方向

* `forward` - forward
* `backward` - backward
* `both` - both
- **mode** (string) 拓扑模式: blast(广度优先扩展)/path(路径查询)/neighbor(邻居节点)

* `blast` - blast
* `path` - path
* `neighbor` - neighbor
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **start_nodes** (array) 起始节点ID列表
- **end_nodes** (array) 结束节点ID列表(path模式时必填)
- **depth** (integer) 搜索深度(1-10)
- **direction** (string) 搜索方向

* `forward` - forward
* `backward` - backward
* `both` - both
- **mode** (string) 拓扑模式: blast(广度优先扩展)/path(路径查询)/neighbor(邻居节点)

* `blast` - blast
* `path` - path
* `neighbor` - neighbor
```

**请求体** (`multipart/form-data`):
```
- **start_nodes** (array) 起始节点ID列表
- **end_nodes** (array) 结束节点ID列表(path模式时必填)
- **depth** (integer) 搜索深度(1-10)
- **direction** (string) 搜索方向

* `forward` - forward
* `backward` - backward
* `both` - both
- **mode** (string) 拓扑模式: blast(广度优先扩展)/path(路径查询)/neighbor(邻居节点)

* `blast` - blast
* `path` - path
* `neighbor` - neighbor
```

**响应** (`200`):
```
- **nodes** (array) 节点列表(包含可见节点和受限节点)
- **edges** (array) 边列表
- **statistics** (TopologyStatistics) 
```

---

### GET /api/v1/cmdb/model_instance_group/

获取实例分组树

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| model | query | string | 否 | 根据模型ID过滤分组 |

**响应** (`200`):
```
Array<- **__root__** (object) 按模型ID分组的实例分组树，每个键为模型ID，对应的值为该模型的分组信息>
```

---

### POST /api/v1/cmdb/model_instance_group/

创建实例分组

**请求体** (`application/json`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`multipart/form-data`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | string | 是 | 是否内置分组 |
| create_user | query | string | 是 | 创建用户 |
| label | query | string | 是 | 分组名称 |
| level | query | integer | 否 | 分组层级, 未提供时将自动计算 |
| order | query | integer | 否 | 排序值, 未提供时分组默认创建在最后 |
| parent | query | string | 否 | 父分组ID |
| path | query | string | 否 | 分组完整路径, 未提供时将自动计算 |
| update_user | query | string | 是 | 更新用户 |

**响应** (`201`):
```
- **id** (string) 
- **label** (string) 
- **children** (array) 
- **count** (integer) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

---

### GET /api/v1/cmdb/model_instance_group/{id}/

获取实例分组详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 分组ID |

**响应** (`200`):
```
- **id** (string) 分组ID
- **label** (string) 分组名称
- **level** (integer) 分组层级
- **built_in** (boolean) 是否内置
- **instance_count** (integer) 实例数量
- **children** (array) 子分组列表
```

---

### PUT /api/v1/cmdb/model_instance_group/{id}/

更新实例分组

**请求体** (`application/json`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`multipart/form-data`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | string | 否 | 是否内置分组 |
| id | path | string | 是 | A UUID string identifying this model instance group. |
| label | query | string | 否 | 分组名称 |
| level | query | integer | 否 | 分组层级 |
| order | query | integer | 否 | 排序值 |
| parent | query | string | 否 | 父分组ID |
| path | query | string | 否 | 分组完整路径 |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **id** (string) 
- **label** (string) 
- **children** (array) 
- **count** (integer) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

---

### PATCH /api/v1/cmdb/model_instance_group/{id}/

部分更新实例分组

**请求体** (`application/json`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**请求体** (`multipart/form-data`):
```
- **label** (string) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | string | 否 | 是否内置分组 |
| id | path | string | 是 | A UUID string identifying this model instance group. |
| label | query | string | 否 | 分组名称 |
| level | query | integer | 否 | 分组层级 |
| order | query | integer | 否 | 排序值 |
| parent | query | string | 否 | 父分组ID |
| path | query | string | 否 | 分组完整路径 |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **id** (string) 
- **label** (string) 
- **children** (array) 
- **count** (integer) 
- **built_in** (boolean) 
- **level** (integer) 
- **model** (string) 
- **parent** (string) 
```

---

### DELETE /api/v1/cmdb/model_instance_group/{id}/

删除实例分组

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model instance group. |

---

### GET /api/v1/cmdb/model_instance_group_relation/

获取实例与分组的关联列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| group | query | string | 否 | 根据分组ID查询 |
| instance | query | string | 否 | 根据实例ID查询 |
| page | query | integer | 否 | 页码 |
| page_size | query | integer | 否 | 每页数量 |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/model_instance_group_relation/

创建实例与分组的关联

**请求体** (`application/json`):
```
- **create_user** (string) 
- **update_user** (string) 
- **instance** (string) 
- **group** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **create_user** (string) 
- **update_user** (string) 
- **instance** (string) 
- **group** (string) 
```

**请求体** (`multipart/form-data`):
```
- **create_user** (string) 
- **update_user** (string) 
- **instance** (string) 
- **group** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| create_user | query | string | 是 | 创建用户 |
| group | query | string | 是 | 分组ID |
| instance | query | string | 是 | 实例ID |
| update_user | query | string | 是 | 更新用户 |

**响应** (`200`):
```
- **id** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **instance** (string) 
- **group** (string) 
```

---

### GET /api/v1/cmdb/model_instance_group_relation/{id}/

获取实例与分组的关联

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 关联ID |

**响应** (`200`):
```
- **id** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **instance** (string) 
- **group** (string) 
```

---

### POST /api/v1/cmdb/model_instance_group_relation/create_relations/

批量创建实例与分组的关联

**请求体** (`application/json`):
```
- **instances** (array) 
- **groups** (array) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **instances** (array) 
- **groups** (array) 
```

**请求体** (`multipart/form-data`):
```
- **instances** (array) 
- **groups** (array) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| groups | query | array | 是 | 分组ID列表 |
| instances | query | array | 是 | 实例ID列表 |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### GET /api/v1/cmdb/model_ref/

获取模型关联列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| instance_name | query | string | 否 | 根据实例名称模糊查询 |
| model | query | string | 否 | 根据模型ID查询 |
| page | query | integer | 否 | 页码 |
| page_size | query | integer | 否 | 每页数量 |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### GET /api/v1/cmdb/model_ref/{id}/

获取模型关联详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 关联ID |

**响应** (`200`):
```
- **id** (string) 
- **model** (string) 
- **instance_name** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### GET /api/v1/cmdb/relation_definition/

获取模型引用定义列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| any_model | query | string | 否 |  |
| attribute_schema_key | query | string | 否 |  |
| description | query | string | 否 |  |
| name | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| source_model | query | array | 否 |  |
| target_model | query | array | 否 |  |
| topology_type | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/relation_definition/

创建模型引用定义

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**响应** (`201`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

---

### GET /api/v1/cmdb/relation_definition/{id}/

获取模型引用定义详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this relation definition. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

---

### PUT /api/v1/cmdb/relation_definition/{id}/

更新模型引用定义

**请求体** (`application/json`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this relation definition. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **built_in** (boolean) 
- **topology_type** (string) * `directed` - 有向图
* `undirected` - 无向图
* `daggered` - 有向无环图
- **forward_verb** (string) 
- **reverse_verb** (string) 
- **attribute_schema** (object) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **source_model** (array) 
- **target_model** (array) 
```

---

### DELETE /api/v1/cmdb/relation_definition/{id}/

删除模型引用定义

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this relation definition. |

---

### GET /api/v1/cmdb/models/

获取模型列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 | 根据是否内置模型查询 |
| description | query | string | 否 |  |
| editable | query | boolean | 否 | 根据是否可编辑查询 |
| model_group | query | string | 否 | 根据模型分组ID查询 |
| name | query | string | 否 | 根据模型名称模糊查询 |
| verbose_name | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/models/

创建模型

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 是 | 是否内置模型 |
| create_user | query | string | 是 | 创建用户 |
| description | query | string | 否 | 模型描述 |
| editable | query | boolean | 是 | 是否可编辑 |
| model_group | query | string | 否 | 所属模型分组ID |
| name | query | string | 是 | 模型名称 |
| update_user | query | string | 是 | 更新用户 |
| verbose_name | query | string | 是 | 显示名称 |

**响应** (`201`):
```
- **id** (string) 
- **instance_count** (integer) 获取模型关联的实例总数
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

---

### GET /api/v1/cmdb/models/{id}/

获取模型详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 模型ID |

**响应** (`200`):
```
- **model** (Models) 
- **field_groups** (array) 
```

---

### PUT /api/v1/cmdb/models/{id}/

更新模型

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this models. |

**响应** (`200`):
```
- **id** (string) 
- **instance_count** (integer) 获取模型关联的实例总数
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

---

### PATCH /api/v1/cmdb/models/{id}/

部分更新模型

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this models. |

**响应** (`200`):
```
- **id** (string) 
- **instance_count** (integer) 获取模型关联的实例总数
- **name** (string) 
- **verbose_name** (string) 
- **instance_name_template** (object) 
- **description** (string) 
- **built_in** (boolean) 
- **icon** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model_group** (string) 
```

---

### DELETE /api/v1/cmdb/models/{id}/

删除模型

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this models. |

---

### POST /api/v1/cmdb/password_manage/re_encrypt/

重新加密密码

**响应** (`200`):
```
- **success** (boolean) 
- **message** (string) 
```

---

### POST /api/v1/cmdb/password_manage/reset_passwords/

重置密码

**响应** (`200`):
```
- **success** (boolean) 
- **message** (string) 
```

---

### POST /api/v1/cmdb/system_cache/clear_cache/

清理系统缓存

---

### GET /api/v1/cmdb/unique_constraint/

获取唯一约束列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 |  |
| fields | query | string | 否 |  |
| model | query | string | 否 | 根据模型ID查询 |
| validate_null | query | boolean | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/unique_constraint/

创建唯一约束

**请求体** (`application/json`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 是 | 是否内置唯一约束 |
| create_user | query | string | 是 | 创建用户 |
| description | query | string | 否 | 唯一约束描述 |
| fields | query | array | 是 | 字段ID |
| model | query | string | 是 | 模型ID |
| update_user | query | string | 是 | 更新用户 |
| validate_null | query | boolean | 是 | 是否验证空值, 设置为false时将忽略空值重复, 否则将对重复的空值进行校验 |

**响应** (`201`):
```
- **id** (string) 
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### GET /api/v1/cmdb/unique_constraint/{id}/

获取唯一约束详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 唯一约束ID |

**响应** (`200`):
```
- **id** (string) 
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### PUT /api/v1/cmdb/unique_constraint/{id}/

更新唯一约束

**请求体** (`application/json`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this unique constraint. |

**响应** (`200`):
```
- **id** (string) 
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### PATCH /api/v1/cmdb/unique_constraint/{id}/

部分更新唯一约束

**请求体** (`application/json`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this unique constraint. |

**响应** (`200`):
```
- **id** (string) 
- **fields** (object) 
- **validate_null** (boolean) 
- **built_in** (boolean) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
```

---

### DELETE /api/v1/cmdb/unique_constraint/{id}/

删除唯一约束

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this unique constraint. |

---

### GET /api/v1/cmdb/validation_rules/

获取校验规则列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 |  |
| editable | query | boolean | 否 |  |
| field_type | query | string | 否 | 根据字段类型查询 |
| name | query | string | 否 | 根据规则名称模糊查询 |
| type | query | string | 否 |  |
| verbose_name | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/cmdb/validation_rules/

创建字段校验规则

**请求体** (`application/json`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| built_in | query | boolean | 否 | 是否内置规则 |
| create_user | query | string | 是 | 创建用户 |
| description | query | string | 是 | 规则描述 |
| editable | query | boolean | 否 | 是否可编辑 |
| field_type | query | string | 是 | 适配的字段类型 |
| name | query | string | 是 | 校验规则名称 |
| rule | query | string | 否 | 具体的验证规则 |
| type | query | string | 是 | 验证类型(regex/range/length等) |
| update_user | query | string | 是 | 更新用户 |
| verbose_name | query | string | 是 | 显示名称 |

**响应** (`201`):
```
- **id** (string) 
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### GET /api/v1/cmdb/validation_rules/{id}/

获取校验规则详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | 校验规则ID |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PUT /api/v1/cmdb/validation_rules/{id}/

更新校验规则

**请求体** (`application/json`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this validation rules. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### PATCH /api/v1/cmdb/validation_rules/{id}/

部分更新校验规则

**请求体** (`application/json`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_user** (string) 
- **update_user** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this validation rules. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 规则名称
- **verbose_name** (string) 显示名称
- **field_type** (string) 适配字段类型
- **type** (string) 验证类型
- **rule** (string) 验证规则
- **built_in** (boolean) 是否内置
- **editable** (boolean) 是否可编辑
- **description** (string) 规则描述
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
```

---

### DELETE /api/v1/cmdb/validation_rules/{id}/

删除校验规则

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this validation rules. |

---

### GET /api/v1/node_mg/modelConfig/

获取模型配置列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| model | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/node_mg/modelConfig/

创建模型配置

**请求体** (`application/json`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **model_name** (string) 
- **model_verbose_name** (string) 
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **create_time** (string) 
- **update_time** (string) 
- **model** (string) 
```

---

### GET /api/v1/node_mg/modelConfig/{id}/

获取模型配置详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model config. |

**响应** (`200`):
```
- **id** (string) 
- **model_name** (string) 
- **model_verbose_name** (string) 
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **create_time** (string) 
- **update_time** (string) 
- **model** (string) 
```

---

### PUT /api/v1/node_mg/modelConfig/{id}/

更新模型配置

**请求体** (`application/json`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**请求体** (`multipart/form-data`):
```
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **model** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model config. |

**响应** (`200`):
```
- **id** (string) 
- **model_name** (string) 
- **model_verbose_name** (string) 
- **built_in** (boolean) 
- **is_manage** (boolean) 
- **zabbix_sync_info** (object) 
- **create_time** (string) 
- **update_time** (string) 
- **model** (string) 
```

---

### DELETE /api/v1/node_mg/modelConfig/{id}/

删除模型配置

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this model config. |

---

### GET /api/v1/node_mg/nodes/

获取节点列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| agent_status | query | string | 否 |  |
| enable_sync | query | boolean | 否 |  |
| ip_address | query | string | 否 |  |
| manage_status | query | string | 否 |  |
| model_instance | query | string | 否 |  |
| model_instance_name | query | string | 否 |  |
| model_name | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| proxy | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/node_mg/nodes/

创建节点

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### GET /api/v1/node_mg/nodes/{id}/

获取节点详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this nodes. |

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### PUT /api/v1/node_mg/nodes/{id}/

更新节点

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this nodes. |

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### DELETE /api/v1/node_mg/nodes/{id}/

删除节点

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this nodes. |

---

### POST /api/v1/node_mg/nodes/associate_proxy/

关联代理

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### POST /api/v1/node_mg/nodes/dissociate_proxy/

解除代理关联

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### GET /api/v1/node_mg/nodes/get_info_by_instance/

根据实例ID获取节点信息

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### POST /api/v1/node_mg/nodes/get_inventory/

获取资产信息

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### POST /api/v1/node_mg/nodes/install_agent/

安装Agent

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### GET /api/v1/node_mg/nodes/list_all_nodes/

获取所有节点（不分页）

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### POST /api/v1/node_mg/nodes/sync_zabbix/

同步到Zabbix

**请求体** (`application/json`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**请求体** (`multipart/form-data`):
```
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

**响应** (`200`):
```
- **id** (string) 
- **model_instance_name** (string) 
- **model_name** (string) 
- **proxy_name** (string) 
- **manage_status** (string) 
- **agent_status** (string) 
- **model_verbose_name** (string) 
- **manage_error_message** (string) 
- **agent_error_message** (string) 
- **ip_address** (string) 
- **enable_sync** (boolean) 
- **create_time** (string) 
- **update_time** (string) 
- **create_user** (string) 
- **update_user** (string) 
- **model** (string) 
- **model_instance** (string) 
- **proxy** (string) 
```

---

### GET /api/v1/node_mg/nodeTask/

获取节点任务列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| node_ip | query | string | 否 |  |
| node_name | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| status | query | string | 否 |  |
| task_name | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### GET /api/v1/node_mg/nodeTask/{id}/

获取节点任务详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this node tasks. |

**响应** (`200`):
```
- **id** (string) 
- **node_name** (string) 
- **node_ip** (string) 
- **results** (string) 
- **error_message** (string) 
- **task_name** (string) 
- **status** (integer) * `1` - 成功
* `0` - 失败
* `2` - 未知
- **record_info** (object) 
- **cost_time** (number) 
- **created_at** (string) 
- **completed_at** (string) 
- **node** (string) 
```

---

### GET /api/v1/node_mg/proxy/

获取代理列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/node_mg/proxy/

创建代理

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **node_count** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
- **created_at** (string) 
- **updated_at** (string) 
```

---

### GET /api/v1/node_mg/proxy/{id}/

获取代理详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 代理配置. |

**响应** (`200`):
```
- **id** (string) 
- **node_count** (string) 
- **nodes** (array) 
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
- **created_at** (string) 
- **updated_at** (string) 
```

---

### PUT /api/v1/node_mg/proxy/{id}/

更新代理

**请求体** (`application/json`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 代理配置. |

**响应** (`200`):
```
- **id** (string) 
- **node_count** (string) 
- **name** (string) 
- **verbose_name** (string) 
- **proxy_type** (string) * `all` - all
* `zabbix` - zabbix
* `ansible` - ansible
- **enabled** (boolean) 
- **ip_address** (string) 
- **port** (integer) 
- **auth_user** (string) 
- **auth_pass** (string) 
- **zbx_proxyid** (string) 
- **description** (string) 
- **created_at** (string) 
- **updated_at** (string) 
```

---

### DELETE /api/v1/node_mg/proxy/{id}/

删除代理

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 代理配置. |

---

### GET /api/v1/access/button/

获取按钮列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| menu | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/access/button/

创建按钮

**请求体** (`application/json`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

---

### GET /api/v1/access/button/{id}/

获取按钮详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单按钮. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

---

### PUT /api/v1/access/button/{id}/

更新按钮

**请求体** (`application/json`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**请求体** (`multipart/form-data`):
```
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单按钮. |

**响应** (`200`):
```
- **id** (string) 
- **name** (string) 
- **action** (string) 
- **menu** (string) 
```

---

### DELETE /api/v1/access/button/{id}/

删除按钮

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单按钮. |

---

### GET /api/v1/access/menu/

获取菜单列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/access/menu/

创建菜单

**请求体** (`application/json`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**请求体** (`multipart/form-data`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

---

### GET /api/v1/access/menu/{id}/

获取菜单详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单. |

**响应** (`200`):
```
- **id** (string) 
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

---

### PUT /api/v1/access/menu/{id}/

更新菜单

**请求体** (`application/json`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**请求体** (`multipart/form-data`):
```
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单. |

**响应** (`200`):
```
- **id** (string) 
- **label** (string) 
- **icon** (string) 
- **name** (string) 
- **status** (boolean) 
- **path** (string) 
- **is_menu** (boolean) 
- **sort** (integer) 
- **has_info** (boolean) 
- **info_view_name** (string) 
- **is_iframe** (boolean) 
- **keepalive** (boolean) 
- **iframe_url** (string) 
- **description** (string) 
- **parentid** (string) 
```

---

### DELETE /api/v1/access/menu/{id}/

删除菜单

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 菜单. |

---

### GET /api/v1/access/data_scope/

获取数据权限列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| role | query | string | 否 |  |
| scope_type | query | string | 否 | * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建 |
| user | query | string | 否 |  |
| user_group | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/access/data_scope/

创建数据权限

**请求体** (`application/json`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**请求体** (`multipart/form-data`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**响应** (`201`):
```
- **id** (string) 
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **role_name** (string) 
- **user_name** (string) 
- **user_group_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
```

---

### GET /api/v1/access/data_scope/{id}/

获取数据权限详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this data scope. |

**响应** (`200`):
```
- **id** (string) 
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **role_name** (string) 
- **user_name** (string) 
- **user_group_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
```

---

### PUT /api/v1/access/data_scope/{id}/

更新数据权限

**请求体** (`application/json`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**请求体** (`multipart/form-data`):
```
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **description** (string) 
- **targets** (array) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this data scope. |

**响应** (`200`):
```
- **id** (string) 
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **role_name** (string) 
- **user_name** (string) 
- **user_group_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
```

---

### DELETE /api/v1/access/data_scope/{id}/

删除数据权限

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this data scope. |

---

### GET /api/v1/access/data_scope/aggregated_permissions/

获取聚合权限

**响应** (`200`):
```
- **id** (string) 
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **role_name** (string) 
- **user_name** (string) 
- **user_group_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
```

---

### GET /api/v1/access/data_scope/check-permission/

检查权限

**响应** (`200`):
```
- **id** (string) 
- **role** (string) 
- **user** (string) 
- **user_group** (string) 
- **app_label** (string) 
- **scope_type** (string) * `all` - 全部数据
* `filter` - 按条件过滤
* `self` - 仅自身创建
- **role_name** (string) 
- **user_name** (string) 
- **user_group_name** (string) 
- **description** (string) 
- **create_time** (string) 
- **update_time** (string) 
```

---

### GET /api/v1/access/permission/

获取权限列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### POST /api/v1/access/permission/

创建权限

**请求体** (`application/json`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**请求体** (`multipart/form-data`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**响应** (`201`):
```
- **id** (string) 
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

---

### GET /api/v1/access/permission/{id}/

获取权限详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 权限. |

**响应** (`200`):
```
- **id** (string) 
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

---

### PUT /api/v1/access/permission/{id}/

更新权限

**请求体** (`application/json`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**请求体** (`application/x-www-form-urlencoded`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**请求体** (`multipart/form-data`):
```
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 权限. |

**响应** (`200`):
```
- **id** (string) 
- **user** (string) 
- **user_group** (string) 
- **role** (string) 
- **menu** (string) 
- **button** (string) 
```

---

### DELETE /api/v1/access/permission/{id}/

删除权限

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this 权限. |

---

### GET /api/v1/audit/logs/

获取审计日志列表

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| action | query | array | 否 | Multiple values may be separated by commas. |
| object_id | query | string | 否 |  |
| operator | query | string | 否 |  |
| operator_ip | query | string | 否 |  |
| page | query | integer | 否 | A page number within the paginated result set. |
| page_size | query | integer | 否 | Number of results to return per page. |
| target_type | query | string | 否 |  |
| time_after | query | string | 否 |  |
| time_before | query | string | 否 |  |
| timestamp | query | string | 否 |  |

**响应** (`200`):
```
- **count** (integer) 
- **next** (string) 
- **previous** (string) 
- **results** (array) 
```

---

### GET /api/v1/audit/logs/{id}/

获取审计日志详情

**路径/查询参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|------|------|
| id | path | string | 是 | A UUID string identifying this audit log. |

**响应** (`200`):
```
- **id** (string) 
- **correlation_id** (string) 
- **action** (string) * `CREATE` - 创建
* `UPDATE` - 更新
* `DELETE` - 删除
- **action_display** (string) 
- **target_type** (string) 
- **object_id** (string) 
- **changed_fields** (object) 
- **operator** (string) 
- **operator_ip** (string) 
- **request_id** (string) 
- **timestamp** (string) 
- **comment** (string) 
- **details** (array) 
- **is_reverted** (boolean) 
- **reverted_from** (string) 
```

---
