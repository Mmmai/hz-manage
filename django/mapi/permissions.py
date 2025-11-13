from typing import TypedDict, Set
from .models import UserInfo, DataScope


class ScopeResult(TypedDict):
    all: bool                     # 全部数据权限
    self: bool                    # 仅看本人
    models: Set[str]              # Models.id 集合
    groups: Set[str]              # ModelInstanceGroup.id 集合


def get_user_data_scope(username: str) -> ScopeResult:
    """
    计算用户的数据范围
    优先级：all > group > model > self
    """
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return {"all": False, "self": True, "models": set(), "groups": set()}

    # 获取所有角色的数据范围
    roles = list(user.roles.all())
    scopes = DataScope.objects.filter(role__in=roles).prefetch_related('groups', 'model')

    result: ScopeResult = {
        "all": False,
        "self": False,
        "models": set(),
        "groups": set()
    }

    for scope in scopes:
        if scope.scope_type == DataScope.ScopeType.ALL:
            result["all"] = True
        elif scope.scope_type == DataScope.ScopeType.SELF:
            result["self"] = True
        elif scope.scope_type == DataScope.ScopeType.MODEL and scope.model_id:
            result["models"].add(str(scope.model_id))
        elif scope.scope_type == DataScope.ScopeType.GROUP:
            if scope.model_id:
                result["models"].add(str(scope.model_id))
            result["groups"].update(str(g.id) for g in scope.groups.all())

    # 如果没有配置任何范围，默认只能看自己的
    if not any([result["all"], result["models"], result["groups"]]):
        result["self"] = True

    return result


def has_button_permission(username: str, action: str) -> bool:
    """
    检查用户是否拥有指定按钮权限
    用于字段级权限控制（如 showPassword）
    """
    from mapi.models import Permission
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return False
    return Permission.objects.filter(
        role__in=user.roles.all(),
        button__action=action
    ).exists()
