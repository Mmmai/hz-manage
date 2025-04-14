import functools
import logging
from .services import AuditService

logger = logging.getLogger(__name__)


def audit_create(func):
    """
    记录创建操作的审计日志装饰器

    装饰在视图函数上，自动记录实例创建操作
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # 执行原始创建操作
        response = func(self, *args, **kwargs)

        try:
            # 从响应中提取创建的实例和数据
            if hasattr(response, 'data'):
                # 获取实例
                instance = getattr(response, 'instance', None)
                if not instance and hasattr(self, 'get_object'):
                    try:
                        instance = self.get_object()
                    except Exception:
                        pass

                if instance:
                    # 提取实例数据和字段数据
                    instance_data = {}
                    fields_data = {}

                    # 从响应数据中提取信息
                    if isinstance(response.data, dict):
                        for key, value in response.data.items():
                            if key == 'fields' and isinstance(value, dict):
                                fields_data.update(value)
                            elif not key.startswith('_'):
                                instance_data[key] = value

                    # 记录审计日志
                    AuditService.record_instance_created(
                        instance=instance,
                        instance_data=instance_data,
                        fields_data=fields_data
                    )
        except Exception as e:
            logger.error(f"记录创建审计日志失败: {str(e)}")

        return response
    return wrapper


def audit_update(func):
    """
    记录更新操作的审计日志装饰器

    装饰在视图函数上，自动记录实例更新操作
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # 获取更新前的实例和数据
        old_instance = None
        old_instance_data = {}
        old_fields_data = {}

        try:
            # 获取更新前的实例
            if hasattr(self, 'get_object'):
                old_instance = self.get_object()

                # 获取实例基本数据
                for field in old_instance._meta.fields:
                    if not field.name.startswith('_'):
                        old_instance_data[field.name] = getattr(old_instance, field.name)

                # 获取实例字段值数据
                if hasattr(old_instance, 'get_fields_values'):
                    old_fields_values = old_instance.get_fields_values()
                    for field_name, field_value in old_fields_values.items():
                        old_fields_data[field_name] = field_value
        except Exception as e:
            logger.error(f"获取更新前数据失败: {str(e)}")

        # 执行原始更新操作
        response = func(self, *args, **kwargs)

        try:
            # 从响应中提取更新后的实例和数据
            if hasattr(response, 'data') and old_instance:
                # 更新后的实例
                instance = old_instance
                if hasattr(instance, 'refresh_from_db'):
                    instance.refresh_from_db()

                # 提取实例数据和字段数据
                new_instance_data = {}
                new_fields_data = {}

                # 获取实例基本数据
                for field in instance._meta.fields:
                    if not field.name.startswith('_'):
                        new_instance_data[field.name] = getattr(instance, field.name)

                # 从响应数据中提取字段值
                if isinstance(response.data, dict):
                    for key, value in response.data.items():
                        if key == 'fields' and isinstance(value, dict):
                            new_fields_data.update(value)

                # 如果没有从响应中获取到字段值，尝试从实例获取
                if not new_fields_data and hasattr(instance, 'get_fields_values'):
                    new_fields_values = instance.get_fields_values()
                    for field_name, field_value in new_fields_values.items():
                        new_fields_data[field_name] = field_value

                # 记录审计日志
                AuditService.record_instance_updated(
                    instance=instance,
                    old_instance_data=old_instance_data,
                    new_instance_data=new_instance_data,
                    old_fields_data=old_fields_data,
                    new_fields_data=new_fields_data
                )
        except Exception as e:
            logger.error(f"记录更新审计日志失败: {str(e)}")

        return response
    return wrapper


def audit_delete(func):
    """
    记录删除操作的审计日志装饰器

    装饰在视图函数上，自动记录实例删除操作
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # 获取删除前的实例和数据
        old_instance = None
        old_instance_data = {}
        old_fields_data = {}

        try:
            # 获取删除前的实例
            if hasattr(self, 'get_object'):
                old_instance = self.get_object()

                # 获取实例基本数据
                for field in old_instance._meta.fields:
                    if not field.name.startswith('_'):
                        old_instance_data[field.name] = getattr(old_instance, field.name)

                # 获取实例字段值数据
                if hasattr(old_instance, 'get_fields_values'):
                    old_fields_values = old_instance.get_fields_values()
                    for field_name, field_value in old_fields_values.items():
                        old_fields_data[field_name] = field_value

                # 记录审计日志 - 在删除前记录
                AuditService.record_instance_deleted(
                    instance=old_instance,
                    instance_data=old_instance_data,
                    fields_data=old_fields_data
                )
        except Exception as e:
            logger.error(f"记录删除审计日志失败: {str(e)}")

        # 执行原始删除操作
        return func(self, *args, **kwargs)
    return wrapper
