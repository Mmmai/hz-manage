import logging
from django.db import models
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework.generics import GenericAPIView

logger = logging.getLogger(__name__)


class PermissionManager:
    """
    一个全局权限管理器，用于获取任何模型的、经过权限过滤的安全查询集。
    """

    def __init__(self, user):
        if not user:
            raise ValueError("PermissionManager requires a user object or username string.")
        self.user = user
        self.username = user if isinstance(user, str) else getattr(user, 'username', None)
        self._view_cache = {}

    def get_queryset(self, model_or_queryset) -> models.QuerySet:
        """
        获取一个模型或查询集的、经过完整权限过滤的安全版本。
        """
        if isinstance(model_or_queryset, models.QuerySet):
            model = model_or_queryset.model
            base_queryset = model_or_queryset
        elif isinstance(model_or_queryset, type) and issubclass(model_or_queryset, models.Model):
            model = model_or_queryset
            base_queryset = model.objects.all()
        else:
            raise TypeError("Input must be a Django Model or QuerySet.")

        # 模拟一个最小化的 View 和 Request，以复用 DRF 的 filter_queryset 机制
        view = self._get_mock_view(model)

        # 调用视图的 filter_queryset，这将触发我们所有的 FilterBackend
        return view.filter_queryset(base_queryset)

    def _get_mock_view(self, model):
        """
        为给定的模型创建一个模拟的、带缓存的 APIView 实例。
        这个模拟视图将拥有正确的 filter_backends 设置。
        """
        model_name = model._meta.model_name
        if model_name in self._view_cache:
            return self._view_cache[model_name]

        # 创建一个最小化的 request 对象
        factory = APIRequestFactory()
        request = factory.get('/')

        drf_request = Request(request)
        drf_request.user = self.user
        drf_request.username = self.username

        # 创建一个模拟的 APIView 类
        class MockView(GenericAPIView):
            queryset = model.objects.all()

        view = MockView()
        view.request = drf_request

        self._view_cache[model_name] = view
        return view
