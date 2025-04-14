from django_filters import rest_framework as filters
from .models import AuditLog

class AuditLogFilter(filters.FilterSet):
    action = filters.CharFilter(field_name='action', lookup_expr='icontains')
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    timestamp = filters.DateTimeFromToRangeFilter(field_name='timestamp')

    class Meta:
        model = AuditLog
        fields = ['action', 'user', 'timestamp']