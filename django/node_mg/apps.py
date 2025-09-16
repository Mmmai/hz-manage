from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError
from django.apps import apps

class NodeMgConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'node_mg'
    def ready(self):
        try:
            import sys
            import node_mg.signals
            # if any(keyword in sys.argv for keyword in ['makemigrations', 'migrate', 'test', 'shell']):
            #     return        
            post_migrate.connect(self.init_script, sender=self)   
            # init_script() 
            #信号接收
            # cmdb_app = apps.get_app_config('cmdb')
            # print(cmdb_app)
            # cmdb_app.signals.cmdb_signal.connect(create_node)


        except OperationalError:
            pass
        except Exception as e:
            raise 
    # 初始化数据
    def init_script(self,sender,**kwargs):
        from .tasks import sync_node_mg
        print("初始化接节点管理平台")
        task = sync_node_mg.delay()
        