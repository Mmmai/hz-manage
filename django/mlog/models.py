from django.db import models
from mapi.models import UserInfo,Datasource
from enum import Enum
import uuid
# Create your models here.
class LogModule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module_name = models.CharField(max_length=32, unique=True,verbose_name = "模块名称")
    label_name = models.CharField(max_length=32,null=False,default="",verbose_name = "标签")
    label_value = models.CharField(max_length=254,null=False,default="",verbose_name = "标签值")
    label_match = models.CharField(max_length=32,null=False,default="",verbose_name = "匹配方式")
    group = models.CharField(max_length=64, verbose_name="分组",null=True,blank=True)
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="是否启用",default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "tb_log_module"
        verbose_name = "数据源"
        app_label = 'mlog'
class LogFlow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=32,null=False,unique=True, verbose_name="流程名称")
    group = models.CharField(max_length=64, verbose_name="分组",null=True,blank=True)
    # token = models.CharField(max_length=128,null=True,blank=True)
    status = models.BooleanField(verbose_name="是否启用",default=True)
    update_time = models.DateTimeField(auto_now=True)
    create_time = models.DateTimeField(auto_now_add=True)
    describe = models.TextField( verbose_name="描述",null=True,blank=True,default="")

    # steps = models.ManyToManyField(to='LogModule',verbose_name='环节')
    steps = models.ManyToManyField(LogModule,through="LogFlowModule")

    class Meta:
        db_table = "tb_log_flow"
        verbose_name = "日志业务流程"
        app_label = 'mlog'

class LogFlowModule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step_id = models.ForeignKey(LogModule,on_delete=models.CASCADE)
    flow_id = models.ForeignKey(LogFlow,on_delete=models.CASCADE)
    order = models.IntegerField()
    class Meta:
        db_table = 'tb_log_flow_steps'
        ordering = ['order']
        app_label = 'mlog'

        

class LogFlowMission(models.Model):
    mission_status_choice = (
        (1,'Success'),
        (2,'Failed'),
        (3,'Unknown')
    )
    mission_id = models.CharField(max_length=254,primary_key=True)
    task_id = models.CharField(max_length=254)
    user_id = models.ForeignKey(UserInfo,on_delete=models.CASCADE)
    flow_id = models.ForeignKey(LogFlow,on_delete=models.CASCADE)
    dataSource_id = models.ForeignKey(Datasource,on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    mission_query = models.JSONField()
    results = models.JSONField()
    status = models.IntegerField(choices=mission_status_choice,default=3)
    # flow_sort
    class Meta:
        db_table = 'tb_log_flow_missions'
        ordering = ['create_time']
        app_label = 'mlog'