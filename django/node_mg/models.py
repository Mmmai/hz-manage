from django.db import models
from cmdb.models import ModelInstance,Models
# Create your models here.
import uuid


class Proxy(models.Model):
    PROXY_TYPES = (
        ('all', 'all'),
        ('zabbix', 'zabbix'),
        ('ansible', 'ansible'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, verbose_name="代理名称")
    verbose_name = models.CharField(max_length=50,null=True,blank=True,verbose_name="代理中文名称")
    proxy_type = models.CharField(max_length=20, choices=PROXY_TYPES,default=PROXY_TYPES[0][0], verbose_name="代理类型")
    enabled = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(verbose_name="代理主机")
    port = models.PositiveIntegerField(default=22, verbose_name="代理端口")
    auth_user = models.CharField(max_length=100, blank=True, verbose_name="认证用户")
    auth_pass = models.CharField(max_length=100, blank=True, verbose_name="认证密码")
    zbx_proxyid = models.CharField(max_length=50, null=True, blank=True, verbose_name="Zabbix代理ID")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = "代理配置"
        verbose_name_plural = "代理配置"
        db_table = 'tb_proxy'
        managed = True
        app_label = 'node_mg'

    # STATUS_CHOICES = (
    #     ('online', '在线'),
    #     ('offline', '离线'),
    #     ('unknown', '未知'),
    # )

class Nodes(models.Model):
    class statusChoices(models.IntegerChoices):
        ABNORMAL = '0', '异常'
        UNKNOW = '1', '未知'
        NORMAL = '2', '正常'
    class Meta:
        db_table = 'tb_nodes'
        managed = True
        app_label = 'node_mg'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey("cmdb.Models", on_delete=models.CASCADE,related_name="nodes")
    model_instance = models.ForeignKey("cmdb.ModelInstance", on_delete=models.CASCADE,related_name="nodes")
    ip_address = models.GenericIPAddressField(null=False, blank=False,verbose_name='IP地址',default='127.0.0.1')
    proxy = models.ForeignKey(
            Proxy,
            on_delete=models.SET_NULL,  # 代理删除时设为NULL
            null=True,
            blank=True,
            related_name='nodes',       # 反向查询名称
            verbose_name="关联代理"
        )
    # instance_id = models.CharField(max_length=256, null=False, blank=False,unique=True)
    # ping_status = models.IntegerField(choices=statusChoices.choices,verbose_name='连通性',default=statusChoices.UNKNOW)
    # node_status = models.IntegerField(choices=statusChoices.choices,verbose_name='管理状态',default=statusChoices.UNKNOW)
    # zabbix_status = models.IntegerField(choices=statusChoices.choices,verbose_name='zabbix状态',default=statusChoices.UNKNOW)
    enable_sync = models.BooleanField(blank=False,null=False,verbose_name='是否同步',default=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    #最后更新时间
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


class NodeInfoTask(models.Model):
    MANAGE_STATUS =  (
            (1, '成功'),
            (0, '失败'),
            (2, '未知'),
        )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(Nodes, on_delete=models.CASCADE,related_name='node_info_tasks')
    status = models.IntegerField(choices=MANAGE_STATUS,default=MANAGE_STATUS[2][0])
    results = models.TextField(null=True,blank=True)
    error_message = models.TextField(null=True,blank=True)
    asset_info = models.JSONField(blank=True,null=True)
    cost_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True,null=True)
    class Meta:
        db_table = 'tb_node_info_tasks'
        managed = True
        app_label = 'node_mg'
class NodeSyncZabbix(models.Model):
    AGENT_STATUS =  (
            (1, '成功'),
            (0, '失败'),
            (2, '未知'),
        )
    ZBX_STATUS =  (
            (1, '正常'),
            (0, '异常'),
            (2, '未知'),
        )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(Nodes, on_delete=models.CASCADE,related_name='node_sync_zabbix')
    agent_status = models.IntegerField(choices=AGENT_STATUS,default=AGENT_STATUS[2][0])
    zbx_status = models.IntegerField(choices=ZBX_STATUS,default=ZBX_STATUS[2][0])
    results = models.TextField(null=True,blank=True)
    error_message = models.TextField(null=True,blank=True)
    zabbix_info = models.JSONField(null=True, blank=True)   
    cost_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True,null=True)
    class Meta:
        db_table = 'tb_node_sync_zabbix'
        managed = True
        app_label = 'node_mg'

class ModelConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.OneToOneField(
        "cmdb.Models", 
        on_delete=models.CASCADE,
        related_name="model_config",
        verbose_name="资产模型"
    )    
    built_in = models.BooleanField(default=False)
    is_manage = models.BooleanField(default=False)
    zabbix_sync_info = models.JSONField(default=dict)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    class Meta:
        db_table = 'tb_model_config'
        managed = True
        app_label = 'node_mg'