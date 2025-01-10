import io
import uuid
import logging
import traceback
from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from .models import ModelInstance
from .serializers import ModelInstanceSerializer
from .excel import ExcelHandler

logger = logging.getLogger(__name__)

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
def setup_host_monitoring(instances):
    try:
        for instance in instances:
            # register host logic
            pass
    except Exception as e:
        logger.error(f"Error setting up host monitoring: {str(e)}")
        raise ValidationError({'detail': f'Failed to setup host monitoring: {str(e)}'})