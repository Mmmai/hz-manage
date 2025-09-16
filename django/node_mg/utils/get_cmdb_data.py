from cmdb.models import (
    Models,
    ModelInstance,
    ModelFieldMeta
    )
from cmdb.utils import password_handler, zabbix_config

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
                res[field.model_fields.name] = password_handler.decrypt_to_plain(field.data)
            else:
                res[field.model_fields.name] = field.data
    return res
if __name__ == "__main__":
    pass
    # obj = ModelInstance.objects.get(id=1)
    # print(get_instance_field_value(obj, 'ip'))
    # print(get_instance_field_value_info(obj, ['system_user','system_password','ssh_port','ipmi_user','ipmi_password','mgmt_ip']))