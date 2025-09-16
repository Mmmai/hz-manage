from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework import filters,status
from rest_framework.viewsets import ModelViewSet
from .models import Nodes
from rest_framework.decorators import api_view

from .serializers import NodesSerializer
from .tasks import ansible_getinfo
from .filters import NodesFilter
# Create your views here.
class NodesViewSet(ModelViewSet):
    #处理外键,1对多,1对1
    queryset = Nodes.objects.select_related('model','model_instance').prefetch_related(
    'node_info_tasks').all()
    # queryset = Nodes.objects.prefetch_related('model_instance', 'publishers')
    serializer_class =  NodesSerializer
    filterset_class = NodesFilter
    # filter_backends = [filters.OrderingFilter,filters.SearchFilter]
    search_fields = ['model_instance__instance_name','ip_address']
    filterset_fields = ['model','enable_sync','proxy','model_instance','ip_address','node_info_tasks__status']
    # pagination_class = StandardResultsSetPagination
    order_fields = ["id"]

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

