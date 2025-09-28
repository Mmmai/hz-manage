from operator import is_
from django.apps import AppConfig
from cacheops import invalidate_all
from django.core.cache import cache
from .utils import password_handler, zabbix_config
from .utils.zabbix import ZabbixTokenManager
import sys
import logging
import threading

logger = logging.getLogger(__name__)


class CmdbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'

    def ready(self):
        """应用启动时加载密钥及zabbix相关实例"""
        import cmdb.signals

        if 'runserver' in sys.argv or any(
                'celery' in arg for arg in sys.argv) or 'daphne' in sys.modules or '--host' in sys.argv:
            # 清除缓存
            invalidate_all()
            password_handler.load_keys()
            zabbix_config.load_config()

            if zabbix_config.is_zabbix_sync_enabled():
                token_manager = ZabbixTokenManager()
                token_manager.initialize()
                logger.info(f'Zabbix token manager initialized')
            else:
                logger.warning(f'Zabbix synchronization is disabled')

            from audit.registry import registry
            from .models import ModelGroups, Models, ModelFields, ModelInstance, ModelFieldMeta

            # 注册模式变更审计
            registry.register_schema(ModelGroups, ignore_fields=['updated_at', 'created_at'])
            registry.register_schema(Models, ignore_fields=['updated_at', 'created_at'])
            registry.register_schema(ModelFields, ignore_fields=['updated_at', 'created_at'])

            # 注册实例变更审计（特别标记为字段感知）
            registry.register_field_aware(
                model=ModelInstance,
                field_definition_model=ModelFields,
                field_value_model=ModelFieldMeta,
                instance_field_name='model_instance'
            )
            from audit import signals as audit_signals
