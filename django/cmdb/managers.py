"""
CMDB的管理器模块
定义CMDB系统中各模型的自定义管理器，提供跨权限边界的特权方法。
"""

import functools
import uuid
import json
import logging
import time
from django.db.models import Q
from django.db import models

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

    def get_default_field_group(self, model_id: str):
        """
        获取或创建默认字段组
        """
        default_group = self.filter(
            name='basic',
            model_id=model_id
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

    def get_by_model(self, model_id):
        """根据模型ID获取所有字段"""
        return self.filter(model_id=model_id).order_by('order')

    def get_by_model_ordered(self, model_id):
        """根据模型ID获取排序后的字段，按分组和顺序"""
        return self.filter(model_id=model_id).select_related(
            'model_field_group', 'validation_rule', 'ref_model'
        ).order_by('model_field_group__create_time', 'order')

    def check_name_exists(self, model_id, name, exclude_id=None):
        """检查字段名是否已存在（跨权限查询）"""
        qs = self.filter(model_id=model_id, name=name)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        return qs.exists()

    def check_ref_fields_exists(self, model_id):
        """检查是否存在引用到该模型的字段"""
        return self.filter(ref_model_id=model_id).exists()

    def get_ref_fields_for_model(self, model_id):
        """获取引用某模型的所有字段"""
        return self.filter(ref_model_id=model_id).select_related('model')

    def get_fields_by_type(self, model_id, field_type):
        """根据类型获取字段"""
        return self.filter(model_id=model_id, type=field_type)

    def get_password_fields(self, model_id=None):
        """获取密码类型字段"""
        qs = self.filter(type='password')
        if model_id:
            qs = qs.filter(model_id=model_id)
        return qs

    def get_max_order(self, model_id, group_id=None):
        """获取当前最大顺序值"""
        qs = self.filter(model_id=model_id)
        if group_id:
            qs = qs.filter(model_field_group_id=group_id)
        result = qs.aggregate(max_order=models.Max('order'))
        return result['max_order'] or 0


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

    def check_instance_id_exists(self, instance_id):
        """检查指定实例ID是否存在"""
        return self.filter(
            id=instance_id
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

    def filter_groups_by_model(self, model_id, group_ids):
        """筛选给定分组列表中属于指定模型下的可用分组"""
        return self.filter(model_id=model_id, id__in=group_ids).all()

    def get_all_children_ids(self, group_ids, model_id=None) -> set:
        """
        获取指定ID列表的所有子分组ID（递归，广度优先）
        供权限处理器等批量查询使用

        Args:
            group_ids: 分组ID列表
            model_id: 可选，指定模型ID以限定查询范围，提升性能
        """
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
        logger.debug(f'children ids: {all_children_ids}')

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


class RelationDefinitionManager(models.Manager):
    """关系定义管理器"""

    def get_by_name(self, name: str):
        """根据名称获取关系定义"""
        return self.get(name=name)

    def get_for_models(self, source_model_id: str = None, target_model_id: str = None):
        """获取适用于指定模型的关系定义"""
        qs = self.all()
        if source_model_id:
            qs = qs.filter(source_model__id=source_model_id)
        if target_model_id:
            qs = qs.filter(target_model__id=target_model_id)
        return qs


class RelationsManager(models.Manager):
    """
    关系实例管理器。
    提供跨越权限边界的特权方法，用于系统内部调用。
    """

    def check_relation_exists(self, source_instance_id: str, target_instance_id: str, relation_id: str):
        """检查指定关系实例是否存在"""
        return self.filter(
            source_instance_id=source_instance_id,
            target_instance_id=target_instance_id,
            relation_id=relation_id
        ).exists()

    def get_all_relations_for_instance(self, instance_id: str):
        return self.filter(
            Q(source_instance_id=instance_id) | Q(target_instance_id=instance_id)
        ).select_related('source_instance', 'target_instance', 'relation')

    def get_connected_instances(self, instance_id: str, direction: str = 'both'):
        connected_ids = set()

        if direction in ('forward', 'both'):
            forward_ids = self.filter(
                source_instance_id=instance_id
            ).values_list('target_instance_id', flat=True)
            connected_ids.update(str(id) for id in forward_ids)

        if direction in ('reverse', 'both'):
            reverse_ids = self.filter(
                target_instance_id=instance_id
            ).values_list('source_instance_id', flat=True)
            connected_ids.update(str(id) for id in reverse_ids)

        return connected_ids

    def get_topology_edges(self, start_node_ids: list, depth: int, direction: str = 'both'):
        """
        获取拓扑图的边数据（忽略权限）。
        用于构建完整拓扑后再进行节点级权限过滤。

        :param start_node_ids: 起始节点ID列表
        :param depth: 遍历深度
        :param direction: 遍历方向
        :return: 关系查询集
        """
        visited_nodes = set(start_node_ids)
        all_relations = []
        current_nodes = set(start_node_ids)

        for _ in range(depth):
            if not current_nodes:
                break

            q_filter = Q()
            if direction in ('forward', 'both'):
                q_filter |= Q(source_instance_id__in=current_nodes)
            if direction in ('reverse', 'both'):
                q_filter |= Q(target_instance_id__in=current_nodes)

            relations = self.filter(q_filter).select_related(
                'source_instance', 'target_instance', 'relation'
            )

            new_nodes = set()
            for rel in relations:
                all_relations.append(rel)
                source_id = str(rel.source_instance_id)
                target_id = str(rel.target_instance_id)

                if source_id not in visited_nodes:
                    new_nodes.add(source_id)
                if target_id not in visited_nodes:
                    new_nodes.add(target_id)

            visited_nodes.update(new_nodes)
            current_nodes = new_nodes

        return all_relations, visited_nodes
