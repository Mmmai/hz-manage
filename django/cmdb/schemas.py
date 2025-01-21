from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter
from .serializers import (
    ModelGroupsSerializer,
    ModelsSerializer,
)

model_groups_schema = extend_schema_view(
    # 标准CRUD方法
    create=extend_schema(
        summary='创建模型分组',
        tags=['模型分组管理']
    ),
    list=extend_schema(
        summary='获取模型分组列表',
        tags=['模型分组管理']
    ),
    update=extend_schema(
        summary='更新模型分组',
        tags=['模型分组管理']
    ),
    destroy=extend_schema(
        summary='删除模型分组',
        tags=['模型分组管理']
    )
)
