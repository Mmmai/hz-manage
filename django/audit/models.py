from django.db import models


class AuditLog(models.Model):
    """CMDB 审计日志模型 - 优化事务设计"""

    # 操作类型
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_CHOICES = (
        (ACTION_CREATE, '创建'),
        (ACTION_UPDATE, '更新'),
        (ACTION_DELETE, '删除'),
    )

    # 基本信息
    id = models.AutoField(primary_key=True)
    request_id = models.UUIDField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    user_ip = models.GenericIPAddressField(null=True, blank=True)

    # 实例相关
    # 使用字符串引用避免循环导入
    model = models.ForeignKey('cmdb.Models', on_delete=models.CASCADE, verbose_name='模型')
    instance_id = models.CharField(max_length=100, verbose_name='实例ID')
    instance_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='实例名称')

    # 操作信息
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    comment = models.TextField(blank=True, verbose_name='备注')

    # 变更内容 - 存储整个事务的全部变更
    changes = models.JSONField(default=dict, verbose_name='变更详情')  # 存储所有字段变更
    snapshot_before = models.JSONField(null=True, blank=True, verbose_name='操作前快照')
    snapshot_after = models.JSONField(null=True, blank=True, verbose_name='操作后快照')

    # 撤销相关
    can_revert = models.BooleanField(default=False, verbose_name='是否可撤销')
    reverted = models.BooleanField(default=False, verbose_name='是否已被撤销')
    reverted_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reverted_logs', verbose_name='撤销用户'
    )
    reverted_time = models.DateTimeField(null=True, blank=True, verbose_name='撤销时间')

    class Meta:
        db_table = 'cmdb_audit_log'
        verbose_name = '审计日志'
        verbose_name_plural = '审计日志'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model', 'instance_id'], name='audit_model_instance_idx'),
            models.Index(fields=['user'], name='audit_user_idx'),
            models.Index(fields=['action'], name='audit_action_idx'),
            models.Index(fields=['timestamp'], name='audit_timestamp_idx'),
            models.Index(fields=['request_id'], name='audit_request_id_idx'),
        ]

    def __str__(self):
        action_display = dict(self.ACTION_CHOICES).get(self.action, self.action)
        return f"{action_display}-{self.model.name}-{self.instance_name or self.instance_id}"

    def get_changes_summary(self):
        """获取变更摘要信息"""
        if not self.changes:
            return []

        result = []
        for field_name, change in self.changes.items():
            # 获取字段显示名称
            field_verbose = change.get('verbose_name', field_name)

            # 敏感字段处理
            old_value = change.get('old_value')
            new_value = change.get('new_value')
            if field_name.endswith('password') and old_value:
                old_value = '******'
            if field_name.endswith('password') and new_value:
                new_value = '******'

            result.append({
                'field': field_name,
                'field_verbose': field_verbose,
                'old_value': old_value,
                'new_value': new_value,
                'group': change.get('group', '基本信息')
            })

        return result

    def get_field_count(self):
        """获取变更字段数量"""
        return len(self.changes) if self.changes else 0
