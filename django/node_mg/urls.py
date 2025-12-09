from django.urls import path,include,re_path
from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
  re_path("test/",views.test),
  re_path("zabbixApi/",views.zabbixApi.as_view())

  ]
router = DefaultRouter()
router.register('nodes',views.NodesViewSet)
router.register('proxy',views.ProxyViewSet)
router.register('modelConfig',views.ModelConfigViewSet)


urlpatterns += router.urls