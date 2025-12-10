from rest_framework.filters import BaseFilterBackend
from .tools import get_scope_query

# 添加新的app过滤
class DataScopeFilterBackend(BaseFilterBackend):
    TARGET_APP = {'cmdb'}

    def filter_queryset(self, request, queryset, view):
        if queryset.model._meta.app_label not in self.TARGET_APP:
            return queryset

        username = getattr(request.user, 'username', None)
        scope_query = get_scope_query(username, queryset.model)

        if scope_query is None:
            return queryset.none()
        return queryset.filter(scope_query)
