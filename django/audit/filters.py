from django_filters import rest_framework as filters
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


class AuditLogFilter(filters.FilterSet):
    """审计日志的过滤器"""
    
    # 时间范围过滤
    start_time = filters.DateTimeFilter(
        field_name="create_time", 
        lookup_expr='gte',
        help_text="开始时间 (格式: 2025-10-17T00:00:00Z)"
    )
    end_time = filters.DateTimeFilter(
        field_name="create_time", 
        lookup_expr='lte',
        help_text="结束时间 (格式: 2025-10-17T23:59:59Z)"
    )
    
    # 按模型类型过滤
    content_type = filters.CharFilter(
        method='filter_by_content_type',
        help_text="模型类型 (格式: app_label.model，例如 cmdb.model)"
    )
    
    # 操作员模糊搜索
    operator = filters.CharFilter(
        field_name='operator',
        lookup_expr='icontains',
        help_text="操作员用户名（支持模糊搜索）"
    )

    class Meta:
        model = AuditLog
        fields = {
            'action': ['exact'],
            'object_id': ['exact'],
        }

    def filter_by_content_type(self, queryset, name, value):
        """
        自定义过滤器，支持 'app.model' 格式的字符串或 ContentType ID。
        """
        if not value:
            return queryset
        
        try:
            if '.' in value:
                app_label, model = value.lower().split('.')
                ct = ContentType.objects.get(app_label=app_label, model=model)
                return queryset.filter(content_type=ct)
            else:
                return queryset.filter(content_type_id=int(value))
        except (ContentType.DoesNotExist, ValueError):
            return queryset.none()