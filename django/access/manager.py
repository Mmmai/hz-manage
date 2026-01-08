"""
访问控制(access)应用 - 权限管理器模块
提供了一个全局权限管理器类，用于获取任何模型的、经过权限过滤的安全查询集。

***所有外部应用在访问受权限控制的数据时，必须通过此管理器获取查询集，以确保数据安全。***
"""
import logging
from django.db import models
from .tools import get_scope_query

logger = logging.getLogger(__name__)

# 在模型中提供其他模型的查询 权限过滤后的数据
class PermissionManager:
    """
    一个全局权限管理器，用于获取任何模型的、经过权限过滤的安全查询集。
    """

    def __init__(self, user):
        self.username = user if isinstance(user, str) else getattr(user, 'username', None)
        if not self.username:
            raise ValueError("A valid username must be provided to PermissionManager.")

    def get_queryset(self, model_or_queryset) -> models.QuerySet:
        """
        获取安全查询集。
        """
        # 确定 Model 和 Base QuerySet
        if isinstance(model_or_queryset, models.QuerySet):
            model = model_or_queryset.model
            queryset = model_or_queryset
        elif isinstance(model_or_queryset, type) and issubclass(model_or_queryset, models.Model):
            model = model_or_queryset
            queryset = model.objects.all()
        else:
            raise TypeError("Input must be a Django Model or QuerySet.")

        query_obj = get_scope_query(self.username, model)

        if query_obj is None:
            return queryset.none()

        return queryset.filter(query_obj)
