"""
Node Management API接口文档模块
定义节点管理应用对外API接口的Schema文档，供drf-spectacular生成接口文档使用。
"""

from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.types import OpenApiTypes
from .serializers import *


# 节点任务管理
node_tasks_schema = extend_schema_view(
    list=extend_schema(
        summary='获取节点任务列表',
        description='支持分页、搜索、过滤，可按节点、任务名称、状态过滤',
        tags=['节点任务'],
        responses={200: NodeTasksDetailSerializer},
    ),
    retrieve=extend_schema(
        summary='获取节点任务详情',
        tags=['节点任务'],
    ),
)


# 节点管理
nodes_schema = extend_schema_view(
    list=extend_schema(
        summary='获取节点列表',
        description='支持分页、搜索、过滤，可按模型、实例、分组过滤',
        tags=['节点管理'],
        responses={200: NodesSerializer},
    ),
    retrieve=extend_schema(
        summary='获取节点详情',
        description='支持通过节点ID或实例ID查询',
        tags=['节点管理'],
    ),
    create=extend_schema(
        summary='创建节点',
        request=NodesSerializer,
        tags=['节点管理'],
    ),
    update=extend_schema(
        summary='更新节点',
        request=NodesSerializer,
        tags=['节点管理'],
    ),
    destroy=extend_schema(
        summary='删除节点',
        tags=['节点管理'],
    ),
    get_info_by_instance=extend_schema(
        summary='根据实例ID获取节点信息',
        tags=['节点管理'],
    ),
    list_all_nodes=extend_schema(
        summary='获取所有节点（不分页）',
        description='返回简化节点信息，包含id、ip、实例名',
        tags=['节点管理'],
    ),
    install_agent=extend_schema(
        summary='安装Agent',
        description='手动触发节点Agent安装任务',
        tags=['节点管理'],
    ),
    get_inventory=extend_schema(
        summary='获取资产信息',
        description='触发Ansible资产信息获取任务',
        tags=['节点管理'],
    ),
    sync_zabbix=extend_schema(
        summary='同步到Zabbix',
        description='触发节点信息同步到Zabbix',
        tags=['节点管理'],
    ),
    associate_proxy=extend_schema(
        summary='关联代理',
        description='批量为节点关联Zabbix Proxy',
        tags=['节点管理'],
    ),
    dissociate_proxy=extend_schema(
        summary='解除代理关联',
        description='批量为节点解除Zabbix Proxy关联',
        tags=['节点管理'],
    ),
)


# 代理管理
proxy_schema = extend_schema_view(
    list=extend_schema(
        summary='获取代理列表',
        description='支持分页和搜索',
        tags=['代理管理'],
        responses={200: ProxyDetailSerializer},
    ),
    retrieve=extend_schema(
        summary='获取代理详情',
        tags=['代理管理'],
    ),
    create=extend_schema(
        summary='创建代理',
        request=ProxySerializer,
        tags=['代理管理'],
    ),
    update=extend_schema(
        summary='更新代理',
        request=ProxySerializer,
        tags=['代理管理'],
    ),
    destroy=extend_schema(
        summary='删除代理',
        tags=['代理管理'],
    ),
    sync_proxy=extend_schema(
        summary='同步代理',
        description='触发Zabbix代理同步任务',
        tags=['代理管理'],
    ),
)


# 模型配置管理
model_config_schema = extend_schema_view(
    list=extend_schema(
        summary='获取模型配置列表',
        description='支持分页',
        tags=['节点管理'],
        responses={200: ModelConfigSerializer},
    ),
    retrieve=extend_schema(
        summary='获取模型配置详情',
        tags=['节点管理'],
    ),
    create=extend_schema(
        summary='创建模型配置',
        request=ModelConfigSerializer,
        tags=['节点管理'],
    ),
    update=extend_schema(
        summary='更新模型配置',
        request=ModelConfigSerializer,
        tags=['节点管理'],
    ),
    destroy=extend_schema(
        summary='删除模型配置',
        tags=['节点管理'],
    ),
)
