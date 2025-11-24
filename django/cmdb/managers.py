import functools
import uuid
from django.db import models, transaction


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
