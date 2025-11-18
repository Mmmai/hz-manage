from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import DataScope
from .serializers import DataScopeSerializer


class DataScopeViewSet(ModelViewSet):
    queryset = DataScope.objects.all().prefetch_related('targets', 'targets__content_type')
    serializer_class = DataScopeSerializer
    filterset_fields = ['role', 'user', 'user_group', 'scope_type']
    search_fields = ['description']
    ordering_fields = ['create_time', 'update_time']

    def _format_response_data(self, data):
        if isinstance(data, list):
            for item in data:
                scope_id = item.get('id')
                scope_instance = next((s for s in self.queryset if str(s.id) == scope_id), None)
                if scope_instance:
                    item['targets_detail'] = self._get_targets_detail(scope_instance)
        else:
            instance_id = data.get('id')
            instance = self.get_queryset().get(id=instance_id)
            data['targets_detail'] = self._get_targets_detail(instance)
        return data

    def _get_targets_detail(self, instance):
        targets_detail = {}
        for target in instance.targets.all():
            key = f"{target.content_type.app_label}.{target.content_type.model}"
            targets_detail.setdefault(key, []).append(str(target.object_id))
        return targets_detail

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if response.data.get('results'):
            response.data['results'] = self._format_response_data(response.data['results'])
        else:
            response.data = self._format_response_data(response.data)
        return response

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = self._format_response_data(response.data)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if status.is_success(response.status_code):
            response.data = self._format_response_data(response.data)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if status.is_success(response.status_code):
            response.data = self._format_response_data(response.data)
        return response
