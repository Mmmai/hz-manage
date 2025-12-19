import logging
from collections import defaultdict
from django.core.cache import cache
from django.db.models import Q
from threading import local

from mapi.models import UserInfo
from .models import DataScope, Permission
from .registry import get_handler

logger = logging.getLogger(__name__)


def get_data_scope_cache(username: str) -> dict:
    cache_key = f'user_data_scope_{username}'
    return cache.get(cache_key)


def set_data_scope_cache(username: str, data: dict):
    cache_key = f'user_data_scope_{username}'
    cache.set(cache_key, data)


def clear_data_scope_cache(username: str):
    cache_key = f'user_data_scope_{username}'
    cache.delete(cache_key)


def get_password_permission_cache(username: str) -> bool:
    cache_key = f'password_permission_{username}'
    return cache.get(cache_key)


def set_password_permission_cache(username: str, has_permission: bool):
    cache_key = f'password_permission_{username}'
    cache.set(cache_key, has_permission)


def clear_password_permission_cache(username: str):
    cache_key = f'password_permission_{username}'
    cache.delete(cache_key)


def get_user_data_scope(username: str) -> dict:

    try:
        user = UserInfo.objects.get(username=username)
    except UserInfo.DoesNotExist:
        logger.warning(f"User '{username}' not found while getting data scope.")
        return {'scope_type': 'none', 'targets': {}}

    if username == 'system':
        return {'scope_type': 'all', 'targets': {}}

    cached_scope = get_data_scope_cache(username)
    if cached_scope:
        return cached_scope

    roles = set()
    for group in user.groups.all():
        roles.update(group.roles.all())
    roles.update(user.roles.all())
    user_scopes = DataScope.objects.filter(
        Q(role__in=roles) | Q(user=user) | Q(user_group__in=user.groups.all())
    ).prefetch_related('targets', 'targets__content_type').distinct()
    if not user_scopes.exists():
        logger.info(f"No data scopes found for user '{username}'.")
        result = {'scope_type': 'none', 'targets': {}}
        set_data_scope_cache(username, result)
        return result

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
    set_data_scope_cache(username, result)

    logger.info(f'Computed data scope for user \'{username}\': {result}')
    return result


def get_scope_query(username, model):

    if not username or username == 'anonymous':
        return None

    scope = get_user_data_scope(username)
    scope_type = scope.get('scope_type', 'none')

    if scope_type == DataScope.ScopeType.ALL:
        return Q()  # 空 Q 对象表示不过滤，即所有

    if scope_type == 'none':
        return None  # 明确表示无权

    app_label = model._meta.app_label
    model_name = model._meta.model_name
    model_key = f"{app_label}.{model_name}"

    final_query = Q()

    allowed_ids = scope['targets'].get(model_key)
    if allowed_ids:
        final_query |= Q(id__in=allowed_ids)

    if scope_type == 'self' or scope_type == 'filter':
        if hasattr(model, 'create_user'):
            final_query |= Q(create_user=username)

    indirect_handler = get_handler(app_label)
    if indirect_handler:
        indirect_query = indirect_handler(scope, model, username)
        if indirect_query:
            final_query |= indirect_query

    return final_query


def has_password_permission(user: UserInfo) -> bool:
    """
    检查用户是否有权限查看密码字段
    """
    if hasattr(user, 'username'):
        username = user.username
    elif isinstance(user, str):
        username = user
    else:
        return False

    if username == 'system':
        return True

    # 检查缓存
    request_cache = get_password_permission_cache(username)
    if request_cache is not None:
        return request_cache

    # 缓存未命中，查询数据库
    query = Q(role__in=user.roles.all()) | Q(role__in=user.groups.values_list('roles', flat=True))
    user_permissions = Permission.objects.filter(
        query
    ).distinct().select_related('button')

    for perm in user_permissions:
        if perm.button and perm.button.action == 'showPassword':
            set_password_permission_cache(username, True)
            return True
    set_password_permission_cache(username, False)
    return False
