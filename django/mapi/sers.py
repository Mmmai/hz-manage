#序列化类
from rest_framework import serializers
from mapi.models import (UserInfo,Role,Menu,Portal,Pgroup,Datasource,
                         sysConfigParams
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
    # depth = 1
# RoleModelSerializer
class RoleModelSerializer(serializers.ModelSerializer):
  #显示__str__的字段
  # userinfo_set = serializers.StringRelatedField(many=True, read_only=True)
  #显示primkey
  userinfo_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
  class Meta:
    # 表名
    model = Role
    fields = "__all__"
    # depth = 1

class MenuModelSerializer(serializers.ModelSerializer):
  role_set = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

  class Meta:
    # 表名
    model = Menu
    fields = "__all__"
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