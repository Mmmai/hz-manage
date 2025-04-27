import io
import os
import uuid
import logging
import traceback
from celery import chain, shared_task
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from celery.result import AsyncResult
from .models import ModelInstanceGroupRelation, Models, ModelFields, ModelInstance, ModelFieldMeta, ZabbixProxy, ZabbixSyncHost
from .serializers import ModelInstanceSerializer
from .excel import ExcelHandler
from .utils.zabbix import ZabbixAPI
from .utils.name_generator import generate_instance_name
from .utils.assign_proxy import ProxyAssignment as pa

logger = logging.getLogger(__name__)

# 仅在Linux环境下导入ansible相关功能
if os.name != 'nt':
    from .utils.ansible import AnsibleAPI
    ANSIBLE_AVAILABLE = True
else:
    ANSIBLE_AVAILABLE = False
    logger.warning("Ansible functionality not available on Windows")


@shared_task(bind=True)
def process_import_data(self, excel_data, model_id, request):
    try:
        task_id = self.request.id
        cache_key = f'import_task_{task_id}'

        class MiniRequest:
            def __init__(self, data):
                self.data = data

        request = MiniRequest(request['data'])
        results = {
            'status': 'processing',
            'total': len(excel_data.get('instances', [])),
            'progress': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'failed': 0,
            'errors': [],
            'error_file_key': None
        }
        cache.set(cache_key, results, timeout=600)
        processed_instance = set()
        error_data = []
        excel_handler = ExcelHandler()
        with transaction.atomic():
            for instance_data in excel_data.get('instances', []):
                try:
                    instance_name = instance_data.get('instance_name')
                    instance = None

                    if instance_name in processed_instance:
                        results['skipped'] += 1
                        continue

                    if instance_name:
                        instance = ModelInstance.objects.filter(
                            model_id=model_id,
                            instance_name=instance_name
                        ).first()
                        processed_instance.add(instance_name)
                    else:
                        # TODO: 处理未提交name的实例，应用name填充规则补充
                        results['skipped'] += 1
                        continue

                    # 过滤空值字段
                    fields_data = {
                        k: v for k, v in instance_data['fields'].items()
                        if v not in (None, '')
                    }

                    data = {
                        'model': model_id,
                        'fields': fields_data
                    }
                    if instance:
                        serializer = ModelInstanceSerializer(
                            instance=instance,
                            data=data,
                            partial=True,
                            context={
                                'request': request,
                                'from_excel': True
                            }
                        )
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            results['updated'] += 1
                    else:
                        # TODO: get user name from request
                        data.update({
                            'instance_name': instance_name,
                            'create_user': 'system',
                            'update_user': 'system'
                        })
                        logger.info(f"Creating instance: {instance_name}, data: {data}")
                        serializer = ModelInstanceSerializer(
                            data=data,
                            context={
                                'request': request,
                                'from_excel': True
                            }
                        )
                        if serializer.is_valid(raise_exception=True):
                            serializer.save()
                            results['created'] += 1

                except Exception as e:
                    logger.error(f"Error preparing data for instance: {traceback.format_exc()}")
                    results['failed'] += 1
                    results['errors'].append(f"Error preparing data for instance: {str(e)}")
                    error_data.append({
                        'instance_name': instance_data.get('instance_name'),
                        'fields': instance_data.get('fields'),
                        'error': str(e)
                    })
                    continue
                percent = (results['created'] + results['updated'] + results['skipped'] +
                           results['failed']) * 100 // results['total']
                results['progress'] = percent
                cache.set(cache_key, results, timeout=600)
            if results['failed'] > 0:
                try:
                    logger.info(f"Generating error report for {len(error_data)} instances")
                    error_wb = excel_handler.generate_error_export(
                        excel_data['headers'], excel_data['header_rows'], error_data)
                    output = io.BytesIO()
                    error_wb.save(output)
                    output.seek(0)
                    error_key = f"import_error_{uuid.uuid4()}"
                    cache.set(error_key, output.getvalue(), timeout=600)
                    results['error_file_key'] = error_key
                except Exception as e:
                    logger.error(f"Error generating error report: {str(e)}")
                    raise ValidationError({'detail': f'Failed to generate error report: {str(e)}'})
        results['status'] = 'completed'
        results['progress'] = 100
        cache.set(cache_key, results, timeout=600)

    except Exception as e:
        results['status'] = 'failed'
        results['errors'].append(f"Error loading Excel data: {str(e)}")
        cache.set(cache_key, results, timeout=600)


@shared_task(bind=True)
def update_instance_names_for_model_template_change(self, model_id, old_template, new_template):
    logger.info(f"Starting update of instance_name for model {model_id}")
    cache_key = f'rename_task_{self.request.id}'
    logger.info(f"Cache key for task {self.request.id}: {cache_key}")
    result_dict = {
        'status': 'processing',
        'progress': 0,
        'total': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'conflict': 0,
        'conflict_details': [],
    }
    try:
        model = Models.objects.get(id=model_id)

        # 只处理使用模板的实例
        instances = ModelInstance.objects.filter(
            model=model,
            using_template=True
        )

        result_dict['total'] = instances.count()
        cache.set(cache_key, result_dict, timeout=600)

        if not instances.exists():
            logger.info(f"No instances using template for model {model.name}")
            result_dict['status'] = 'completed'
            result_dict['progress'] = 100
            cache.set(cache_key, result_dict, timeout=600)
            return

        logger.info(f"Found {instances.count()} instances to update for model {model.name}")

        # 收集所有需要更改的实例和新名称，在提交事务前进行唯一性检查
        name_updates = []
        name_conflicts = []

        template_fields = ModelFields.objects.filter(id__in=new_template).values_list('id', 'name')
        template_fields = {str(f[0]): f[1] for f in template_fields}
        template_fields = [template_fields[str(id)] for id in new_template]

        # 计算所有新名称并检查冲突
        for instance in instances:
            percent = (result_dict['updated'] + result_dict['skipped'] +
                       result_dict['conflict'] + result_dict['failed']) * 100 // result_dict['total']
            result_dict['progress'] = percent
            cache.set(cache_key, result_dict, timeout=600)

            # 获取实例的所有字段值
            field_values = {}
            field_metas = ModelFieldMeta.objects.filter(
                model_instance=instance,
                model_fields__id__in=new_template
            ).select_related('model_fields')

            for meta in field_metas:
                field_values[meta.model_fields.name] = meta.data

            # 生成新名称
            new_name = generate_instance_name(field_values, new_template, template_fields)

            # 如果无法生成名称，跳过
            if not new_name:
                logger.warning(f"Cannot generate name for instance {instance.id} - missing values for template fields")
                result_dict['skipped'] += 1
                continue

            # 检查这个新名称是否已存在或和本次更新中的其他实例冲突
            if ModelInstance.objects.filter(
                model=model,
                instance_name=new_name
            ).exclude(id=instance.id).exists() or new_name in [update[1] for update in name_updates]:
                name_conflicts.append((instance.id, new_name))
                result_dict['conflict'] += 1
                continue

            # 名称有变化且无冲突
            if new_name != instance.instance_name:
                try:
                    instance = ModelInstance.objects.get(id=instance.id)
                    instance.instance_name = new_name
                    instance.save(update_fields=['instance_name', 'update_time'])
                    result_dict['updated'] += 1
                except Exception as e:
                    logger.error(f"Error updating instance {instance.id}: {str(e)}")
                    result_dict['failed'] += 1
            else:
                result_dict['skipped'] += 1

        # 如果有冲突，记录日志但继续处理无冲突的部分
        if name_conflicts:
            conflict_details = ", ".join([f"{instance_id}:{name}" for instance_id, name in name_conflicts])
            result_dict['conflict_details'] = name_conflicts
            logger.warning(f"Name conflicts detected for {len(name_conflicts)} instances: {conflict_details}")

        logger.info(f"Successfully updated {result_dict['updated']} instances for model {model.name}")

        result_dict['progress'] = 100
        result_dict['status'] = 'completed'
        cache.set(cache_key, result_dict, timeout=600)

        if name_conflicts and not name_updates:
            logger.error(f"All instances for model {model.name} have name conflicts after template change")

        return result_dict

    except Models.DoesNotExist:
        logger.error(f"Model {model_id} does not exist")
        return None
    except Exception as e:
        logger.error(f"Error updating instance names for model {model_id}: {str(e)}")
        return None


@shared_task(bind=True)
def setup_host_monitoring(self, instance_id, instance_name, ip, password,
                          groups=None, delete=False, force=False):
    try:

        # 删除主机监控
        if delete:
            zabbix_api = ZabbixAPI()
            result = zabbix_api.host_get(host=ip)
            host_id = result[0].get('hostid') if result else None
            if host_id:
                result = zabbix_api.host_delete(hostid=str(host_id))
                if result:
                    ZabbixSyncHost.objects.filter(instance_id=instance_id).delete()
                    logger.info(f"Zabbix host monitoring deleted for {ip}")
                    return {'status': 'success', 'detail': f"Zabbix host monitoring deleted for {ip}"}
                else:
                    raise ValidationError({'detail': f'Failed to delete host: {result}'})
            else:
                logger.debug(f"Host monitoring does not exist for {ip}, skipping deletion")
                return {'status': 'skipped', 'detail': f"Host monitoring does not exist for {ip}, skipping deletion"}

        proxy = pa.find_proxy_for_ip(ip)
        logger.info(f"Proxy found for IP {ip}: {proxy}")
        proxy_ip = None
        if proxy:
            proxy_id = proxy.proxy_id
            proxy_ip = proxy.ip
        else:
            proxy_id = '0'

        zabbix_host = ZabbixSyncHost.objects.filter(instance_id=instance_id)
        # 更新主机监控
        if zabbix_host.exists():
            ip_cur = zabbix_host.first().ip
            # 更新监控配置
            if ip != ip_cur or instance_name != zabbix_host.first().name or \
                    zabbix_host.first().proxy != proxy or force:
                zabbix_api = ZabbixAPI()
                result = zabbix_api.host_update(hostid=str(zabbix_host.first().host_id),
                                                host=ip, name=instance_name, ip=ip, proxy=proxy_id)
                host_id = result.get('hostids', [None])[0] if result.get('hostids') else None
                if host_id and host_id.isdigit():
                    ZabbixSyncHost.objects.filter(
                        instance_id=instance_id).update(
                        ip=ip, name=instance_name, proxy=proxy)
                    logger.info(f"Zabbix host monitoring updated for {ip}")
                    self.update_state(state='SUCCESS', meta={'status': 'updated'})
                else:
                    self.update_state(state='FAILURE', meta={'status': 'failed'})
                    raise ValidationError({'detail': f'Failed to update host: {result}'})

            # IP地址发生变化/安装状态为失败/强制重装
            if ANSIBLE_AVAILABLE and (ip != ip_cur or not zabbix_host.first().agent_installed or force):

                task = install_zabbix_agent.s(ip, password, proxy_ip=proxy_ip)
                task_chain = chain(task)
                chain_result = task_chain.apply_async()
                zabbix_host.update(
                    agent_installed=False,
                    installation_error=None
                )
                return {'status': 'success', 'chain_task_id': chain_result.id}
            else:
                logger.debug(f"No changes detected for {ip}, skipping update")
                return {'status': 'skipped', 'detail': f"No changes detected for {ip}, skipping update"}
        # 创建主机监控
        else:
            zabbix_api = ZabbixAPI()
            result = zabbix_api.host_get(host=ip)
            host_id = result[0].get('hostid') if result else None
            # 主机ip已存在则跳过
            if host_id:
                logger.debug(f"Host monitoring already exists for {ip}, skipping creation")
                ZabbixSyncHost.objects.create(instance_id=instance_id, host_id=int(host_id), name=instance_name, ip=ip)
                return {'detail': f"Host monitoring already exists for {ip}, skipping creation"}
            # 主机ip不存在则创建主机并设置监控
            else:
                groupids = [zabbix_api.get_or_create_hostgroup(g) for g in groups]
                result = zabbix_api.host_create(host=ip, name=instance_name, ip=ip, groups=groupids)
                host_id = result.get('hostids', [None])[0] if result.get('hostids') else None
                if host_id and host_id.isdigit():
                    ZabbixSyncHost.objects.create(instance_id=instance_id,
                                                  host_id=int(host_id),
                                                  name=instance_name,
                                                  ip=ip,
                                                  proxy=proxy
                                                  )
                    logger.info(f"Zabbix host monitoring setup for {ip}")
                if ANSIBLE_AVAILABLE:
                    task = install_zabbix_agent.s(ip, password, proxy_ip=proxy_ip)
                    task_chain = chain(task)
                    chain_result = task_chain.apply_async()
                    return {'status': 'success', 'chain_task_id': chain_result.id}
                else:
                    raise ValidationError({'detail': f'Failed to create host: {result}'})
    except Exception as e:
        logger.error(f"Error setting up host monitoring: {str(e)}")
        raise ValidationError({'detail': f'Failed to setup host monitoring: {str(e)}'})


@shared_task(bind=True)
def install_zabbix_agent(self, host_ip, password, proxy_ip=None):
    try:
        self.update_state(state='PROGRESS', meta={'status': 'installing'})
        logger.info(f'Installing Zabbix agent on {host_ip}')
        ansible_api = AnsibleAPI()
        if not proxy_ip:
            result = ansible_api.install_zabbix_agent(host_ip, 'root', 22, password)
        else:
            ppassword = ZabbixProxy.objects.filter(ip=proxy_ip).first().password
            result = ansible_api.install_zabbix_agent(
                host_ip, 'root', 22, password,
                jump_host=proxy_ip, jump_user='root', jump_pass=ppassword,
                jump_port=22, zabbix_proxy=proxy_ip
            )
        agent_installed = result.get('status') == 'success'
        error_message = None

        if not result:
            result = {
                'status': 'failed',
                'message': 'Installation result is empty.',
                'task_details': []
            }
            self.update_state(state='FAILURE', meta=result)()

        if not agent_installed:
            main_error = result.get('message', 'Unknown error')
            task_details = result.get('task_details', [])

            formatted_error = {
                'main_error': main_error,
                'details': []
            }

            if task_details:
                for task in task_details:
                    task_name = task.get('task', 'Unknown task')
                    task_status = task.get('status', 'Unknown status')
                    task_msg = task.get('message', '')

                    # 避免重复的错误信息
                    if task_msg and task_msg not in main_error:
                        formatted_error['details'].append({
                            'task': task_name,
                            'status': task_status,
                            'message': task_msg
                        })

            error_message = formatted_error

        zabbix_host = ZabbixSyncHost.objects.filter(ip=host_ip).first()
        if zabbix_host:
            fields = ['agent_installed', 'update_time']
            zabbix_host.agent_installed = agent_installed
            if error_message:
                zabbix_host.installation_error = error_message
                fields.append('installation_error')
            elif agent_installed:
                zabbix_host.installation_error = None
                fields.append('installation_error')
            zabbix_host.save(update_fields=fields)
            logger.info(f"Zabbix agent installation status updated for {host_ip}.")
        else:
            logger.warning(f"No Zabbix host found for IP: {host_ip}.")

        return {
            'status': 'success' if agent_installed else 'failed',
            'message': error_message if error_message else ''
        }

    except Exception as e:
        logger.error(f"Error installing Zabbix agent: {str(e)}")
        zabbix_host = ZabbixSyncHost.objects.filter(ip=host_ip).first()
        if zabbix_host:
            zabbix_host.agent_installed = False
            zabbix_host.installation_error = f'Error during installation: {str(e)}'
            zabbix_host.save(update_fields=['agent_installed', 'installation_error'])
        return {
            'status': 'error',
            'message': f'Error during installation: {str(e)}'
        }


@shared_task(bind=True)
def update_zabbix_interface_availability(self):
    """定时获取 Zabbix 主机接口可用性状态并更新数据库"""
    logger.info("Starting Zabbix interface availability update")

    try:
        zabbix_api = ZabbixAPI()

        # 获取已同步的 Zabbix 主机
        sync_hosts = ZabbixSyncHost.objects.all()
        host_ids = [str(host.host_id) for host in sync_hosts]

        if not host_ids:
            logger.info("No synchronized Zabbix hosts found")
            return {"status": "success", "count": 0, "message": "No synchronized hosts"}

        # 获取主机接口可用性
        try:
            hosts_data = zabbix_api.get_hosts_interface_availability(host_ids)
            hosts_data = hosts_data.get('result', [])
            if not hosts_data:
                logger.info("No host interface availability data found")
                return {"status": "success", "count": 0, "message": "No host interface availability data"}
            logger.info(f"Retrieved {len(hosts_data)} hosts data from Zabbix")
        except Exception as e:
            logger.error(f"Error getting host interface availability: {str(e)}")
            return {"status": "error", "message": f"API error: {str(e)}"}

        # 更新数据库
        updated_count = 0
        for host_data in hosts_data:
            zabbix_hostid = host_data.get('hostid')

            # 获取接口状态（1=可用，2=不可用）
            interfaces = host_data.get('interfaces', [])
            # 优先获取 IP 类型接口的状态
            interface_available = None
            for interface in interfaces:
                if interface.get('type') == '1':  # 1 = agent
                    interface_available = interface.get('available')
                    break

            if interface_available is None and interfaces:
                # 如果没有找到 agent 接口，使用第一个接口的状态
                interface_available = interfaces[0].get('available')

            if interface_available is None:
                continue

            try:
                # 更新 ZabbixSyncHost 表中的状态
                host_obj = ZabbixSyncHost.objects.filter(host_id=zabbix_hostid).first()
                if host_obj:
                    host_obj.interface_available = interface_available
                    host_obj.save(update_fields=['interface_available', 'update_time'])
                    updated_count += 1
            except Exception as e:
                logger.error(f"Error updating host {zabbix_hostid}: {str(e)}")

        logger.info(f"Successfully updated {updated_count} hosts interface availability")
        return {
            "status": "success",
            "count": updated_count,
            "message": f"Updated {updated_count}/{len(hosts_data)} hosts"
        }

    except Exception as e:
        logger.error(f"Error in Zabbix interface availability update task: {str(e)}")
        return {"status": "error", "message": str(e)}


@shared_task
def sync_zabbix_host_task():
    logger.info(f"Beginning Zabbix host synchronization")

    try:
        zabbix_api = ZabbixAPI()

        model = Models.objects.get(name='hosts')
        instances_query = ModelInstance.objects.filter(model=model)

        instances = instances_query.all()
        if not instances:
            logger.info(f"No instances found for model {model.name}")
            return {"status": "warning", "message": f"No instances found for model {model.name}"}

        valid_instance_ids = set(instance.id for instance in instances)

        # 获取Zabbix中的主机组
        hostgroups = zabbix_api.get_hostgroups()
        hostgroup_map = {hg['name']: hg['groupid'] for hg in hostgroups}

        # 处理结果统计
        result = {
            "total": len(instances),
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "deleted": 0,
            "errors": []
        }

        # 获取所有已同步的主机记录
        all_zabbix_hosts = ZabbixSyncHost.objects.all().select_related('instance')

        # 清理无效的同步记录（实例已不存在）
        for zabbix_host in all_zabbix_hosts:
            if zabbix_host.instance_id not in valid_instance_ids:
                try:
                    logger.info(
                        f"Deleting invalid Zabbix host: {zabbix_host.host_id} (Instance: {zabbix_host.instance_id})")
                    if zabbix_api.host_delete(zabbix_host.host_id):
                        zabbix_host.delete()
                        result["deleted"] += 1
                        logger.info(f"Successfully deleted Zabbix host {zabbix_host.host_id}")
                    else:
                        result["errors"].append({
                            "host_id": zabbix_host.host_id,
                            "error": f"Failed to delete Zabbix host {zabbix_host.host_id}"
                        })
                except Exception as e:
                    logger.error(f"Error deleting Zabbix host {zabbix_host.host_id}: {str(e)}")
                    result["errors"].append({
                        "host_id": zabbix_host.host_id,
                        "error": f"Error deleting: {str(e)}"
                    })

        valid_zabbix_hosts = [zh for zh in all_zabbix_hosts if zh.instance_id in valid_instance_ids]
        instance_to_zabbix = {zh.instance.id: zh for zh in valid_zabbix_hosts}

        # 处理每个实例
        for instance in instances:
            try:
                # 获取实例的分组信息
                instance_groups = ModelInstanceGroupRelation.objects.filter(
                    instance=instance
                ).select_related('group')

                # 从分组中排除"所有"和"空闲池"内置分组
                group_names = []
                for relation in instance_groups:
                    group = relation.group
                    group_names.append(group.path.replace('所有/', ''))

                # 确保至少有一个分组
                if not group_names:
                    group_names = ['空闲池']

                # 为Zabbix准备主机组ID
                group_ids = []
                for group_name in group_names:
                    if group_name in hostgroup_map:
                        group_ids.append(hostgroup_map[group_name])
                    else:
                        # 如果主机组不存在，则创建
                        new_group_id = zabbix_api.create_hostgroup(group_name)
                        if new_group_id:
                            hostgroup_map[group_name] = new_group_id
                            group_ids.append(new_group_id)

                # 检查是否已有Zabbix同步记录
                zabbix_host = instance_to_zabbix.get(instance.id)

                # 获取主机IP地址
                ip_field_meta = ModelFieldMeta.objects.filter(
                    model_instance=instance,
                    model_fields__name='ip'
                ).first()

                ip_address = ip_field_meta.data

                if zabbix_host:
                    # 更新现有主机
                    if zabbix_api.host_sync(zabbix_host.host_id, instance.instance_name, group_ids):
                        # 更新成功，更新本地记录
                        zabbix_host.name = instance.instance_name
                        zabbix_host.ip = ip_address
                        zabbix_host.save(update_fields=['name', 'ip', 'update_time'])
                        result["updated"] += 1
                        logger.info(f"Updated zabbix host: {zabbix_host.host_id} ({instance.instance_name})")
                    else:
                        result["errors"].append({
                            "instance_id": str(instance.id),
                            "error": f"Failed to update Zabbix host {zabbix_host.host_id}"
                        })
                else:
                    # 创建新主机
                    interfaces = [{
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": ip_address,
                        "dns": "",
                        "port": "10050"
                    }]

                    host_data = {
                        'host': ip_address,
                        'name': instance.instance_name,
                        'interfaces': interfaces,
                        'groups': [{'groupid': gid} for gid in group_ids]
                    }

                    # 创建主机
                    host_id = zabbix_api.create_host(host_data)
                    if host_id:
                        # 创建成功，保存同步记录
                        ZabbixSyncHost.objects.create(
                            instance=instance,
                            host_id=host_id,
                            ip=ip_address,
                            name=instance.instance_name,
                            agent_installed=False,
                            interface_available=0
                        )
                        result["created"] += 1
                        logger.info(f"Created zabbix host {host_id} ({instance.instance_name})")
                    else:
                        result["errors"].append({
                            "instance_id": str(instance.id),
                            "error": f"Failed to create zabbix host"
                        })

            except Exception as e:
                logger.error(f"Failed to sync Zabbix host for instance {instance.id}: {str(e)}")
                result["errors"].append({
                    "instance_id": str(instance.id),
                    "error": str(e)
                })

        # 生成最终结果
        status_message = "success"
        if result["errors"]:
            status_message = "partial_success" if (result["created"] + result["updated"]) > 0 else "error"

        logger.info(f"Sync status: {status_message}")
        logger.info(f"Total: {result['total']}, Created: {result['created']}, Updated: {result['updated']}, "
                    f"Skipped: {result['skipped']}, Errors: {len(result['errors'])}")
        return {
            "status": status_message,
            "total": result["total"],
            "created": result["created"],
            "updated": result["updated"],
            "skipped": result["skipped"],
            "errors": result["errors"]
        }

    except Exception as e:
        logger.error(f"Error during Zabbix host synchronization: {str(e)}")
        return {"status": "error", "message": str(e)}
