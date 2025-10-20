import logging
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils import timezone

logger = logging.getLogger(__name__)


from .registry import registry
from .models import AuditLog, FieldAuditDetail
from .context import get_audit_context
from .utils import clean_for_json
from .snapshots import (
    get_dynamic_field_snapshot,
    get_prefetched_snapshot,
    get_static_field_snapshot,
)

def build_audit_comment(action, instance):
    verb = {"CREATE": "创建", "UPDATE": "更新", "DELETE": "删除"}.get(action, action)
    model_name = ""
    if hasattr(instance, "_meta"):
        model_name = instance._meta.model_name
    else:
        model_name = instance.__class__.__name__.lower()

    if model_name == "models":
        model_label = getattr(instance, "verbose_name", str(instance))
        return f"{verb}了模型：{model_label}"

    if model_name == 'modelfields':
        field_name = getattr(instance, "name", str(instance))
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        return f"{verb}了{model_label}的字段：{field_name}"
    
    if model_name == "modelinstance":
        # model_label = getattr(getattr(instance, "model", None), "name", "模型")
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")

        instance_name = getattr(instance, "instance_name", str(instance))
        return f"{verb}了{model_label}实例：{instance_name}"


    if model_name == "modelinstancegroup":
        group_name = getattr(instance, "label", str(instance))
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        parent = getattr(instance, "parent", None)
        if parent:
            parent_name = getattr(parent, "label", str(parent))
            return f"{verb}了{model_label}分组：{group_name}，父分组：{parent_name}"
        return f"{verb}了{model_label}分组：{group_name}"

    if model_name == "modelinstancegrouprelation":
        inst = getattr(instance, "instance", None)
        model_label = getattr(getattr(inst, "model", None), "verbose_name", "模型")
        group = getattr(instance, "group", None)
        inst_name = getattr(inst, "instance_name", inst) or inst
        group_name = getattr(group, "label", group) or group
        return f"{verb}了{model_label}实例 <{inst_name}> 与分组 <{group_name}> 的关联关系"
    
    if model_name == "validationrules":
        rule_name = getattr(instance, "name", str(instance))
        return f"{verb}了校验规则：{rule_name}"
    
    if model_name == "uniqueconstraint":
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        return f"{verb}了{model_label}的唯一约束"

    readable = getattr(instance.__class__, "__name__", model_name)
    return f"{verb}了{readable}"

@receiver(pre_save)
def capture_old_state(sender, instance, **kwargs):
    """在保存前，捕获旧的实例状态和动态字段值"""
    if not registry.is_registered(sender) or not instance.pk:
        return
    
    prefetched = get_prefetched_snapshot(instance)
    if prefetched:
        instance._old_instance_snapshot = prefetched["static"]
        instance._old_dynamic_fields_snapshot = prefetched["dynamic"]
        return
    try:
        db_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._old_instance_snapshot = {}
        instance._old_dynamic_fields_snapshot = {}
        return
    instance._old_instance_snapshot = get_static_field_snapshot(db_instance)
    if registry.is_field_aware(sender):
        instance._old_dynamic_fields_snapshot = get_dynamic_field_snapshot(db_instance)
    else:
        instance._old_dynamic_fields_snapshot = {}

@receiver(post_save)
def log_changes(sender, instance, created, **kwargs):
    """
    在模型保存后，注册一个在事务提交后才执行的审计任务。
    """
    if not registry.is_registered(sender):
        return

    context_snapshot = get_audit_context()
    logger.info(f"Context snapshot captured: {context_snapshot}")

    new_static_snapshot = get_static_field_snapshot(instance)
    
    old_static_snapshot = getattr(instance, '_old_instance_snapshot', {})
    old_dynamic_snapshot = getattr(instance, '_old_dynamic_fields_snapshot', {})

    def delayed_process(context=context_snapshot):
        logger.info(f"Context for delayed process: {context}")
        action = 'CREATE' if created else 'UPDATE'

        new_dynamic_snapshot = get_dynamic_field_snapshot(instance)

        static_changes = {}
        all_static_keys = old_static_snapshot.keys() | new_static_snapshot.keys()
        for key in all_static_keys:
            old_val = old_static_snapshot.get(key)
            new_val = new_static_snapshot.get(key)
            if old_val != new_val:
                static_changes[key] = [old_val, new_val]

        dynamic_changes = []
        all_dynamic_keys = old_dynamic_snapshot.keys() | new_dynamic_snapshot.keys()
        for key in all_dynamic_keys:
            old_field_data = old_dynamic_snapshot.get(key, {})
            new_field_data = new_dynamic_snapshot.get(key, {})
            old_val = old_field_data.get('value')
            new_val = new_field_data.get('value')

            if old_val != new_val:
                dynamic_changes.append({
                    'name': key,
                    'verbose_name': new_field_data.get('verbose_name') or old_field_data.get('verbose_name', ''),
                    'old_value': old_val,
                    'new_value': new_val,
                })

        if created:
            static_changes = {key: [None, val] for key, val in new_static_snapshot.items()}
            dynamic_changes = [{
                'name': key,
                'verbose_name': data.get('verbose_name', ''),
                'old_value': None,
                'new_value': data.get('value'),
            } for key, data in new_dynamic_snapshot.items()]

        if not created and not static_changes and not dynamic_changes:
            return
        
        if not created and sender.__name__ == 'ModelFields' and \
            static_changes.keys() == {'order'} and not dynamic_changes:
            return

        comment = context.get("comment") or build_audit_comment(action, instance)

        log = AuditLog.objects.create(
            content_object=instance,
            action=action,
            changed_fields=clean_for_json(static_changes),
            operator=context.get('operator', ''),
            operator_ip=context.get('operator_ip', None),
            request_id=context.get('request_id', ''),
            correlation_id=context.get('correlation_id', ''),
            comment=comment
        )

        if dynamic_changes:
            details_to_create = [
                FieldAuditDetail(
                    audit_log=log,
                    name=change['name'],
                    verbose_name=change['verbose_name'],
                    old_value=str(change['old_value']) if change['old_value'] is not None else None,
                    new_value=str(change['new_value']) if change['new_value'] is not None else None,
                ) for change in dynamic_changes
            ]
            FieldAuditDetail.objects.bulk_create(details_to_create)

    transaction.on_commit(delayed_process)


@receiver(post_delete)
def log_deletion(sender, instance, **kwargs):
    if not registry.is_registered(sender):
        return

    context = get_audit_context()
    
    static_snapshot = get_static_field_snapshot(instance)
    dynamic_snapshot = get_dynamic_field_snapshot(instance)

    static_changes = {key: [val, None] for key, val in static_snapshot.items()}
    dynamic_changes = [{
        'name': key,
        'verbose_name': data.get('verbose_name', ''),
        'old_value': data.get('value'),
        'new_value': None,
    } for key, data in dynamic_snapshot.items()]
    
    
    comment = context.get("comment") or build_audit_comment("DELETE", instance)

    log = AuditLog.objects.create(
        content_object=instance,
        action='DELETE',
        changed_fields=clean_for_json(static_changes),
        operator=context.get('operator', ''),
        operator_ip=context.get('operator_ip', None),
        request_id=context.get('request_id', ''),
        correlation_id=context.get('correlation_id', ''),
        comment=comment
    )

    if dynamic_changes:
        details_to_create = [
            FieldAuditDetail(
                audit_log=log,
                name=change['name'],
                verbose_name=change['verbose_name'],
                old_value=str(change['old_value']) if change['old_value'] is not None else None,
                new_value=None,
            ) for change in dynamic_changes
        ]
        FieldAuditDetail.objects.bulk_create(details_to_create)
        
        