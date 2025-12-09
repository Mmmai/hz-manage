from rest_framework.decorators import action
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import filters, status
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Nodes, Proxy, NodeInfoTask, ModelConfig
from rest_framework.decorators import api_view
from cmdb.models import ModelInstance
from django.db.models import Q, OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from audit.context import audit_context
from audit.mixins import AuditContextMixin
from .serializers import NodesSerializer, ProxySerializer, ProxyDetailSerializer, ModelConfigSerializer
from .tasks import (
    ansible_getinfo,
    ansible_getinfo_batch,
    ansible_agent_install,
    ansible_agent_install_batch,
    zabbix_sync_batch,
    zabbix_proxy_sync
)
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


class NodesViewSet(AuditContextMixin, ModelViewSet):
    """
    节点信息视图集，用于管理节点信息的增删改查操作

    该视图集提供了对节点信息的完整RESTful API操作，包括：
    - 列出所有节点信息
    - 创建新的节点
    - 更新现有节点信息
    - 删除节点
    - 根据条件过滤和搜索节点

    属性:
        queryset: 查询集，包含所有节点信息，并通过select_related和prefetch_related优化数据库查询
        serializer_class: 序列化器类，用于节点信息的序列化和反序列化
        filterset_class: 过滤器类，用于节点信息的过滤
        search_fields: 搜索字段，支持按实例名称和IP地址搜索
        filterset_fields: 过滤字段，支持按模型、同步状态、代理、实例、IP地址、管理状态、代理状态和zabbix状态过滤
        order_fields: 排序字段，支持按ID排序
    """
    # 处理外键,1对多,1对1
    queryset = Nodes.objects.select_related('model', 'model_instance').prefetch_related('node_info_tasks').all()
    serializer_class = NodesSerializer
    filterset_class = NodesFilter
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    # search_fields = ['model_instance__instance_name','ip_address','proxy__name']
    filterset_fields = ['model', 'enable_sync', 'proxy', 'model_instance',
                        'ip_address', 'manage_status', 'agent_status', 'zbx_status']
    # pagination_class = StandardResultsSetPagination
    # order_fields = ["id"]

    def get_queryset(self):
        """
        重写get_queryset方法，支持对manage_error_message和agent_error_message的搜索
        """
        queryset = super().get_queryset()
        # 获取搜索参数
        search_term = self.request.query_params.get('search', None)

        # 如果有搜索参数，且在普通字段中没有匹配结果，则尝试搜索错误消息字段
        if search_term:
            # 子查询：获取每个节点的最新NodeInfoTask错误消息
            latest_manage_error_subquery = NodeInfoTask.objects.filter(
                node=OuterRef('pk')
            ).order_by('-created_at').values('error_message')[:1]
            # 注解查询集，添加最新的错误消息字段
            queryset = queryset.annotate(
                latest_manage_error=Subquery(latest_manage_error_subquery),
            )
            # 先检查是否在普通搜索字段中匹配
            queryset = queryset.filter(
                Q(model_instance__instance_name__icontains=search_term) |
                Q(ip_address__icontains=search_term) |
                Q(proxy__name__icontains=search_term) |
                Q(node_info_tasks__error_message__icontains=search_term) |
                Q(node_sync_zabbix__error_message__icontains=search_term)
            ).distinct()
        return queryset

    @action(detail=False, methods=['get'], pagination_class=None)
    def list_all_nodes(self, request):
        """
        返回所有节点的部分字段信息，不受分页影响

        此接口返回所有节点的简化信息，包括：
        - id: 节点ID
        - ip_address: IP地址
        - model_instance_name: 模型实例名称
        返回格式:
        [
            {
                "id": "uuid",
                "ip_address": "192.168.1.1",
                "instance_name": "server01",
                "proxy_id": "proxy01id"
            },
            ...
        ]
        """
        model = request.query_params.get('model', None)
        if not model:
            return JsonResponse({"status": "error", "message": "请指定模型"}, status=status.HTTP_400_BAD_REQUEST)
        # 指定model获取node
        queryset = Nodes.objects.filter(model=model)
        # 获取所有节点数据
        queryset = self.filter_queryset(self.get_queryset())
        # 选择需要的字段
        nodes_data = queryset.values(
            'id',
            'ip_address',
            'model_instance__instance_name',
            'model_instance',
            'model',
            'proxy'
        )

        # 处理状态字段，需要从关联对象中获取最新状态
        result = []
        for node in nodes_data:
            result.append({
                'id': node['id'],
                'ip_address': node['ip_address'],
                'model_instance': node['model_instance'],
                'instance_name': node['model_instance__instance_name'],
                "model_id": node['model'],
                "proxy_id": node['proxy'],

            })

        return JsonResponse(result, safe=False)

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
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'No node_id provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def get_inventory(self, request):
        """触发资产信息获取"""
        #
        audit_context = self.get_audit_context()
        node_id = request.data.get('id', None)
        # all_failed = request.data.get('all', False)
        if node_id:
            # 判断id是否为列表
            if isinstance(node_id, list):
                task = ansible_getinfo_batch.delay(node_id, audit_context)
            else:
                task = ansible_getinfo.delay(node_id, audit_context)
            # task = ansible_getinfo.delay(node_id)
            return JsonResponse({
                'status': 'success',
                'message': 'Asset information task triggered.',
                'task_id': task.id
            }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                'status': 'failed',
                'message': 'No node_id provided.'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def sync_zabbix(self, request):
        """触发资产信息同步zabbix"""
        instance_data_list = []

        # 获取请求参数
        node_id = request.data.get('node_id')
        model_name = request.data.get('model_name')

        # 如果提供了node_id，则只同步单个节点
        if node_id:
            try:
                node = Nodes.objects.select_related('model_instance__model').get(id=node_id)
                if node.enable_sync:
                    instance_data_list.append({
                        "instance_id": node.model_instance.id,
                        "ip": node.ip_address
                    })
            except Nodes.DoesNotExist:
                return HttpResponse("Node not found", status=404)
        # 如果提供了model_name，则同步整个模型的所有节点
        elif model_name:
            model_names = [model_name]
            queryset = ModelInstance.objects.filter(
                model__name__in=model_names
            ).prefetch_related('nodes')

            for instance in queryset:
                node = instance.nodes.all().first()
                if node.enable_sync:
                    instance_data_list.append({
                        "instance_id": node.model_instance.id,
                        "ip": node.ip_address
                    })
        # 如果没有提供参数，则同步默认模型的所有节点
        else:
            model_names = [i.model.name for i in ModelConfig.objects.filter(is_manage=True)]
            queryset = ModelInstance.objects.filter(
                model__name__in=model_names
            ).prefetch_related('nodes')

            for instance in queryset:
                node = instance.nodes.all().first()
                if node.enable_sync:
                    instance_data_list.append({
                        "instance_id": node.model_instance.id,
                        "ip": node.ip_address
                    })

        if instance_data_list:
            zabbix_sync_batch.delay(instance_data_list)
        else:
            return HttpResponse("No instances to sync", status=400)

        return HttpResponse("Sync task triggered successfully")

    @action(detail=False, methods=['post'])
    def associate_proxy(self, request):
        """
        批量为Nodes关联Proxy

        请求参数:
        - ids: Node ID列表
        - proxy_id: 要关联的Proxy ID

        示例请求:
        POST /nodes/associate_proxy/
        {
            "ids": ["node_id_1", "node_id_2", "..."],
            "proxy_id": "proxy_id"
        }
        """
        instance_ids = request.data.get('ids', [])
        proxy_id = request.data.get('proxy_id')

        if not instance_ids:
            return JsonResponse(
                {'error': 'ids参数不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not proxy_id:
            return JsonResponse(
                {'error': 'proxy_id参数不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 验证proxy是否存在
        try:
            proxy = Proxy.objects.get(id=proxy_id)
        except Proxy.DoesNotExist:
            return JsonResponse(
                {'error': f'Proxy ID {proxy_id} 不存在'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 批量更新Nodes的proxy字段
        # updated_count = Nodes.objects.filter(id__in=node_ids).update(proxy=proxy)
        nodesObj = Nodes.objects.filter(model_instance__id__in=instance_ids)
        # 获取node_ids
        node_ids = list(nodesObj.values_list('id', flat=True))
        updated_count = nodesObj.update(proxy=proxy)
        # 批量更新zabbix的proxy
        proxy_info = {
            "proxy_name": proxy.name,
            "proxy_ip": proxy.ip_address,
            "proxy_type": proxy.proxy_type,
            "proxy_status": proxy.enabled,
        }
        zabbix_proxy_sync.delay(proxy_info, action="associate_host", node_ids=node_ids)
        return JsonResponse(
            {
                'message': f'成功为{updated_count}个节点关联代理{proxy.name}',
                'updated_count': updated_count
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def dissociate_proxy(self, request):
        """
        批量为Nodes解除Proxy关联

        请求参数:
        - ids: Node ID列表

        示例请求:
        POST /nodes/dissociate_proxy/
        {
            "ids": ["node_id_1", "node_id_2", "..."]
        }
        """
        instance_ids = request.data.get('ids', [])
        proxy_id = request.data.get('proxy_id')

        if not instance_ids:
            return JsonResponse(
                {'error': 'ids参数不能为空'},
                status=status.HTTP_400_BAD_REQUEST
            )
        proxy = Proxy.objects.get(id=proxy_id)
        proxy_info = {
            "proxy_name": proxy.name,
            "proxy_ip": proxy.ip_address,
            "proxy_type": proxy.proxy_type,
            "proxy_status": proxy.enabled,
        }
        # 批量将Nodes的proxy字段设为NULL
        # updated_count = Nodes.objects.filter(id__in=node_ids).update(proxy=None)
        nodesObj = Nodes.objects.filter(model_instance__id__in=instance_ids)
        node_ids = list(nodesObj.values_list('id', flat=True))
        updated_count = nodesObj.update(proxy=None)
        zabbix_proxy_sync.delay(proxy_info=proxy_info, action="dissociate_host", node_ids=node_ids)

        return JsonResponse(
            {
                'message': f'成功为{updated_count}个节点解除代理关联',
                'updated_count': updated_count
            },
            status=status.HTTP_200_OK
        )


class ProxyViewSet(ModelViewSet):
    queryset = Proxy.objects.all()
    serializer_class = ProxySerializer

    def get_serializer_class(self):
        if self.action == 'retrieve':  # 单个对象查询
            return ProxyDetailSerializer
        return ProxySerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # 检查是否有节点关联到此代理
        if instance.nodes.exists():
            return JsonResponse(
                {"error": "无法删除代理，因为还有节点关联到此代理"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class ModelConfigViewSet(ModelViewSet):
    queryset = ModelConfig.objects.all()
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    serializer_class = ModelConfigSerializer
    filterset_fields = ['model']
    ordering_fields = ['id', 'model', 'create_time', 'updated_time']


class zabbixApi(APIView):
    """
    Zabbix API接口类
    """

    def get(self, request):
        """
        获取Zabbix模板列表
        """
        try:
            # 导入ZabbixAPI工具类
            from .utils.zabbix import ZabbixAPI
            # 创建ZabbixAPI实例
            zapi = ZabbixAPI()
            result = zapi.get_all_templates()
            if result:
                # 检查结果并返回
                templates = [{"label": i["host"], "value":i["templateid"]} for i in result]
                templates = [{"label": i["host"], "value":i["host"]} for i in result]

                return JsonResponse({
                    'code': 200,
                    'data': templates,
                    'message': 'success'
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    'code': 500,
                    'message': 'Failed to get templates from Zabbix',
                    'data': result.get('error', {})
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return JsonResponse({
                'code': 500,
                'message': f'Error occurred: {str(e)}',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
