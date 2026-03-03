"""
Audit API接口文档模块
定义审计应用对外API接口的Schema文档，供drf-spectacular生成接口文档使用。
"""

from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.types import OpenApiTypes
from .serializers import *


# 审计日志
audit_log_schema = extend_schema_view(
    list=extend_schema(
        summary='获取审计日志列表',
        description='支持分页、搜索、过滤，可按用户、操作类型、模块过滤',
        tags=['审计日志'],
        responses={200: AuditLogSerializer},
    ),
    retrieve=extend_schema(
        summary='获取审计日志详情',
        tags=['审计日志'],
    ),
    statistics=extend_schema(
        summary='获取审计统计',
        description='按模块、操作类型等维度统计审计日志',
        tags=['审计日志'],
    ),
    export=extend_schema(
        summary='导出审计日志',
        tags=['审计日志'],
    ),
)
