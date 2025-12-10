from .crypto import PasswordHandler
from .celery import CeleryManager
# 创建单例
password_handler = PasswordHandler()
celery_manager = CeleryManager()

__all__ = ['password_handler', 'celery_manager']
