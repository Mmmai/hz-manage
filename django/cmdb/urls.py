from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'model_groups', ModelGroupsViewSet)
router.register(r'models', ModelsViewSet)
router.register(r'model_field_groups', ModelFieldGroupsViewSet)
router.register(r'validation_rules', ValidationRulesViewSet)
router.register(r'model_fields', ModelFieldsViewSet)
router.register(r'model_field_preference', ModelFieldPreferenceViewSet)
router.register(r'unique_constraint', UniqueConstraintViewSet)
router.register(r'model_instance', ModelInstanceViewSet)
router.register(r'model_ref', ModelInstanceBasicViewSet, basename='model_ref')
router.register(r'model_field_meta', ModelFieldMetaViewSet)
router.register(r'model_instance_group', ModelInstanceGroupViewSet)
router.register(r'model_instance_group_relation', ModelInstanceGroupRelationViewSet)
router.register(r'relation_definition', RelationDefinitionViewSet)
router.register(r'relations', RelationsViewSet)
router.register(r'password_manage', PasswordManageViewSet, basename='password_manage')
router.register(r'zabbix_sync_host', ZabbixSyncHostViewSet, basename='zabbix_sync_host')
router.register(r'zabbix_proxy', ZabbixProxyViewSet, basename='zabbix_proxy')
router.register(r'proxy_assign_rule', ProxyAssignRuleViewSet, basename='proxy_assign_rule')

urlpatterns = [
    path('', include(router.urls)),
]
