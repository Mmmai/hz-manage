from django.urls import path,include,re_path
from django.conf.urls import url
from . import views
from . import importExport
from rest_framework.routers import DefaultRouter
from . import test
# urlpatterns = [
#     path('test',views.test),
#     path('user',views.user)
      
#   ]
urlpatterns = [
  path('login/',views.LoginView.as_view()),
  # path('testroute/', views.TestRoute.as_view()),
  path('getMenu/', views.getMenu.as_view()),
  path('getPermissionToRole/', views.getPermissionToRole.as_view()),

  path('getSecret/', views.getSecret.as_view()),
  path('getUserPermission/', views.getUserButton.as_view()),

  path('export/', importExport.PortalExport.as_view()),
  # path('test/', views.sysConfig.as_view()),
  # 测试
  path('sse/', test.sse_stream, name='sse_stream'),
  path('test_celery/', test.test_celery, name='trigger_task'),
  path('check_task/<str:task_id>/', test.check_task, name='check_task_status'),

  # path('order/',views.orderMethod.as_view() )
  # path('loki/labels',lokiapi.lokiLabels),
  # path('loki/label',lokiapi.lokiLabelValue),
  # path('loki/query',lokiapi.lokiQuery),
  #   path('loki/queryContext',lokiapi.lokiNearLogQuery)


  # re_path("login/(?P<ok>\d+)",views.LoginView.as_view())

  ]
router = DefaultRouter()
# router.register('user',views.UserViewSet)
# router.register('cmdb/ciModelGroup/',cmdb.ciModelGroup)

router.register('userinfo',views.UserInfoViewSet)
router.register('userGroup',views.UserGroupViewSet)

router.register('role',views.RoleViewSet)
router.register('menu',views.MenuViewSet)
router.register('button',views.ButtonViewSet)

router.register('portal',views.PortalViewSet)
router.register('pgroup',views.PgroupViewSet)
router.register('datasource',views.dataSourceViewSet)
router.register('sysconfig',views.sysConfigViewSet)

# router.register('logModule',views.LogModuleViewSet)


# router.register('permission',views.PermissionViewSet)

# router.register('login',views.LoginView)
urlpatterns += router.urls