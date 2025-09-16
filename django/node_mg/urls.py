from django.urls import path,include,re_path
from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
  re_path("test/",views.test)

  ]
router = DefaultRouter()
router.register('nodes',views.NodesViewSet)


urlpatterns += router.urls