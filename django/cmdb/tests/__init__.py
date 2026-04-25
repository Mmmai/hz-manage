from unittest.mock import patch, MagicMock
from django.db.models import Q
from rest_framework.test import APITestCase
from mapi.models import UserInfo

# 禁用 CMDB 初始化信号，避免创建内置数据
from django.db.models.signals import post_migrate, post_save, pre_save, pre_delete
from cmdb.signals import (
    initialize_cmdb,
    create_field_meta_for_instances,
    update_instance_name_on_field_change,
    send_model_instance_signal,
    send_model_instance_delete_signal,
    model_instance_signal,
)
from cmdb.models import ModelFields, ModelFieldMeta, ModelInstance

post_migrate.disconnect(initialize_cmdb)
post_save.disconnect(create_field_meta_for_instances, sender=ModelFields)
post_save.disconnect(update_instance_name_on_field_change, sender=ModelFieldMeta)
post_save.disconnect(send_model_instance_signal, sender=ModelInstance, dispatch_uid="sync_to_nodes")
pre_delete.disconnect(send_model_instance_delete_signal, sender=ModelInstance, dispatch_uid="delete_to_nodes")

# 禁用 node_mg 的 sync_node 信号（依赖 ModelConfig）
from node_mg.signals import sync_node
model_instance_signal.disconnect(sync_node)

# 禁用审计信号（避免缺少 request context 导致 NOT NULL 错误）
from audit.signals import capture_old_state, log_changes
post_save.disconnect(log_changes)
pre_save.disconnect(capture_old_state)


class CmdbAPITestCase(APITestCase):
    """CMDB 测试基类：处理认证和权限模拟"""

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = UserInfo.objects.create(
            username='testadmin',
            password='dummy_encrypted',
            password_salt='testsalt',
            status=True,
            built_in=False,
        )

    def setUp(self):
        self.client.force_authenticate(user=self.admin_user)
        # mock 数据权限过滤器（patch where used, not where defined）
        self._scope_patcher = patch(
            'access.backends.get_scope_query',
            return_value=Q()
        )
        self._scope_patcher.start()
        self._pm_patcher = patch(
            'access.manager.PermissionManager.get_queryset',
            side_effect=lambda model_or_qs: (
                model_or_qs if hasattr(model_or_qs, 'filter')
                else model_or_qs.objects.all()
            )
        )
        self._pm_patcher.start()
        self._pw_patcher = patch(
            'access.tools.has_password_permission',
            return_value=False
        )
        self._pw_patcher.start()

    def tearDown(self):
        self._scope_patcher.stop()
        self._pm_patcher.stop()
        self._pw_patcher.stop()
