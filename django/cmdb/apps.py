from django.apps import AppConfig
from cacheops import invalidate_all
from django.core.cache import cache
from .utils import password_handler
from .utils.zabbix import ZabbixTokenManager
import sys
import logging
import threading

logger = logging.getLogger(__name__)


class CMDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    label = 'cmdb'

    def ready(self):
        """应用启动时初始化内置模型和验证规则"""
        if 'runserver' in sys.argv or any('celery' in arg for arg in sys.argv) or 'daphne' in sys.modules:
            # 清除缓存
            invalidate_all()
            password_handler.load_keys()

            threading.Thread(target=self._initialize_zabbix, daemon=True).start()
            logger.info("ZabbixTokenManager initialization thread started")

    def _initialize_zabbix(self):
        token_manager = ZabbixTokenManager()
        token_manager.initialize()
        logger.info(f"ZabbixTokenManager initialized")
