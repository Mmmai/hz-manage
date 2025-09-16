# notifications/signals.py
from django.dispatch import receiver
from django.apps import apps
from .models import (
    Nodes,
    NodeSyncZabbix
)
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, post_migrate

from django.db import transaction
from .utils.get_cmdb_data import get_instance_field_value,get_instance_field_value_info
from .tasks import ansible_getinfo,zabbix_sync
from cmdb.signals import instance_signal
from cmdb.models import ModelInstanceGroupRelation
# 监听实例的创建和删除信号
@receiver(instance_signal)
def sync_node(sender,instance,action, **kwargs):
    def delayed_process():
        #确保在事务提交后执行操作
        print(f"Processing instance {instance} after transaction commit")
        print("IP=" + get_instance_field_value(instance, 'ip'))
        if action == 'delete':
            try:
                node_obj = Nodes.objects.get(model_instance=instance)
                if node_obj.enable_sync:
                # 操作zabbix删除主机
                    zabbix_sync.delay(is_delete=True,host_info={'ip':node_obj.ip_address})
                #删除节点
                node_obj.delete()
                print(f"节点[{instance}]删除成功")
            except Nodes.DoesNotExist:
                print(f"节点[{instance}]不存在，无法删除")
            return
        else:

            #后续预留增加是否默认开启同步的功能
            obj,created = Nodes.objects.update_or_create(
                model_instance=instance,
                defaults={
                        "ip_address": get_instance_field_value(instance, 'ip') ,
                        "model": instance.model,
                        "create_user": instance.create_user,
                        "update_user": instance.update_user
                }
            )

            # 信息获取
            _host_info = {}
            if instance.model.name == 'hosts':
                _host_info = get_instance_field_value_info(instance, ['ipmi_user','ipmi_password',
                                                                     'mgmt_ip'])
                if _host_info['mgmt_ip']:
                    # 0-agent , 1-agent+ipmi , 2-snmp
                    host_info = {**_host_info, 'ip': obj.ip_address,'hostname': instance.instance_name,'type': 1}
                else:
                    host_info = {**_host_info, 'ip': obj.ip_address,'hostname': instance.instance_name,'type': 0}
            elif instance.model.name == 'switches':
                # _host_info = get_instance_field_value_info(instance, ['mgmt_user','mgmt_password'])
                host_info = {'ip': obj.ip_address,'hostname': instance.instance_name,'type': 2}
            groups = []
            instance_group_relations = ModelInstanceGroupRelation.objects.filter(
                instance=instance
            ).select_related('group')
            for relation in instance_group_relations:
                if relation.group.path not in ['所有', '所有/空闲池']:
                    groups.append(relation.group.path.replace('所有/', ''))
            if created:
                #触发node探测任务
                info_task = ansible_getinfo.delay(obj.id)
                print(f"节点[{instance}]创建成功")
            else:

                print(f"节点[{instance}]更新成功")
            if obj.enable_sync:
                #触发zabbix同步
                zabbix_sync.delay(host_info={**host_info,'groups':groups})
                print(f"节点[{instance}]触发了zabbix同步任务")
    
    transaction.on_commit(delayed_process)

@receiver(post_save, sender=Nodes)
def create_initial_sync_zabbix(sender, instance, created, **kwargs):
    def delayed_process():
        if created and instance.enable_sync:
            # 创建与节点关联的NodeSyncZabbix实例
            NodeSyncZabbix.objects.create(node=instance)
            # 触发zabbix同步
            # 触发agent安装任务

            print(f"为节点[{instance}]创建了初始的NodeSyncZabbix实例")
    transaction.on_commit(delayed_process)

