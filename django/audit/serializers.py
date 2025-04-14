from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models.audit import AuditLog

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志基本信息序列化器"""
    user = UserSerializer(read_only=True)
    action_display = serializers.SerializerMethodField()
    field_count = serializers.SerializerMethodField()
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_verbose_name = serializers.CharField(source='model.verbose_name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'request_id', 'timestamp', 'user', 'user_ip',
            'model_name', 'model_verbose_name', 'instance_id', 'instance_name',
            'action', 'action_display', 'field_count',
            'comment', 'reverted', 'can_revert'
        ]

    def get_action_display(self, obj):
        """获取操作类型的显示名称"""
        return dict(obj.ACTION_CHOICES).get(obj.action, obj.action)

    def get_field_count(self, obj):
        """获取变更字段数量"""
        return obj.get_field_count()


class AuditLogDetailSerializer(AuditLogSerializer):
    """审计日志详细信息序列化器"""
    changes_summary = serializers.SerializerMethodField()
    reverted_by = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = AuditLogSerializer.Meta.fields + [
            'changes_summary', 'changes', 'snapshot_before', 'snapshot_after',
            'reverted_by', 'reverted_time'
        ]

    def get_changes_summary(self, obj):
        """获取变更摘要信息"""
        return obj.get_changes_summary()
