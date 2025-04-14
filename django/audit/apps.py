from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'audit'
    verbose_name = '审计日志'

    def ready(self):
        """应用启动时执行的初始化代码"""
        # 导入信号处理器
        # 未来可以在此处添加信号处理来自动审计记录，现在先用装饰器实现
        pass
