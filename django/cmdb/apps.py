from operator import is_
from django.apps import AppConfig
from cacheops import invalidate_all
from django.core.cache import cache
from .utils import password_handler
from node_mg.utils import sys_config
from node_mg.utils.zabbix import ZabbixTokenManager
import sys
import threading
import logging
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
            import cmdb.permission_handlers
