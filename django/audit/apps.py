from django.apps import AppConfig


class AuditConfig(AppConfig):
    name = "audit"
    verbose_name = "Audit"

    def ready(self):
        from audit.registry import registry
        from cmdb.models import CmdbAttributeDef, CmdbObject
        # 注册需要审计的模型
        registry.register_schema(CmdbAttributeDef, ignore_fields={"version", "updated_at"})
        registry.register_instance(CmdbObject, ignore_fields={"updated_at"})
        # 导入 signals
        import audit.signals
