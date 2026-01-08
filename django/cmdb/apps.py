import sys

from django.apps import AppConfig
from cacheops import invalidate_all
from .utils import password_handler


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
            # 加载密钥
            password_handler.load_keys()
            # 注册权限处理器
            import cmdb.permission_handlers
