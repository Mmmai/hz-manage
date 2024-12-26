from django_filters import rest_framework as filters
from .models import (
sysConfigParams
  )

class sysConfigParamsFilter(filters.FilterSet):
    param_name = filters.CharFilter(field_name='user_id',lookup_expr='icontains')
    param_value = filters.CharFilter(field_name='username',lookup_expr='icontains')

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
        