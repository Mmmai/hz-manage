import logging
import json
from .constants import ValidationType

logger = logging.getLogger(__name__)

def resolve_model_field_id_list(value):
    """
    一个“值解析器”，专门用于处理 ModelFields的ID列表字段。
    例如：Models.instance_name_template UniqueConstraints.fields
    它接收原始值（一个ID列表），并返回一个 ModelFields 对象列表。
    """
    from .models import ModelFields

    if value and isinstance(value, list):
        # 根据ID列表查询出所有关联的 ModelFields 对象
        return list(ModelFields.objects.filter(id__in=value))
    return []

def resolve_dynamic_value(model_field, value):
    """
    一个“值解析器”，专门用于处理enum/model_ref字段的值。
    它接收一个 ModelFields 对象和一个原始值，并根据字段类型返回带label/instance_name的字典。
    """
    from .models import ModelInstance, ValidationRules

    if value is None:
        return None

    if model_field.type == ValidationType.ENUM and model_field.validation_rule:
        try:
            enum_dict = ValidationRules.get_enum_dict(model_field.validation_rule.id)
            return json.dumps({
                'key': value,
                'label': enum_dict.get(value, f"[未知选项: {value}]")
            }, ensure_ascii=False)
        except Exception:
            logger.error(f"Failed to resolve enum value for field '{model_field.name}' with value: {value}", exc_info=True)
            return value

    if model_field.type == ValidationType.MODEL_REF:
        try:
            ref_instance = ModelInstance.objects.get(id=value)
            return json.dumps({
                'id': str(ref_instance.id),
                'instance_name': ref_instance.instance_name
            }, ensure_ascii=False)
        except ModelInstance.DoesNotExist:
            return json.dumps({
                'id': value,
                'instance_name': f'[已删除的实例: {value}]'
            }, ensure_ascii=False)
        except Exception:
            logger.error(f"Failed to resolve model reference value for field '{model_field.name}' with value: {value}", exc_info=True)
            return value

    return value