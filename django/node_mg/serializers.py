import json
from rest_framework import serializers
from .models import (Nodes,NodeTasks,Proxy,ModelConfig)


class NodeTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeTasks
        fields = ['status']


class NodeTasksDetailSerializer(serializers.ModelSerializer):
    """NodeTasks详细信息序列化器"""
    node_name = serializers.CharField(source='node.model_instance.instance_name', read_only=True)
    node_ip = serializers.CharField(source='node.ip_address', read_only=True)
    
    # 重写results和error_message字段，使其返回解析后的JSON对象
    results = serializers.SerializerMethodField()
    error_message = serializers.SerializerMethodField()
    
    class Meta:
        model = NodeTasks
        fields = '__all__'
        
    def get_results(self, obj):
        """解析results字段为JSON对象"""
        if obj.results:
            try:
                # 如果results是字符串格式的JSON，解析它
                if isinstance(obj.results, str):
                    return json.loads(obj.results)
                # 如果已经是Python对象，直接返回
                return obj.results
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，返回原值
                return obj.results
        return None
        
    def get_error_message(self, obj):
        """解析error_message字段为JSON对象"""
        if obj.error_message:
            try:
                # 如果error_message是字符串格式的JSON，解析它
                if isinstance(obj.error_message, str):
                    return json.loads(obj.error_message)
                # 如果已经是Python对象，直接返回
                return obj.error_message
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，返回原值
                return obj.error_message
        return None
class NodesSerializer(serializers.ModelSerializer):
    #对象
    model_instance_name = serializers.CharField(source='model_instance.instance_name', read_only=True)
    model_name = serializers.CharField(source='model.name', read_only=True)
    proxy_name = serializers.CharField(source='proxy.name', read_only=True)
    manage_status = serializers.SerializerMethodField()
    agent_status = serializers.SerializerMethodField()
    model_verbose_name = serializers.CharField(source='model.verbose_name', read_only=True)
    manage_error_message = serializers.SerializerMethodField()
    agent_error_message = serializers.SerializerMethodField()
    class Meta:
        model = Nodes
        fields = '__all__'
    def get_manage_status(self, obj):
        """获取节点关联的最新任务状态"""
        try:
            latest_task = obj.node_tasks.filter(task_name='get_system_info').order_by('-created_at').first()
            if latest_task:
                # return NodeTasksSerializer(latest_task).data
                return latest_task.status
            return 2
        except Exception as e:
            return 2
    def get_agent_status(self, obj):
        """获取节点agent状态"""
        try:
            latest_task = obj.node_tasks.filter(task_name='zabbix_agent_install').order_by('-created_at').first()
            if latest_task:
                # return NodeTasksSerializer(latest_task).data
                return latest_task.status
            return 2
        except Exception as e:
            return 2
    def get_manage_error_message(self, obj):
        """获取节点关联的最新任务错误信息"""
        try:
            latest_task = obj.node_tasks.filter(task_name='get_system_info').order_by('-created_at').first()
            if latest_task:
                # return NodeTasksSerializer(latest_task).data
                return latest_task.error_message
            return ""
        except Exception as e:
            return ""
    def get_agent_error_message(self, obj):
        """获取节点关联的最新任务错误信息"""
        try:
            latest_task = obj.node_tasks.filter(task_name='zabbix_agent_install').order_by('-created_at').first()
            if latest_task:
                # return NodeTasksSerializer(latest_task).data
                return latest_task.error_message
            return ""
        except Exception as e:
            return ""

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
