#序列化类
from rest_framework import serializers
from mlog.models import LogModule,LogFlow,LogFlowMission

# class UserModelSerializer(serializers.ModelSerializer):
#   class Meta:
#     # 表名
#     model = userlist
#     fields = "__all__"


class LogModuleModelSerializer(serializers.ModelSerializer):
    class Meta:
        # 表名
        model = LogModule
        fields = "__all__"

class LogFlowModelSerializer(serializers.ModelSerializer):
    # dataSource_name = 
    class Meta:
        # 表名
        model = LogFlow
        fields = "__all__"

class LogFlowMissionModelSerializer(serializers.ModelSerializer):
    # 将choice显示为可显示字段
    status = serializers.CharField(source='get_status_display')
    dataSource_name = serializers.CharField(source='dataSource_id.source_name')
    username = serializers.CharField(source='user_id.username')
    flow_name = serializers.CharField(source='flow_id.name')
    class Meta:
        # 表名
        model = LogFlowMission
        fields = ('mission_id','user_id','username','flow_id','flow_name','search_key','dataSource_id','dataSource_name','create_time','status')
class LogFlowMissionModelSerializerAll(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    dataSource_name = serializers.CharField(source='dataSource_id.source_name')
    username = serializers.CharField(source='user_id.username')
    flow_name = serializers.CharField(source='flow_id.name')
    class Meta:
        # 表名
        model = LogFlowMission
        fields =  "__all__"