from django_filters import rest_framework as filters
# import django_filters as filters
from .models import (
Role,
sysConfigParams
  )

class sysConfigParamsFilter(filters.FilterSet):
    param_name = filters.CharFilter(field_name='param_name',lookup_expr='icontains')
    param_value = filters.CharFilter(field_name='param_value',lookup_expr='icontains')

    # create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    # create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    # update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    # update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = sysConfigParams
        fields = [
            'param_name',
            'param_value',
        ]
class roleFilter(filters.FilterSet):
    role = filters.CharFilter(field_name='role',lookup_expr='icontains')
    class Meta:
        model = Role
        fields = [
            'role',
        ]
        