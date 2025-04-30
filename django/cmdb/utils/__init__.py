from .crypto import PasswordHandler
from .celery import CeleryManager
from .config_manager import ConfigManager
# 创建单例
password_handler = PasswordHandler()
celery_manager = CeleryManager()
zabbix_config = ConfigManager()

__all__ = ['password_handler', 'celery_manager', 'zabbix_config']
