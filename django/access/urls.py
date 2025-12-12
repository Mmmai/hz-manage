from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()

router.register('menu', MenuViewSet)
router.register('button', ButtonViewSet)
router.register('permission', PermissionViewSet)
router.register('data_scope', DataScopeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('getMenu/', getMenu.as_view()),
    path('getPermissionToRole/', getPermissionToRole.as_view()),
    path('getUserPermission/', getUserButton.as_view()),

]
