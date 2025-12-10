from django_filters import rest_framework as filters
from .models import Nodes,NodeTasks
from django.db.models import OuterRef, Subquery



class NodesFilter(filters.FilterSet):
    # 精确匹配
    enable_sync = filters.BooleanFilter(field_name='enable_sync', lookup_expr='exact')    
    # 模糊匹配
    model_name = filters.CharFilter(field_name='model__name', lookup_expr='icontains')
    ip_address = filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    model_instance_name = filters.CharFilter(field_name='model_instance__instance_name', lookup_expr='icontains')
    # status = filters.NumberFilter(field_name='node_info_tasks__status', lookup_expr='exact')
    manage_status = filters.CharFilter(method='filter_latest_get_system_info_status')
    agent_status = filters.CharFilter(method='filter_latest_zabbix_agent_install_status')

    # manage_status__in = filters.BaseCSVFilter(method='filter_latest_status_in', lookup_expr='in')
    # agent_status = filters.BaseCSVFilter(field_name='node_sync_zabbix__agent_status', lookup_expr='in')    
    # zbx_status = filters.BaseCSVFilter(field_name='node_sync_zabbix__zbx_status', lookup_expr='in')    
    # 范围查询
    # price_range = filters.NumericRangeFilter(field_name='price')


    class Meta:
        model = Nodes
        fields = ['ip_address', 'model_instance_name','enable_sync','model_name','proxy','model_instance']
    def filter_latest_get_system_info_status(self, queryset, name, value):
        # 子查询：获取每个 NodeInfo 的最新任务状态
        latest_task_subquery = NodeTasks.objects.filter(
            node=OuterRef('pk'),task_name='get_system_info'
        ).order_by('-created_at').values('status')[:1]  # 取第一条（最新）

        # 注解主查询，将子查询结果映射为 latest_status
        return queryset.annotate(
            latest_status=Subquery(latest_task_subquery)
        ).filter(latest_status__in=[v.strip() for v in value.split(',')])
    def filter_latest_zabbix_agent_install_status(self, queryset, name, value):
          # 子查询：获取每个 NodeInfo 的最新任务状态
          latest_task_subquery = NodeTasks.objects.filter(
              node=OuterRef('pk'),task_name='zabbix_agent_install'
          ).order_by('-created_at').values('status')[:1]  # 取第一条（最新）    
          # 注解主查询，将子查询结果映射为 latest_status
          return queryset.annotate(
              latest_status=Subquery(latest_task_subquery)
          ).filter(latest_status__in=[v.strip() for v in value.split(',')])


class NodeTasksFilter(filters.FilterSet):
    node_name = filters.CharFilter(field_name='node__model_instance__instance_name', lookup_expr='icontains')
    node_ip = filters.CharFilter(field_name='node__ip_address', lookup_expr='icontains')
    task_name = filters.CharFilter(field_name='task_name', lookup_expr='icontains')
    status = filters.CharFilter()

    class Meta:
        model = NodeTasks
        fields = ['node_name', 'node_ip','task_name','status']