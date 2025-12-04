from audit.context import audit_context
from cmdb.models import (
    Models,
    ModelInstance,
    ModelFieldMeta
)
from cmdb.serializers import ModelInstanceSerializer
from cmdb.utils import password_handler, sys_config
import os
import json
import uuid
import logging
logger = logging.getLogger(__name__)


def get_instance_field_value(obj, field_name):
    """获取节点关联的实例IP"""
    field_values = ModelFieldMeta.objects.filter(
        model_instance=obj
    ).select_related('model_fields')
    # print(field_values)
    for field in field_values:
        if field.model_fields.name == field_name:
            if field.model_fields.type == 'password':
                return password_handler.decrypt_to_plain(field.data)
            else:
                return field.data
    return None


def get_instance_field_value_info(obj, field_name_list):
    """获取节点关联的实例IP"""
    res = {}
    field_values = ModelFieldMeta.objects.filter(
        model_instance=obj
    ).select_related('model_fields')

    # print(field_values)
    for field in field_values:
        if field.model_fields.name in field_name_list:
            # return field.data
            if field.model_fields.type == 'password':
                logger.debug(f"字段解密: {field.data}")
                res[field.model_fields.name] = password_handler.decrypt_to_plain(field.data)
            else:
                # print(field.model_fields.name,field.data)
                res[field.model_fields.name] = field.data
        # else:
        #     res[field.model_fields.name] = None
    return res


def update_asset_info(instance, info, context=None):
    """
    更新资产信息

    该函数用于更新指定实例的字段信息。它会比较传入的新信息与实例当前字段值，
    对于发生变化的字段进行更新操作。

    参数:
        instance: 模型实例对象，需要更新的资产实例
        info: 字典类型，包含需要更新的字段信息

    返回值:
        无返回值
    """
    if not info:
        logger.debug("No info to update")
        return
    logger.debug(f"update_asset_info: {instance.instance_name}, {info}")
    # 从更新信息中移除IP字段（如果存在）
    info.pop('ip', None)

    # 获取实例当前字段值信息
    res = get_instance_field_value_info(instance, info.keys())
    # 比较并筛选出需要更新的字段
    update_fields = {}
    if res:
        for k, v in res.items():
            _info_value = info.get(k)
            v_str = str(v)
            if isinstance(_info_value, dict):
                info_value = json.dumps(_info_value)
            else:
                info_value = str(_info_value)
            if v != info_value:
                logger.debug(f"字段更新: {k},旧{v},新{info_value}")
                update_fields[k] = info_value
    # 如果有需要更新的字段且实例存在，则执行更新操作
    if not context:
        correlation_id = str(uuid.uuid4())
        context = {
            "request_id": correlation_id,
            "correlation_id": correlation_id,
            "operator": 'system',
            "operator_ip": '127.0.0.1',
            "comment": '首次添加时，自动获取并更新资产信息'
        }
    with audit_context(**context):
        if update_fields and instance:
            serializer = ModelInstanceSerializer(
                instance=instance,
                data={
                    "model": instance.model.id,
                    "fields": update_fields
                },
                partial=True,
                context={
                    'request': None,
                    'from_excel': False
                }
            )
            if serializer.is_valid(raise_exception=True):
                try:
                    serializer.save()
                    logger.info(f"update field success. update_fields: {update_fields}")
                except Exception as e:
                    logger.error(f"Failed to save updated fields: {e}")
        else:
            logger.debug(f"{instance.instance_name} has no fields to update")


def node_inventory(node):
    """
    获取节点的配置信息，生成Ansible inventory格式的字典

    参数:
        node: 节点对象，包含节点的IP地址、代理信息和模型实例等属性

    返回值:
        dict: 包含节点SSH连接配置的inventory字典，格式为Ansible所需格式
    """
    proxy = node.proxy
    ssh_user = get_instance_field_value(node.model_instance, 'system_user') or 'root'
    ssh_pass = get_instance_field_value(node.model_instance, 'system_password') or ''
    ssh_port = get_instance_field_value(node.model_instance, 'ssh_port') or 22

    # 构建基础inventory配置
    inventory = {'all': {'hosts': {node.ip_address: {
        'ansible_ssh_user': ssh_user,
        'ansible_ssh_pass': ssh_pass,
        'ansible_ssh_port': ssh_port,
        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
    }}}}

    # 如果存在代理节点，则添加代理跳转配置
    if proxy:
        if proxy.proxy_type != 'zabbix' and proxy.enabled:
            jump_host = proxy.ip_address
            jump_user = proxy.auth_user
            jump_pass = proxy.auth_pass
            jump_port = proxy.port
            inventory['all']['hosts'][node.ip_address][
                'ansible_ssh_common_args'] += f" -o ProxyCommand=\"sshpass -p '{jump_pass}' ssh -W %h:%p -p {jump_port} {jump_user}@{jump_host}\""
    return inventory


def nodes_inventory(nodes):
    """
    获取多个节点的配置信息，生成Ansible inventory格式的字典

    参数:
        nodes: 节点对象列表，每个节点包含IP地址、代理信息和模型实例等属性

    返回值:
        dict: 包含所有节点SSH连接配置的inventory字典，格式为Ansible所需格式
    """
    if not nodes:
        return {}

    hosts = {}

    # 遍历所有节点，为每个节点构建inventory配置
    for node in nodes:
        proxy = node.proxy
        ssh_user = get_instance_field_value(node.model_instance, 'system_user') or 'root'
        ssh_pass = get_instance_field_value(node.model_instance, 'system_password') or ''
        ssh_port = get_instance_field_value(node.model_instance, 'ssh_port') or 22

        # 为当前节点构建inventory配置
        host_config = {
            'ansible_ssh_user': ssh_user,
            'ansible_ssh_pass': ssh_pass,
            'ansible_ssh_port': ssh_port,
        }

        # 如果存在代理节点，则添加代理跳转配置
        if proxy:
            if proxy.proxy_type != 'zabbix' and proxy.enabled:
                jump_host = proxy.ip_address
                jump_user = proxy.auth_user
                jump_pass = proxy.auth_pass
                jump_port = proxy.port
                host_config[
                    'ansible_ssh_common_args'] = f" -o StrictHostKeyChecking=no -o ProxyCommand=\"sshpass -p '{jump_pass}' ssh -W %h:%p -p {jump_port} {jump_user}@{jump_host}\""

        # 将当前节点配置添加到hosts字典中
        hosts[node.ip_address] = host_config

    # 构建完整的inventory结构
    inventory = {
        'all': {
            'hosts': hosts
        }
    }

    return inventory


if __name__ == "__main__":
    # print(123)
    # info = {"hostname": "localhost", "ip": "192.168.163.160", "kernel": "3.10.0-693.el7.x86_64", "os_arch": "x86_64", "os_type": "Linux", "os_name": "RedHat 7.4", "os_version": "7.4", "cpu_info": {"model": "AMD Ryzen 7 8845HS w/ Radeon 780M Graphics", "cores": 8}, "memory_info": {"total_mb": "3.685546875"}, "disk_size": ["40.00 GB"], "hardware_info": {"name": "VMware Virtual Platform", "vendor": "VMware, Inc.", "serial_number": "VMware-56 4d 4c 32 e1 91 70 bb-b5 68 c2 d9 aa 2a 8d 91"}}
    # obj = ModelInstance.objects.get(id="f59bef929aa24dd89d09c54ea3928735")
    # print(obj)
    # # print(get_instance_field_value(obj, 'ip'))
    # # print(get_instance_field_value_info(obj, ['system_user','system_password','ssh_port','ipmi_user','ipmi_password','mgmt_ip']))
    # update_asset_info(obj,info)
    pass
