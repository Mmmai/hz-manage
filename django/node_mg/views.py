from rest_framework.decorators import action
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework import filters,status
from rest_framework.viewsets import ModelViewSet
from .models import Nodes,Proxy
from rest_framework.decorators import api_view
from cmdb.models import ModelInstance
from .serializers import NodesSerializer,ProxySerializer,ProxyDetailSerializer
from .tasks import (
    ansible_getinfo,
    ansible_getinfo_batch,
    ansible_agent_install,
    ansible_agent_install_batch,
    zabbix_sync_batch,
)
from .utils.cmdb_tools import get_instance_field_value
from .filters import NodesFilter
# Create your views here.
@api_view(['POST'])
def test(request):
    if request.method == 'POST':
        hostIp = request.data.get('ip')
        print(hostIp)
        obj = Nodes.objects.filter(ip_address=hostIp).first()
        print(obj)
        if not obj:
            return JsonResponse({"status": "error", "message": "节点不存在"}, status=status.HTTP_400_BAD_REQUEST)
        test = ansible_getinfo.delay(obj.id)
        print(test) 
        return JsonResponse({"status": "success", "message": "任务已触发"}, status=status.HTTP_200_OK)
    return JsonResponse({"status": "error", "message": "只支持POST请求"}, status=status.HTTP_400_BAD_REQUEST)

 
class NodesViewSet(ModelViewSet):
    #处理外键,1对多,1对1
    queryset = Nodes.objects.select_related('model','model_instance').prefetch_related('node_info_tasks').all()
    # queryset = Nodes.objects.prefetch_related('model_instance', 'publishers')
    serializer_class =  NodesSerializer
    filterset_class = NodesFilter
    # filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    search_fields = ['model_instance__instance_name','ip_address']
    filterset_fields = ['model','enable_sync','proxy','model_instance','ip_address','manage_status','agent_status','zbx_status']
    # pagination_class = StandardResultsSetPagination
    order_fields = ["id"]
    @action(detail=False, methods=['post'])
    def install_agent(self, request):
        """手动触发安装agent"""
        node_id = request.data.get('id', None)
        # print(node_id)
        # all_failed = request.data.get('all', False)
        if node_id:
            # 判断id是否为列表
            if isinstance(node_id, list):
                # print(123)
                task = ansible_agent_install_batch.delay(node_id)
            else:
                task = ansible_agent_install.delay(node_id)
            # task = ansible_agent_install.delay(node_id)
            return JsonResponse({
                    'status': 'success',
                    'message': 'Agent installation task triggered.',
                    'task_id': task.id
                },status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                    'status': 'failed',
                    'message': 'No node_id provided.'
                },status=status.HTTP_400_BAD_REQUEST)  
    @action(detail=False, methods=['post'])
    def get_inventory(self, request):
        """触发资产信息获取"""
        node_id = request.data.get('id', None)
        # all_failed = request.data.get('all', False)
        if node_id:
            # 判断id是否为列表
            if isinstance(node_id, list):
                task = ansible_getinfo_batch.delay(node_id)
            else:
                task = ansible_getinfo.delay(node_id)
            #task = ansible_getinfo.delay(node_id)
            return JsonResponse({
                    'status': 'success',
                    'message': 'Asset information task triggered.',
                    'task_id': task.id
                },status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                    'status': 'failed',
                    'message': 'No node_id provided.'
                },status=status.HTTP_400_BAD_REQUEST) 
    @action(detail=False, methods=['post'])
    def sync_zabbix(self, request):
        """触发资产信息同步zabbix"""
        instance_data_list = []
        model_names = ["hosts", "Switches"]
        
        # 预取所有相关关系避免N+1查询
        queryset = ModelInstance.objects.filter(
            model__name__in=model_names
        )
        try:
            for instance in queryset:
                node = instance.nodes.all().first()
                if instance.model.name == "hosts":
                    if node.enable_sync:
                        try:
                            # 安全访问nodes关系和ip_address属性
                            instance_data_list.append({
                                "instance_id": instance.id, 
                                "ip": node.ip_address
                            })
                        except AttributeError:
                            # 处理nodes或ip_address不存在的情况
                            continue
                else:
                    ip = get_instance_field_value(instance, 'ip')
                    instance_data_list.append({"instance_id": instance.id,"ip":ip})
            zabbix_sync_batch.delay(instance_data_list)
            # print(instance_data_list)
        except Exception as e:
            # 记录异常但不暴露给前端
            print(f"Sync zabbix failed: {str(e)}")
            return HttpResponse("Internal Server Error", status=500)
        
        return HttpResponse("xxx")
    
class ProxyViewSet(ModelViewSet):
    queryset = Proxy.objects.all()
    serializer_class = ProxySerializer
    def get_serializer_class(self):
        if self.action == 'retrieve':  # 单个对象查询
            return ProxyDetailSerializer
        return ProxySerializer