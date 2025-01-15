from django.apps import AppConfig
from cacheops import invalidate_all
from django.core.cache import cache
from .utils import password_handler
import logging

logger = logging.getLogger(__name__)


class CMDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    label = 'cmdb'

    def ready(self):
        """应用启动时初始化内置模型和验证规则"""
        import sys
        if 'runserver' in sys.argv or any('celery' in arg for arg in sys.argv) or 'uwsgi' in sys.modules:
            # 清除缓存
            invalidate_all()
            cache.delete('zabbix_token')
            from .utils.zabbix import ZabbixTokenManager
            token_manager = ZabbixTokenManager()
            token_manager.initialize()
            logger.info(f"ZabbixTokenManager initialized")
            password_handler.load_keys()
        from .signals import create_field_meta_for_instances
