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



class UserInfoModelSerializer(serializers.ModelSerializer):

  class Meta:
    # 表名
    model = UserInfo
    fields = "__all__"
class UserGroupModelSerializer(serializers.ModelSerializer):
  # id = serializers.IntegerField()
  # users_id = serializers.ListField()
  # users_id = serializers.ListField(
  #       child=serializers.IntegerField(), write_only=True, required=False
  #   )
  users = UserInfoModelSerializer(many=True,read_only=True)
  userinfo_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
  user_count = serializers.SerializerMethodField()
  class Meta:
    # 表名
    model = UserGroup
    fields = "__all__"
    # fields = ["id","group_name","users","user_count","userinfo_set","roles"]

  def get_user_count(self,obj):
    """获取角色关联的用户总数"""
    try:
      return UserInfo.objects.filter(roles=obj).count()
    except Exception as e:
      return 0
  # def create(self, validated_data):
  #    print(validated_data)
  #   #  return
  #   #  userList = validated_data.pop('users_id')
  #    instance = UserGroup.objects.create(**validated_data)
  #   #  for item in userList:
  #   #    userinfoObj, _ = UserInfo.objects.get_or_create(id=item)
  #   #    userinfoObj.groups.add(instance)
  #    return instance      

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