import logging
from rest_framework import serializers
from .models import AuditLog, FieldAuditDetail
from .registry import registry

logger = logging.getLogger(__name__)
class FieldAuditDetailSerializer(serializers.ModelSerializer):
    """字段级别变更详情的序列化器"""
    
    class Meta:
        model = FieldAuditDetail
        fields = ['name', 'verbose_name', 'old_value', 'new_value']


class AuditLogSerializer(serializers.ModelSerializer):
    """审计日志的序列化器，包含嵌套的字段变更详情"""
    
    details = FieldAuditDetailSerializer(many=True, read_only=True)
    action_display = serializers.SerializerMethodField()
    target_type = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'correlation_id',
            'action',
            'action_display',
            # 'content_type',
            'target_type',
            'object_id',
            'changed_fields',
            'operator',
            'operator_ip',
            'request_id',
            'timestamp',
            'comment',
            'details',
        ]
    
    def get_target_type(self, obj):
        if obj.content_type:
            model_class = obj.content_type.model_class()
            return registry.get_public_name_by_model(model_class)
        return None
    
    def get_action_display(self, obj):
        """返回操作类型的中文显示"""
        action_map = {
            'CREATE': '创建',
            'UPDATE': '更新',
            'DELETE': '删除'
        }
        return action_map.get(obj.action, obj.action)
    