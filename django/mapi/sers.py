# 序列化类
from rest_framework import serializers
from mapi.models import (
    UserInfo,Role,Menu,Button,Permission,Portal,
    Pgroup,Datasource,
    sysConfigParams,UserGroup
                         )
import secrets
from cmdb.utils import password_handler
import logging
logger = logging.getLogger(__name__)

# 为显示详细的外键信息
class RoleForSer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Role
        fields = ["id","role_name"]
        # depth = 1
        
class UserGroupForSer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = UserGroup
        fields = ["id","group_name"]
        
class UserInfoModelSerializer(serializers.ModelSerializer):
    roles = RoleForSer(many=True,read_only=True)
    groups = UserGroupForSer(many=True,read_only=True)
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
        role_ids = validated_data.pop('role_ids',[])
        group_ids = validated_data.pop('group_ids',[])
        username = validated_data.get('username',None)
        password = validated_data.get('password',None)
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
        role_ids = validated_data.pop('role_ids',[])
        group_ids = validated_data.pop('group_ids',[])
        password = validated_data.get('password',None)
        old_password = validated_data.get('old_password',None)
        print(validated_data)
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
        if len(role_ids) > 0:
            instance.roles.clear()
            for i in role_ids:
                try:
                    i_obj = Role.objects.get(id=i)
                    instance.roles.add(i_obj)
                except Role.DoesNotExist:
                    pass
        if len(group_ids) > 0:
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
        
    def get_user_count(self,obj):
        """获取角色关联的用户总数"""
        try:
            return UserInfo.objects.filter(groups=obj).count()
        except Exception as e:
            return 0
            
    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids',[])
        user_ids = validated_data.pop('user_ids',[])
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
        #   print(validated_data)
        role_ids = validated_data.pop('role_ids', [])
        user_ids = validated_data.pop('user_ids', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.roles.clear()
        # 处理多对多关系
        if len(role_ids) > 0:
            for i in role_ids:
                try:
                    i_obj = Role.objects.get(id=i)
                    instance.roles.add(i_obj)
                except Role.DoesNotExist:
                    pass
        instance.users.clear()
        if len(user_ids) > 0:
            for i in user_ids:
                try:
                    i_obj = UserInfo.objects.get(id=i)
                    instance.users.add(i_obj)
                except UserInfo.DoesNotExist:
                    pass
        instance.save()
        return instance
        
    def validate_for_delete(self, instance):
        """
        删除前验证用户组
        """
        # 检查用户组是否包含用户
        if instance.users.count() > 0:
            raise serializers.ValidationError(f"用户组 '{instance.group_name}' 仍包含 {instance.users.count()} 个用户，不能删除")
        
        return instance
    # depth = 1
    
# RoleModelSerializer  
class RoleModelSerializer(serializers.ModelSerializer):
    # 显示__str__的字段
    # userinfo_set = serializers.StringRelatedField(many=True, read_only=True)
    # 显示primkey
    userinfo_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    usergroup_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    # 新增显示字段的场景
    user_count = serializers.SerializerMethodField()
    userGroup_count = serializers.SerializerMethodField()
    rolePermission = serializers.SerializerMethodField()
    
    class Meta:
        # 表名
        model = Role
        fields = "__all__"
        # depth = 1

    def get_user_count(self, obj):
        """获取角色关联的用户总数"""
        try:
            return UserInfo.objects.filter(roles=obj).count()
        except Exception as e:
            return 0
            
    def get_userGroup_count(self,obj):
        """获取角色关联的用户组总数"""
        try:
            return UserGroup.objects.filter(roles=obj).count()
        except Exception as e:
            return 0   
            
    def get_rolePermission(self,obj):
        """获取角色关联的权限列表"""
        try:
            allRolePermission = Permission.objects.filter(role=obj).all()
            permissionList = []
            for roleP in allRolePermission:
                # permissionList.append(roleP.menu.id)
                permissionList.append(roleP.button.id)
            return list(set(permissionList))
        except Exception as e:
            return []   
            
    def validate_for_delete(self, instance):
        """
        删除前验证角色
        """
        # 检查角色是否分配给用户
        user_count = UserInfo.objects.filter(roles=instance).count()
        if user_count > 0:
            raise serializers.ValidationError(f"角色 '{instance.role_name}' 仍分配给 {user_count} 个用户，不能删除")
            
        # 检查角色是否分配给用户组
        usergroup_count = UserGroup.objects.filter(roles=instance).count()
        if usergroup_count > 0:
            raise serializers.ValidationError(f"角色 '{instance.role_name}' 仍分配给 {usergroup_count} 个用户组，不能删除")
        
        return instance

class MenuModelSerializer(serializers.ModelSerializer):
    # role_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #     rolePermission = serializers.SerializerMethodField()
    class Meta:
        # 表名
        model = Menu
        fields = "__all__"
        # depth = 1


class ButtonModelSerializer(serializers.ModelSerializer):
    # role_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #     rolePermission = serializers.SerializerMethodField()
    class Meta:
        # 表名
        model = Button
        fields = "__all__"
        # depth = 1
class PermissionModelSerializer(serializers.ModelSerializer):
    # role_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)   
    #     rolePermission = serializers.SerializerMethodField() 
    class Meta:
        # 表名
        model = Permission
        fields = "__all__"
class getPortalModelSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.group')

    class Meta:
        # 表名
        model = Portal
        fields = "__all__"
        
class PortalModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Portal
        fields = "__all__"        
        
class PgroupModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Pgroup
        fields = "__all__"
    
    def validate_for_delete(self, instance):
        """
        删除前验证参数组
        """
        # 可以添加特定的删除验证逻辑
        return instance
    
class DatasourceModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = Datasource
        fields = "__all__"

# class LogModuleModelSerializer(serializers.ModelSerializer):
#   class Meta:
#     # 表名
#     model = LogModule
#     fields = "__all__"


class SysConfigSerializer(serializers.ModelSerializer):

    class Meta:
        # 表名
        model = sysConfigParams
        fields = "__all__"
