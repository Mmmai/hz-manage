"""
Access API接口文档模块
定义访问控制应用对外API接口的Schema文档，供drf-spectacular生成接口文档使用。
"""

from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.types import OpenApiTypes
from .serializers import *


# 菜单管理
menu_schema = extend_schema_view(
    list=extend_schema(
        summary='获取菜单列表',
        description='支持分页和搜索',
        tags=['菜单管理'],
        responses={200: MenuModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取菜单详情',
        tags=['菜单管理'],
    ),
    create=extend_schema(
        summary='创建菜单',
        request=MenuModelSerializer,
        tags=['菜单管理'],
    ),
    update=extend_schema(
        summary='更新菜单',
        request=MenuModelSerializer,
        tags=['菜单管理'],
    ),
    destroy=extend_schema(
        summary='删除菜单',
        tags=['菜单管理'],
    ),
    tree=extend_schema(
        summary='获取菜单树',
        tags=['菜单管理'],
    ),
)


# 按钮管理
button_schema = extend_schema_view(
    list=extend_schema(
        summary='获取按钮列表',
        description='支持分页和搜索',
        tags=['菜单管理'],
        responses={200: ButtonModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取按钮详情',
        tags=['菜单管理'],
    ),
    create=extend_schema(
        summary='创建按钮',
        request=ButtonModelSerializer,
        tags=['菜单管理'],
    ),
    update=extend_schema(
        summary='更新按钮',
        request=ButtonModelSerializer,
        tags=['菜单管理'],
    ),
    destroy=extend_schema(
        summary='删除按钮',
        tags=['菜单管理'],
    ),
)


# 权限管理
permission_schema = extend_schema_view(
    list=extend_schema(
        summary='获取权限列表',
        description='支持分页和搜索',
        tags=['权限管理'],
        responses={200: PermissionModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取权限详情',
        tags=['权限管理'],
    ),
    create=extend_schema(
        summary='创建权限',
        request=PermissionModelSerializer,
        tags=['权限管理'],
    ),
    update=extend_schema(
        summary='更新权限',
        request=PermissionModelSerializer,
        tags=['权限管理'],
    ),
    destroy=extend_schema(
        summary='删除权限',
        tags=['权限管理'],
    ),
    set_permission=extend_schema(
        summary='设置权限',
        tags=['权限管理'],
    ),
    getPermissionToRole=extend_schema(
        summary='获取角色权限',
        tags=['权限管理'],
    ),
    getUserButton=extend_schema(
        summary='获取用户按钮权限',
        tags=['权限管理'],
    ),
)


# 数据权限管理
data_scope_schema = extend_schema_view(
    list=extend_schema(
        summary='获取数据权限列表',
        description='支持分页和过滤，返回包含targets详情',
        tags=['数据权限'],
        responses={200: DataScopeSerializer},
    ),
    retrieve=extend_schema(
        summary='获取数据权限详情',
        tags=['数据权限'],
    ),
    create=extend_schema(
        summary='创建数据权限',
        tags=['数据权限'],
    ),
    update=extend_schema(
        summary='更新数据权限',
        tags=['数据权限'],
    ),
    destroy=extend_schema(
        summary='删除数据权限',
        tags=['数据权限'],
    ),
    aggregated_permissions=extend_schema(
        summary='获取聚合权限',
        description='获取用户/用户组/角色的所有聚合权限列表',
        tags=['数据权限'],
    ),
    check_permission=extend_schema(
        summary='检查权限',
        description='检查用户对特定对象是否有权限',
        tags=['数据权限'],
    ),
    get_targets=extend_schema(
        summary='获取权限目标',
        tags=['数据权限'],
    ),
)
