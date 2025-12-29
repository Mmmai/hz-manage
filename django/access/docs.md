# 权限控制设计

## 权限分类
### 菜单按钮权限
- 菜单按钮权限迁移自mapi，代码逻辑无改动，CMDB内仅额外应用密码权限
- 建议在视图层同步校验是否具备菜单权限，避免非法API调用绕过该部分权限控制
### 模型数据权限
- 基本设计理念
  1. 基于RBAC设计，允许根据用户、用户组、角色进行行级别的访问权限控制。
  2. 用户如果对某实例具备权限，则将对其具有完整权限，包含创建、修改、删除，如果需要应用操作权限，建议优化菜单按钮权限相关
- 权限入口
   - 当需要获取经过权限过滤后的数据集时，必须通过access/manager.py的PermissionManager()注册用户并通过实例方法get_queryset()进行查询
- PermissionManager权限查询流程
  1. 提交用户(UserInfo)
  2. 获取用户的数据范围查询条件(Q对象)
  3. 返回经过该条件过滤的查询集
   


# 应用权限控制


## 添加自定义权限过滤器
- 在存在间接权限时需要提供对应的处理方法，例如：用户对组A具备权限时，那么组A下的所有实例用户应该也具备权限，自动推导出相关的数据范围
- 参考样例
```python
# cmdb/permission_handlers.py
from abc import ABC, abstractmethod
from django.db.models import Q
from access.registry import register_indirect_permission_handler

from .models import *


# 定义抽象处理器基类
class BaseQueryHandler(ABC):

    @abstractmethod
    def get_query(self, scope, model, username):
        pass


# Models专用的处理器逻辑
class ModelsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'models':

            # 如果分配了实例组权限，动态推导出相关模型权限
            instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            if instance_group_ids:
                related_model_ids = ModelInstanceGroup.objects.filter(
                    id__in=instance_group_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)
            logger.debug(f'CMDB indirect query for models: {query}')

            # 如果分配了模型字段权限，动态推导出相关模型权限
            model_field_ids = scope['targets'].get('cmdb.modelfields')
            if model_field_ids:
                related_model_ids = ModelFields.objects.filter(
                    id__in=model_field_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)

            # 如果分配了模型字段组权限，动态推导出相关模型权限
            model_field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
            if model_field_group_ids:
                related_model_ids = ModelFields.objects.filter(
                    model_field_group_id__in=model_field_group_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)

            return query


# 工厂模式配置
class CMDBIndirectQueryHandler:
    def __init__(self):
        self.handlers = {
            'models': ModelsQueryHandler(),
        }

    def get_query(self, scope, model, username):
        model_name = model._meta.model_name
        handler = self.handlers.get(model_name)
        if handler:
            return handler.get_query(scope, model, username)
        return Q()


# 提供单例获取处理器，减少处理器实例化开销
def get_cmdb_indirect_query(scope, model, username):
    """
    CMDB 应用的间接权限处理器。
    """
    cmdb_handler = CMDBIndirectQueryHandler()
    return cmdb_handler.get_query(scope, model, username)


# 注册间接权限处理器
register_indirect_permission_handler('cmdb', get_cmdb_indirect_query)
```

## 在app启动时注册处理器
```python
# cmdb/apps.py

class CmdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'

    def ready(self):
        """应用启动时加载密钥及zabbix相关实例"""
        import cmdb.signals

        if 'runserver' in sys.argv or any(
                'celery' in arg for arg in sys.argv) or 'daphne' in sys.modules or '--host' in sys.argv:
            
            #...

            # 注册处理器
            import cmdb.permission_handlers
```

## 在过滤器后端添加对应app注册到drf过滤后端
```python
# access/backends.py

from rest_framework.filters import BaseFilterBackend
from .tools import get_scope_query


class DataScopeFilterBackend(BaseFilterBackend):
    # 在TARGET_APP添加需要drf全局应用权限控制的app名
    TARGET_APP = {'cmdb'}

    def filter_queryset(self, request, queryset, view):
        if queryset.model._meta.app_label not in self.TARGET_APP:
            return queryset

        username = getattr(request.user, 'username', None)
        scope_query = get_scope_query(username, queryset.model)

        if scope_query is None:
            return queryset.none()
        return queryset.filter(scope_query)
```

## 在视图层获取受权限控制的查询集

- 样例1 - 在任意需要获取当前模型查询集的地方使用
```python
# 获取基础查询集
queryset = self.get_queryset()
# 获取权限过滤后的查询集
queryset = self.filter_queryset(queryset)
```
- 样例2 - 重写视图集的get_queryset()方法
```python
# 如果重写了filter_queryset，需要在重写的方法顶部先调用super().filter_queryset()
def get_queryset():
    # 获取基础查询集
    queryset = self.get_queryset()
    # 获取权限过滤后的查询集
    queryset = self.filter_queryset(queryset)
    return queryset
```

- 样例3 - 设置基类，子类继承
```python
# 参考CMDB基类设计
class CmdbBaseViewSet(AuditContextMixin, viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination

    def get_base_queryset(self):
        """
        特殊情况下提供的获取基础查询集的方法，子类可以重写此方法以动态生成基础查询集。
        ** 正常情况下只调用 super().get_queryset() 避免权限漏洞。 **
        """
        if not hasattr(self, 'queryset') or self.queryset is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define a 'queryset' attribute or override get_base_queryset()."
            )
        # 如果 queryset 是一个 QuerySet 对象，需要先克隆它以避免修改类属性
        if hasattr(self.queryset, '_clone'):
            return self.queryset._clone()
        return self.queryset

    def get_queryset(self):
        base_queryset = self.get_base_queryset()
        filtered_queryset = super().filter_queryset(base_queryset)
        return filtered_queryset

    def filter_queryset(self, queryset):
        """
        在被 DRF 意外调用时，防止DRF的默认行为绕过权限过滤。
        """
        # 直接返回已经完整过滤的 get_queryset 结果，确保数据源唯一。
        return self.get_queryset()
```

## 在任意地方获取权限过滤后的查询集
```python
from access.manager import PermissionManager

# user可以填写user对象，也可以填写username
pm = PermissionManager(user)
# 将需要过滤的模型传作为参数传递
qs = pm.get_queryset(ModelInstance)
```

## 跨越权限边界
1. 需求：部分业务逻辑不可避免地需要跨越权限边界。
   - 例如：用户创建实例A，用户对实例A所属模型的部分实例不具备权限，该模型内存在一个unique约束，在校验时如果直接应用ORM方法查询会导致权限控制混淆不清。
2. 处理方案：建议将该部分方法设计在managers.py中作为特权方法，在模型中自定义管理器后调用