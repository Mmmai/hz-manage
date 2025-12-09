from django.apps import AppConfig


class AuditConfig(AppConfig):
    name = "audit"
    verbose_name = "Audit"

    def ready(self):
        # 导入 signals
        import audit.signals