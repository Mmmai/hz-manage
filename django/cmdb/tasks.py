import io
import uuid
import logging
import traceback

from celery import shared_task
from django.core.cache import cache
from django.db import transaction
from rest_framework.exceptions import ValidationError

from mapi.models import UserInfo
from .models import *
from .services import *
from .serializers import ModelInstanceSerializer
from .excel import ExcelHandler
from .utils.name_generator import generate_instance_name
from audit.context import audit_context

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def process_import_data(self, excel_data: dict, model_id: str, userid: str, _audit_context: dict):
    """
    通过表格导入数据创建或更新模型实例的异步任务。
    使用序列化器进行校验，服务层执行创建/更新。
    """
    task_id = self.request.id
    cache_key = f'import_task_{task_id}'

    user = UserInfo.objects.get(id=userid)

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

    error_data = []
    processed_names = set()

    try:
        model = Models.objects.get(id=model_id)
        instances_data = excel_data.get('instances', [])

        if not instances_data:
            results['status'] = 'completed'
            results['progress'] = 100
            cache.set(cache_key, results, timeout=600)
            return results

        import_context = ModelInstanceService.build_import_context(model, instances_data)
        logger.info(f"Starting import of {len(instances_data)} instances for model {model.name}")

        for idx, instance_data in enumerate(instances_data):
            instance_name = instance_data.get('instance_name', '')
            using_template = instance_data.get('using_template', None)

            # 跳过重复
            if instance_name and instance_name in processed_names:
                results['skipped'] += 1
                _update_progress(results, cache_key)
                continue
            if instance_name:
                processed_names.add(instance_name)

            # 跳过无名称
            if not instance_name:
                results['skipped'] += 1
                _update_progress(results, cache_key)
                continue

            try:
                raw_fields = {
                    k: v for k, v in instance_data.get('fields', {}).items()
                    if v not in (None, '')
                }
                processed_fields = ModelInstanceService.preprocess_import_fields(raw_fields, import_context)

                existing_instance = import_context['existing_instances'].get(instance_name)
                is_update = existing_instance is not None

                serializer_data = {
                    'model': model_id,
                    'instance_name': instance_name,
                    'fields': processed_fields,
                    'input_mode': 'import',
                    'using_template': using_template
                }
                logger.debug(f'Processing instance: {serializer_data}')

                if is_update:
                    if using_template is None:
                        serializer_data['using_template'] = existing_instance.using_template
                    serializer = ModelInstanceSerializer(
                        instance=existing_instance,
                        data=serializer_data,
                        partial=True,
                        context=import_context
                    )
                else:
                    if using_template is None:
                        serializer_data['using_template'] = True
                    serializer = ModelInstanceSerializer(
                        data=serializer_data,
                        context=import_context
                    )

                serializer.is_valid(raise_exception=True)
                validated_data = serializer.validated_data

                with audit_context(**_audit_context):
                    if is_update:
                        logger.debug(f"Updating existing instance '{instance_name}'")
                        ModelInstanceService.validate_fields_for_import_update(
                            model=model,
                            input_fields=raw_fields,
                            user=user,
                            import_context=import_context
                        )
                        logger.debug(f"Validated fields for update of instance '{instance_name}'")
                        ModelInstanceService.update_instance(
                            instance=existing_instance,
                            validated_data=validated_data,
                            user=user,
                            from_excel=True
                        )
                        results['updated'] += 1
                    else:
                        # 获取空闲池
                        unassigned_group = import_context.get('unassigned_group')
                        group_ids = [unassigned_group.id] if unassigned_group else None
                        filled_fields = ModelInstanceService.prepare_fields_for_import_creation(
                            model=model,
                            input_fields=processed_fields,
                            user=user,
                            import_context=import_context
                        )
                        validated_data['fields'] = filled_fields
                        with transaction.atomic():
                            instance = ModelInstanceService.create_instance(
                                validated_data=validated_data,
                                user=user,
                                instance_group_ids=group_ids,
                                from_excel=True
                            )
                            ModelInstanceService.backfill_field_values(
                                instance=instance,
                                fields_data=filled_fields,
                                from_excel=True
                            )
                        results['created'] += 1

            except ValidationError as e:
                error_msg = str(e.detail) if hasattr(e, 'detail') else str(e)
                results['failed'] += 1
                results['errors'].append(f"Row {idx + 1} '{instance_name}': {error_msg}")
                error_data.append({
                    'instance_name': instance_name,
                    'fields': instance_data.get('fields'),
                    'error': error_msg
                })
            except Exception as e:
                logger.error(f"Error importing instance '{instance_name}': {traceback.format_exc()}")
                results['failed'] += 1
                results['errors'].append(f"Row {idx + 1} '{instance_name}': {str(e)}")
                error_data.append({
                    'instance_name': instance_name,
                    'using_template': using_template,
                    'fields': instance_data.get('fields'),
                    'error': str(e)
                })

            _update_progress(results, cache_key)

        if error_data:
            _generate_error_report(model_id, excel_data, error_data, results)

        results['status'] = 'completed'
        results['progress'] = 100
        cache.set(cache_key, results, timeout=600)

        logger.info(
            f"Import completed for model {model.name}: "
            f"created={results['created']}, updated={results['updated']}, "
            f"skipped={results['skipped']}, failed={results['failed']}"
        )

    except Models.DoesNotExist:
        results['status'] = 'failed'
        results['errors'].append(f"Model with id {model_id} not found")
        cache.set(cache_key, results, timeout=600)
    except Exception as e:
        logger.error(f"Fatal error in import task: {traceback.format_exc()}")
        results['status'] = 'failed'
        results['errors'].append(f"Fatal error: {str(e)}")
        cache.set(cache_key, results, timeout=600)

    return results


def _update_progress(results: dict, cache_key: str):
    """更新进度到缓存"""
    processed = results['created'] + results['updated'] + results['skipped'] + results['failed']
    results['progress'] = int(processed * 100 / results['total']) if results['total'] > 0 else 100
    cache.set(cache_key, results, timeout=600)


def _generate_error_report(model_id: str, excel_data: dict, error_data: list, results: dict):
    """生成错误报告文件"""
    try:
        excel_handler = ExcelHandler()
        error_wb = excel_handler.generate_error_export(
            model_id,
            excel_data.get('headers', []),
            excel_data.get('header_rows', []),
            error_data
        )
        output = io.BytesIO()
        error_wb.save(output)
        output.seek(0)
        error_key = f"import_error_{uuid.uuid4()}"
        cache.set(error_key, output.getvalue(), timeout=600)
        results['error_file_key'] = error_key
        logger.info(f"Generated error report with {len(error_data)} errors")
    except Exception as e:
        logger.error(f"Error generating error report: {str(e)}")


@shared_task(bind=True)
def update_instance_names_for_model_template_change(self, model_id, old_template, new_template, context):
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
        # logger.debug(f'Audit context passed to task: {context}')
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
                with audit_context(**context):
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
