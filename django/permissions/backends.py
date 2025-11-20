import logging

from rest_framework.filters import BaseFilterBackend
from django.db.models import Q
from .models import *
from .tools import get_user_data_scope
from .registry import get_handler

logger = logging.getLogger(__name__)


class DataScopeFilterBackend(BaseFilterBackend):
    """
    统一的数据范围权限过滤器。

    工作流程：
    1. 获取用户的合并权限范围 (scope)。
    2. 如果是 'all'，直接返回所有数据。
    3. 应用直接权限（用户被直接授权的资源 ID）。
    4. 应用 'self' 权限（用户自己创建的资源）。
    5. 查找并调用已注册的、特定于当前应用的间接权限处理器。
    6. 合并所有查询条件，过滤查询集。
    """

    TARGET_APP = {'cmdb'}

    def filter_queryset(self, request, queryset, view):
        logger.debug(
            f'Filtering queryset for user: {getattr(request, "username", None)} on model: {queryset.model._meta.label}')
        if queryset.model._meta.app_label not in self.TARGET_APP:
            return queryset

        username = getattr(request, 'username', None)
        if not username:
            return queryset.none()

        scope = get_user_data_scope(username)
        scope_type = scope.get('scope_type', 'none')

        if scope_type == DataScope.ScopeType.ALL:
            return queryset

        if scope_type == 'none':
            return queryset.none()

        model = queryset.model
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        model_key = f"{app_label}.{model_name}"

        final_query = Q()

        # 1. 应用直接权限
        allowed_ids = scope['targets'].get(model_key)
        if allowed_ids:
            final_query |= Q(id__in=allowed_ids)

        # 2. 应用 'self' 权限
        if scope_type == 'self' or scope_type == 'filter':
            if hasattr(model, 'create_user'):
                final_query |= Q(create_user=username)

        # 3. 应用间接权限（通过注册表）
        indirect_handler = get_handler(app_label)
        logger.debug(f'Checking for indirect handler for app: {app_label}, found: {indirect_handler is not None}')
        if indirect_handler:
            indirect_query = indirect_handler(scope, model, username)
            if indirect_query:
                final_query |= indirect_query

        # 如果没有任何查询条件，说明用户无权访问任何数据
        if not final_query:
            return queryset.none()
        logger.debug(f'Final data scope query for user {username} on {model_key}: {final_query}')
        return queryset.filter(final_query).distinct()
