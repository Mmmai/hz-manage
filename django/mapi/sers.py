# 序列化类
import logging
import secrets

from rest_framework import serializers
from cmdb.utils import password_handler
from .models import *

logger = logging.getLogger(__name__)

# 为显示详细的外键信息


class RoleForSer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Role
        fields = ["id", "role_name"]
        # depth = 1


class UserGroupForSer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = UserGroup
        fields = ["id", "group_name"]


class UserInfoModelSerializer(serializers.ModelSerializer):
    roles = RoleForSer(many=True, read_only=True)
    groups = UserGroupForSer(many=True, read_only=True)
    role_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    group_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    # 添加旧密码字段，用于密码修改验证
    old_password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="修改密码时需要提供旧密码"
    )

    class Meta:
        # 表名
        model = UserInfo
        fields = "__all__"
        extra_kwargs = {
            'password': {'write_only': True},
            'old_password': {'write_only': True}
        }

    def _generate_salt(self):
        """生成随机盐值"""
        return secrets.token_hex(16)

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        group_ids = validated_data.pop('group_ids', [])
        username = validated_data.get('username', None)
        password = validated_data.get('password', None)
        if not password or not username:
            raise serializers.ValidationError({
                'error': f'password and username is required'
            })
        # 生成随机盐值
        salt = self._generate_salt()
        validated_data['password_salt'] = salt
        # 使用盐值处理原始密码，再用SM4加密密码
        salted_password = f'{salt}:{password}'
        validated_data['password'] = password_handler.encrypt_to_sm4(salted_password)
        newObj = UserInfo.objects.create(**validated_data)
        # 处理角色列表
        for i in role_ids:
            try:
                i_obj = Role.objects.get(id=i)
                newObj.roles.add(i_obj)
            except Role.DoesNotExist:
                pass
        # 处理用户组列表
        for i in group_ids:
            try:
                i_obj = UserGroup.objects.get(id=i)
                newObj.groups.add(i_obj)
            except UserGroup.DoesNotExist:
                pass
        return newObj

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids',None)
        group_ids = validated_data.pop('group_ids',None)
        password = validated_data.get('password',None)
        old_password = validated_data.get('old_password',None)
        if old_password:
            # 将提供的旧密码与instance密码比较
            pre_password = password_handler.decrypt_sm4(f'{instance.password}')
            if not pre_password.split(":")[-1] == old_password:
                raise serializers.ValidationError({
                    'error': f'原密码错误，修改失败!'
                })
        if password:
            # 使用SM4加密密码
            salt = self._generate_salt()
            validated_data['password_salt'] = salt
            # 使用盐值处理原始密码，再用SM4加密密码
            salted_password = f'{salt}:{password}'
            validated_data['password'] = password_handler.encrypt_to_sm4(salted_password) 
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # 处理多对多关系
        # 如果role_ids字段存在于请求数据中（即使为空列表），则清除并重新设置角色
        if role_ids or role_ids == []:
            instance.roles.clear()
            for i in role_ids:
                try:
                    i_obj = Role.objects.get(id=i)
                    instance.roles.add(i_obj)
                except Role.DoesNotExist:
                    pass
        # 如果group_ids字段存在于请求数据中（即使为空列表），则清除并重新设置用户组
        if group_ids or group_ids == []:
            instance.groups.clear()
            for i in group_ids:
                try:
                    i_obj = UserGroup.objects.get(id=i)
                    instance.groups.add(i_obj)
                except UserGroup.DoesNotExist:
                    pass
        instance.save()
        return instance

    def validate_for_delete(self, instance):
        """
        删除前验证，防止删除重要用户
        """
        # 防止删除admin用户
        if instance.username == 'admin':
            raise serializers.ValidationError("不能删除admin用户")

        # 可以添加其他删除验证逻辑
        # 例如检查用户是否关联了重要数据等
        return instance
    # depth = 1


class UserGroupModelSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # users_id = serializers.ListField()
    # users_id = serializers.ListField(
    #       child=serializers.IntegerField(), write_only=True, required=False
    #   )
    # users = UserInfoModelSerializer(many=True,read_only=True)
    users = UserInfoModelSerializer(many=True, read_only=True)
    roles = RoleForSer(many=True, read_only=True)
    role_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    user_ids = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )
    user_count = serializers.SerializerMethodField()

    class Meta:
        # 表名
        model = UserGroup
        fields = "__all__"
    #   fields = ["id","group_name","user_count","roles","users","role_ids","user_ids"]

    def get_user_count(self, obj):
        """获取角色关联的用户总数"""
        try:
            return UserInfo.objects.filter(groups=obj).count()
        except Exception as e:
            return 0

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        user_ids = validated_data.pop('user_ids', [])
        newObj = UserGroup.objects.create(**validated_data)
        # 处理角色列表
        for i in role_ids:
            try:
                i_obj = Role.objects.get(id=i)
                newObj.roles.add(i_obj)
            except Role.DoesNotExist:
                pass
        # 处理角色列表
        for i in user_ids:
            try:
                i_obj = UserInfo.objects.get(id=i)
                newObj.users.add(i_obj)
            except UserInfo.DoesNotExist:
                pass
        return newObj

    def update(self, instance, validated_data):
        # 获取传入的数据
        role_ids = validated_data.pop('role_ids', [])
        user_ids = validated_data.pop('user_ids', [])

        # 更新普通字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # 更新角色关联
        if len(role_ids) > 0:
            instance.roles.clear()
            for role_id in role_ids:
                try:
                    role_obj = Role.objects.get(id=role_id)
                    instance.roles.add(role_obj)
                except Role.DoesNotExist:
                    pass

        # 更新用户关联（特别处理admin用户）
        if len(user_ids) > 0:
            # 清空现有用户关联，但保留admin用户（如果适用）
            current_users = list(instance.users.all())
            for user in current_users:
                # 除非是系统管理组且尝试移除admin用户，否则可以移除
                if not (instance.group_name == '系统管理组' and user.username == 'admin'):
                    instance.users.remove(user)

            # 添加新用户
            for user_id in user_ids:
                try:
                    user_obj = UserInfo.objects.get(id=user_id)
                    # 特殊处理：确保admin用户始终在系统管理组中
                    if instance.group_name == '系统管理组' and user_obj.username == 'admin':
                        instance.users.add(user_obj)
                    # 对于非admin用户，正常添加
                    elif user_obj.username != 'admin':
                        instance.users.add(user_obj)
                    # 对于admin用户但不是系统管理组的情况，不允许添加
                    elif user_obj.username == 'admin' and instance.group_name != '系统管理组':
                        pass  # 忽略添加admin用户到非系统管理组的操作
                except UserInfo.DoesNotExist:
                    pass
        else:
            # 如果没有提供用户列表，检查是否是系统管理组且包含admin用户
            if instance.group_name == '系统管理组':
                admin_user = UserInfo.objects.filter(username='admin').first()
                if admin_user:
                    # 确保admin用户保留在系统管理组中
                    instance.users.add(admin_user)

        instance.save()
        return instance

    def validate_for_delete(self, instance):
        """
        删除前验证用户组
        """
        # 检查是否为内置用户组
        if instance.built_in:
            raise serializers.ValidationError(f"用户组 '{instance.group_name}' 是系统内置用户组，不能删除")

        # 检查用户组是否包含用户
        if instance.users.count() > 0:
            raise serializers.ValidationError(f"用户组 '{instance.group_name}' 仍包含 {instance.users.count()} 个用户，不能删除")

        return instance

# RoleModelSerializer


class RoleModelSerializer(serializers.ModelSerializer):
    # 显示__str__的字段
    # userinfo_set = serializers.StringRelatedField(many=True, read_only=True)
    # 新增显示字段的场景
    user_count = serializers.SerializerMethodField()
    userGroup_count = serializers.SerializerMethodField()
    rolePermission = serializers.SerializerMethodField()
 # 添加关联的用户和用户组简要信息
    associated_users = serializers.SerializerMethodField()
    associated_user_groups = serializers.SerializerMethodField()

    class Meta:
        # 表名
        model = Role
        fields = "__all__"
        # depth = 1

    def get_associated_users(self, obj):
        """获取角色关联的用户简要信息 {id: xx, username: xxx}"""
        try:
            users = UserInfo.objects.filter(roles=obj).all()
            return [{"id": user.id, "username": user.username} for user in users]
        except Exception as e:
            return []

    def get_associated_user_groups(self, obj):
        """获取角色关联的用户组简要信息 {id: xx, group_name: xxx}"""
        try:
            user_groups = UserGroup.objects.filter(roles=obj).all()
            return [{"id": group.id, "group_name": group.group_name} for group in user_groups]
        except Exception as e:
            return []

    def get_user_count(self, obj):
        """获取角色关联的用户总数"""
        try:
            return UserInfo.objects.filter(roles=obj).count()
        except Exception as e:
            return 0

    def get_userGroup_count(self, obj):
        """获取角色关联的用户组总数"""
        try:
            return UserGroup.objects.filter(roles=obj).count()
        except Exception as e:
            return 0

    def get_rolePermission(self, obj):
        """获取角色关联的权限列表"""
        try:
            allRolePermission = obj.permission.all()
            permissionList = []
            for roleP in allRolePermission:
                permissionList.append(roleP.button.id)
            return list(set(permissionList))
        except Exception as e:
            return []

    def validate_for_delete(self, instance):
        """
        删除前验证角色
        """
        # 检查是否为内置用户组
        if instance.built_in:
            raise serializers.ValidationError(f"用户组 '{instance.role}' 是系统内置角色，不能删除")
        # 检查角色是否分配给用户
        user_count = UserInfo.objects.filter(roles=instance).count()
        if user_count > 0:
            raise serializers.ValidationError(f"角色 '{instance.role_name}' 仍分配给 {user_count} 个用户，不能删除")

        # 检查角色是否分配给用户组
        usergroup_count = UserGroup.objects.filter(roles=instance).count()
        if usergroup_count > 0:
            raise serializers.ValidationError(f"角色 '{instance.role_name}' 仍分配给 {usergroup_count} 个用户组，不能删除")

        return instance


class PgroupModelSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True, allow_null=True)
    # 添加门户列表字段
    portals = serializers.SerializerMethodField()

    class Meta:
        model = Pgroup
        fields = "__all__"
        read_only_fields = ('owner',)

    def get_portals(self, obj):
        # 返回该分组下的门户列表，并按照用户自定义排序
        portals = obj.portals.all()

        # 获取当前请求用户（如果有的话）
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            # 获取该用户对该分组内门户的排序偏好
            user_sort_prefs = UserPortalSortOrder.objects.filter(
                user=user,
                portal__in=portals,
                group=obj
            )

            if user_sort_prefs.exists():
                # 如果用户有自定义排序，则使用用户排序
                user_sort_dict = {str(pref.portal_id): pref.sort_order for pref in user_sort_prefs}

                def sort_key(portal):
                    return user_sort_dict.get(str(portal.id), portal.sort_order)

                portals = sorted(portals, key=sort_key)
            else:
                # 默认按sort_order字段排序
                portals = portals.order_by('sort_order')
        else:
            # 如果没有用户上下文或用户未认证，按默认排序
            portals = portals.order_by('sort_order')

        return PortalModelSerializer(portals, many=True, context=self.context).data

    def create(self, validated_data):
        # 在创建时，owner将在view中设置
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # 不允许更改owner
        validated_data.pop('owner', None)
        return super().update(instance, validated_data)


class getPortalModelSerializer(serializers.ModelSerializer):
    # 修改为支持多分组
    groups = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.username', read_only=True, allow_null=True)

    class Meta:
        model = Portal
        fields = "__all__"

    def get_groups(self, obj):
        # 返回该门户所属的分组列表
        groups = obj.groups.all()
        return [{'id': group.id, 'group': group.group} for group in groups]


class PortalModelSerializer(serializers.ModelSerializer):
    # 定义 groups 字段以支持多对多关系
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Pgroup.objects.all(),
        many=True,
        required=False
    )
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Portal
        fields = "__all__"
        read_only_fields = ('owner',)

    def get_is_favorite(self, obj):
        """获取用户是否收藏了该门户"""
        user = self.context.get('request').user
        return PortalFavorites.objects.filter(portal=obj, user=user).exists()

    def create(self, validated_data):
        # 在创建时，owner将在view中设置
        groups_data = validated_data.pop('groups', [])
        portal = Portal.objects.create(**validated_data)
        if groups_data:
            portal.groups.set(groups_data)
        return portal

    def update(self, instance, validated_data):
        # 不允许更改owner
        validated_data.pop('owner', None)
        groups_data = validated_data.pop('groups', None)

        # 更新门户基本信息
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新分组关系
        if groups_data is not None:
            instance.groups.set(groups_data)

        return instance


class PortalFavoritesSerializer(serializers.ModelSerializer):
    portal_info = serializers.SerializerMethodField()

    class Meta:
        model = PortalFavorites
        fields = ['id', 'portal', 'create_time', 'portal_info']
        read_only_fields = ['user', 'create_time']

    def get_portal_info(self, obj):
        # 返回门户的基本信息
        portal = obj.portal
        return {
            'id': portal.id,
            'name': portal.name,
            'url': portal.url,
            'describe': portal.describe,
            'status': portal.status,
            'sharing_type': portal.sharing_type,
            'owner_name': portal.owner.username if portal.owner else None,
            'groups': [{'id': group.id, 'group': group.group} for group in portal.groups.all()]
        }


class DatasourceModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Datasource
        fields = "__all__"


class SysConfigSerializer(serializers.ModelSerializer):

    class Meta:
        # 表名
        model = sysConfigParams
        fields = "__all__"
