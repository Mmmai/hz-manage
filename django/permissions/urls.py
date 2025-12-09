from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DataScopeViewSet

router = DefaultRouter()
router.register('data_scope', DataScopeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
