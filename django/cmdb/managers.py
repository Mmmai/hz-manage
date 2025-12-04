import functools
import uuid
import json
import logging
import time
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

    def get_all_fields_for_model(self, model_id):
        fields = self.filter(model_id=model_id).select_related('validation_rule')
        return {f.name: f for f in fields}

    def get_required_field_names(self, model_id):
        return list(self.filter(model_id=model_id, required=True).values_list('name', flat=True))


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

    def check_data_exists(self, data):
        """检查是否存在指定数据的记录"""
        return self.get_queryset().filter(data=data).exists()

    def get_instance_field_values_by_names(self, instance_id, field_names=None):
        queryset = self.filter(model_instance_id=instance_id).select_related('model_fields')
        if field_names:
            queryset = queryset.filter(model_fields__name__in=field_names)
        return {meta.model_fields.name: meta.data for meta in queryset}


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
    def check_instance_name_exists(self, model_id, instance_name):
        """检查指定模型下是否存在同名实例"""
        return self.filter(
            model_id=model_id,
            instance_name=instance_name
        ).exists()

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

    def get_existing_instances_by_names(self, model_id, instance_names: list) -> dict:
        instances = self.filter(model_id=model_id, instance_name__in=instance_names)
        return {inst.instance_name: inst for inst in instances}

    def get_ref_instances_by_names(self, instance_names: list) -> dict:
        instances = self.filter(instance_name__in=instance_names).values('id', 'instance_name')
        return {item['instance_name']: str(item['id']) for item in instances}

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

    def get_all_children_ids(self, group_ids, model_id=None) -> set:
        """
        获取指定ID列表的所有子分组ID（递归，广度优先）
        供权限处理器等批量查询使用

        Args:
            group_ids: 分组ID列表
            model_id: 可选，指定模型ID以限定查询范围，提升性能
        """
        a = time.perf_counter()
        if not group_ids:
            return set()

        # 统一转为集合处理
        if isinstance(group_ids, (str, uuid.UUID)):
            target_ids = {str(group_ids)}
        else:
            target_ids = {str(gid) for gid in group_ids}

        # 一次性查询所有分组的父子关系
        queryset = self.all()
        if model_id:
            queryset = queryset.filter(model_id=model_id)

        all_groups = queryset.values_list('id', 'parent_id')

        b = time.perf_counter()
        logger.debug(f'Fetched all groups for model_id={model_id} in {b - a:.4f} seconds.')

        # 构建父子关系映射: parent_id -> [child_ids]
        parent_to_children = {}
        for group_id, parent_id in all_groups:
            group_id_str = str(group_id)
            parent_id_str = str(parent_id) if parent_id else None
            if parent_id_str:
                if parent_id_str not in parent_to_children:
                    parent_to_children[parent_id_str] = []
                parent_to_children[parent_id_str].append(group_id_str)

        # 在内存中广度优先遍历获取所有子节点
        all_children_ids = set()
        current_ids = target_ids.copy()

        while current_ids:
            next_level_ids = set()
            for parent_id in current_ids:
                children = parent_to_children.get(parent_id, [])
                next_level_ids.update(children)

            # 排除已处理的节点，防止死循环
            new_ids = next_level_ids - all_children_ids
            if not new_ids:
                break

            all_children_ids.update(new_ids)
            current_ids = new_ids

        c = time.perf_counter()
        logger.debug(f'Computed all children IDs for group_ids={group_ids} in {c - b:.4f} seconds.')
        return all_children_ids

    def get_all_children_ids_with_cache(self, group_ids, model_id=None) -> set:
        """
        带缓存版本的获取子分组ID方法
        适用于短时间内多次调用相同参数的场景
        """
        # 将参数转换为可哈希的格式用于缓存
        if isinstance(group_ids, (str, uuid.UUID)):
            cache_key = (str(group_ids), str(model_id) if model_id else None)
        else:
            cache_key = (tuple(sorted(str(gid) for gid in group_ids)), str(model_id) if model_id else None)

        return self._get_all_children_ids_cached(cache_key, model_id)

    @functools.lru_cache(maxsize=256)
    def _get_all_children_ids_cached(self, cache_key, model_id) -> set:
        """内部缓存方法"""
        group_ids = cache_key[0] if isinstance(cache_key[0], tuple) else [cache_key[0]]
        return self.get_all_children_ids(group_ids, model_id)

    def clear_children_cache(self):
        """清理子分组缓存"""
        self._get_all_children_ids_cached.cache_clear()

    # 保留旧方法签名的兼容性，但标记为废弃
    @functools.lru_cache(maxsize=1024)
    def _get_all_children_ids(self, group_ids) -> set:
        """
        [已废弃] 请使用 get_all_children_ids 方法
        保留此方法仅为兼容性考虑
        """
        return self.get_all_children_ids(group_ids)
