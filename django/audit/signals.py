import json
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict

from .registry import registry
from .models import AuditLog, FieldAuditDetail
from .context import get_audit_context


def get_changed_data(instance):
    """获取模型变更的字段"""
    changed_data = {}
    if not hasattr(instance, '_old_instance') or not instance._old_instance:
        return {}

    old_instance_dict = model_to_dict(instance._old_instance)
    new_instance_dict = model_to_dict(instance)

    # 忽略的字段
    ignore_fields = registry.config(instance.__class__).get('ignore_fields', set())
    ignore_fields.add(instance._meta.pk.name)  # 总是忽略主键

    for field, new_value in new_instance_dict.items():
        if field in ignore_fields:
            continue

        old_value = old_instance_dict.get(field)
        if old_value != new_value:
            changed_data[field] = [old_value, new_value]

    return changed_data


def get_dynamic_field_changes(instance):
    """获取CMDB动态字段的变更"""
    if not hasattr(instance, '_old_dynamic_fields'):
        return {}

    old_fields = instance._old_dynamic_fields
    new_fields = {
        fv.model_field.field_name: {
            "value": fv.field_value,
            "verbose_name": fv.model_field.field_verbose_name
        }
        for fv in instance.field_values.all().select_related('model_field')
    }

    changed_fields = {}
    all_field_names = set(old_fields.keys()) | set(new_fields.keys())

    for field_name in all_field_names:
        old_data = old_fields.get(field_name)
        new_data = new_fields.get(field_name)

        old_value = old_data['value'] if old_data else None
        new_value = new_data['value'] if new_data else None

        if old_value != new_value:
            verbose_name = (new_data['verbose_name'] if new_data
                            else old_data['verbose_name'])
            changed_fields[field_name] = {
                "verbose_name": verbose_name,
                "old": old_value,
                "new": new_value
            }
    return changed_fields


@receiver(pre_save)
def capture_old_state(sender, instance, **kwargs):
    """在保存前捕获旧实例和旧的动态字段值"""
    if not (registry.is_instance(sender) or registry.is_schema(sender)):
        return

    if instance.pk:
        try:
            instance._old_instance = sender.objects.get(pk=instance.pk)

            # 如果是字段感知模型，捕获旧的动态字段值
            if registry.is_field_aware(sender):
                instance._old_dynamic_fields = {
                    fv.model_field.field_name: {
                        "value": fv.field_value,
                        "verbose_name": fv.model_field.field_verbose_name
                    }
                    for fv in instance._old_instance.field_values.all().select_related('model_field')
                }
        except sender.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None


@receiver(post_save)
def log_changes(sender, instance, created, **kwargs):
    """
    在保存后记录变更，聚合CMDB动态字段。
    这个信号处理器将取代之前只处理ModelFieldValues的逻辑。
    """
    if not (registry.is_instance(sender) or registry.is_schema(sender)):
        return

    context = get_audit_context()
    if not context:
        return

    action = 'CREATE' if created else 'UPDATE'

    # 1. 获取模型自身字段的变更
    changed_data = {}
    if not created:
        changed_data = get_changed_data(instance)

    # 2. 如果是字段感知模型，获取动态字段的变更
    dynamic_changes = {}
    if registry.is_field_aware(sender) and not created:
        dynamic_changes = get_dynamic_field_changes(instance)

    # 如果没有任何变更，则不记录
    if not created and not changed_data and not dynamic_changes:
        return

    # 3. 创建主审计日志
    log = AuditLog.objects.create(
        action=action,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=str(instance.pk),
        changed_fields=changed_data,
        operator=context.get('operator', ''),
        operator_ip=context.get('operator_ip'),
        request_id=context.get('request_id', ''),
        comment=f"{'创建' if created else '更新'}了实例: {getattr(instance, 'instance_name', str(instance.pk))}"
    )

    # 4. 为动态字段的变更创建详细记录
    if dynamic_changes:
        details_to_create = [
            FieldAuditDetail(
                audit_log=log,
                field_name=field_name,
                field_verbose_name=changes['verbose_name'],
                old_value=changes['old'],
                new_value=changes['new']
            )
            for field_name, changes in dynamic_changes.items()
        ]
        FieldAuditDetail.objects.bulk_create(details_to_create)


@receiver(post_delete)
def log_deletion(sender, instance, **kwargs):
    """记录删除操作"""
    if not (registry.is_instance(sender) or registry.is_schema(sender)):
        return

    context = get_audit_context()
    if not context:
        return

    # 将模型数据转为字典以供记录
    deleted_data = model_to_dict(instance)

    AuditLog.objects.create(
        action='DELETE',
        content_type=ContentType.objects.get_for_model(sender),
        object_id=str(instance.pk),
        changed_fields=deleted_data,  # 在changed_fields中记录被删除的数据
        operator=context.get('operator', ''),
        operator_ip=context.get('operator_ip'),
        request_id=context.get('request_id', ''),
        comment=f"删除了实例: {getattr(instance, 'instance_name', str(instance.pk))}"
    )
