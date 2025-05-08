import json
from ..models import ModelFields, ModelInstance
import logging

logger = logging.getLogger(__name__)


def generate_instance_name(field_values, template_field_ids, template_field_names=None):
    if not template_field_ids and not template_field_names:
        return None

    MAX_FIELD_VALUE_LENGTH = 30  # 每个字段值的最大长度
    MAX_INSTANCE_NAME_LENGTH = 100  # 实例名称的最大总长度

    if not template_field_names:
        template_fields = ModelFields.objects.filter(
            id__in=template_field_ids
        ).prefetch_related('validation_rule__rule').values('id', 'name', 'type', 'validation_rule__rule')
        field_id_to_info = {
            str(f['id']): {
                'name': f['name'],
                'type': f['type'],
                'validation_rule': f['validation_rule__rule']
            } for f in template_fields
        }
        template_field_info = [
            field_id_to_info[str(id)]
            for id in template_field_ids
            if str(id) in field_id_to_info
        ]
    else:
        template_fields = ModelFields.objects.filter(
            name__in=template_field_names
        ).prefetch_related('validation_rule__rule').values('id', 'name', 'type', 'validation_rule__rule')
        field_id_to_info = {
            str(f['id']): {
                'name': f['name'],
                'type': f['type'],
                'validation_rule': f['validation_rule__rule']
            } for f in template_fields
        }
        template_field_info = [
            field_id_to_info[str(id)]
            for id in template_field_ids
            if str(id) in field_id_to_info
        ]

    parts = []
    for field_info in template_field_info:
        field_name = field_info['name']
        field_type = field_info.get('type')
        validation_rule = field_info.get('validation_rule')

        if field_type in ['password', 'json']:
            continue

        value = field_values.get(field_name)
        if value is not None and value != '':
            display_value = value

            try:
                if field_type == 'enum' and value and validation_rule:
                    try:
                        enum_options = json.loads(validation_rule)
                        display_value = enum_options.get(value, value)
                    except Exception as e:
                        logger.warning(f"Error processing enum field '{field_name}': {str(e)}")

                elif field_type == 'model_ref' and value:
                    try:
                        ref_instance = ModelInstance.objects.filter(id=value).first()
                        if ref_instance and ref_instance.instance_name:
                            display_value = ref_instance.instance_name
                    except Exception as e:
                        logger.warning(f"Error processing model_ref field '{field_name}': {str(e)}")
            except Exception as e:
                logger.error(f"Error processing field '{field_name}' for name generation: {str(e)}")

            # 截断过长的字段值
            if len(str(display_value)) > MAX_FIELD_VALUE_LENGTH:
                truncated_value = str(display_value)[:MAX_FIELD_VALUE_LENGTH - 3] + "..."
                parts.append(truncated_value)
            else:
                parts.append(str(display_value))

    if not parts:
        return None

    # 连接各字段值
    instance_name = ' - '.join(parts)

    # 如果总长度超过限制，进行截断
    if len(instance_name) > MAX_INSTANCE_NAME_LENGTH:
        instance_name = instance_name[:MAX_INSTANCE_NAME_LENGTH - 3] + "..."

    return instance_name
