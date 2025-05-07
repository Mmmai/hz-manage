from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuditLogViewSet

# 创建路由器并注册视图
router = DefaultRouter()
router.register(r'audit', AuditLogViewSet, basename='audit')

urlpatterns = [
    path('', include(router.urls)),
]
