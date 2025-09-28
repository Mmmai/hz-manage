import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    """主审计日志表"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlation_id = models.CharField(max_length=100, blank=True, db_index=True)
    action = models.CharField(max_length=20, choices=[('CREATE', '创建'), ('UPDATE', '更新'), ('DELETE', '删除')])

    # 关联的目标对象
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_constraint=False)
    object_id = models.CharField(max_length=255, db_index=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # 变更内容
    changed_fields = models.JSONField(default=dict, blank=True)

    # 操作上下文
    operator = models.CharField(max_length=100, blank=True, db_index=True)
    operator_ip = models.GenericIPAddressField(null=True, blank=True)
    request_id = models.CharField(max_length=100, blank=True, db_index=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'audit_log'
        managed = True
        app_label = 'cmdb'
        ordering = ['-timestamp']


class FieldAuditDetail(models.Model):
    """CMDB动态字段的详细审计记录"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audit_log = models.ForeignKey(AuditLog, on_delete=models.CASCADE, related_name='field_details')

    # 字段信息
    field_id = models.CharField(max_length=100, null=True, blank=True)

    # 变更的值
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    # 字段定义变更
    field_definition_changed = models.BooleanField(default=False)
    old_field_definition = models.JSONField(null=True, blank=True)
    new_field_definition = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'audit_field_detail'
        managed = True
        app_label = 'cmdb'
