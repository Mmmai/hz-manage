from django_filters import rest_framework as filters
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog
from .registry import registry

class CustomCharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class AuditLogFilter(filters.FilterSet):

    target_type = filters.CharFilter(method='filter_by_target_type')
    operator = filters.CharFilter(field_name='operator', lookup_expr='icontains')
    operator_ip = filters.CharFilter(field_name='operator_ip', lookup_expr='icontains')
    action = CustomCharInFilter(field_name='action', lookup_expr='in')
    object_id = filters.CharFilter(field_name='object_id', lookup_expr='exact')
    time = filters.DateTimeFromToRangeFilter(field_name='timestamp')
    
    
    class Meta:
        model = AuditLog
        fields = [
            'operator',
            'operator_ip',
            'action',
            'object_id',
            'timestamp',
        ]

    def filter_by_target_type(self, queryset, name, value):
        try:
            if not value:
                return queryset
            public_names = [name.strip() for name in value.split(',')]
            models = [registry.get_model_by_public_name(name) for name in public_names]
            content_types = [ContentType.objects.get_for_model(model) for model in models if model]
            return queryset.filter(content_type__in=content_types)
        except ContentType.DoesNotExist:
            return queryset.none()
        