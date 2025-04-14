from django.utils import timezone
from django.db.models import Q
from .models import AuditLog
from .middlewares import get_audit_context
from cmdb.models import Models, ModelFields, ModelFieldMeta
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """审计服务类 - 处理批量操作的审计记录"""

    @classmethod
    def get_field_metadata(cls, model_obj, field_name):
        """获取字段的元数据信息

        Args:
            model_obj: 模型对象
            field_name: 字段名称

        Returns:
            包含字段元数据的字典
        """
        try:
            # 查询字段定义
            model_field = ModelFields.objects.filter(
                Q(model=model_obj) & Q(field__name=field_name)
            ).select_related('field').first()

            if model_field:
                return {
                    'verbose_name': model_field.field.verbose_name or field_name,
                }

            return {'verbose_name': field_name}

        except Exception as e:
            logger.error(f"获取字段元数据失败: {str(e)}")
            return {'verbose_name': field_name}

    @classmethod
    def record_instance_created(cls, instance, instance_data=None, fields_data=None):
        """记录实例创建的审计日志

        Args:
            instance: 实例对象
            instance_data: 实例基本信息
            fields_data: 实例字段值数据，格式为 {field_name: field_value}

        Returns:
            创建的审计日志记录
        """
        try:
            context = get_audit_context()
            model_obj = instance.model

            # 构建字段变更详情
            changes = {}

            # 处理实例基本数据变更
            if instance_data:
                for field_name, value in instance_data.items():
                    if field_name == 'id' or field_name.startswith('_'):
                        continue

                    # 记录实例基本属性的变更
                    changes[field_name] = {
                        'verbose_name': field_name,
                        'old_value': None,
                        'new_value': value
                    }

            # 处理字段值数据变更
            if fields_data:
                for field_name, value in fields_data.items():
                    if field_name == 'id' or field_name.startswith('_'):
                        continue

                    # 获取字段元数据
                    field_meta = cls.get_field_metadata(model_obj, field_name)

                    # 记录字段值的变更
                    changes[field_name] = {
                        'verbose_name': field_meta.get('verbose_name', field_name),
                        'old_value': None,
                        'new_value': value
                    }

            # 合并数据快照
            snapshot = {}
            if instance_data:
                snapshot.update(instance_data)
            if fields_data:
                snapshot['fields'] = fields_data

            # 创建审计记录
            return AuditLog.objects.create(
                request_id=context['request_id'],
                user=context['user'],
                user_ip=context['ip'],
                model=model_obj,
                instance_id=str(instance.id),
                instance_name=instance.instance_name,
                action=AuditLog.ACTION_CREATE,
                changes=changes,
                snapshot_after=snapshot,
                can_revert=True,
                comment=f"创建{model_obj.verbose_name}实例"
            )

        except Exception as e:
            logger.error(f"记录实例创建审计失败: {str(e)}")
            return None

    @classmethod
    def record_instance_updated(cls, instance, old_instance_data=None, new_instance_data=None,
                                old_fields_data=None, new_fields_data=None):
        """记录实例更新的审计日志

        Args:
            instance: 实例对象
            old_instance_data: 更新前的实例基本信息
            new_instance_data: 更新后的实例基本信息
            old_fields_data: 更新前的字段值数据，格式为 {field_name: field_value}
            new_fields_data: 更新后的字段值数据，格式为 {field_name: field_value}

        Returns:
            创建的审计日志记录，如果没有变更则返回None
        """
        try:
            context = get_audit_context()
            model_obj = instance.model

            # 构建字段变更详情
            changes = {}

            # 处理实例基本数据变更
            if old_instance_data and new_instance_data:
                for field_name, new_value in new_instance_data.items():
                    if field_name == 'id' or field_name.startswith('_'):
                        continue

                    old_value = old_instance_data.get(field_name)

                    # 值没有变化则跳过
                    if old_value == new_value:
                        continue

                    # 记录实例基本属性的变更
                    changes[field_name] = {
                        'verbose_name': field_name,
                        'old_value': old_value,
                        'new_value': new_value
                    }

            # 处理字段值数据变更
            if old_fields_data is None:
                old_fields_data = {}
            if new_fields_data:
                for field_name, new_value in new_fields_data.items():
                    old_value = old_fields_data.get(field_name)

                    # 值没有变化则跳过
                    if old_value == new_value:
                        continue

                    # 获取字段元数据
                    field_meta = cls.get_field_metadata(model_obj, field_name)

                    # 记录字段值的变更
                    changes[field_name] = {
                        'verbose_name': field_meta.get('verbose_name', field_name),
                        'old_value': old_value,
                        'new_value': new_value
                    }

            # 如果没有实际变更，则不创建审计记录
            if not changes:
                return None

            # 合并数据快照
            snapshot_before = {}
            if old_instance_data:
                snapshot_before.update(old_instance_data)
            if old_fields_data:
                snapshot_before['fields'] = old_fields_data

            snapshot_after = {}
            if new_instance_data:
                snapshot_after.update(new_instance_data)
            if new_fields_data:
                snapshot_after['fields'] = new_fields_data

            # 创建审计记录
            return AuditLog.objects.create(
                request_id=context['request_id'],
                user=context['user'],
                user_ip=context['ip'],
                model=model_obj,
                instance_id=str(instance.id),
                instance_name=instance.instance_name,
                action=AuditLog.ACTION_UPDATE,
                changes=changes,
                snapshot_before=snapshot_before,
                snapshot_after=snapshot_after,
                can_revert=True,
                comment=f"更新{model_obj.verbose_name}实例"
            )

        except Exception as e:
            logger.error(f"记录实例更新审计失败: {str(e)}")
            return None

    @classmethod
    def record_instance_deleted(cls, instance, instance_data=None, fields_data=None):
        """记录实例删除的审计日志

        Args:
            instance: 实例对象
            instance_data: 实例基本信息
            fields_data: 实例字段值数据，格式为 {field_name: field_value}

        Returns:
            创建的审计日志记录
        """
        try:
            context = get_audit_context()
            model_obj = instance.model

            # 合并数据快照
            snapshot = {}
            if instance_data:
                snapshot.update(instance_data)
            if fields_data:
                snapshot['fields'] = fields_data

            # 创建审计记录
            return AuditLog.objects.create(
                request_id=context['request_id'],
                user=context['user'],
                user_ip=context['ip'],
                model=model_obj,
                instance_id=str(instance.id),
                instance_name=instance.instance_name,
                action=AuditLog.ACTION_DELETE,
                snapshot_before=snapshot,
                can_revert=True,
                comment=f"删除{model_obj.verbose_name}实例"
            )

        except Exception as e:
            logger.error(f"记录实例删除审计失败: {str(e)}")
            return None
