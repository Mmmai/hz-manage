import uuid
import logging

from django.dispatch import receiver
from django.apps import apps
from django.db import transaction
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, post_migrate

from cmdb.signals import model_instance_signal, model_signal
from cmdb.public_services import PublicModelInstanceService
from cmdb.models import ModelInstanceGroupRelation
from audit.context import audit_context
from mapi.messages import zabbix_config_updated


from .models import (
    Nodes,
    NodeSyncZabbix,
    Proxy,
    ModelConfig
)
from .utils import sys_config
from .tasks import (
    ansible_getinfo,
    zabbix_sync,
    ansible_agent_install,
    zabbix_proxy_sync,
    sync_node_mg
)


logger = logging.getLogger(__name__)

# 监听模型创建信号，创建初始化同步配置


@receiver(model_signal)
def create_model_sync_config(sender, instance, action, **kwargs):
    def delayed_process():
        if action == 'create':
            # 定义不同模型类型的配置映射
            MODEL_CONFIG_MAP = {
                "hosts": {
                    "is_manage": True,
                    "built_in": True,
                    "zabbix_sync_info": [
                        {"type": "agent", "template": "Linux by Zabbix agent"},
                        {"type": "ipmi", "template": "Chassis by IPMI"}
                    ]
                },
                "switches": {
                    "is_manage": True,
                    "built_in": True,
                    "zabbix_sync_info": [
                        {"type": "snmp", "template": "Generic by SNMP"},
                    ]
                },
                "npb": {
                    "is_manage": True,
                    "built_in": True,
                    "zabbix_sync_info": [
                        {"type": "snmp", "template": ""},
                    ]
                }
            }

            # 根据模型名称获取配置或使用默认配置
            model_config_base = MODEL_CONFIG_MAP.get(instance.name, {
                "is_manage": False,
                "built_in": False,
                "zabbix_sync_info": []
            })

            # 构建最终配置字典
            modelConfigDict = {
                "model": instance,
                **model_config_base
            }

            try:
                obj, created = ModelConfig.objects.update_or_create(
                    model=instance,
                    defaults=modelConfigDict
                )
                if created:
                    logger.info(f"创建模型同步配置:{instance.name}")
            except Exception as e:
                logger.error(f"创建模型同步配置失败:{instance.name}, 错误信息:{str(e)}")
                raise
    transaction.on_commit(delayed_process)


# 用于存储实例保存前状态的字典
model_config_pre_save_state = {}

# 监听ModelConfig的pre_save信号，保存更新前的数据


@receiver(pre_save, sender=ModelConfig)
def model_config_pre_save(sender, instance, **kwargs):
    # 如果是更新操作（不是新建），获取更新前的数据
    if instance.pk:
        try:
            old_instance = ModelConfig.objects.get(pk=instance.pk)
            # 保存旧实例到全局字典中
            model_config_pre_save_state[instance.pk] = old_instance
        except ModelConfig.DoesNotExist:
            # 如果实例不存在，说明是新建操作，不需要保存旧状态
            pass


@receiver(post_save, sender=ModelConfig)
def model_config_signal(sender, instance, created, **kwargs):
    # 判断is_manage的改变
    if not created:
        # 获取保存前的实例
        old_instance = model_config_pre_save_state.get(instance.pk)
        if old_instance:
            # 比较字段变化
            changed_fields = {}

            # 比较is_manage字段
            if old_instance.is_manage != instance.is_manage:
                changed_fields['is_manage'] = {
                    'old': old_instance.is_manage,
                    'new': instance.is_manage
                }
                # 停用-> 启用,全量同步node
                if not old_instance.is_manage and instance.is_manage:
                    sync_node_mg.delay(model_id=instance.model.id)
                # 启用-> 停用
                else:
                    pass

            # 比较zabbix_sync_info字段
            if old_instance.zabbix_sync_info != instance.zabbix_sync_info:
                changed_fields['zabbix_sync_info'] = {
                    'old': old_instance.zabbix_sync_info,
                    'new': instance.zabbix_sync_info
                }

            # 如果有字段变化，记录日志或执行相应操作
            if changed_fields:
                logger.info(f"ModelConfig {instance.pk} 字段变化: {changed_fields}")
                # 在这里可以添加你想要执行的业务逻辑
                # 例如触发某些任务或通知

            # 清理保存的旧实例数据
            model_config_pre_save_state.pop(instance.pk, None)


# 监听实例的创建和删除信号
@receiver(model_instance_signal)
def sync_node(sender, instance, action, **kwargs):
    def delayed_process():
        # 确保在事务提交后执行操作
        ip = PublicModelInstanceService.get_instance_field_value(instance, 'ip')
        if not ip:
            logger.warning(f"实例[{instance.instance_name}]没有IP地址，跳过节点同步。")
            return

        # 后续预留增加是否默认开启同步的功能
        if instance.model.name == "hosts":
            obj, created = Nodes.objects.update_or_create(
                model_instance=instance,
                defaults={
                    "ip_address": ip,
                    "model": instance.model,
                    "create_user": instance.create_user,
                    "update_user": instance.update_user
                }
            )
            if created:
                # 只有主机才能触发node探测任务
                info_task = ansible_getinfo.delay(obj.id)
                logger.debug(f"节点[{instance.instance_name}]触发资产更新任务。")
                logger.info(f"节点[{instance.instance_name}]创建成功")
                if not sys_config.is_zabbix_sync_enabled():
                    return
                if obj.enable_sync:
                    # 只有在新建主机的时候才触发ansible安装agent
                    agent_task = ansible_agent_install.delay(obj.id)
                    logger.debug(f"节点[{instance.instance_name}]触发agent安装")
            else:
                logger.info(f"节点[{instance.instance_name}]更新成功")
            if not sys_config.is_zabbix_sync_enabled():
                return
            if obj.enable_sync:
                # 触发zabbix同步
                zabbix_sync.delay(instance_id=instance.id, ip=ip)
                logger.info(f"节点[{instance.instance_name}]IP[{ip}]触发了zabbix同步任务")
        # 非主机模型的同步，比如交换机
        else:
            if not sys_config.is_zabbix_sync_enabled():
                return
            obj, created = Nodes.objects.update_or_create(
                model_instance=instance,
                defaults={
                    "ip_address": ip,
                    "model": instance.model,
                    "create_user": instance.create_user,
                    "update_user": instance.update_user
                }
            )
            zabbix_sync.delay(instance_id=instance.id, ip=ip)
            logger.info(f"节点[{instance.instance_name}]IP[{ip}]触发了zabbix同步任务")
    # 判断模型是否可管理
    obj = ModelConfig.objects.get(model=instance.model)
    if not obj.is_manage:
        return
    # 删除动作
    if action == 'delete':
        try:
            ip = PublicModelInstanceService.get_instance_field_value(instance, 'ip')
            node_obj = Nodes.objects.get(model_instance=instance)
            if sys_config.is_zabbix_sync_enabled():
                if node_obj.enable_sync:
                    # 操作zabbix删除主机
                    zabbix_sync.delay(instance_id=instance.id, is_delete=True, ip=ip)
            else:
                logger.warning(f"Zabbix sync is not enabled. 节点[{instance.instance_name}]没有从zabbix上删除")
            # 删除节点
            node_obj.delete()
            logger.info(f"节点[{instance.instance_name}]删除成功")
        except Nodes.DoesNotExist:
            logger.error(f"节点[{instance.instance_name}]不存在，无法删除")
        return
    else:
        transaction.on_commit(delayed_process)


@receiver(post_save, sender=Nodes)
def create_initial_sync_zabbix(sender, instance, created, **kwargs):
    """
    节点创建成功后触发zabbix同步创建及更新
    """
    def delayed_process():
        if created:
            # 创建与节点关联的NodeSyncZabbix实例
            NodeSyncZabbix.objects.create(node=instance)
            # 触发zabbix同步
            # 触发agent安装任务
            logger.info(f"为节点[{instance.model_instance.instance_name}]创建了初始的NodeSyncZabbix实例")
    transaction.on_commit(delayed_process)
# @receiver(post_save, sender=Nodes)


@receiver(post_save, sender=Proxy)
def proxy_sync_zabbix(sender, instance, created, **kwargs):
    """
    proxy创建成功后触发zabbix同步创建及更新
    """
    def delayed_process():
        if not sys_config.is_zabbix_sync_enabled() or instance.proxy_type not in ['all', 'zabbix']:
            return
        proxy_info = {
            "proxy_id": instance.id,
            "proxy_name": instance.name,
            "proxy_ip": instance.ip_address,
            "proxy_type": instance.proxy_type,
            "proxy_status": instance.enabled,
            "zbx_proxyid": instance.zbx_proxyid
        }
        if created:
            zabbix_proxy_sync.delay(proxy_info=proxy_info, action='create')
        else:
            zabbix_proxy_sync.delay(proxy_info=proxy_info, action='update')
    transaction.on_commit(delayed_process)


@receiver(post_delete, sender=Proxy)
def proxy_delete_zabbix(sender, instance, **kwargs):
    """
    proxy删除成功后触发zabbix同步删除
    """
    if not sys_config.is_zabbix_sync_enabled():
        return
    if instance.proxy_type in ['all', 'zabbix']:
        proxy_info = {
            "proxy_name": instance.name,
            "proxy_ip": instance.ip_address,
        }
        zabbix_proxy_sync.delay(proxy_info=proxy_info, action='delete')


@receiver(zabbix_config_updated)
def handle_zabbix_config_update(sender, **kwargs):
    """
    处理Zabbix配置更新的信号，触发节点管理平台配置刷新
    """
    logger.info("Received zabbix_config_updated signal, reloading configuration.")
    sys_config.load_config(force=True)
