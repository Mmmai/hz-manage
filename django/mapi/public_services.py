from .models import (UserInfo, UserGroup, Role)


class PublicRbcaService:
    """对外的rbca服务类"""

    @staticmethod
    def get_user_with_relations(user_id):
        """
        根据用户ID获取用户及其关联的所有用户组和角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 包含用户信息、关联的用户组列表和角色列表的字典
        """
        try:
            user = UserInfo.objects.get(id=user_id)
            # 获取用户直接关联的角色
            direct_roles = user.roles.all()
            # 获取用户关联的用户组
            user_groups = user.groups.all()
            # 获取用户组关联的角色
            group_roles = Role.objects.filter(usergroup__in=user_groups).distinct()
            # 合并直接角色和通过用户组获得的角色
            all_roles = (direct_roles | group_roles).distinct()
            
            return {
                'user': user,
                'groups': user_groups,
                'roles': all_roles
            }
        except UserInfo.DoesNotExist:
            return None

    @staticmethod
    def get_user_groups_with_relations(group_id):
        """
        根据用户组ID获取用户组及其关联的所有用户和角色
        
        Args:
            group_id: 用户组ID
            
        Returns:
            dict: 包含用户组信息、关联的用户列表和角色列表的字典
        """
        try:
            group = UserGroup.objects.get(id=group_id)
            # 获取用户组中的所有用户
            users = group.users.all()
            # 获取用户组关联的角色
            roles = group.roles.all()
            
            return {
                'group': group,
                'users': users,
                'roles': roles
            }
        except UserGroup.DoesNotExist:
            return None

    @staticmethod
    def get_role_with_relations(role_id):
        """
        根据角色ID获取角色及其关联的所有用户和用户组
        
        Args:
            role_id: 角色ID
            
        Returns:
            dict: 包含角色信息、关联的用户列表和用户组列表的字典
        """
        try:
            role = Role.objects.get(id=role_id)
            # 获取直接关联该角色的用户
            direct_users = role.userinfo_set.all()
            # 获取关联该角色的用户组
            groups = role.usergroup_set.all()
            # 获取用户组中的所有用户
            group_users = UserInfo.objects.filter(groups__in=groups).distinct()
            # 合并直接用户和通过用户组关联的用户
            all_users = (direct_users | group_users).distinct()
            
            return {
                'role': role,
                'users': all_users,
                'groups': groups
            }
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_user_roles(user_id):
        """
        获取指定用户的所有角色（包括直接角色和通过用户组继承的角色）
        
        Args:
            user_id: 用户ID
            
        Returns:
            QuerySet: 用户的所有角色
        """
        try:
            user = UserInfo.objects.get(id=user_id)
            # 获取用户直接关联的角色
            direct_roles = user.roles.all()
            # 获取用户所属用户组的角色
            group_roles = Role.objects.filter(usergroup__users=user).distinct()
            # 合并所有角色并去重
            all_roles = (direct_roles | group_roles).distinct()
            return all_roles
        except UserInfo.DoesNotExist:
            return None

    @staticmethod
    def get_user_groups(user_id):
        """
        获取指定用户所属的所有用户组
        
        Args:
            user_id: 用户ID
            
        Returns:
            QuerySet: 用户所属的所有用户组
        """
        try:
            user = UserInfo.objects.get(id=user_id)
            return user.groups.all()
        except UserInfo.DoesNotExist:
            return None

    @staticmethod
    def get_group_users(group_id):
        """
        获取指定用户组中的所有用户
        
        Args:
            group_id: 用户组ID
            
        Returns:
            QuerySet: 用户组中的所有用户
        """
        try:
            group = UserGroup.objects.get(id=group_id)
            return group.users.all()
        except UserGroup.DoesNotExist:
            return None

    @staticmethod
    def get_group_roles(group_id):
        """
        获取指定用户组关联的所有角色
        
        Args:
            group_id: 用户组ID
            
        Returns:
            QuerySet: 用户组关联的所有角色
        """
        try:
            group = UserGroup.objects.get(id=group_id)
            return group.roles.all()
        except UserGroup.DoesNotExist:
            return None

    @staticmethod
    def get_role_users(role_id):
        """
        获取指定角色关联的所有用户（包括直接关联和通过用户组关联的）
        
        Args:
            role_id: 角色ID
            
        Returns:
            QuerySet: 角色关联的所有用户
        """
        try:
            # 直接关联该角色的用户
            direct_users = UserInfo.objects.filter(roles__id=role_id)
            # 通过用户组关联该角色的用户
            group_users = UserInfo.objects.filter(groups__roles__id=role_id).distinct()
            # 合并所有用户并去重
            all_users = (direct_users | group_users).distinct()
            return all_users
        except Role.DoesNotExist:
            return None

    @staticmethod
    def get_role_groups(role_id):
        """
        获取指定角色关联的所有用户组
        
        Args:
            role_id: 角色ID
            
        Returns:
            QuerySet: 角色关联的所有用户组
        """
        try:
            role = Role.objects.get(id=role_id)
            return role.usergroup_set.all()
        except Role.DoesNotExist:
            return None