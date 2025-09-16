from celery import chain, shared_task
from .models import Nodes,NodeInfoTask,NodeSyncZabbix
from cmdb.models import (
    Models,
    ModelInstance,
    ModelFieldMeta
    )
import os,time
from django.utils import timezone
import ping3
from .utils.get_cmdb_data import get_instance_field_value
from .utils.zabbix import ZabbixAPI

if os.name != 'nt':
    from .utils.ansible import AnsibleAPI
    ANSIBLE_AVAILABLE = True
else:
    ANSIBLE_AVAILABLE = False
    logger.warning("Ansible functionality not available on Windows")
@shared_task(bind=True)
def sync_node_mg(self):
    """初始化加载node_mg"""
    try:
        sync_model_list = [ i.id for i in Models.objects.filter(name__in=['hosts']) ]
        all_instance = ModelInstance.objects.filter(model__in=sync_model_list)
        node_create_counter = 0
        node_update_counter = 0
        fail_instance = []
        for _instance in all_instance:   
            try:
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
            except Exception as e:
                fail_instance.append(_instance.instance_name)
                continue         
            node_obj,node_created = Nodes.objects.update_or_create(
                model_instance=_instance,
                defaults={
                "ip_address": get_instance_field_value(_instance, 'ip') ,
                "model": _instance.model,
                "create_user": _instance.create_user,
                "update_user": _instance.update_user
                }
            )
            if node_created:
                node_create_counter += 1
            else:
                node_update_counter += 1
        print(f"创建[{node_create_counter}],更新[{node_update_counter},]失败[{len(fail_instance)}],失败实例[{','.join(fail_instance)}]")
    except Exception as exc:
        # 自动重试
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

def node_inventory(node):
    """获取节点的配置"""
    proxy = node.proxy
    ssh_user = get_instance_field_value(node.model_instance, 'system_user') or 'root'
    ssh_pass = get_instance_field_value(node.model_instance, 'system_password') or ''
    ssh_port = get_instance_field_value(node.model_instance, 'ssh_port') or 22
    inventory = { 'all': { 'hosts': { node.ip_address: {
        'ansible_ssh_user': ssh_user,
        'ansible_ssh_pass': ssh_pass,
        'ansible_ssh_port': ssh_port,
        'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
    } } } }

    if proxy:
        jump_host = proxy.ip_address
        jump_user = proxy.ssh_user
        jump_pass = proxy.ssh_pass
        jump_port = proxy.ssh_port
        inventory['all']['hosts'][node.ip_address]['ansible_ssh_common_args'] += f" -o ProxyCommand=\"sshpass -p '{jump_pass}' ssh -W %h:%p -p {jump_port} {jump_user}@{jump_host}\""
    return inventory
@shared_task(bind=True, max_retries=3)
def ansible_getinfo(self, node_id):
    """
    执行 Ansible 获取系统信息 任务
    :param node: 目标节点对象
    :return: 任务结果字典
    """
    ansible_api = AnsibleAPI()
    try:
        start = time.perf_counter()
        node = Nodes.objects.get(id=node_id)
        print(f"Starting Ansible playbook for node {node.ip_address}")

        inventory = node_inventory(node)
        print(inventory)
        result = ansible_api.run_playbook('/opt/get_system_info.yaml',inventory)
        end_time = time.perf_counter()

        if result['rc'] != 0:
            try:
                NodeInfoTask.objects.create(
                    node=node,
                    status=False,
                    results=str(result),
                    cost_time=float(f"{end_time - start:.2f}"),
                )
                # obj,created = NodeInfoTask.objects.update_or_create(
                #     node=node,
                #     defaults={
                #         "status": False,
                #         "results": str(result),
                #         "cost_time": float(f"{end_time - start:.2f}"),
                #     }
                # )
            except Exception as e:
                print(e)
            print(f"Ansible playbook failed with return code {result['rc']},{end_time - start:.2f} seconds")
            raise Exception(f"Ansible playbook failed with return code {result['rc']}")
        info = ansible_api.extract_debug_json(result['events'])
        # info['ansible_playbook_time'] = f"{end_time - start:.2f}"
        try:
            NodeInfoTask.objects.create(
                node=node,
                status=True,
                results=str(info),
                cost_time=float(f"{end_time - start:.2f}"),
            )
        except Exception as e:
            print(e)
        # NodeInfoTask.objects.update_or_create(
        #     node=node,
        #     defaults={
        #         "status": True,
        #         "results": str(info),
        #         "cost_time": float(f"{end_time - start:.2f}"),
        #     }
        # )
        # 更新资产 info
        
        print(f"Ansible playbook completed in {end_time - start:.2f} seconds")
        return {
            'status': 'success',
            'node': node.ip_address,
            'result': info,
            'timestamp': timezone.now().isoformat()
        }
    except Exception as exc:
        return None

@shared_task(bind=True)
def ansible_agent_install(self, node_id):
    """
    执行 Ansible 安装 Zabbix Agent 任务
    :param node: 目标节点对象
    :return: 任务结果字典
    """
    ansible_api = AnsibleAPI()
    try:
        start = time.perf_counter()
        node = Nodes.objects.get(id=node_id)
        # print(f"Starting Ansible playbook for node {node.ip_address}")

        inventory = node_inventory(node)
        # print(inventory)
        result = ansible_api.run_playbook('/opt/zabbix_agent/main.yaml',inventory)
        end_time = time.perf_counter()

        if result['rc'] != 0:
            NodeSyncZabbix.objects.update_or_create(
                node=node,
                defaults={
                    "agent_status": 0,
                    "results": str(result),
                    "cost_time": float(f"{end_time - start:.2f}"),
                }
            )
            print(f"Ansible playbook failed with return code {result['rc']},{end_time - start:.2f} seconds")
            raise Exception(f"Ansible playbook failed with return code {result['rc']}")
        info = ansible_api.extract_debug_json(result['events'])
        NodeSyncZabbix.objects.update_or_create(
            node=node,
            defaults={
                "agent_status": 1,
                "results": str(info),
                "cost_time": float(f"{end_time - start:.2f}"),
            }
        )
        # info['ansible_playbook_time'] = f"{end_time - start:.2f}"
        
        print(f"Ansible playbook completed in {end_time - start:.2f} seconds")
        return {
            'status': 'success',
            'node': node.ip_address,
            'result': info,
            'timestamp': timezone.now().isoformat()
        }
    except Exception as exc:
        return None
@shared_task(bind=True)
def zabbix_sync(self,host_info,is_delete=False):
    """
    执行同步 Zabbix 任务
    :param node: 目标节点对象
    :return: 任务结果字典
    """
    zabbix_api = ZabbixAPI()
    ip = host_info.get('ip')
    if not ip:
        return {
            'status': 'failed',
            'node': ip,
            'result': "IP address is required",
            'timestamp': timezone.now().isoformat()
        }
    #主机删除
    if is_delete:
        # 以ip作为host去查询
        result = zabbix_api.host_get(host=ip)
        host_id = result[0].get('hostid') if result else None
        if host_id:
            result = zabbix_api.host_delete(host_id)
            if result:
                print(f"Zabbix host monitoring deleted for {ip}")
                return {'status': 'success', 'detail': f"Zabbix host monitoring deleted for {ip}"}      
            else:
                print(f"Failed to delete Zabbix host monitoring for {ip}")
                return {'status': 'failed', 'detail': f"Failed to delete Zabbix host monitoring for {ip}"}        
        else:  
            print(f"Host {ip} not find in Zabbix")
            return {
                'status': 'failed',
                'node': ip,
                'result': f"Host {ip} not find in Zabbix",
                'timestamp': timezone.now().isoformat()
            }
    # 主机更新或创建
    else:
        #groups 创建和判断
        # group_ids = []
        # for group in host_info.get('groups',None):
        #     group_id = zabbix_api.get_hostgroup(group_name=group)
        #     if not group_id:
        #         group_id = zabbix_api.create_hostgroup(group_name=group)
        #     group_ids.append({"groupid": group_id})
        group_ids = [zabbix_api.get_or_create_hostgroup(g) for g in host_info.get('groups',None)]
        result = zabbix_api.host_get(host=ip,output=["hostid","name"])
        host_id = result[0].get('hostid') if result else None
        # 接口类型判断,关联模板和接口
        interfaces = []
        template_ids = []
        if host_info.get('type') == 0:
            template_id = zabbix_api.get_template(template_names='Template OS Linux')
            interfaces = [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "10050"
            }]
        elif host_info.get('type') == 1:
            template_id = zabbix_api.get_template('Template OS Linux')
            ipmi_template_id = zabbix_api.get_template('Template IPMI')
            interfaces = [{
                "type": 1,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "port": "10050",
                "dns": ""
            },{
                "type": 3,
                "main": 1,
                "useip": 1,
                "ip": host_info.get('mgmt_ip',''),
                "port": "623",
                "dns": "",
            }]
            if ipmi_template_id:
                template_id = f"{template_id},{ipmi_template_id}"
        elif host_info.get('type') == 2:
            template_ids = zabbix_api.get_template('Template Net Cisco')
            interfaces = [{
                "type": 2,
                "main": 1,
                "useip": 1,
                "ip": ip,
                "dns": "",
                "port": "161"
            }]
        
        if host_id:
            # 更新host
            print(f"Host {ip} already exists in Zabbix with hostid {host_id}")
            return {
                'status': 'success',
                'node': ip,
                'result': f"Host {ip} already exists in Zabbix with hostid {host_id}",
                'timestamp': timezone.now().isoformat()
            }
        else:
            # 创建host
            result = zabbix_api.host_create(host=ip, interfaces=interfaces, groups=group_ids, templates=[{"templateid": template_id}])
            if result:
                print(f"Zabbix host monitoring created for {ip}")
                return {'status': 'success', 'detail': f"Zabbix host monitoring created for {ip}"}      
            else:
                print(f"Failed to create Zabbix host monitoring for {ip}")
                return {'status': 'failed', 'detail': f"Failed to create Zabbix host monitoring for {ip}"}