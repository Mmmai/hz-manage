from django.db import transaction
from django.utils import timezone
import json
import logging

from .models import AuditLog
from cmdb.models import Instance, ModelField, InstanceField
from .middlewares import get_audit_context

logger = logging.getLogger(__name__)


class RevertException(Exception):
    """撤销操作异常"""
    pass


@transaction.atomic
def revert_audit_log(audit_log_id):
    """
    撤销审计日志记录的操作

    Args:
        audit_log_id: 审计日志ID

    Returns:
        撤销后的对象

    Raises:
        RevertException: 撤销失败时抛出异常
    """
    try:
        # 获取审计记录
        audit_log = AuditLog.objects.select_for_update().get(id=audit_log_id)

        # 检查是否可撤销
        if not audit_log.can_revert:
            raise RevertException("此操作不可撤销")

        if audit_log.reverted:
            raise RevertException("此操作已被撤销")

        context = get_audit_context()

        # 确认实例是否存在
        try:
            if audit_log.action != AuditLog.ACTION_DELETE:  # 删除操作时实例不存在
                instance = Instance.objects.get(id=audit_log.instance_id, model=audit_log.model)
            else:
                instance = None
        except Instance.DoesNotExist:
            if audit_log.action == AuditLog.ACTION_DELETE:  # 删除操作时可以恢复
                instance = None
            else:
                raise RevertException(f"实例 {audit_log.instance_id} 不存在，无法撤销")

        # 根据操作类型执行不同撤销逻辑
        if audit_log.action == AuditLog.ACTION_CREATE:
            # 撤销创建 = 删除该实例
            result = _revert_create(audit_log, instance)
        elif audit_log.action == AuditLog.ACTION_UPDATE:
            # 撤销更新 = 恢复为原值
            result = _revert_update(audit_log, instance)
        elif audit_log.action == AuditLog.ACTION_DELETE:
            # 撤销删除 = 重新创建
            result = _revert_delete(audit_log)
        else:
            raise RevertException(f"不支持的操作类型: {audit_log.action}")

        # 标记审计记录为已撤销
        audit_log.reverted = True
        audit_log.reverted_by = context.get('user')
        audit_log.reverted_time = timezone.now()
        audit_log.save(update_fields=['reverted', 'reverted_by', 'reverted_time'])

        # 记录撤销操作的审计日志
        AuditLog.objects.create(
            request_id=context.get('request_id'),
            user=context.get('user'),
            user_ip=context.get('ip'),
            model=audit_log.model,
            instance_id=audit_log.instance_id,
            instance_name=audit_log.instance_name,
            action="revert",
            changes={},  # 没有实际的变更，只是标记撤销
            snapshot_before=audit_log.snapshot_after,
            snapshot_after=audit_log.snapshot_before,
            comment=f"撤销了操作: {audit_log.get_action_display()}-{audit_log.instance_name or audit_log.instance_id}",
            can_revert=False  # 撤销操作不能被撤销
        )

        return result

    except AuditLog.DoesNotExist:
        raise RevertException("找不到审计记录")
    except Exception as e:
        logger.error(f"撤销操作失败: {str(e)}")
        raise RevertException(f"撤销操作失败: {str(e)}")


def _revert_create(audit_log, instance):
    """撤销创建操作

    Args:
        audit_log: 审计日志记录
        instance: 实例对象

    Returns:
        None

    Raises:
        RevertException: 撤销失败时抛出异常
    """
    if not instance:
        raise RevertException("要撤销的实例不存在")

    # 删除实例及其相关的字段值
    instance.delete()
    return None


def _revert_update(audit_log, instance):
    """撤销更新操作

    Args:
        audit_log: 审计日志记录
        instance: 实例对象

    Returns:
        更新后的实例对象

    Raises:
        RevertException: 撤销失败时抛出异常
    """
    if not instance:
        raise RevertException("要撤销的实例不存在")

    if not audit_log.snapshot_before:
        raise RevertException("没有可恢复的原始数据")

    # 恢复实例基本属性
    snapshot = audit_log.snapshot_before
    for key, value in snapshot.items():
        # 跳过字段值和内部字段
        if key == 'fields' or key.startswith('_') or key == 'id':
            continue
        # 恢复实例属性
        setattr(instance, key, value)

    # 保存实例
    instance.save()

    # 恢复字段值
    fields_data = snapshot.get('fields', {})
    if fields_data:
        for field_name, field_value in fields_data.items():
            # 查找字段定义
            model_field = ModelField.objects.filter(
                name=field_name,
                models=audit_log.model
            ).first()

            if not model_field:
                logger.warning(f"字段定义不存在: {field_name}")
                continue

            # 查找或创建字段值
            instance_field, created = InstanceField.objects.get_or_create(
                instance=instance,
                field=model_field,
                defaults={'value': field_value}
            )

            # 如果字段值已存在，更新其值
            if not created:
                instance_field.value = field_value
                instance_field.save()

    return instance


def _revert_delete(audit_log):
    """撤销删除操作

    Args:
        audit_log: 审计日志记录

    Returns:
        重新创建的实例对象

    Raises:
        RevertException: 撤销失败时抛出异常
    """
    if not audit_log.snapshot_before:
        raise RevertException("没有可恢复的原始数据")

    # 从快照恢复实例数据
    snapshot = audit_log.snapshot_before
    instance_data = {}
    for key, value in snapshot.items():
        if key != 'fields' and not key.startswith('_'):
            instance_data[key] = value

    # 去除id，让数据库自动生成
    if 'id' in instance_data:
        instance_id = instance_data.pop('id')
    else:
        instance_id = audit_log.instance_id

    # 创建新实例
    instance = Instance(model=audit_log.model, **instance_data)

    # 如果需要保持原ID
    try:
        instance.id = instance_id
        instance.save()
    except Exception:
        # 如果保持原ID失败，则使用新ID
        instance.id = None
        instance.save()

    # 恢复字段值
    fields_data = snapshot.get('fields', {})
    if fields_data:
        for field_name, field_value in fields_data.items():
            # 查找字段定义
            model_field = ModelField.objects.filter(
                name=field_name,
                models=audit_log.model
            ).first()

            if not model_field:
                logger.warning(f"字段定义不存在: {field_name}")
                continue

            # 创建字段值
            InstanceField.objects.create(
                instance=instance,
                field=model_field,
                value=field_value
            )

    return instance
