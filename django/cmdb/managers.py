import functools
import uuid
import json
import logging
from django.db import models, transaction

from .constants import FieldType

logger = logging.getLogger(__name__)


class ModelGroupsManager(models.Manager):

    def get_default_model_group(self):
        """
        获取或创建默认模型组
        创建行为在系统初始化时已执行，此处仅作保障
        """
        default_group, created = self.get_or_create(
            name='others',
            defaults={
                'verbose_name': '其他',
                'built_in': True,
                'editable': False,
                'description': '默认模型组',
                'create_user': 'system',
                'update_user': 'system'
            }
        )
        return default_group


class ModelFieldGroupsManager(models.Manager):

    def get_default_field_group(self, model):
        """
        获取或创建默认字段组
        """
        default_group = self.filter(
            name='basic',
            model=model
        ).first()
        return default_group


class ModelFieldsManager(models.Manager):

    def check_ref_fields_exists(self, model_id):
        """检查是否存在引用指定模型的字段"""
        return self.get_queryset().filter(ref_model_id=model_id).exists()

    def get_all_required_fields(self, model_id):
        """获取指定模型的所有必填字段"""
        return self.get_queryset().filter(
            model_id=model_id,
            required=True
        )

    def get_fields_map(self, model_id, field_ids):
        if not field_ids:
            return {}
        if hasattr(model_id, 'id'):
            model_id = model_id.id
        normalized_ids = [str(fid) for fid in field_ids]
        queryset = self.filter(
            model_id=str(model_id),
            id__in=normalized_ids
        ).select_related('validation_rule')
        return {str(field.id): field for field in queryset}


class ModelFieldMetaManager(models.Manager):

    def get_instance_field_values(self, instance_id, field_ids):
        if not instance_id or not field_ids:
            return {}
        normalized_ids = [str(fid) for fid in field_ids]
        values = self.filter(
            model_instance_id=str(instance_id),
            model_fields_id__in=normalized_ids
        ).values('model_fields_id', 'data')
        return {str(item['model_fields_id']): item['data'] for item in values}


class UniqueConstraintManager(models.Manager):

    def get_sync_constraint_for_model(self, model):
        """
        获取指定模型的唯一约束
        """
        return self.filter(
            model=model,
            built_in=True,
            description='自动生成的实例名称唯一性约束'
        ).first()

    def get_constraints_for_model(self, model):
        """
        获取指定模型的所有唯一约束
        """
        return self.filter(model=model).all()


class ModelInstanceManager(models.Manager):
    def get_instance_names_by_models(self, model_ids: list) -> dict:
        if not model_ids:
            return {}

        instances = self.filter(model_id__in=model_ids).values('id', 'instance_name')

        return {str(inst['id']): inst['instance_name'] for inst in instances}

    def get_instance_names_by_instance_ids(self, instance_ids: list) -> dict:
        if not instance_ids:
            return {}

        instances = self.filter(id__in=instance_ids).values('id', 'instance_name')

        return {str(inst['id']): inst['instance_name'] for inst in instances}

    def check_uniqueness(self, model, field_values: dict, instance_to_exclude=None) -> list:
        if not field_values:
            return []

        from .models import ModelFieldMeta

        matching_instances = set()
        first = True

        for field_name, value in field_values.items():
            instances_with_field = ModelFieldMeta.objects.filter(
                model=model,
                model_fields__name=field_name,
                data=str(value)
            ).values_list('model_instance_id', flat=True)

            current_set = set(instances_with_field)

            # 首次迭代，直接赋值
            if first:
                matching_instances = current_set
                first = False
            # 后续迭代，取交集
            else:
                matching_instances.intersection_update(current_set)

            # 如果中途交集为空，可以直接返回
            if not matching_instances:
                return []

        # 排除当前实例
        if instance_to_exclude:
            matching_instances.discard(instance_to_exclude.id)

        return list(matching_instances)

    def generate_instance_name(self, model, field_values: dict) -> str:
        from .models import ModelFields

        template_field_ids = model.instance_name_template
        if not template_field_ids:
            return None

        MAX_FIELD_VALUE_LENGTH = 30  # 每个字段值的最大长度
        MAX_INSTANCE_NAME_LENGTH = 100  # 实例名称的最大总长度

        template_fields_qs = ModelFields.objects.filter(
            id__in=template_field_ids
        ).select_related('validation_rule')
        field_id_to_info = {
            str(f.id): f for f in template_fields_qs
        }

        ref_instance_ids = []
        for field_id in template_field_ids:
            field_info = field_id_to_info.get(str(field_id))
            if field_info and field_info.type == FieldType.MODEL_REF:
                value = field_values.get(field_info.name)
                if value:
                    ref_instance_ids.append(value)

        ref_instance_names = {}
        if ref_instance_ids:
            ref_instance_names = self.get_instance_names_by_instance_ids(ref_instance_ids)

        parts = []
        for field_id in template_field_ids:
            field_info = field_id_to_info.get(str(field_id))
            if not field_info:
                continue

            field_name = field_info.name
            field_type = field_info.type

            if field_type in [FieldType.PASSWORD, FieldType.JSON]:
                continue

            value = field_values.get(field_name)
            if value is None or value == '':
                continue

            display_value = value
            try:
                if field_type == FieldType.ENUM and field_info.validation_rule:
                    enum_options = json.loads(field_info.validation_rule.rule)
                    display_value = enum_options.get(str(value), value)
                elif field_type == FieldType.MODEL_REF:
                    display_value = ref_instance_names.get(str(value), value)
            except Exception as e:
                logger.error(f'Error generating instance name for field "{field_name}": {str(e)}')
                raise ValueError(f'Error processing field "{field_name}" while generating instance name: {str(e)}')

            # 截断过长的字段值
            display_value_str = str(display_value)
            if len(display_value_str) > MAX_FIELD_VALUE_LENGTH:
                display_value_str = display_value_str[:MAX_FIELD_VALUE_LENGTH - 3] + "..."
            parts.append(display_value_str)

        if not parts:
            return None

        # 连接各字段值
        instance_name = ' - '.join(parts)

        # 如果总长度超过限制，进行截断
        if len(instance_name) > MAX_INSTANCE_NAME_LENGTH:
            logger.warning(f'Generated instance name exceeds max length: {instance_name}')
            instance_name = instance_name[:MAX_INSTANCE_NAME_LENGTH - 3] + "..."

        return instance_name


class ModelInstanceGroupManager(models.Manager):

    def get_root_group(self, model_id):
        """获取指定模型的【所有】分组"""
        return self.filter(model_id=model_id, parent=None).first()

    def get_unassigned_group(self, model_id):
        """获取指定模型的【空闲池】分组"""
        root_group = self.get_root_group(model_id)
        return self.filter(model_id=model_id, parent=root_group, label='空闲池').first()

    def get_all_children_ids(self, group_ids) -> set:
        """
        获取指定ID列表的所有子分组ID（递归，广度优先）
        供权限处理器等批量查询使用
        """
        return self._get_all_children_ids(tuple(sorted(str(gid) for gid in group_ids)))

    def clear_children_cache(self):
        """清理子分组缓存"""
        self._get_all_children_ids.cache_clear()

    @functools.lru_cache(maxsize=1024)
    def _get_all_children_ids(self, group_ids) -> set:
        """
        获取指定ID列表的所有子分组ID（递归，广度优先）
        供权限处理器等批量查询使用
        """
        if not group_ids:
            return set()

        # 统一转为集合处理
        if isinstance(group_ids, (str, uuid.UUID)):
            current_ids = {str(group_ids)}
        else:
            current_ids = {str(gid) for gid in group_ids}

        all_children_ids = set()

        while current_ids:
            # 批量查询下一层子节点
            # 注意：values_list 返回的是 UUID 对象或字符串，取决于数据库后端，这里统一转字符串
            next_level_ids = set(
                self.filter(parent_id__in=current_ids)
                .values_list('id', flat=True)
            )
            # 转换为字符串以确保兼容性
            next_level_ids = {str(nid) for nid in next_level_ids}

            # 排除已存在的，防止死循环（如果有环状结构）
            new_ids = next_level_ids - all_children_ids

            if not new_ids:
                break

            all_children_ids.update(new_ids)
            current_ids = new_ids

        return all_children_ids
