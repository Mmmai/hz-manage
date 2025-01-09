from django.apps import AppConfig
from cacheops import invalidate_all
from .utils import password_handler
import logging

logger = logging.getLogger(__name__)

class CMDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    label = 'cmdb'
    
    def ready(self):
        """应用启动时初始化内置模型和验证规则"""
        try:
            import sys
            if any(keyword in sys.argv for keyword in ['makemigrations', 'migrate', 'test', 'shell']):
                return
            elif 'runserver' in sys.argv:
                # 清除缓存
                invalidate_all()
        import sys
        if 'runserver' in sys.argv:
            # 清除缓存
            invalidate_all()
            
            # from .utils.zabbix import ZabbixTokenManager
            
            # config = {
            #     'url': 'http://192.168.137.2/zabbix/api_jsonrpc.php',
            #     'username': 'Admin',
            #     'password': 'zabbix',
            #     'interval': 0
            # }
            # if config:
            #     token_manager = ZabbixTokenManager()
            #     token_manager.initialize(config)
            #     logger.info("Zabbix token manager initialized")

            
            password_handler.load_keys()
            
        
        from .signals import create_field_meta_for_instances
        
