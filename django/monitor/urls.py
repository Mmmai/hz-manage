from django.urls import path,include,re_path
from django.conf.urls import url
from . import views
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('zabbix_api/',views.ZabbixData.as_view()),
]

# urlpatterns += router.urls