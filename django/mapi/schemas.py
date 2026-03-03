"""
MAPI API接口文档模块
定义MAPI应用对外API接口的Schema文档，供drf-spectacular生成接口文档使用。
"""

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .sers import *


# 登录接口
login_schema = extend_schema(
    tags=['用户管理'],
    summary='用户登录',
    description='用户登录接口，无需认证，返回JWT Token',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': '用户名'},
                'password': {'type': 'string', 'description': '密码'},
                'timeout': {'type': 'integer', 'description': 'token超时时间(天)，默认3天', 'default': 3},
            },
            'required': ['username', 'password'],
        }
    },
    responses={
        200: OpenApiResponse(
            description='登录成功，返回token和用户信息',
            response={
                'type': 'object',
                'properties': {
                    'code': {'type': 'integer', 'example': 200},
                    'token': {'type': 'string', 'description': 'JWT Token'},
                    'userinfo': {
                        'type': 'object',
                        'properties': {
                            'user_id': {'type': 'string'},
                            'username': {'type': 'string'}
                        }
                    },
                    'permission': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        )
    },
    auth=[]
)


# 用户管理
user_info_schema = extend_schema_view(
    list=extend_schema(
        summary='获取用户列表',
        description='支持分页和搜索，搜索支持username字段',
        tags=['用户管理'],
        responses={200: UserInfoModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取用户详情',
        tags=['用户管理'],
    ),
    create=extend_schema(
        summary='创建用户',
        request=UserInfoModelSerializer,
        tags=['用户管理'],
    ),
    update=extend_schema(
        summary='更新用户',
        request=UserInfoModelSerializer,
        tags=['用户管理'],
    ),
    destroy=extend_schema(
        summary='删除用户',
        description='admin用户不可删除',
        tags=['用户管理'],
    ),
    multiple_delete=extend_schema(
        summary='批量删除用户',
        tags=['用户管理'],
    ),
    update_status=extend_schema(
        summary='更新用户状态',
        tags=['用户管理'],
    ),
    reset_password=extend_schema(
        summary='重置用户密码',
        tags=['用户管理'],
    ),
    user_export=extend_schema(
        summary='导出用户数据',
        tags=['用户管理'],
    ),
)


# 用户组管理
user_group_schema = extend_schema_view(
    list=extend_schema(
        summary='获取用户组列表',
        description='支持分页和搜索',
        tags=['用户组管理'],
        responses={200: UserGroupModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取用户组详情',
        tags=['用户组管理'],
    ),
    create=extend_schema(
        summary='创建用户组',
        request=UserGroupModelSerializer,
        tags=['用户组管理'],
    ),
    update=extend_schema(
        summary='更新用户组',
        request=UserGroupModelSerializer,
        tags=['用户组管理'],
    ),
    destroy=extend_schema(
        summary='删除用户组',
        tags=['用户组管理'],
    ),
    multiple_delete=extend_schema(
        summary='批量删除用户组',
        tags=['用户组管理'],
    ),
)


# 角色管理
role_schema = extend_schema_view(
    list=extend_schema(
        summary='获取角色列表',
        description='支持分页和搜索',
        tags=['角色管理'],
        responses={200: RoleModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取角色详情',
        tags=['角色管理'],
    ),
    create=extend_schema(
        summary='创建角色',
        request=RoleModelSerializer,
        tags=['角色管理'],
    ),
    update=extend_schema(
        summary='更新角色',
        request=RoleModelSerializer,
        tags=['角色管理'],
    ),
    destroy=extend_schema(
        summary='删除角色',
        tags=['角色管理'],
    ),
    multiple_delete=extend_schema(
        summary='批量删除角色',
        tags=['角色管理'],
    ),
    set_permission=extend_schema(
        summary='设置角色权限',
        tags=['角色管理'],
    ),
    copy_role=extend_schema(
        summary='复制角色',
        tags=['角色管理'],
    ),
)


# 门户管理
portal_schema = extend_schema_view(
    list=extend_schema(
        summary='获取门户列表',
        description='支持分页和搜索',
        tags=['门户管理'],
        responses={200: PortalModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取门户详情',
        tags=['门户管理'],
    ),
    create=extend_schema(
        summary='创建门户',
        request=PortalModelSerializer,
        tags=['门户管理'],
    ),
    update=extend_schema(
        summary='更新门户',
        request=PortalModelSerializer,
        tags=['门户管理'],
    ),
    destroy=extend_schema(
        summary='删除门户',
        tags=['门户管理'],
    ),
    multiple_delete=extend_schema(
        summary='批量删除门户',
        tags=['门户管理'],
    ),
    set_default=extend_schema(
        summary='设置默认门户',
        tags=['门户管理'],
    ),
)


# 门户分组管理
pgroup_schema = extend_schema_view(
    list=extend_schema(
        summary='获取门户分组列表',
        description='支持分页和搜索',
        tags=['门户管理'],
        responses={200: PgroupModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取门户分组详情',
        tags=['门户管理'],
    ),
    create=extend_schema(
        summary='创建门户分组',
        request=PgroupModelSerializer,
        tags=['门户管理'],
    ),
    update=extend_schema(
        summary='更新门户分组',
        request=PgroupModelSerializer,
        tags=['门户管理'],
    ),
    destroy=extend_schema(
        summary='删除门户分组',
        tags=['门户管理'],
    ),
)


# 门户收藏管理
portal_favorites_schema = extend_schema_view(
    list=extend_schema(
        summary='获取门户收藏列表',
        description='支持分页',
        tags=['门户管理'],
        responses={200: PortalFavoritesSerializer},
    ),
    retrieve=extend_schema(
        summary='获取门户收藏详情',
        tags=['门户管理'],
    ),
    create=extend_schema(
        summary='添加门户收藏',
        request=PortalFavoritesSerializer,
        tags=['门户管理'],
    ),
    destroy=extend_schema(
        summary='删除门户收藏',
        tags=['门户管理'],
    ),
)


# 数据源管理
datasource_schema = extend_schema_view(
    list=extend_schema(
        summary='获取数据源列表',
        description='支持分页',
        tags=['数据源管理'],
        responses={200: DatasourceModelSerializer},
    ),
    retrieve=extend_schema(
        summary='获取数据源详情',
        tags=['数据源管理'],
    ),
    create=extend_schema(
        summary='创建数据源',
        request=DatasourceModelSerializer,
        tags=['数据源管理'],
    ),
    update=extend_schema(
        summary='更新数据源',
        request=DatasourceModelSerializer,
        tags=['数据源管理'],
    ),
    destroy=extend_schema(
        summary='删除数据源',
        tags=['数据源管理'],
    ),
    test_connection=extend_schema(
        summary='测试数据源连接',
        tags=['数据源管理'],
    ),
)


# 系统配置管理
sys_config_schema = extend_schema_view(
    list=extend_schema(
        summary='获取系统配置列表',
        description='支持分页',
        tags=['数据源管理'],
        responses={200: SysConfigSerializer},
    ),
    retrieve=extend_schema(
        summary='获取系统配置详情',
        tags=['数据源管理'],
    ),
    create=extend_schema(
        summary='创建系统配置',
        request=SysConfigSerializer,
        tags=['数据源管理'],
    ),
    update=extend_schema(
        summary='更新系统配置',
        request=SysConfigSerializer,
        tags=['数据源管理'],
    ),
    destroy=extend_schema(
        summary='删除系统配置',
        tags=['数据源管理'],
    ),
)
