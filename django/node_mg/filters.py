import django_filters
from .models import Nodes,NodeInfoTask
from django.db.models import OuterRef, Subquery

class NodesFilter(django_filters.FilterSet):
    # 精确匹配
    enable_sync = django_filters.BooleanFilter(field_name='enable_sync', lookup_expr='exact')    
    # 模糊匹配
    ip_address = django_filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    model_instance_name = django_filters.CharFilter(field_name='model_instance__instance_name', lookup_expr='icontains')
    # status = django_filters.NumberFilter(field_name='node_info_tasks__status', lookup_expr='exact')
    status = django_filters.NumberFilter(method='filter_latest_status', lookup_expr='exact')
    # 范围查询
    # price_range = django_filters.NumericRangeFilter(field_name='price')


    class Meta:
        model = Nodes
        fields = ['ip_address', 'model_instance_name','enable_sync','model','proxy','model_instance','status']
    def filter_latest_status(self, queryset, name, value):
        # 子查询：获取每个 NodeInfo 的最新任务状态
        latest_task_subquery = NodeInfoTask.objects.filter(
            node=OuterRef('pk')
        ).order_by('-created_at').values('status')[:1]  # 取第一条（最新）

        # 注解主查询，将子查询结果映射为 latest_status
        return queryset.annotate(
            latest_status=Subquery(latest_task_subquery)
        ).filter(latest_status=value)