from ..models import ModelFields


def generate_instance_name(field_values, template_field_ids, template_field_names=None):
    if not template_field_ids and not template_field_names:
        return None

    MAX_FIELD_VALUE_LENGTH = 30  # 每个字段值的最大长度
    MAX_INSTANCE_NAME_LENGTH = 100  # 实例名称的最大总长度

    if not template_field_names:
        template_fields = ModelFields.objects.filter(id__in=template_field_ids).values_list('id', 'name')
        template_fields = {str(f[0]): f[1] for f in template_fields}
        template_fields = [template_fields[str(id)] for id in template_field_ids]

    else:
        template_fields = template_field_names

    parts = []
    for field in template_fields:
        value = field_values.get(field)
        if value is not None and value != '':
            # 截断过长的字段值
            if len(str(value)) > MAX_FIELD_VALUE_LENGTH:
                truncated_value = str(value)[:MAX_FIELD_VALUE_LENGTH - 3] + "..."
                parts.append(truncated_value)
            else:
                parts.append(str(value))

    if not parts:
        return None

    # 连接各字段值
    instance_name = ' - '.join(parts)

    # 如果总长度超过限制，进行截断
    if len(instance_name) > MAX_INSTANCE_NAME_LENGTH:
        instance_name = instance_name[:MAX_INSTANCE_NAME_LENGTH - 3] + "..."

    return instance_name
