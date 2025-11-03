from rest_framework import serializers
from .models import (Nodes,NodeInfoTask,NodeSyncZabbix,Proxy,ModelConfig)
from cmdb.models import ModelInstance,Models,ModelFieldMeta


class NodeInfoTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeInfoTask
        fields = ['status']
class NodesSerializer(serializers.ModelSerializer):
    #对象
    #model_instance = serializers.StringRelatedField(read_only=True)
    #model = serializers.StringRelatedField(read_only=True)

    #返回指定字段值
    # author = serializers.SlugRelatedField(
    #     source='author',
    #     slug_field='name',
    #     read_only=True
    # )
    model_instance_name = serializers.CharField(source='model_instance.instance_name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    proxy_name = serializers.CharField(source='proxy.name', read_only=True)
    # status = NodeInfoTaskSerializer(many=True, source='node_info_tasks', read_only=True)
    	# "status": [
		# {
		# 	"status": false
		# }
    manage_status = serializers.SerializerMethodField()
    agent_status = serializers.SerializerMethodField()
    zbx_status = serializers.SerializerMethodField()

    model_verbose_name = serializers.CharField(source='model.verbose_name', read_only=True)
    manage_error_message = serializers.SerializerMethodField()
    agent_error_message = serializers.SerializerMethodField()

    # node_ip = serializers.SerializerMethodField()
    class Meta:
        model = Nodes
        fields = '__all__'

    # def get_instance_name(self, obj):
    #     """获取模型关联的实例总数"""
    #     try:
    #         return ModelInstance.objects.filter(model=obj).count()
    #     except Exception as e:
    #         return 0
    def get_manage_status(self, obj):
        """获取节点关联的最新任务状态"""
        try:
            latest_task = obj.node_info_tasks.order_by('-created_at').first()
            if latest_task:
                # return NodeInfoTaskSerializer(latest_task).data
                return latest_task.status
            return 2
        except Exception as e:
            return 2
    def get_agent_status(self, obj):
        """获取节点agent状态"""
        try:
            latest_task = obj.node_sync_zabbix.first()
            if latest_task:
                # return NodeInfoTaskSerializer(latest_task).data
                return latest_task.agent_status
            return 2
        except Exception as e:
            return 2
    def get_zbx_status(self, obj):
        """获取节点zbx状态"""
        try:
            latest_task = obj.node_sync_zabbix.first()
            if latest_task:
                # return NodeInfoTaskSerializer(latest_task).data
                return latest_task.zbx_status
            return 2
        except Exception as e:
            return 2
    def get_manage_error_message(self, obj):
        """获取节点关联的最新任务错误信息"""
        try:
            latest_task = obj.node_info_tasks.order_by('-created_at').first()
            if latest_task:
                # return NodeInfoTaskSerializer(latest_task).data
                return latest_task.error_message
            return ""
        except Exception as e:
            return ""
    def get_agent_error_message(self, obj):
        """获取节点关联的最新任务错误信息"""
        try:
            latest_task = obj.node_sync_zabbix.order_by('-created_at').first()
            if latest_task:
                # return NodeInfoTaskSerializer(latest_task).data
                return latest_task.error_message
            return ""
        except Exception as e:
            return ""
    # def get_node_ip(self, obj):
    #     """获取节点关联的实例IP"""
    #     try:
            
    #         field_values = ModelFieldMeta.objects.filter(
    #             model_instance=obj.model_instance
    #         ).select_related('model_fields')
    #         # print(field_values)
    #         for field in field_values:
    #             if field.model_fields.name == 'ip':
    #                 return field.data
    #         return ""
    #     except Exception as e:
    #         return ""




class NodeForProxySerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source='model_instance.instance_name', read_only=True)
    class Meta:
        model = Nodes
        fields = ['id','ip_address','model_instance','instance_name']
class ProxySerializer(serializers.ModelSerializer):
    node_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Proxy
        fields = '__all__'
    def get_node_count(self,obj):
        return Nodes.objects.filter(proxy=obj).count()
    
class ProxyDetailSerializer(serializers.ModelSerializer):
    node_count = serializers.SerializerMethodField()
    nodes = NodeForProxySerializer(many=True, read_only=True)
    class Meta:
        model = Proxy
        # 可以自定义需要返回的字段
        fields = '__all__'
    
    def get_node_count(self,obj):
        return Nodes.objects.filter(proxy=obj).count()
class ModelConfigSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_verbose_name = serializers.CharField(source='model.verbose_name', read_only=True)
    class Meta:
        model = ModelConfig
        # 可以自定义需要返回的字段
        fields = '__all__'
