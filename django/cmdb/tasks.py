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
from .models import ModelInstance, ZabbixSyncHost
from .serializers import ModelInstanceSerializer
from .excel import ExcelHandler
from .utils.zabbix import ZabbixAPI

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
                percent = (results['created'] + results['updated'] + results['skipped'] + results['failed']) * 100 // results['total']
                results['progress'] = percent
                cache.set(cache_key, results, timeout=600)
            if results['failed'] > 0:
                try:
                    logger.info(f"Generating error report for {len(error_data)} instances")
                    error_wb = excel_handler.generate_error_export(excel_data['headers'], excel_data['header_rows'] , error_data)
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
        results['progress'] = '100 %'
        cache.set(cache_key, results, timeout=600)
        
    except Exception as e:
        results['status'] = 'failed'
        results['errors'].append(f"Error loading Excel data: {str(e)}")
        cache.set(cache_key, results, timeout=600)
        
@shared_task
def setup_host_monitoring(instance_id, instance_name, ip, password, delete=False):
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
                    return {'detail': f"Zabbix host monitoring deleted for {ip}"}
                else:
                    raise ValidationError({'detail': f'Failed to delete host: {result}'})
            else:
                logger.debug(f"Host monitoring does not exist for {ip}, skipping deletion")
                return {'detail': f"Host monitoring does not exist for {ip}, skipping deletion"}
        
        zabbix_host = ZabbixSyncHost.objects.filter(instance_id=instance_id)
        # 更新主机监控
        if zabbix_host.exists():
            ip_cur = zabbix_host.first().ip
            # 更新监控配置
            if ip != ip_cur or instance_name != zabbix_host.first().name:
                zabbix_api = ZabbixAPI()
                result = zabbix_api.host_update(hostid=str(zabbix_host.first().host_id), host=ip, name=instance_name, ip=ip)
                host_id = result.get('hostids', [None])[0] if result.get('hostids') else None
                if host_id and host_id.isdigit():
                    ZabbixSyncHost.objects.filter(instance_id=instance_id).update(ip=ip, name=instance_name)
                    logger.info(f"Zabbix host monitoring updated for {ip}")
                else:
                    raise ValidationError({'detail': f'Failed to update host: {result}'})
                
                # 当IP地址发生变化时触发ansible重新安装客户端
                if ANSIBLE_AVAILABLE and ip != ip_cur:
                    chain(
                        install_zabbix_agent.s(ip, password)
                    ).apply_async()
            else:
                logger.debug(f"No changes detected for {ip}, skipping update")
                return {'detail': f"No changes detected for {ip}, skipping update"}
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
                result = zabbix_api.host_create(host=ip, name=instance_name, ip=ip)
                host_id = result.get('hostids', [None])[0] if result.get('hostids') else None
                if host_id and host_id.isdigit():
                    ZabbixSyncHost.objects.create(instance_id=instance_id, host_id=int(host_id), name=instance_name, ip=ip)
                    logger.info(f"Zabbix host monitoring setup for {ip}")
                if ANSIBLE_AVAILABLE:
                    chain(
                        install_zabbix_agent.s(ip, password)
                    ).apply_async()
                else:
                    raise ValidationError({'detail': f'Failed to create host: {result}'})
    except Exception as e:
        logger.error(f"Error setting up host monitoring: {str(e)}")
        raise ValidationError({'detail': f'Failed to setup host monitoring: {str(e)}'})
    
@shared_task
def install_zabbix_agent(host_ip, password):
    try:
        logger.info(f'Installing Zabbix agent on {host_ip}')
        ansible_api = AnsibleAPI()
        result = ansible_api.install_zabbix_agent(host_ip, ssh_pass=password)
        if result['status'] == 'success':
            ZabbixSyncHost.objects.filter(ip=host_ip).update(agent_installed=True)
            return result
        else:
            ZabbixSyncHost.objects.filter(ip=host_ip).update(agent_installed=False)
            raise ValidationError({'detail': f'Failed to install Zabbix agent: {result["message"]}'})
    except Exception as e:
        logger.error(f"Error installing Zabbix agent: {str(e)}")
        raise ValidationError({'detail': f'Failed to install Zabbix agent: {str(e)}'})