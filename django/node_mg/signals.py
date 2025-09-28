# notifications/signals.py
from django.dispatch import receiver
from django.apps import apps
from .models import (
    Nodes,
    NodeSyncZabbix
)
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, post_migrate
import logging
from .utils import zabbix_config
from django.db import transaction
from .utils.cmdb_tools import get_instance_field_value,get_instance_field_value_info
from .tasks import ansible_getinfo,zabbix_sync,ansible_agent_install
from cmdb.signals import instance_signal
from cmdb.models import ModelInstanceGroupRelation
logger = logging.getLogger(__name__)

# 监听实例的创建和删除信号
@receiver(instance_signal)
def sync_node(sender,instance,action, **kwargs):
    def delayed_process():
        #确保在事务提交后执行操作
        logger.info(f"Processing instance {instance} after transaction commit")
        logger.info("IP=" + get_instance_field_value(instance, 'ip'))
        ip = get_instance_field_value(instance, 'ip')
        if action == 'delete':
            try:
                if instance.model.name == "hosts":
                    node_obj = Nodes.objects.get(model_instance=instance)
                    if zabbix_config.is_zabbix_sync_enabled():                        
                        if node_obj.enable_sync:
                        # 操作zabbix删除主机
                            zabbix_sync.delay(instance_id=instance.id,is_delete=True,ip=ip)
                    #删除节点
                    node_obj.delete()
                    logger.info(f"节点[{instance.instance_name}]删除成功")
                else:
                    zabbix_sync.delay(instance_id=instance.id,is_delete=True,ip=ip)
            except Nodes.DoesNotExist:
                logger.error(f"节点[{instance.instance_name}]不存在，无法删除")
            return
        else:
            #后续预留增加是否默认开启同步的功能
            if instance.model.name == "hosts":
                obj,created = Nodes.objects.update_or_create(
                    model_instance=instance,
                    defaults={
                            "ip_address": ip ,
                            "model": instance.model,
                            "create_user": instance.create_user,
                            "update_user": instance.update_user
                    }
                )
                if created:
                    #只有主机才能触发node探测任务
                    info_task = ansible_getinfo.delay(obj.id)
                    logger.debug(f"节点[{instance.instance_name}]触发资产更新任务。")
                    logger.info(f"节点[{instance.instance_name}]创建成功")

                    if not zabbix_config.is_zabbix_sync_enabled():
                        return
                    if obj.enable_sync:
                        # 只有在新建主机的时候才触发ansible安装agent
                        agent_task = ansible_agent_install.delay(obj.id)
                        logger.debug(f"节点[{instance.instance_name}]触发agent安装")
                else:
                    logger.info(f"节点[{instance.instance_name}]更新成功")
                if not zabbix_config.is_zabbix_sync_enabled():
                    return
                if obj.enable_sync:
                    #触发zabbix同步
                    zabbix_sync.delay(instance_id=instance.id,ip=ip)
                    logger.info(f"节点[{instance.instance_name}]IP[{ip}]触发了zabbix同步任务")
            # 非主机模型的同步，比如交换机
            else:
                if not zabbix_config.is_zabbix_sync_enabled():
                    return
                zabbix_sync.delay(instance_id=instance.id,ip=ip)
                logger.info(f"节点[{instance.instance_name}]IP[{ip}]触发了zabbix同步任务")

                
    transaction.on_commit(delayed_process)

@receiver(post_save, sender=Nodes)
def create_initial_sync_zabbix(sender, instance, created, **kwargs):
    def delayed_process():
        if created:
            # 创建与节点关联的NodeSyncZabbix实例
            NodeSyncZabbix.objects.create(node=instance)
            # 触发zabbix同步
            # 触发agent安装任务

            print(f"为节点[{instance.model_instance.instance_name}]创建了初始的NodeSyncZabbix实例")
    transaction.on_commit(delayed_process)

