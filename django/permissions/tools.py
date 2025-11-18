import logging
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from mapi.models import UserInfo
from .models import DataScope, PermissionTarget

logger = logging.getLogger(__name__)


def get_user_data_scope(username: str):

    try:
        user = UserInfo.objects.get(username=username)
    except UserInfo.DoesNotExist:
        logger.warning(f"User '{username}' not found while getting data scope.")
        return {'scope_type': 'none', 'targets': {}}

    roles = set()
    for group in user.groups.all():
        roles.update(group.roles.all())
    roles.update(user.roles.all())
    user_scopes = DataScope.objects.filter(
        Q(role__in=roles) | Q(user=user) | Q(user_group__in=user.groups.all())
    ).prefetch_related('targets', 'targets__content_type').distinct()
    if not user_scopes.exists():
        logger.info(f"No data scopes found for user '{username}'.")
        return {'scope_type': 'none', 'targets': {}}

    logger.info(f'Found {user_scopes.count()} data scopes for user \'{username}\'.')

    final_scope_type = 'self'  # 默认最低权限
    final_targets = defaultdict(set)

    has_all_scope = any(scope.scope_type == DataScope.ScopeType.ALL for scope in user_scopes)

    if has_all_scope:
        final_scope_type = 'all'
    else:
        for scope in user_scopes:
            if scope.scope_type == DataScope.ScopeType.FILTER:
                final_scope_type = 'filter'

                for target in scope.targets.all():
                    ct = target.content_type
                    key = f"{ct.app_label}.{ct.model}"
                    final_targets[key].add(target.object_id)

    result = {
        'scope_type': final_scope_type,
        'targets': dict(final_targets)  # 将 defaultdict 转换为普通 dict
    }

    logger.info(f'Computed data scope for user \'{username}\': {result}')
    return result
