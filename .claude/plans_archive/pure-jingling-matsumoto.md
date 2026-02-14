# API 文档优化实现计划

## Context

当前项目使用 drf-spectacular 生成 OpenAPI 3.0 文档，提供 Swagger UI 和 ReDoc 两种访问方式，但存在以下问题：

1. **前端缺少入口**：用户需要手动输入 URL 才能访问 API 文档
2. **文档范围被过滤**：`preprocessing_filter_spec` 只保留 cmdb 模块接口，其他模块文档被过滤
3. **文档注释不完整**：只有 cmdb 模块有较完整的文档注释，其他模块（mapi、node_mg、access、audit、monitor）缺少 schemas.py

## 修改方案

### 阶段一：前端集成入口

**文件**: `hz-ui/src/components/layout/headerCom.vue`

在第 59 行后（主题选择按钮之前）添加 API 文档下拉菜单：

```vue
<!-- API 文档入口 -->
<el-tooltip content="API 文档" placement="bottom" effect="dark">
  <el-dropdown trigger="click" @command="openApiDocs">
    <el-button circle size="small">
      <el-icon :size="16"><Document /></el-icon>
    </el-button>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item command="swagger">
          <el-icon><Document /></el-icon>
          Swagger UI
        </el-dropdown-item>
        <el-dropdown-item command="redoc">
          <el-icon><Reading /></el-icon>
          ReDoc
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</el-tooltip>
```

在 `<script setup>` 中：

1. 第 210 行附近添加图标导入：
```javascript
import { Document, Reading } from "@element-plus/icons-vue";
```

2. 第 285 行附近（`confirmCustomTheme` 函数后）添加函数：
```javascript
const openApiDocs = (docType) => {
  const baseUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  const url = docType === 'swagger'
    ? `${baseUrl}/api/docs/`
    : `${baseUrl}/api/redoc/`;
  window.open(url, '_blank');
};
```

### 阶段二：修复文档过滤范围

**文件**: `django/vuedjango/drf_spectacular_hooks.py`

修改 `preprocessing_filter_spec` 函数（第 21-27 行）：

```python
def preprocessing_filter_spec(endpoints):
    """
    移除路径过滤，展示所有模块的 API 接口
    """
    return endpoints
```

**可选**：改为白名单模式明确包含需要展示的模块：
```python
def preprocessing_filter_spec(endpoints):
    """
    只展示核心业务模块的 API 接口
    """
    filtered = []
    prefix_list = ['/api/v1/cmdb', '/api/v1/mapi', '/api/v1/node_mg',
                   '/api/v1/access', '/api/v1/audit', '/api/v1/monitor']
    for (path, path_regex, method, callback) in endpoints:
        if any(path.startswith(prefix) for prefix in prefix_list):
            filtered.append((path, path_regex, method, callback))
    return filtered
```

**文件**: `django/vuedjango/settings.py`

更新 SPECTACULAR_SETTINGS 中的 TAGS（第 253-276 行），添加所有模块标签：
- 通用说明、CMDB 相关标签（已存在）
- 用户管理、用户组管理、角色管理、门户管理、数据源管理（mapi 模块）
- 节点管理、节点任务、代理管理（node_mg 模块）
- 菜单管理、权限管理、数据权限（access 模块）
- 审计日志（audit 模块）
- 监控数据（monitor 模块）

### 阶段三：后端文档完善

#### 优先级 P0 - cmdb 模块

**文件**: `django/cmdb/schemas.py`（已存在，需扩展）

为以下 ViewSet 补充 schema（参考现有的 `model_groups_schema` 模式）：
- `ModelInstanceViewSet` - 实例管理（优先）
- `ModelFieldGroupsViewSet` - 字段分组管理
- `ValidationRulesViewSet` - 字段校验规则管理
- `ModelFieldsViewSet` - 字段管理
- `ModelFieldPreferenceViewSet` - 字段展示管理
- `UniqueConstraintViewSet` - 实例唯一性约束管理
- `ModelInstanceBasicViewSet` - 实例基础信息
- `ModelInstanceGroupViewSet` - 实例分组管理
- `ModelInstanceGroupRelationViewSet` - 实例分组关联管理
- `RelationDefinitionViewSet` - 模型引用管理
- `RelationsViewSet` - 关联管理
- `PasswordManageViewSet` - 密码及密钥管理
- `SystemCacheViewSet` - 系统缓存管理

在 `django/cmdb/views.py` 中为对应 ViewSet 添加 `@extend_schema_view` 装饰器。

#### 优先级 P1 - mapi 模块

**新建**: `django/mapi/schemas.py`

为以下 ViewSet 添加文档：
- `LoginView` - 登录接口（无认证，特殊标注）
- `UserInfoViewSet` - 用户管理
- `UserGroupViewSet` - 用户组管理
- `RoleViewSet` - 角色管理
- `PortalViewSet` - 门户管理
- `dataSourceViewSet` - 数据源管理
- `sysConfigViewSet` - 系统配置

在 `django/mapi/views.py` 中为对应 ViewSet 添加 `@extend_schema_view` 装饰器。

#### 优先级 P2 - node_mg 模块

**新建**: `django/node_mg/schemas.py`

为以下 ViewSet 添加文档：
- `NodesViewSet` - 节点管理（优先）
- `NodeTasksViewSet` - 任务管理
- `ProxyViewSet` - 代理管理
- `ModelConfigViewSet` - 模型配置

在 `django/node_mg/views.py` 中为对应 ViewSet 添加 `@extend_schema_view` 装饰器。

#### 优先级 P3 - access & audit 模块

**新建**: `django/access/schemas.py`

为以下 ViewSet 添加文档：
- `MenuViewSet` - 菜单管理
- `ButtonViewSet` - 按钮管理
- `PermissionViewSet` - 权限管理
- `DataScopeViewSet` - 数据权限管理

**新建**: `django/audit/schemas.py`

为以下 ViewSet 添加文档：
- `AuditLogViewSet` - 审计日志

#### 文档注释规范（参考 `django/cmdb/schemas.py`）

```python
from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from .serializers import XXXSerializer

xxx_schema = extend_schema_view(
    list=extend_schema(
        summary='获取XX列表',
        description='详细业务逻辑说明',
        tags=['标签名'],
        responses={200: XXXSerializer},
    ),
    retrieve=extend_schema(
        summary='获取XX详情',
        tags=['标签名'],
    ),
    create=extend_schema(
        summary='创建XX',
        request=XXXSerializer,
        responses={201: XXXSerializer},
        tags=['标签名']
    ),
    update=extend_schema(
        summary='更新XX',
        request=XXXSerializer,
        tags=['标签名']
    ),
    destroy=extend_schema(
        summary='删除XX',
        tags=['标签名']
    ),
    # 自定义 action
    custom_action=extend_schema(
        summary='自定义操作',
        tags=['标签名']
    ),
)
```

## 编译验证

### 前端编译
```bash
cd hz-ui && npm run build
```

### 后端编译
```bash
cd django && python manage.py check
```

## 关键文件

| 文件 | 说明 |
|------|------|
| `hz-ui/src/components/layout/headerCom.vue` | 前端头部组件，添加文档入口 |
| `django/vuedjango/drf_spectacular_hooks.py` | 修复文档过滤范围 |
| `django/vuedjango/settings.py` | SPECTACULAR_SETTINGS 配置 |
| `django/cmdb/schemas.py` | cmdb 文档参考模式 |
| `django/cmdb/views.py` | cmdb 视图层（需添加装饰器） |
| `django/mapi/schemas.py` | mapi 文档（新建） |
| `django/mapi/views.py` | mapi 视图层（需添加装饰器） |
| `django/node_mg/schemas.py` | node_mg 文档（新建） |
| `django/node_mg/views.py` | node_mg 视图层（需添加装饰器） |
| `django/access/schemas.py` | access 文档（新建） |
| `django/access/views.py` | access 视图层（需添加装饰器） |
| `django/audit/schemas.py` | audit 文档（新建） |
| `django/audit/views.py` | audit 视图层（需添加装饰器） |

## 实施顺序

1. **阶段一**（前端入口）- 独立，可优先完成
2. **阶段二**（修复过滤）- 应在阶段三之前完成
3. **阶段三**（文档完善）- 按优先级 P0 → P1 → P2 → P3 逐步实施
