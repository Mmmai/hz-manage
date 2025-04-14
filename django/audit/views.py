from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogDetailSerializer
from .revert import revert_audit_log, RevertException


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    审计日志视图集
    提供查询和撤销功能
    """
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AuditLogDetailSerializer
        return AuditLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # 筛选请求ID - 同一个操作的所有变更
        request_id = self.request.query_params.get('request_id')
        if request_id:
            queryset = queryset.filter(request_id=request_id)

        # 筛选指定模型
        model_id = self.request.query_params.get('model_id')
        if model_id:
            queryset = queryset.filter(model_id=model_id)

        # 筛选指定实例ID
        instance_id = self.request.query_params.get('instance_id')
        if instance_id:
            queryset = queryset.filter(instance_id=instance_id)

        # 筛选指定操作类型
        action_type = self.request.query_params.get('action')
        if action_type:
            queryset = queryset.filter(action=action_type)

        # 筛选时间范围
        start_time = self.request.query_params.get('start_time')
        if start_time:
            queryset = queryset.filter(timestamp__gte=start_time)

        end_time = self.request.query_params.get('end_time')
        if end_time:
            queryset = queryset.filter(timestamp__lte=end_time)

        # 筛选指定用户
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # 是否筛选可撤销的
        revertable = self.request.query_params.get('revertable')
        if revertable == 'true':
            queryset = queryset.filter(can_revert=True, reverted=False)

        # 搜索操作
        search = self.request.query_params.get('search')
        if search:
            model_field_name = 'model__name'
            model_verbose_field = 'model__verbose_name'

            queryset = queryset.filter(
                Q(**{f'{model_field_name}__icontains': search}) |
                Q(**{f'{model_verbose_field}__icontains': search}) |
                Q(instance_id__icontains=search) |
                Q(instance_name__icontains=search) |
                Q(comment__icontains=search)
            )

        return queryset

    @action(detail=True, methods=['post'])
    def revert(self, request, pk=None):
        """撤销操作"""
        audit_log = self.get_object()

        if not audit_log.can_revert:
            return Response(
                {"detail": "此操作不可撤销"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if audit_log.reverted:
            return Response(
                {"detail": "此操作已被撤销"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = revert_audit_log(audit_log.id)
            return Response(
                {"detail": "操作已成功撤销", "success": True},
                status=status.HTTP_200_OK
            )
        except RevertException as e:
            return Response(
                {"detail": str(e), "success": False},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def instance_history(self, request):
        """获取指定实例的历史记录"""
        model_id = request.query_params.get('model_id')
        instance_id = request.query_params.get('instance_id')

        if not model_id or not instance_id:
            return Response(
                {"detail": "缺少必要参数 model_id 或 instance_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = self.queryset.filter(
            model_id=model_id,
            instance_id=instance_id
        ).order_by('-timestamp')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def changes_detail(self, request, pk=None):
        """获取特定审计日志的字段变更详情"""
        audit_log = self.get_object()
        changes = audit_log.get_changes_summary()

        # 按字段组分组展示
        grouped_changes = {}
        for change in changes:
            group = change.get('group', '基本信息')
            if group not in grouped_changes:
                grouped_changes[group] = []
            grouped_changes[group].append(change)

        return Response({
            'field_count': len(changes),
            'grouped_changes': grouped_changes
        })
