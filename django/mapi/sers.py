#序列化类
from rest_framework import serializers
from mapi.models import (UserInfo,Role,Menu,Portal,Pgroup,Datasource,
                         sysConfigParams,UserGroup
                         )

# from mapi.models import UserInfo,Role,Menu,Portal,Pgroup,Datasource,LogModule


# class UserModelSerializer(serializers.ModelSerializer):
#   class Meta:
#     # 表名
#     model = userlist
#     fields = "__all__"

# 为显示详细的外键信息
class RoleForSer(serializers.ModelSerializer):
  class Meta:
    # 表名
    model = Role
    fields = ["id","role"]
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
  class Meta:
    # 表名
    model = UserInfo
    fields = "__all__"
  def create(self, validated_data):
     role_ids = validated_data.pop('role_ids',[])
     group_ids = validated_data.pop('group_ids',[])
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
      print(validated_data)
      role_ids = validated_data.pop('role_ids',[])
      group_ids = validated_data.pop('group_ids',[])
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
    # depth = 1

class UserGroupModelSerializer(serializers.ModelSerializer):
  # id = serializers.IntegerField()
  # users_id = serializers.ListField()
  # users_id = serializers.ListField(
  #       child=serializers.IntegerField(), write_only=True, required=False
  #   )
  # users = UserInfoModelSerializer(many=True,read_only=True)
  users = UserInfoModelSerializer(many=True,read_only=True)
  roles = RoleForSer(many=True,read_only=True)
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
    # fields = "__all__"
    fields = ["id","group_name","user_count","roles","users","role_ids","user_ids"]

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
            newObj.roles.add(i_obj)
        except UserInfo.DoesNotExist:
          pass        
     return newObj      
  def update(self, instance, validated_data):
      print(validated_data)
      role_ids = validated_data.pop('role_ids',[])
      user_ids = validated_data.pop('user_ids',[])
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
      if len(user_ids) > 0:
          instance.users.clear()
          for i in user_ids:
              try:
                  i_obj = UserInfo.objects.get(id=i)
                  instance.users.add(i_obj)
              except UserInfo.DoesNotExist:
                  pass
      instance.save()
      return instance
    # depth = 1
# RoleModelSerializer  
class RoleModelSerializer(serializers.ModelSerializer):
  #显示__str__的字段
  # userinfo_set = serializers.StringRelatedField(many=True, read_only=True)
  #显示primkey
  userinfo_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
  usergroup_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

  # 新增显示字段的场景
  user_count = serializers.SerializerMethodField()
  userGroup_count = serializers.SerializerMethodField()

  class Meta:
    # 表名
    model = Role
    fields = "__all__"
    # depth = 1
  
  def get_user_count(self,obj):
    """获取角色关联的用户总数"""
    try:
      return UserInfo.objects.filter(roles=obj).count()
    except Exception as e:
      return 0
  def get_userGroup_count(self,obj):
    """获取角色关联的用户总数"""
    try:
      return UserGroup.objects.filter(roles=obj).count()
    except Exception as e:
      return 0   

class MenuModelSerializer(serializers.ModelSerializer):
  role_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

  class Meta:
    # 表名
    model = Menu
    fields = "__all__"
  def create(self, validated_data):
    # print(validated_data)
    # role = validated_data.pop('role')
    # print(role)
    menu = Menu.objects.create(**validated_data)
    # 自动添加到系统管理员
    if (menu):
      sysadminObj = Role.objects.get(role="管理员")
      sysadminObj.menu.add(*[menu.id])
    return menu
  #
# class PermissionModelSerializer(serializers.ModelSerializer):
#   class Meta:
#     # 表名
#     model = Permission
#     fields = "__all__"

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