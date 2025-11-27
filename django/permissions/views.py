import logging
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import DataScope
from .serializers import DataScopeSerializer

logger = logging.getLogger(__name__)


class DataScopeViewSet(ModelViewSet):
    queryset = DataScope.objects.all().prefetch_related('targets', 'targets__content_type')
    serializer_class = DataScopeSerializer
    filterset_fields = ['role', 'user', 'user_group', 'scope_type']
    search_fields = ['description']
    ordering_fields = ['create_time', 'update_time']

    def _format_response_data(self, data, targets_map):
        if isinstance(data, list):
            for item in data:
                item['targets_detail'] = targets_map.get(item.get('id'), {})
        else:
            data['targets_detail'] = targets_map.get(data.get('id'), {})
        return data

    def _get_targets_detail_map(self, queryset):
        logger.debug(f'Building targets detail map for queryset of size: {len(queryset)}')
        targets_map = {}
        for scope in queryset:
            logger.debug(f'Processing DataScope ID: {scope.id} for targets detail mapping')
            detail = {}
            for target in scope.targets.all():
                key = f"{target.content_type.app_label}.{target.content_type.model}"
                detail.setdefault(key, []).append(str(target.object_id))
                logger.debug(f'Added target {str(target.object_id)} under key {key} for DataScope ID: {scope.id}')
            targets_map[str(scope.id)] = detail

        logger.debug(f'Constructed targets detail map: {targets_map}')
        return targets_map

    def _get_targets_detail(self, instance):
        targets_detail = {}
        for target in instance.targets.all():
            key = f"{target.content_type.app_label}.{target.content_type.model}"
            targets_detail.setdefault(key, []).append(str(target.object_id))
        return targets_detail

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            targets_map = self._get_targets_detail_map(page)
            formatted_data = self._format_response_data(serializer.data, targets_map)
            return self.get_paginated_response(formatted_data)

        serializer = self.get_serializer(queryset, many=True)
        targets_map = self._get_targets_detail_map(queryset)
        formatted_data = self._format_response_data(serializer.data, targets_map)
        return Response(formatted_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        targets_map = self._get_targets_detail_map([instance])
        formatted_data = self._format_response_data(serializer.data, targets_map)
        return Response(formatted_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = serializer.instance
        response_serializer = self.get_serializer(instance)
        targets_map = self._get_targets_detail_map([instance])
        formatted_data = self._format_response_data(response_serializer.data, targets_map)

        headers = self.get_success_headers(formatted_data)
        return Response(formatted_data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_serializer(instance)
        targets_map = self._get_targets_detail_map([instance])
        formatted_data = self._format_response_data(response_serializer.data, targets_map)
        return Response(formatted_data)
