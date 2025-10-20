from contextlib import contextmanager
from threading import local

from django.forms.models import model_to_dict

from .registry import registry

_thread_locals = local()


def get_static_field_snapshot(instance):
    if not instance:
        return {}
    config = registry.config(instance.__class__)
    ignore_fields = set(config.get('ignore_fields', ()))
    if instance._meta.pk:
        ignore_fields.add(instance._meta.pk.name)
    data = {}
    for field in instance._meta.fields:
        if field.name in ignore_fields:
            continue
        data.update(model_to_dict(instance, fields=[field.name]))
    return data


def get_dynamic_field_snapshot(instance):
    if not instance or not registry.is_field_aware(instance.__class__):
        return {}
    return {
        fv.model_fields.name: {
            "value": fv.data,
            "verbose_name": fv.model_fields.verbose_name,
        }
        for fv in instance.field_values.all().select_related('model_fields')
    }


def _snapshot_storage():
    if not hasattr(_thread_locals, "audit_snapshots"):
        _thread_locals.audit_snapshots = {}
    return _thread_locals.audit_snapshots


def set_prefetched_snapshot(instance, static_snapshot, dynamic_snapshot):
    storage = _snapshot_storage()
    storage[(instance.__class__, instance.pk)] = {
        "static": static_snapshot,
        "dynamic": dynamic_snapshot,
    }


def get_prefetched_snapshot(instance):
    storage = _snapshot_storage()
    return storage.pop((instance.__class__, instance.pk), None)


def clear_prefetched_snapshots():
    if hasattr(_thread_locals, "audit_snapshots"):
        _thread_locals.audit_snapshots.clear()


@contextmanager
def capture_audit_snapshots(instances):
    try:
        for inst in instances:
            if not inst.pk:
                continue
            db_inst = inst.__class__.objects.get(pk=inst.pk)
            set_prefetched_snapshot(
                inst,
                get_static_field_snapshot(db_inst),
                get_dynamic_field_snapshot(db_inst),
            )
        yield
    finally:
        clear_prefetched_snapshots()
        
        
def get_field_definition_snapshot(model):
    """
    获取一个模型(Model)的所有字段定义的快照。
    这被用作模型的“动态字段”。
    """
    if not model or model.__class__.__name__ != 'Model':
        return {}

    fields = model.fields.all().order_by('display_order')
    
    snapshot = {}
    for field in fields:
        # 将每个字段的关键定义信息序列化
        snapshot[field.name] = {
            "verbose_name": field.verbose_name,
            "group": field.model_field_group.label,
            "type": field.type,
            "unit": field.unit,
            "ref_model": field.ref_model.name if field.ref_model else None,
            "built_in": field.built_in,
            "required": field.required,
            "editable": field.editable,
            "default": field.default,
            "validation_rule": field.validation_rule.name if field.validation_rule else None,
            "description": field.description,
            "order": field.order,
        }
    return snapshot
