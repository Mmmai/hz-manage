import logging
from django.db import transaction
from django.db.models.signals import pre_save, post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.utils import timezone
from .registry import registry
from .models import AuditLog, FieldAuditDetail
from .context import get_audit_context
from .utils import clean_for_json
from .snapshots import (
    get_dynamic_field_snapshot,
    get_prefetched_snapshot,
    get_static_field_snapshot,
    get_field_value_snapshot
)
from cmdb.message import instance_group_relations_audit, instance_bulk_update_audit

logger = logging.getLogger(__name__)

def build_audit_comment(action, instance):
    verb = {"CREATE": "创建", "UPDATE": "更新", "DELETE": "删除"}.get(action, action)
    model_name = ""
    if hasattr(instance, "_meta"):
        model_name = instance._meta.model_name
    else:
        model_name = instance.__class__.__name__.lower()

    if model_name == "models":
        name = getattr(instance, "name", str(instance))
        model_label = getattr(instance, "verbose_name", str(instance))
        return f"{verb}了模型：{model_label} ({name})"

    if model_name == 'modelfields':
        field_name = getattr(instance, "name", str(instance))
        field_verbose_name = getattr(instance, "verbose_name", field_name)
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        return f"{verb}了{model_label}的字段: {field_verbose_name} ({field_name})"
    
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
        _model_name = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        model_label = getattr(getattr(instance, "model", None), "verbose_name", "模型")
        return f"{verb}了{model_label}({_model_name})的唯一约束"

    if model_name == 'relationdefinition':
        relation_name = getattr(instance, "name", str(instance))
        return f"{verb}了关联关系定义：{relation_name}"

    if model_name == 'relations':
        relation = getattr(instance, "relation", None)
        relation_name = getattr(relation, "name", str(relation))
        source = getattr(instance, "source_instance", str(instance))
        target = getattr(instance, "target_instance", str(instance))
        source_name = getattr(source, "instance_name", str(source))
        target_name = getattr(target, "instance_name", str(target))
        return f"{verb}了关联关系：{relation_name}，源实例：{source_name}，目标实例：{target_name}"

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
    # logger.debug(f"Context snapshot captured: {context_snapshot}")

    # new_static_snapshot = get_static_field_snapshot(instance)
    
    old_static_snapshot = getattr(instance, '_old_instance_snapshot', {})
    old_dynamic_snapshot = getattr(instance, '_old_dynamic_fields_snapshot', {})

    def delayed_process(context=context_snapshot):
        # logger.debug(f"Context for delayed process: {context}")
        action = 'CREATE' if created else 'UPDATE'
        final_instance = None
        try:
            final_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return
        
        new_static_snapshot = get_static_field_snapshot(final_instance)
        new_dynamic_snapshot = get_dynamic_field_snapshot(final_instance)

        static_changes = {}
        all_static_keys = old_static_snapshot.keys() | new_static_snapshot.keys()
        for key in all_static_keys:
            old_val = old_static_snapshot.get(key)
            new_val = new_static_snapshot.get(key)
            if old_val != new_val:
                static_changes[key] = [
                    get_field_value_snapshot(old_val),
                    get_field_value_snapshot(new_val)
                ]

        resolver = registry.get_dynamic_value_resolver(sender)
        dynamic_changes = []
        all_dynamic_keys = old_dynamic_snapshot.keys() | new_dynamic_snapshot.keys()
        for key in all_dynamic_keys:
            old_field_data = old_dynamic_snapshot.get(key, {})
            new_field_data = new_dynamic_snapshot.get(key, {})
            old_val = old_field_data.get('value')
            new_val = new_field_data.get('value')

            if old_val != new_val:
                if resolver:
                    model_field = new_field_data.get('model_field') or old_field_data.get('model_field')
                    if model_field:
                        old_val = resolver(model_field, old_val)
                        new_val = resolver(model_field, new_val)
                dynamic_changes.append({
                    'name': key,
                    'verbose_name': new_field_data.get('verbose_name') or old_field_data.get('verbose_name', ''),
                    'old_value': old_val,
                    'new_value': new_val,
                })

        if created:
            static_changes = {
                key: [None, get_field_value_snapshot(val)]
                for key, val in new_static_snapshot.items()
            }
            dynamic_changes = [{
                'name': key,
                'verbose_name': data.get('verbose_name', ''),
                'old_value': None,
                'new_value': resolver(data.get('model_field'), data.get('value')) if resolver and data.get('model_field') else data.get('value')
            } for key, data in new_dynamic_snapshot.items()]

        if not created and not static_changes and not dynamic_changes:
            return
        
        # 不记录 ModelFields 仅 order 字段的变更
        if not created and sender.__name__ == 'ModelFields' and \
            static_changes.keys() == {'order'} and not dynamic_changes:
            return

        comment = context.get("comment") or build_audit_comment(action, instance)
        logger.info(f'{static_changes}, {dynamic_changes}, {comment}')
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

    resolver = registry.get_dynamic_value_resolver(sender)

    static_changes = {key: [get_field_value_snapshot(val), None] for key, val in static_snapshot.items()}
    dynamic_changes = []
    for key, data in dynamic_snapshot.items():
        old_val = data.get('value')
        model_field = data.get('model_field')
        if resolver and model_field:
            old_val = resolver(model_field, old_val)
        dynamic_changes.append({
            'name': key,
            'verbose_name': data.get('verbose_name', ''),
            'old_value': old_val,
            'new_value': None,
        })
    
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
        
        
@receiver(instance_group_relations_audit)
def log_instance_group_relation_audit(sender, instance, old_groups, new_groups, **kwargs):
    if not instance:
        return

    context = get_audit_context()

    def delayed_audit_log(context=context):
        old_groups_str = '，'.join(f"{group['label']}" for group in old_groups) if old_groups else '无'
        new_groups_str = '，'.join(f"{group['label']}" for group in new_groups) if new_groups else '无'
        comment = f"更新了模型实例 <{instance.instance_name}> 的分组关联关系：<{old_groups_str}> -> <{new_groups_str}>"
        AuditLog.objects.create(
            content_object=instance,
            action='UPDATE',
            changed_fields={
                'groups': [old_groups, new_groups]    
            },
            operator=context.get('operator', ''),
            operator_ip=context.get('operator_ip', None),
            request_id=context.get('request_id', ''),
            correlation_id=context.get('correlation_id', ''),
            comment=comment
        )

    transaction.on_commit(delayed_audit_log)
    
@receiver(instance_bulk_update_audit)
def log_instance_bulk_update_audit(sender, snapshots_list, **kwargs):
    if not snapshots_list:
        return

    context_snapshot = get_audit_context()

    first_instance_class = snapshots_list[0]['instance'].__class__
    if not registry.is_registered(first_instance_class):
        return
        
    resolver = registry.get_dynamic_value_resolver(first_instance_class)

    def delayed_process(context=context_snapshot):
        logs_with_details = []

        for info in snapshots_list:
            logger.info(f'{info}')
            instance = info['instance']
            old_snapshot = info['old_snapshot']
            new_snapshot = info['new_snapshot']
            update_fields = info.get('update_fields', [])
            
            dynamic_changes = []

            all_keys = set(old_snapshot.keys()) | set(new_snapshot.keys())
            
            for field_name in all_keys:
                if field_name not in update_fields:
                    continue

                old_field_data = old_snapshot.get(field_name, {})
                new_field_data = new_snapshot.get(field_name, {})
                old_val = old_field_data.get('value')
                new_val = new_field_data.get('value')

                if old_val != new_val:
                    model_field = new_field_data.get('model_field') or old_field_data.get('model_field')
                    if resolver and model_field:
                        old_val = resolver(model_field, old_val)
                        new_val = resolver(model_field, new_val)
                    
                    dynamic_changes.append({
                        'name': field_name,
                        'verbose_name': new_field_data.get('verbose_name') or old_field_data.get('verbose_name', ''),
                        'old_value': old_val,
                        'new_value': new_val,
                    })

            if not dynamic_changes:
                continue

            comment = context.get("comment") or build_audit_comment('UPDATE', instance)
            
            log = AuditLog(
                content_object=instance,
                action='UPDATE',
                changed_fields={},
                operator=context.get('operator', ''),
                operator_ip=context.get('operator_ip', None),
                request_id=context.get('request_id', ''),
                correlation_id=context.get('correlation_id', ''),
                comment=comment
            )
            
            details = []
            
            for change in dynamic_changes:
                details.append(FieldAuditDetail(
                    name=change['name'],
                    verbose_name=change['verbose_name'],
                    old_value=str(change['old_value']) if change['old_value'] is not None else None,
                    new_value=str(change['new_value']) if change['new_value'] is not None else None,
                ))

            logs_with_details.append((log, details))

        all_logs_to_create = [item[0] for item in logs_with_details]
        if not all_logs_to_create:
            return

        AuditLog.objects.bulk_create(all_logs_to_create)

        all_details_to_create = []
        for log, details in logs_with_details:
            for detail in details:
                detail.audit_log_id = log.id
            all_details_to_create.extend(details)

        if all_details_to_create:
            FieldAuditDetail.objects.bulk_create(all_details_to_create)

    transaction.on_commit(delayed_process)
    
@receiver(m2m_changed)
def log_generic_m2m_changes(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    M2M字段变化处理器。
    在相关M2M关系发生变化时，查找对应的注册字段，并将变更合并到主审计日志中。
    """
    # 不处理反向关系，且在关系添加/删除/清空之后
    if reverse or action not in ["post_add", "post_remove", "post_clear"]:
        return

    if not registry.is_registered(instance.__class__):
        return

    context_snapshot = get_audit_context()
    correlation_id = context_snapshot.get('correlation_id')

    if not correlation_id:
        logger.warning(f"M2M change for {instance} occurred outside of a request context. Skipping merge.")
        return

    # 从注册表中查找哪个字段使用了这个 'through' 模型
    field_name = None
    for registered_model, registered_field_name, through_model in registry.get_m2m_fields_to_audit():
        if registered_model == instance.__class__ and through_model == sender:
            field_name = registered_field_name
            break
    
    # 没有查询到字段，或者字段没有配置resolver
    if not field_name:
        return
    resolver = registry.get_field_resolver(instance.__class__, field_name)
    if not resolver:
        logger.warning(f"No resolver configured for M2M field '{field_name}' on model {instance.__class__.__name__}. Skipping merge.")
        return

    def delayed_merge(context=context_snapshot):
        try:
            manager = getattr(instance, field_name)
            instance_id = instance.pk
            main_log = AuditLog.objects.get(
                correlation_id=correlation_id, 
                object_id=str(instance_id), 
                content_type__model=instance.__class__.__name__.lower()
            )


            new_value_snapshot = resolver(manager.all())
            
            old_value_snapshot = main_log.changed_fields.get(field_name, [None, None])[0]
            if old_value_snapshot is None and action != 'post_clear':
                old_value_snapshot = []

            if main_log.changed_fields is None:
                main_log.changed_fields = {}
            
            main_log.changed_fields[field_name] = [old_value_snapshot, new_value_snapshot]
            
            main_log.save(update_fields=['changed_fields', 'timestamp'])
            logger.debug(f"Merged M2M change for field '{field_name}' into AuditLog {main_log.id}")

        except AuditLog.DoesNotExist:
            logger.warning(f"Could not find main AuditLog with correlation_id {correlation_id} to merge M2M changes. It might not have been created yet.")
        except Exception as e:
            logger.error(f"Failed to merge M2M audit changes: {e}", exc_info=True)

    transaction.on_commit(delayed_merge)