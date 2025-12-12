import logging
from .models import *

logger = logging.getLogger(__name__)


class PermissionService:

    @staticmethod
    def get_user_permissions(user):
        """
        获取用户的所有权限，包括通过角色、用户组和直接授权的权限
        """
        # 通过用户直接角色获取权限
        role_permissions = Permission.objects.filter(role__in=user.roles.all())

        # 通过用户组获取权限（包括用户组关联的角色权限）
        user_groups = user.groups.all()
        user_group_permissions = Permission.objects.filter(user_group__in=user_groups)
        # 通过用户组关联的角色获取权限
        group_roles = []
        for group in user_groups:
            group_roles.extend(group.roles.all())
        group_role_permissions = Permission.objects.filter(role__in=group_roles)

        # 通过直接用户授权获取权限
        user_permissions = Permission.objects.filter(user=user)

        # 合并所有权限并去重
        permissions = (role_permissions | user_group_permissions | group_role_permissions | user_permissions).distinct()
        return permissions
