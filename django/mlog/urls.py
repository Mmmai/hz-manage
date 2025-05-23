from django.urls import path,include,re_path
from django.conf.urls import url
from . import views
from . import lokiapi
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('loki/labels',lokiapi.lokiLabels),
    path('loki/label',lokiapi.lokiLabelValue),
    path('loki/query',lokiapi.lokiQuery),
    path('loki/queryContext',lokiapi.lokiNearLogQuery),
    path('test',views.test),
    path('logFlow/',views.LogFlowViewSet.as_view()),
    path('logFlow/<str:pk>/',views.LogFlowViewSet.as_view()),
    path('logFlow/stepQuery',lokiapi.lokiStepQuery),
    # 流程查询的任务sse接口
    path('logFlowMission/get_lokiAnalysis_status/<str:task_id>/', lokiapi.get_lokiAnalysis_status, name='get_lokiAnalysis_status'),





  # re_path("login/(?P<ok>\d+)",views.LoginView.as_view())

  ]
router = DefaultRouter()
router.register('logModule',views.LogModuleViewSet)
router.register('logFlowMission',views.LogFlowMissionViewSet)


urlpatterns += router.urls