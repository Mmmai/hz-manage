import logging
from contextlib import contextmanager
from threading import local
from django.db.models import Model, QuerySet, ForeignKey, ManyToManyField, JSONField
from django.forms.models import model_to_dict

from .registry import registry

_thread_locals = local()
logger = logging.getLogger(__name__)


def get_static_field_snapshot(instance):
    if not instance:
        return {}
    config = registry.config(instance.__class__)
    ignore_fields = set(config.get('ignore_fields', ()))
    ignore_fields.add(instance._meta.pk.name)

    snapshot = {}

    # TODO: 使用 select_related 和 prefetch_related 来优化查询

    for field in instance._meta.get_fields():
        if field.name in ignore_fields:
            continue
        # 跳过反向关系和多对多字段
        if not field.concrete or field.many_to_many:
            continue

        field_name = field.name
        field_value = getattr(instance, field_name)

        resolver = registry.get_field_resolver(instance.__class__, field_name)

        # 普通字段
        if resolver:
            snapshot[field_name] = resolver(field_value)
            continue

        if isinstance(field, ForeignKey):
            snapshot[field_name] = get_field_value_snapshot(field_value)
            continue

        snapshot[field_name] = field_value

    return snapshot


def get_dynamic_field_snapshot(instance):
    if not instance or not registry.is_field_aware(instance.__class__):
        return {}
    snapshot = {
        fv.model_fields.name: {
            "value": fv.data,
            "verbose_name": fv.model_fields.verbose_name,
            "model_field": fv.model_fields
        }
        for fv in instance.field_values.all().select_related('model_fields')
    }
    logger.info(f"Dynamic field snapshot for {instance}: {snapshot}")
    return snapshot


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
def capture_audit_snapshots(instance, create=False):
    if create:
        try:
            yield
        finally:
            clear_prefetched_snapshots()
        return

    try:
        if not instance.pk:
            yield

        db_inst = instance.__class__.objects.get(pk=instance.pk)
        set_prefetched_snapshot(
            instance,
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


def get_field_value_snapshot(value, end_recursion=False):
    """
    为给定的值创建一个详细的、可序列化的快照。
    - 如果值是模型实例，则根据注册表的配置生成快照字典。
    - 如果值是 QuerySet 或列表，则为其中每个实例生成快照。
    - 否则，返回原始值。
    """
    if isinstance(value, Model):
        model_class = value.__class__
        if not registry.is_registered(model_class):
            return str(value.pk)  # 如果模型未注册，则回退到只存主键

        snapshot_fields = registry.get_snapshot_fields(model_class)
        snapshot = {}
        for field in snapshot_fields:
            resolver = registry.get_field_resolver(model_class, field)
            if hasattr(value, field):
                if resolver:
                    snapshot[field] = resolver(getattr(value, field))
                elif isinstance(getattr(value, field), Model) and not end_recursion:
                    snapshot[field] = get_field_value_snapshot(getattr(value, field), end_recursion=True)
                elif isinstance(getattr(value, field), Model) and end_recursion:
                    snapshot[field] = str(getattr(value, field))
                else:
                    snapshot[field] = getattr(value, field)

        # 确保主键总是存在
        if 'id' not in snapshot and hasattr(value, 'id'):
            snapshot['id'] = value.id
        return snapshot

    if isinstance(value, (QuerySet, list, tuple)):
        # 递归地为列表或QuerySet中的每个项目创建快照
        return [get_field_value_snapshot(item) for item in value]

    # 对于基本类型（字符串、数字、布尔值等），直接返回
    return value
