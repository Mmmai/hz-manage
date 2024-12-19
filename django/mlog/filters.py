from django_filters import rest_framework as filters
from .models import (
    LogModule,
    LogFlow,
    LogFlowModule,
    LogFlowMission
  )



class LogFlowMissionFilter(filters.FilterSet):
    user_id = filters.CharFilter(field_name='user_id')
    username = filters.CharFilter(field_name='username')
    flow_id = filters.CharFilter(field_name='flow_id')
    task_id = filters.CharFilter(field_name='task_id', lookup_expr='icontains')
    dataSource_id = filters.CharFilter(field_name='dataSource_id')
    status = filters.BooleanFilter(field_name='editable')
    # create_time_after = filters.DateTimeFilter(field_name='create_time', lookup_expr='gte')
    # create_time_before = filters.DateTimeFilter(field_name='create_time', lookup_expr='lte')
    # update_time_after = filters.DateTimeFilter(field_name='update_time', lookup_expr='gte')
    # update_time_before = filters.DateTimeFilter(field_name='update_time', lookup_expr='lte')

    class Meta:
        model = LogFlowMission
        fields = [
            'user_id',
            'username',
            'flow_id',
            'task_id',
            'dataSource_id',
            'status',
            # 'create_time_after',
            # 'create_time_before',
            # 'update_time_after',
            # 'update_time_before',
        ]
        