from celery import chain, shared_task,group
from celery.result import AsyncResult

from .models import Nodes,NodeInfoTask,NodeSyncZabbix,Proxy,ModelConfig
from cmdb.models import (
    Models,
    ModelFields,
    ModelInstance,
    ModelFieldMeta,
    ModelInstanceGroupRelation
    )
import os,time,logging
from django.utils import timezone
import ping3
import re
from .utils.cmdb_tools import get_instance_field_value
from .utils.zabbix import ZabbixAPI
from .utils import sys_config
from .utils.commFunc import compare_interfaces
from .utils.cmdb_tools import get_instance_field_value,get_instance_field_value_info,update_asset_info,node_inventory

logger = logging.getLogger(__name__)

if os.name != 'nt':
    from .utils.ansible import AnsibleAPI
    ANSIBLE_AVAILABLE = True
else:
    ANSIBLE_AVAILABLE = False
    logger.warning("Ansible functionality not available on Windows")
@shared_task
def aggregate_results(results):
    """
    处理批量任务的结果
    """
    # 参数验证
    if results is None:
        return {"success": 0, "failure": 0}
    
    success_count = 0
    failure_count = 0
    
    for res in results:
        try:
            if res.get('status') == 'success':
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            failure_count += 1
            logger.error(f"Failed: Exception occurred - {str(e)}")
            
    return {"total":len(results),"success": success_count, "failure": failure_count}

@shared_task(bind=True)
def sync_node_mg(self,model_id=None):
    """
    同步节点管理信息的 Celery 任务
    
    该函数会遍历符合条件的模型实例，提取其中 IP 地址字段，并在 Nodes 表中创建或更新对应的节点记录。
    
    Args:
        self: Celery 任务对象自身
        model_id (int, optional): 指定要同步的模型 ID，如果不提供则同步所有符合条件的模型
        
    Returns:
        str: 同步操作结果信息，格式为"同步成功"
        
    Raises:
        Exception: 当发生异常时会自动重试，延迟60秒后重新执行任务
    """
    try:
        from django.db import transaction
        # 获取所有包含 IP 字段的模型
        modelFieldHasIp = [ i.model.id for i in ModelFields.objects.filter(name="ip") ] 
        # sync_model_list = [ i.id for i in Models.objects.filter(name__in=['hosts']) ]
        # 筛选出管理状态为 True 且包含 IP 字段的模型
        sync_model_list = [ i.id for i in ModelConfig.objects.filter(is_manage=True) if i.id in modelFieldHasIp ]
        if model_id:
            models_to_process = Models.objects.filter(id=model_id)
        else:
            models_to_process = Models.objects.filter(id__in=sync_model_list)
            
        total_node_create_counter = 0
        total_node_update_counter = 0
        total_fail_count = 0
        
        # 按每个model单独处理
        for model in models_to_process:
            logger.info(f"开始处理模型: {model.name} ({model.id})")
            node_create_counter = 0
            node_update_counter = 0
            fail_instance = []
            
            # 获取该model下的所有实例
            all_instance = ModelInstance.objects.filter(model=model)
            for _instance in all_instance:   
                try:
                    # 获取当前实例的所有字段元数据
                    field_values = ModelFieldMeta.objects.filter(
                        model_instance=_instance
                    ).select_related('model_fields')
                    ip_field = None
                    for field in field_values:
                        if field.model_fields.name == 'ip':
                            ip_field = field.data
                            break
                    if not ip_field:
                        fail_instance.append(_instance.instance_name)
                        continue
                    # 缓存IP字段值，避免重复查询
                    ip_value = ip_field
                except Exception as e:
                    fail_instance.append(_instance.instance_name)
                    continue         
                # 创建或更新节点记录
                with transaction.atomic():
                    node_obj,node_created = Nodes.objects.update_or_create(
                        model_instance=_instance,
                        defaults={
                        "ip_address": ip_value,
                        "model": _instance.model,
                        "create_user": _instance.create_user,
                        "update_user": _instance.update_user
                        }
                    )
                    if node_created:
                        node_create_counter += 1
                    else:
                        node_update_counter += 1
                        
            logger.info(f"模型 {model.name} 处理完成: 创建[{node_create_counter}],更新[{node_update_counter}]失败[{len(fail_instance)}],失败实例[{','.join(fail_instance)}]")
            total_node_create_counter += node_create_counter
            total_node_update_counter += node_update_counter
            total_fail_count += len(fail_instance)
            
        logger.info(f"全部模型处理完成: 总创建[{total_node_create_counter}],总更新[{total_node_update_counter}]总失败[{total_fail_count}]")
    except Exception as exc:
        # 发生异常时自动重试，延迟60秒
        raise self.retry(exc=exc, countdown=60)
    return f"同步成功"


@shared_task(bind=True, max_retries=3)
def ping_server(self, node,ip, timeout=5):
    """
    执行 Ping 检测任务
    :param ip: 目标 IP 地址
    :param timeout: 超时时间（秒）
    :return: 检测结果字典
    """
    try:
        response = ping3.ping(
            ip,
            timeout=timeout,
            unit='ms',
            retry=2,  # 自动重试次数
            packet_num=3  # 发送数据包数量
        )
        
        # 记录结果
        is_reachable = response is not None
        error = None if is_reachable else f"Ping failed after {timeout}ms"
        
        PingResult.objects.create(
            ip_address=ip,
            is_reachable=is_reachable,
            response_time=response if is_reachable else None,
            error_message=error
        )
        
        return {
            'status': 'success',
            'ip': ip,
            'response_time': float(response) if response else None,
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            return self.retry(exc=exc, countdown=2 ** self.request.retries)
        
        # 记录最终失败结果
        PingResult.objects.create(
            ip_address=ip,
            is_reachable=False,
            error_message=str(exc)
        )
        return {
            'status': 'failed',
            'ip': ip,
            'error': str(exc)
        }
@shared_task(bind=True, max_retries=3)
def ansible_task(self, node, module, args):
    """
    执行 Ansible 任务
    :param node: 目标节点对象
    :param module: Ansible 模块名称
    :param args: 模块参数
    :return: 任务结果字典
    """
    import ansible_runner
    try:
        r = ansible_runner.run(
            private_data_dir='/tmp/ansible_runner',  # 临时目录
            inventory={ 'all': { 'hosts': { node.ip_address: {} } } },  # 动态库存
            module=module,
            module_args=args,
            quiet=True
        )
        
        if r.rc != 0:
            raise Exception(f"Ansible task failed with return code {r.rc}")
        
        # 提取结果
        result = r.get_fact_cache(node.ip_address)
        
        return {
            'status': 'success',
            'node': node.ip_address,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }
    
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            return self.retry(exc=exc, countdown=2 ** self.request.retries)
        
        return {
            'status': 'failed',
            'node': node.ip_address,
            'error': str(exc)
        }

@shared_task(bind=True)
def ansible_getinfo_batch(self, node_ids,context):
    """
    批量执行 Ansible 获取系统信息任务
    
    该函数使用 Celery 的 group 功能并行执行多个 ansible_getinfo 任务，
    每个节点独立执行并更新各自的数据库记录。
    
    :param self: 当前任务实例
    :param node_ids: 节点ID列表
    :return: 批量任务执行结果字典
    """
    results = {}
    
    # 使用 Celery 的 group 功能并行执行多个任务
    job = group(ansible_getinfo.s(node_id,context) for node_id in node_ids)
    
    # 执行并等待结果
    # result = job.apply_async()
    chord_result = job | aggregate_results.s()
    return chord_result.apply_async()     
@shared_task(bind=True, max_retries=2)
def ansible_getinfo(self, node_id,context):
    """
    执行 Ansible 获取系统信息的异步任务。

    该函数通过 Ansible 执行指定的 Playbook 来获取目标节点的系统信息，
    并将执行结果记录到数据库中。如果任务失败，会根据配置进行重试。

    :param self: 当前任务实例，用于访问任务上下文和控制任务行为（如重试）
    :param node_id: 目标节点的 ID，用于从数据库中获取对应的节点对象
    :return: 包含任务状态、节点 IP、执行结果和时间戳的字典
    """

    ansible_api = AnsibleAPI()
    try:
        start = time.perf_counter()
        node = Nodes.objects.get(id=node_id)
        logger.info(f"Starting Ansible playbook for node {node.ip_address}")

        # 构造 Ansible Inventory 和 Playbook 路径
        inventory = node_inventory(node)
        playbook_path = '/opt/get_system_info.yaml'  # 可考虑从配置中读取

        # 执行 Ansible Playbook
        result = ansible_api.run_playbook(playbook_path, inventory)
        end_time = time.perf_counter()

        cost_time = round(end_time - start, 2)

        # 如果执行失败，记录失败信息并抛出异常
        if result['rc'] != 0:
            try:
                NodeInfoTask.objects.create(
                    node=node,
                    status=False,
                    results=str(result),
                    error_message=result.get('error', ''),
                    cost_time=cost_time,
                )
            except Exception as e:
                logger.error(f"Failed to create NodeInfoTask for node {node.ip_address}: {str(e)}")
            logger.error(f"Ansible playbook failed with return code {result['rc']}, took {cost_time} seconds")
            #self.update_state(state="FAILURE", meta={"status": "fail", "code": 400})
            raise Exception(f"Ansible playbook failed with return code {result['rc']}")

        info = result.get('debug', {})

        # 记录成功执行的结果
        try:
            NodeInfoTask.objects.create(
                node=node,
                status=True,
                asset_info=info,
                results=result,
                error_message=result.get('error', ''),
                cost_time=cost_time,
            )
        except Exception as e:
            logger.error(f"Error creating or updating node {node.ip_address} info task: {str(e)}")

        # 如果启用了资产自动更新，则更新资产信息
        if sys_config.is_asset_auto_update_enabled():
            logger.info(f"Updating asset info for node {node.ip_address}")
            try:
                update_asset_info(node.model_instance, info,context)
            except Exception as e:
                logger.error(f"Failed to update asset info for node {node.ip_address}: {str(e)}")

        logger.info(f"Ansible playbook completed in {cost_time} seconds")
        return {
            'status': 'success',
            'node': node.ip_address,
            'result': info,
            'timestamp': timezone.now().isoformat()
        }
    except Nodes.DoesNotExist:
        logger.error(f"Node with id {node_id} does not exist.")
        raise
    except Exception as exc:
        logger.error(f"Unexpected error in ansible_getinfo for node_id {node_id}: {str(exc)}")
        # 重试任务，延迟时间随重试次数指数增长
        if self.request.retries >= self.max_retries - 1:
            logger.info("超过最大重试次数，任务失败")
        else:
            logger.info("任务重试中...")
            raise self.retry(exc=exc, countdown=2**self.request.retries)



@shared_task(bind=True)
def ansible_agent_install_batch(self, node_ids):
    """
    批量执行 Ansible 安装 Zabbix Agent 任务
    :param node_ids: 节点ID列表
    :return: 批量任务结果字典
    """
    results = {}
    
    # 使用 Celery 的 group 功能并行执行多个任务
    # print("node_ids:", node_ids)
    # 创建子任务组
    job = group(ansible_agent_install.s(node_id) for node_id in node_ids)
    
    # 执行并等待结果
    # result = job.apply_async()
    chord_result = job | aggregate_results.s()
    return chord_result.apply_async()    
    # 等待所有任务完成
    # try:
    #     # 等待所有任务完成，设置合理的超时时间
    #     task_results = result.get(timeout=600)  # 5分钟超时
        
    #     # 整理结果
    #     for i, task_result in enumerate(task_results):
    #         node_id = node_ids[i]
    #         results[node_id] = task_result
            
    #     return {
    #         'status': 'completed',
    #         'results': results,
    #         'timestamp': timezone.now().isoformat()
    #     }
    # except Exception as exc:
    #     logger.exception("Batch ansible agent install task failed")
    #     return {
    #         'status': 'failed',
    #         'error': str(exc),
    #         'timestamp': timezone.now().isoformat()
    #     }

@shared_task(bind=True)
def ansible_agent_install(self, node_id):
    """
    执行 Ansible 安装 Zabbix Agent 任务
    :param node_id: 目标节点 ID
    :return: 任务结果字典
    """
    ansible_api = AnsibleAPI()
    start = time.perf_counter()
    try:
        node = Nodes.objects.get(id=node_id)
    except Nodes.DoesNotExist:
        logger.error(f"Node with id {node_id} does not exist.")
        return {
            'status': 'failed',
            'error': 'Node not found',
            'timestamp': timezone.now().isoformat()
        }
    except Exception as e:
        logger.exception("Unexpected error when fetching node.")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }

    try:
        inventory = node_inventory(node)
        server_ip = sys_config.get('server')
        extra_vars = {
            'hostIp': node.ip_address,
            'serverIp': server_ip,
            'serverActiveIp': server_ip,
        }

        if node.proxy:
            proxy_ip = node.proxy.ip_address
            extra_vars['serverIp'] = f"{server_ip},{proxy_ip}"
            extra_vars['serverActiveIp'] = f"{server_ip},{proxy_ip}"

        playbook_path = '/opt/zabbix_agent/main.yaml'
        result = ansible_api.run_playbook(playbook_path, inventory, extra_vars=extra_vars)
        end_time = time.perf_counter()
        cost_time = float(f"{end_time - start:.2f}")

        defaults = {
            "results": str(result),
            "error_message": result.get('error', ''),
            "cost_time": cost_time,
        }

        if result['rc'] != 0:
            defaults["agent_status"] = 0
            NodeSyncZabbix.objects.update_or_create(node=node, defaults=defaults)
            logger.error(f"Ansible playbook failed with return code {result['rc']}, took {cost_time} seconds")
            return {
                'status': 'failed',
                'node': node.ip_address,
                'result': result,
                'timestamp': timezone.now().isoformat()
            }

        defaults["agent_status"] = 1
        NodeSyncZabbix.objects.update_or_create(node=node, defaults=defaults)
        logger.info(f"Ansible playbook completed in {cost_time} seconds")

        return {
            'status': 'success',
            'node': node.ip_address,
            'result': result,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as exc:
        end_time = time.perf_counter()
        logger.exception(f"Unexpected error during Ansible execution for node {node.ip_address}")
        return {
            'status': 'failed',
            'node': node.ip_address,
            'error': str(exc),
            'timestamp': timezone.now().isoformat()
        }

def is_valid_ip(ip):
    """校验是否为合法的 IPv4 或 IPv6 地址"""
    ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    ipv6_pattern = r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    return re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip)

def build_host_info(instance, ip):
    """根据模型类型构造 host_info"""
    # zabbix_sync_info = ModelConfig.objects.get(model=instance.model).zabbix_sync_info
    zabbix_sync_info = sys_config.get(instance.model.name)
    if instance.model.name == 'hosts':
        _host_info = get_instance_field_value_info(instance, ['mgmt_user', 'mgmt_password', 'mgmt_ip', 'device_status'])
        host_type = 1 if _host_info.get('mgmt_ip') else 0
        return {**_host_info, 'ip': ip, 'hostname': instance.instance_name, 'type': host_type,'zabbix_sync_info': zabbix_sync_info}
    # elif instance.model.name == 'switches':
    else:
        # 根据模型的config，获取接口
        return {
            'ip': ip,
            'hostname': instance.instance_name,
            'type': 2,
            'device_status': get_instance_field_value(instance, 'device_status'),
            'zabbix_sync_info': zabbix_sync_info
        }
    return None

def build_interfaces_and_args(host_info):
    print(host_info)
    """构造接口信息和主机其他参数"""
    if host_info.get('zabbix_sync_info') is None:
        raise None

    type_map = {"agent":{"type":"1","port":"10050"},"snmp": {"type":"2","port":"161"},"ipmi":{"type":"3","port": "623"}}
    interfaces = []
    other_args = {}
    template_names_by_type = {"1": "", "2": "", "3": ""}
    for _zabbix_sync_info in host_info.get('zabbix_sync_info'):
        if _zabbix_sync_info.get("type"):
            _interface = {
                "type": type_map[_zabbix_sync_info.get("type")]["type"],
                "main": "1",
                "useip": "1",
                "ip": host_info.get("ip"),
                "dns": "",
                "port": type_map[_zabbix_sync_info.get("type")]["port"]
            }
            if _zabbix_sync_info.get("type") == "snmp":
                _interface["details"] = {
                    "version": "2",
                    "bulk": "0",
                    "community": "{$SNMP_COMMUNITY}"
                }
                template_names_by_type['2'] = _zabbix_sync_info.get("template")
            elif _zabbix_sync_info.get("type") == "ipmi":
                if not host_info.get('mgmt_ip'):
                    continue
                _interface["ip"] = host_info.get('mgmt_ip')
                other_args = {
                    "ipmi_authtype": 6,
                    "ipmi_password": host_info.get('mgmt_password'),
                    "ipmi_username": host_info.get('mgmt_user'),
                    "ipmi_privilege": 2
                }
                template_names_by_type['3'] = _zabbix_sync_info.get("template")
            elif _zabbix_sync_info.get("type") == "agent":
                template_names_by_type['1'] = _zabbix_sync_info.get("template")
            interfaces.append(_interface)
            
    # if host_info.get('type') == 0:
    #     interfaces = [{
    #         "type": "1",
    #         "main": "1",
    #         "useip": "1",
    #         "ip": host_info['ip'],
    #         "dns": "",
    #         "port": "10050"
    #     }]
    # elif host_info.get('type') == 1:
    #     interfaces = [{
    #         "type": "1",
    #         "main": "1",
    #         "useip": "1",
    #         "ip": host_info['ip'],
    #         "dns": "",
    #         "port": "10050"
    #     }, {
    #         "type": "3",
    #         "main": "1",
    #         "useip": "1",
    #         "ip": host_info.get('mgmt_ip', ''),
    #         "dns": "",
    #         "port": "623"
    #     }]
    #     other_args = {
    #         "ipmi_authtype": 6,
    #         "ipmi_password": host_info.get('mgmt_password'),
    #         "ipmi_username": host_info.get('mgmt_user'),
    #         "ipmi_privilege": 2
    #     }
    # elif host_info.get('type') == 2:
    #     interfaces = [{
    #         "type": "2",
    #         "main": "1",
    #         "useip": "1",
    #         "ip": host_info['ip'],
    #         "dns": "",
    #         "port": "161",
    #         "details": {
    #             "version": "2",
    #             "bulk": "0",
    #             "community": "{$SNMP_COMMUNITY}"
    #         }
    #     }]

    if host_info.get('device_status','in-use') not in ['in-use', 'standby']:
        other_args["status"] = 1
    else:
        other_args["status"] = 0

    return interfaces, other_args,template_names_by_type


@shared_task(bind=True)
def zabbix_sync(self, instance_id=None, ip=None, is_delete=False):
    """
    执行同步 Zabbix 任务
    :param node: 目标节点对象
    :return: 任务结果字典
    """
    zabbix_api = ZabbixAPI()
    now_iso = timezone.now().isoformat()

    # 校验 IP 地址
    if not ip or not ip.strip():
        return {
            'status': 'failed',
            'node': ip,
            'result': "IP address is required",
            'timestamp': now_iso
        }

    ip = ip.strip()

    if not is_valid_ip(ip):
        return {
            'status': 'failed',
            'node': ip,
            'result': "Invalid IP address format",
            'timestamp': now_iso
        }
    

    # 主机删除
    if is_delete:
        try:
            result = zabbix_api.host_get(host=ip, output=["hostid", "name", "status"])
            if not result:
                logger.warning(f"Host {ip} not found in Zabbix")
                return {
                    'status': 'failed',
                    'node': ip,
                    'result': f"Host {ip} not found in Zabbix",
                    'timestamp': now_iso
                }

            if len(result) > 1:
                logger.warning(f"Multiple hosts found for IP {ip}, deleting first one")

            host_id = result[0].get('hostid')
            if not host_id:
                logger.warning(f"Host ID not found for IP {ip}")
                return {
                    'status': 'failed',
                    'node': ip,
                    'result': f"Host ID not found for IP {ip}",
                    'timestamp': now_iso
                }

            delete_result = zabbix_api.host_delete(host_id)
            if delete_result:
                logger.info(f"Zabbix host monitoring deleted for {ip}")
                return {'status': 'success', 'detail': f"Zabbix host monitoring deleted for {ip}"}
            else:
                logger.error(f"Failed to delete Zabbix host monitoring for {ip}")
                return {'status': 'failed', 'detail': f"Failed to delete Zabbix host monitoring for {ip}"}

        except Exception as e:
            logger.exception(f"Exception during host deletion: {e}")
            return {
                'status': 'failed',
                'node': ip,
                'result': str(e),
                'timestamp': now_iso
            }

    # 主机更新或创建
    else:
        try:
            instance = ModelInstance.objects.get(id=instance_id)
        except ModelInstance.DoesNotExist:
            return {
                'status': 'failed',
                'node': ip,
                'result': "Instance not found",
                'timestamp': now_iso
            }
        except Exception as e:
            logger.exception(f"Unexpected error fetching instance: {e}")
            return {
                'status': 'failed',
                'node': ip,
                'result': str(e),
                'timestamp': now_iso
            }
        # 获取节点的proxy信息
        nodeObj = Nodes.objects.get(model_instance=instance)
        proxy_info = {}
        if nodeObj.proxy:
            if nodeObj.proxy.proxy_type in ['zabbix','all']:
                # proxy_info["proxy_id"] = nodeObj.proxy.id
                proxy_info["proxy_name"] = nodeObj.proxy.name
                proxy_info["proxy_ip"] = nodeObj.proxy.ip_address
                proxy_info["proxy_id"] = zabbix_api.get_proxy_by_name(proxy_name=nodeObj.proxy.name).get("proxyid")
        host_info = build_host_info(instance, ip)
        if not host_info:
            return {
                'status': 'failed',
                'node': ip,
                'result': "Unsupported model type",
                'timestamp': now_iso
            }

        # 获取组信息
        groups = []
        instance_group_relations = ModelInstanceGroupRelation.objects.filter(
            instance=instance
        ).select_related('group')
        for relation in instance_group_relations:
            if relation.group.path not in ['所有', '所有/空闲池']:
                groups.append(relation.group.path.replace('所有/', ''))

        group_ids = [zabbix_api.get_or_create_hostgroup(g) for g in groups]

        # 获取主机信息
        try:
            result = zabbix_api.host_get(
                host=ip,
                output="extend",
                other_args={"selectInterfaces": ["type", "main", "useip", "ip", "dns", "port"]}
            )
        except Exception as e:
            logger.exception(f"Failed to get host info from Zabbix: {e}")
            return {
                'status': 'failed',
                'node': ip,
                'result': f"Failed to get host info from Zabbix: {e}",
                'timestamp': now_iso
            }

        old_interfaces = result[0].get('interfaces', []) if result else []
        host_name = result[0].get('name') if result else None
        host_status = result[0].get('status') if result else None
        host_id = result[0].get('hostid') if result else None

        interfaces, other_args ,template_names_by_type = build_interfaces_and_args(host_info)
        template_names = [ v for k,v in template_names_by_type.items()]
        # 更新主机
        if host_id:
            # 对比接口
            added, removed, modified = compare_interfaces(old_interfaces, interfaces)
            logger.info(f"实例: {instance.instance_name} 新增接口: {added}, 删除接口: {removed}, 修改接口: {modified}")

            try:
                if added:
                    for _added in added:
                        zabbix_api.create_interfaces(hostid=host_id, interface=_added,template_names_by_type=template_names_by_type)
                if removed:
                    for __removed in removed:
                        zabbix_api.delete_interfaces(hostid=host_id, interface=__removed,template_names_by_type=template_names_by_type)
                if modified:
                    zabbix_api.update_interfaces(hostid=host_id, interfaces=modified)

                # 判断是否需要更新主机信息
                if (
                    host_name != host_info.get('hostname') or
                    result[0].get('ipmi_password', '') != other_args.get('ipmi_password', '') or
                    result[0].get('ipmi_username', '') != other_args.get('ipmi_username', '') or
                    host_status != other_args.get('status', '') or
                    result[0].get('proxy_hostid', '') != proxy_info.get('proxy_hostid', '')

                ):
                    update_result = zabbix_api.host_update(
                        hostid=host_id,
                        host=ip,
                        name=host_info.get('hostname'),
                        interfaces=interfaces,
                        proxy_id=proxy_info.get("proxy_id",None),
                        other_args=other_args
                    )
                    if update_result:
                        logger.info(f"Zabbix host monitoring updated for {ip}")
                        # return {'status': 'success', 'detail': f"Zabbix host monitoring updated for {ip}"}
                        return {
                                'status': 'success',
                                'node': ip,
                                'result': update_result,
                                'timestamp': timezone.now().isoformat()
                                }
                    else:
                        logger.error(f"Failed to update Zabbix host monitoring for {ip}")
                        return {
                                'status': 'failed',
                                'node': ip,
                                'result': update_result,
                                'timestamp': timezone.now().isoformat()
                                }

                logger.info(f"Host {ip} already exists in Zabbix with hostid {host_id}")
                return {
                    'status': 'success',
                    'node': ip,
                    'result': f"Host {ip} already exists in Zabbix with hostid {host_id}",
                    'timestamp': now_iso
                }
            except Exception as e:
                logger.exception(f"Exception during host update: {e}")
                return {
                    'status': 'failed',
                    'node': ip,
                    'result': str(e),
                    'timestamp': now_iso
                }

        # 创建主机
        else:
            # 主机状态不是使用中或备用状态，则跳过
            if host_info.get('device_status') not in ['in-use', 'standby']:
                logger.info(f"Host {ip} is {host_info.get('device_status')}, skipping Zabbix sync")
                return {
                    'status': 'failed',
                    'node': ip,
                    'result': f"Host {ip} is {host_info.get('device_status')}, skipping Zabbix sync",
                    'timestamp': now_iso
                }

            try:
                result = zabbix_api.host_create(
                    host=ip,
                    name=host_info.get('hostname'),
                    interfaces=interfaces,
                    groups=group_ids,
                    template_names=template_names,
                    proxy_id=proxy_info.get("proxy_id",None),
                    other_args=other_args
                )
                if result:
                    logger.info(f"Zabbix host monitoring created for {ip}")
                    return {'status': 'success', 'detail': f"Zabbix host monitoring created for {ip}"}
                else:
                    logger.error(f"Failed to create Zabbix host monitoring for {ip}")
                    return {'status': 'failed', 'detail': f"Failed to create Zabbix host monitoring for {ip}"}
            except Exception as e:
                logger.exception(f"Exception during host creation: {e}")
                return {
                    'status': 'failed',
                    'node': ip,
                    'result': str(e),
                    'timestamp': now_iso
                }
@shared_task(bind=True)
def zabbix_sync_batch(self, instance_ids):
    """
    批量同步Zabbix主机和交换机模型数据

    该函数通过Celery并行执行多个zabbix_sync子任务，实现对指定实例列表的批量同步操作。
    使用group机制管理并发任务，并设置合理的超时控制以确保任务执行的稳定性。

    参数:
        instance_ids (list): 实例信息列表，每个元素为包含"instance_id"和可选"ip"键的字典
                            例如: [{"instance_id": "i-123", "ip": "192.168.1.1"}, ...]

    返回值:
        dict: 包含执行状态、结果详情和时间戳的字典
             - status (str): 执行状态，'completed'表示成功完成，'failed'表示执行失败
             - results (dict): 当status为'completed'时存在，包含各实例同步结果的映射
             - statistics (dict): 任务统计信息，包含成功、失败、总计等计数
             - error (str): 当status为'failed'时存在，包含错误信息描述
             - timestamp (str): ISO格式的时间戳，表示响应生成时间
    """

    # 参数校验
    if not isinstance(instance_ids, list):
        raise ValueError("instance_ids must be a list")
    if not instance_ids:
        return {
            'status': 'completed',
            'results': {},
            'statistics': {
                'total': 0,
                'success': 0,
                'failed': 0
            },
            'timestamp': timezone.now().isoformat()
        }

    # 使用 Celery 的 group 功能并行执行多个任务
    # 创建子任务组
    job = group(
        zabbix_sync.s(
            instance_id=instance["instance_id"],
            ip=instance.get("ip")
        ) for instance in instance_ids
    )
    chord_result = job | aggregate_results.s()
    return chord_result.apply_async()     

@shared_task(bind=True)
def zabbix_proxy_sync(self,proxy_info,action,node_ids=None):
    zabbix_api = ZabbixAPI()
    proxy_name = proxy_info.get('proxy_name',None)
    proxy_ip = proxy_info.get('proxy_ip',None)
    if action == 'delete':
        result = zabbix_api.delete_proxy_by_name(proxy_name=proxy_name)
        if result:
            logger.info(f"Zabbix Proxy deleted for {proxy_name},response:{result}")
            return {'status': 'success', 'detail': f"Zabbix Proxy deleted for {proxy_name},response:{result}"}
        else:
            logger.error(f"Failed to delete Zabbix Proxy {proxy_name},response:{result}")
            return {'status': 'failed', 'detail': f"Failed to delete Zabbix Proxy {proxy_name},response:{result}"}
    elif action == 'create':
        proxy_zabbix = zabbix_api.get_proxy_by_name(proxy_name=proxy_name)
        if not proxy_zabbix:
            logger.info(f"Zabbix Proxy {proxy_name} does not exist, creating...")
            result = zabbix_api.create_proxy(proxy_ip=proxy_ip,proxy_name=proxy_name)
            if result:
                #获取到proxyid，更新Proxy 表
                proxyid = result.get("proxyids")[0]
                Proxy.objects.filter(id=proxy_info.get("proxy_id")).update(zbx_proxyid=proxyid)
                logger.info(f"Zabbix Proxy created for {proxy_name},response:{result}")
                return {'status': 'success', 'detail': f"Zabbix Proxy created for {proxy_name},response:{result}"}
            else:
                logger.error(f"Failed to create Zabbix Proxy {proxy_name},response:{result}")
                return {'status': 'failed', 'detail': f"Failed to create Zabbix Proxy {proxy_name},response:{result}"}
        else:
            proxyid = proxy_zabbix.get("proxyid")
            logger.info(f"Zabbix Proxy {proxy_name} already exists, updating...")
            Proxy.objects.filter(id=proxy_info.get("proxy_id")).update(zbx_proxyid=proxyid)

    elif action == 'update':
        # proxy_zabbix = zabbix_api.get_proxy_by_proxy_address(ip_address=proxy_ip)
        result = zabbix_api.update_proxy(proxyId=proxy_info.get("zbx_proxyid"),proxy_name=proxy_name,proxy_ip=proxy_ip)
        if result:
            logger.info(f"Zabbix Proxy updated for {proxy_name},response:{result}")
            return {'status': 'success', 'detail': f"Zabbix Proxy updated for {proxy_name},response:{result}"}
        else:
            logger.error(f"Failed to update Zabbix Proxy {proxy_name},response:{result}")
            return {'status': 'failed', 'detail': f"Failed to update Zabbix Proxy {proxy_name},response:{result}"}
    elif action == 'associate_host':
        proxy_zabbix = zabbix_api.get_proxy_by_name(proxy_name=proxy_name)
        # 根据node_id获取host_id
        nodes = Nodes.objects.filter(id__in=node_ids).all()
        associate_hosts = []
        node_ips = []
        for node in nodes:
            result = zabbix_api.host_get(
                host=node.ip_address,
                output=["hostid"],
            )
            node_ips.append(node.ip_address)
            host_id = result[0].get('hostid') if result else None
            if host_id:              
                associate_hosts.append({"hostid":host_id})
            else:
                logger.error(f"Failed to get host id for {node.ip_address}")
                # 触发同步任务,添加主机，并且由zabbix_sync任务处理添加proxy
                zabbix_sync.delay(instance_id=node.model_instance.id,ip=node.ip_address)

        #关联node，应该从host侧更新
        # result = zabbix_api.update_proxy(proxyId=proxy_zabbix.get("proxyid"),proxy_name=proxy_name,proxy_ip=proxy_ip,hosts=associate_hosts)
        result = zabbix_api.host_massadd_proxy(hostids=associate_hosts,proxy_id=proxy_zabbix.get("proxyid"))

        if result:
            logger.info(f"Zabbix host {','.join(node_ips)} has been associated on {proxy_name},response:{result}")
            # 触发修改proxy的剧本
            return {'status': 'success', 'detail': f"Zabbix host {','.join(node_ips)} has been associated on {proxy_name},response:{result}"}
        else:
            logger.error(f"Failed to associate host {','.join(node_ips)} on {proxy_name},response:{result}")
            return {'status': 'failed', 'detail': f"Failed to associate host on {proxy_name},response:{result}"}
    elif action == 'dissociate_host':
        #proxy_zabbix = zabbix_api.get_proxy_by_name(proxy_name=proxy_name)
        nodes = Nodes.objects.filter(id__in=node_ids).all()
        dissociate_hosts = []
        node_ips = []
        for node in nodes:
            result = zabbix_api.host_get(
                host=node.ip_address,
                output=["hostid"],
            )
            node_ips.append(node.ip_address)
            host_id = result[0].get('hostid') if result else None
            if host_id:              
                dissociate_hosts.append({"hostid":host_id})
            else:
                pass     
        # result = zabbix_api.update_proxy(proxyId=proxy_zabbix.proxy_id,proxy_name=proxy_name,proxy_ip=proxy_ip)
        if dissociate_hosts:
            result = zabbix_api.host_massclear_proxy(hostids=dissociate_hosts)
            if result:
                logger.info(f"Zabbix host {','.join(node_ips)} has been dissociated on {proxy_name},response:{result}")
                return {'status': 'success', 'detail': f"Zabbix Proxy dissociated for {proxy_name},response:{result}"}
            else:
                logger.error(f"Failed to dissociate host {','.join(node_ips)} from Zabbix Proxy {proxy_name},response:{result}")
                return {'status': 'failed', 'detail': f"Failed to dissociate Zabbix Proxy"
            }
        else:
            return {'status': 'success', 'detail': f"Zabbix Proxy dissociated for {proxy_name},response:{result}"}

    else:
        return {'status': 'failed', 'detail': f"Invalid action {action}"}