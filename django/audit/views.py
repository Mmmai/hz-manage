import logging
from rest_framework import viewsets, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q, Case, When, Value, CharField
from django.db import transaction

from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter
from .registry import registry


logger = logging.getLogger(__name__)

class AuditLogPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class CustomAuditSearchFilter(SearchFilter):
    def get_search_fields(self, view, request):
        search_fields = super().get_search_fields(view, request)
        return search_fields + ['action_display']

    def filter_queryset(self, request, queryset, view):
        annotated_queryset = queryset.annotate(
            action_display=Case(
                When(action='CREATE', then=Value('创建')),
                When(action='UPDATE', then=Value('更新')),
                When(action='DELETE', then=Value('删除')),
                default=Value(''), # 提供一个默认值
                output_field=CharField()
            )
        )
        
        return super().filter_queryset(request, annotated_queryset, view)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):    
    queryset = AuditLog.objects.all().select_related('content_type').prefetch_related('details')
    serializer_class = AuditLogSerializer
    pagination_class = AuditLogPagination
    filter_backends = [DjangoFilterBackend, CustomAuditSearchFilter]
    filterset_class = AuditLogFilter
    search_fields = [
        'operator',
        'operator_ip',
        'comment',
        'action',
    ]
    ordering_fields = ['timestamp', 'operator', 'operator_ip','action']
    ordering = ['-timestamp']
        
    @action(detail=False, methods=['get'])
    def history(self, request):
        public_name = request.query_params.get('target_type')
        obj_id = request.query_params.get('object_id')
        include_init = request.query_params.get('include_init', 'false').lower() == 'true'

        if not public_name or not obj_id:
            return Response({"Error": "Parameter target_type and object_id are required."}, status=400)

        try:
            target_model = registry.get_model_by_public_name(public_name)
            if not target_model:
                return Response({"Error": f"Invalid target type: '{public_name}'."}, status=400)

            target_ct = ContentType.objects.get_for_model(target_model)
            target_obj = target_model.objects.get(pk=obj_id)
        except (ValueError, LookupError, ContentType.DoesNotExist, target_model.DoesNotExist):
            return Response({"Error": "Invalid target model or object."}, status=400)

        combined_query = Q()
        # 查询对象自身的日志
        combined_query |= Q(content_type=target_ct, object_id=obj_id)

        # 如果目标是 Models，则聚合其字段和分组的日志
        if public_name == 'model':
            field_ct = ContentType.objects.get(app_label='cmdb', model='modelfields')
            field_group_ct = ContentType.objects.get(app_label='cmdb', model='modelfieldgroups')
            field_ids = target_obj.fields.values_list('pk', flat=True)
            field_ids = [str(field_id) for field_id in field_ids]
            field_group_ids = target_obj.field_groups.values_list('pk', flat=True)
            field_group_ids = [str(field_group_id) for field_group_id in field_group_ids]
            combined_query |= Q(content_type=field_ct, object_id__in=field_ids)
            combined_query |= Q(content_type=field_group_ct, object_id__in=field_group_ids)

        # 如果目标是 ModelInstance，则聚合其分组关联及模型字段的日志
        elif public_name == 'model_instance':
            group_relation_ct = ContentType.objects.get(app_label='cmdb', model='modelinstancegrouprelation')
            group_relation_ids = target_obj.group_relations.values_list('pk', flat=True)
            group_relation_ids = [str(group_relation_id) for group_relation_id in group_relation_ids]
            combined_query |= Q(content_type=group_relation_ct, object_id__in=group_relation_ids)
            field_ct = ContentType.objects.get(app_label='cmdb', model='modelfields')
            field_ids = target_obj.model.fields.values_list('pk', flat=True)
            field_ids = [str(field_id) for field_id in field_ids]
            combined_query |= Q(content_type=field_ct, object_id__in=field_ids, action__in=['CREATE', 'DELETE'])

        # 排除系统初始化审计信息
        if not include_init:
            combined_query &= ~Q(correlation_id='migrate_cmdb_init')

        logger.debug(f"Constructed combined query for history: {combined_query}")
        final_query = AuditLog.objects.filter(combined_query).distinct().order_by('-timestamp')
        logger.debug(f"Final query for history has {final_query.count()} records.")
        page = self.paginate_queryset(final_query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(final_query, many=True)
        return Response(serializer.data)
