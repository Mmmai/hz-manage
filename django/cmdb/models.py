import json
import uuid
import logging
import functools

from django.db import models
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models import OuterRef, Exists

from .constants import ValidationType
from .resolver import resolve_model_field_id_list, resolve_dynamic_value, resolve_model
from audit.decorators import register_audit
from audit.snapshots import get_dynamic_field_snapshot

logger = logging.getLogger(__name__)


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_group'
)
class ModelGroups(models.Model):
    class Meta:
        db_table = 'model_groups'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True, null=False, blank=False)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    editable = models.BooleanField(default=True, null=False, blank=False)
    verbose_name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    @classmethod
    def get_default_model_group(cls):
        """获取或创建默认模型组"""
        default_group, created = cls.objects.get_or_create(
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

    def delete(self, *args, **kwargs):
        if self.built_in:
            raise PermissionDenied('Built-in model group cannot be deleted')
        if not self.editable:
            raise PermissionDenied('Non-editable model group cannot be deleted')
        with transaction.atomic():
            default_group = self.__class__.get_default_model_group()
            Models.objects.filter(model_group=self).update(model_group=default_group)
            super().delete(*args, **kwargs)


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model',
    field_resolvers={
        'instance_name_template': resolve_model_field_id_list
    }
)
class Models(models.Model):
    class Meta:
        db_table = 'models'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True, null=False, blank=False)
    verbose_name = models.CharField(max_length=50, null=False, blank=False)
    instance_name_template = models.JSONField(default=list, blank=True, null=True)
    model_group = models.ForeignKey('ModelGroups', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    icon = models.CharField(max_length=50, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        # 保存模型
        super().save(*args, **kwargs)

        self.sync_unique_constraint()

    def sync_unique_constraint(self):
        constraint = UniqueConstraint.objects.filter(
            model=self,
            built_in=True,
            description='自动生成的实例名称唯一性约束'
        ).first()

        if self.instance_name_template:
            if constraint:
                # 更新现有约束
                constraint.fields = self.instance_name_template
                constraint.save()
            else:
                # 创建新约束
                UniqueConstraint.objects.create(
                    model=self,
                    fields=self.instance_name_template,
                    built_in=True,
                    validate_null=False,
                    description='自动生成的实例名称唯一性约束',
                    create_user='system',
                    update_user='system'
                )
        else:
            if constraint:
                constraint.delete()


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_field_group'
)
class ModelFieldGroups(models.Model):
    class Meta:
        db_table = 'model_field_groups'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, db_index=True, null=False, blank=False)
    verbose_name = models.CharField(max_length=50, null=False, blank=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True, related_name='field_groups')
    built_in = models.BooleanField(default=False, null=False, blank=False)
    editable = models.BooleanField(default=True, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    @classmethod
    def get_default_field_group(cls, model):
        """获取或创建默认模型组"""
        default_field_group, created = cls.objects.get_or_create(
            name='basic',
            model=model,
            defaults={
                'name': 'basic',
                'verbose_name': '基础配置',
                'model': model,
                'built_in': True,
                'editable': False,
                'description': '默认字段组',
                'create_user': 'system',
                'update_user': 'system'
            }
        )
        return default_field_group


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name', 'field_type', 'type', 'rule'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='validation_rule'
)
class ValidationRules(models.Model):
    """验证规则表"""
    class Meta:
        db_table = 'validation_rules'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True, help_text='规则名称')
    verbose_name = models.CharField(max_length=50, help_text='显示名称')
    field_type = models.CharField(max_length=50, help_text='适配字段类型')
    type = models.CharField(max_length=50, help_text='验证类型')  # regex, range, length 等
    rule = models.TextField(help_text='验证规则', null=True, blank=True)  # 具体的验证规则
    built_in = models.BooleanField(default=False, help_text='是否内置')
    editable = models.BooleanField(default=True, help_text='是否可编辑')
    description = models.TextField(blank=True, null=True, help_text='规则描述')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    # @classmethod
    # def get_enum_dict(cls, rule_id):
    #     @cached_as(ValidationRules, timeout=60 * 60)
    #     def _get_enum_dict(rule_id):
    #         """获取枚举规则字典"""
    #         try:
    #             rule = cls.objects.get(id=rule_id)
    #             if rule.type == ValidationType.ENUM:
    #                 return json.loads(rule.rule)
    #         except (cls.DoesNotExist, json.JSONDecodeError):
    #             pass
    #         return {}
    #     return _get_enum_dict(rule_id)

    @staticmethod
    @functools.lru_cache(maxsize=128)  # maxsize 可根据枚举规则的数量调整
    def get_enum_dict(rule_id):
        logger.debug(
            f"LRU Cache MISS for get_enum_dict(rule_id={rule_id})."
            f"Executing function body. Cache info: {ValidationRules.get_enum_dict.cache_info()}")
        try:
            rule_instance = ValidationRules.objects.get(id=rule_id)
            if rule_instance.type == ValidationType.ENUM and rule_instance.rule:
                parsed_enum_dict = json.loads(rule_instance.rule)
                return parsed_enum_dict
            return {}
        except ValidationRules.DoesNotExist:
            logger.warning(f"ValidationRule with id {rule_id} not found.")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Error decoding enum_dict from DB for rule_id {rule_id}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching enum_dict for rule_id {rule_id}: {e}")
            return {}

    @staticmethod
    def clear_specific_enum_cache(rule_id):
        ValidationRules.get_enum_dict.cache_clear()


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


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name', 'type', 'unit', 'ref_model'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_field'
)
class ModelFields(models.Model):
    class Meta:
        db_table = 'model_fields'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True, related_name='fields')
    model_field_group = models.ForeignKey('ModelFieldGroups', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=50, db_index=True, null=False, blank=False)
    verbose_name = models.CharField(max_length=50, null=False, blank=False)
    type = models.CharField(max_length=50, null=False, blank=False)
    unit = models.CharField(max_length=50, null=True, blank=True)
    ref_model = models.ForeignKey('Models', on_delete=models.SET_NULL, null=True, blank=True, related_name='ref_model')
    built_in = models.BooleanField(default=False, null=False, blank=False)
    required = models.BooleanField(null=False, blank=False)
    editable = models.BooleanField(default=True, null=False, blank=False)
    default = models.TextField(blank=True, null=True)
    validation_rule = models.ForeignKey('ValidationRules', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


class ModelFieldPreference(models.Model):
    class Meta:
        db_table = 'model_field_preference'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
    fields_preferred = models.JSONField(default=list, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


@register_audit(
    snapshot_fields={'id', 'fields', 'validate_null'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='unique_constraint',
    field_resolvers={
        'fields': resolve_model_field_id_list
    }
)
class UniqueConstraint(models.Model):
    class Meta:
        db_table = 'unique_constraint'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
    fields = models.JSONField(default=list, blank=True, null=True)
    validate_null = models.BooleanField(default=False, null=False, blank=False)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


class ModelInstanceManager(models.Manager):
    def get_instance_names_by_models(self, model_ids: list) -> dict:
        if not model_ids:
            return {}

        # 直接使用 self.get_queryset() 或 _base_manager，确保不经过任何外部权限过滤
        instances = self.get_queryset().filter(model_id__in=model_ids).values('id', 'instance_name')

        # 返回一个 {id_str: name_str} 格式的字典
        return {str(inst['id']): inst['instance_name'] for inst in instances}

    def get_instance_names_by_instances(self, instance_ids: list) -> dict:
        if not instance_ids:
            return {}

        # 直接使用 self.get_queryset() 或 _base_manager，确保不经过任何外部权限过滤
        instances = self.get_queryset().filter(id__in=instance_ids).values('id', 'instance_name')

        # 返回一个 {id_str: name_str} 格式的字典
        return {str(inst['id']): inst['instance_name'] for inst in instances}


@register_audit(
    is_field_aware=True,
    dynamic_snapshot_func=get_dynamic_field_snapshot,
    snapshot_fields={'id', 'instance_name', 'input_mode'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_instance',
    dynamic_value_resolver=resolve_dynamic_value,
    restorer='cmdb.restorer.restore_model_instance',
    locker='cmdb.locker.lock_model_instance_for_update'
)
class ModelInstance(models.Model):

    objects = ModelInstanceManager()

    class Meta:
        db_table = 'model_instance'
        managed = True
        app_label = 'cmdb'
        constraints = [
            models.UniqueConstraint(
                fields=['model', 'instance_name'],
                name='unique_model_instance_name'
            )
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
    instance_name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    using_template = models.BooleanField(default=True, null=False, blank=False)
    input_mode = models.CharField(max_length=20, choices=[
        ('manual', '手动录入'),
        ('import', '表格导入'),
        ('discover', '自动发现')
    ], default='manual', db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def generate_name(self, field_values=None):
        """根据模型模板生成实例名称"""
        if not self.model.instance_name_template:
            return None

        # 如果没有提供字段值，则从数据库获取
        if field_values is None:
            field_values = {}
            field_metas = ModelFieldMeta.objects.filter(
                model_instance=self
            ).select_related('model_fields')

            for meta in field_metas:
                field_values[meta.model_fields.name] = meta.data

        from .utils.name_generator import generate_instance_name
        return generate_instance_name(field_values, self.model.instance_name_template)


class ModelFieldMetaManager(models.Manager):

    def check_data_exists(self, data):
        """检查是否存在指定数据的记录"""
        return self.get_queryset().filter(data=data).exists()


class ModelFieldMeta(models.Model):

    objects = ModelFieldMetaManager()

    class Meta:
        db_table = 'model_field_meta'
        managed = True
        app_label = 'cmdb'

    # TODO: 添加实例name字段，用于存储实例名称，作为唯一性校验
    # TODO: 在模型删除时，如果没有删除子实例，保留字段信息等 待修改
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE)
    model_instance = models.ForeignKey('ModelInstance', on_delete=models.CASCADE, related_name='field_values')
    model_fields = models.ForeignKey('ModelFields', on_delete=models.CASCADE)
    data = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


class ModelInstanceGroupManager(models.Manager):
    @transaction.atomic
    def delete_group(self, group, performing_user):
        """
        删除一个分组及其所有子分组，并将无其他分组关联的实例迁移到空闲池。
        """
        if group.built_in:
            raise PermissionDenied(f'Can not delete built-in group "{group.label}"')

        unassigned_group = self.model.get_unassigned_group(group.model)

        # 递归获取所有待删除的子分组
        all_groups_to_delete = [group] + list(group.get_all_children())
        all_group_ids_to_delete = {g.id for g in all_groups_to_delete}
        logger.debug(f"Preparing to delete {len(all_groups_to_delete)} groups, including '{group.label}'.")

        instances_in_deleted_groups = ModelInstance.objects.filter(
            group_relations__group_id__in=all_group_ids_to_delete
        ).distinct()

        # 检查实例是否存在其他关联分组
        other_groups_subquery = ModelInstanceGroupRelation.objects.filter(
            instance_id=OuterRef('pk'),
        ).exclude(
            group_id__in=all_group_ids_to_delete
        )

        instances_to_move_qs = instances_in_deleted_groups.annotate(
            in_other_groups=Exists(other_groups_subquery)
        ).filter(in_other_groups=False)

        instances_to_move_ids = list(instances_to_move_qs.values_list('id', flat=True))
        logger.debug(f"Found {len(instances_to_move_ids)} instances to move to unassigned pool.")

        deleted_relations_count, _ = ModelInstanceGroupRelation.objects.filter(
            group_id__in=all_group_ids_to_delete
        ).delete()
        logger.debug(f"Deleted {deleted_relations_count} existing group relations.")

        # 创建到 空闲池 的关联
        if instances_to_move_ids:
            relations_to_create = [
                ModelInstanceGroupRelation(
                    instance_id=instance_id,
                    group=unassigned_group,
                    create_user=performing_user,
                    update_user=performing_user
                ) for instance_id in instances_to_move_ids
            ]
            ModelInstanceGroupRelation.objects.bulk_create(relations_to_create)
            logger.debug(f"Created {len(relations_to_create)} new relations in unassigned pool.")

        # 删除所有分组对象
        deleted_groups_count, _ = self.get_queryset().filter(id__in=all_group_ids_to_delete).delete()
        logger.debug(f"Successfully deleted {deleted_groups_count} groups from database.")

        self.model.clear_groups_cache(all_groups_to_delete)

        return {
            'deleted_groups_count': deleted_groups_count,
            'moved_instances_count': len(instances_to_move_ids)
        }

    def get_root_group(self, model_id):
        """获取指定模型的根分组"""
        return self.get_queryset().filter(model_id=model_id, parent=None).first()


@register_audit(
    snapshot_fields={'id', 'label', 'path'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_instance_group'
)
class ModelInstanceGroup(models.Model):

    objects = ModelInstanceGroupManager()

    class Meta:
        db_table = 'model_instance_group'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=50, null=False, blank=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, null=False, blank=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=False)
    level = models.IntegerField(default=1, null=False, blank=False)
    path = models.CharField(max_length=200, null=True, blank=True)
    order = models.IntegerField(blank=True, null=True, db_index=True)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def save(self, *args, **kwargs):
        skip_signal = kwargs.pop('_skip_signal', False)
        self.path = self.get_path()

        if skip_signal:
            self._skip_signal = True

        super().save(*args, **kwargs)

        if hasattr(self, '_skip_signal'):
            delattr(self, '_skip_signal')

    def get_path(self):
        if self.parent:
            return f'{self.parent.path}/{self.label}'
        return self.label

    def update_child_path(self):
        """更新子分组的path"""
        children = self.__class__.objects.filter(parent=self)
        for child in children:
            child.path = child.get_path()
            child.save(update_fields=['path', 'update_time'], _skip_signal=True)
            child.update_child_path()

    def get_all_children(self):
        """获取所有子分组"""
        all_children = set()

        def _get_children(group):
            children = self.__class__.objects.filter(parent=group)
            for child in children:
                all_children.add(child)
                _get_children(child)

        _get_children(self)
        return all_children

    @classmethod
    def get_all_children_ids(cls, group_ids) -> set:
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
                cls.objects.filter(parent_id__in=current_ids)
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

    @classmethod
    def get_root_group(cls, model):
        """获取或创建根分组【所有】"""
        if isinstance(model, str):
            model = Models.objects.get(id=model)
        root_group, created = cls.objects.get_or_create(
            model=model,
            parent=None,
            defaults={
                'label': '所有',
                'built_in': True,
                'level': 1,
                'path': '所有',
                'order': 1,
                'create_user': 'system',
                'update_user': 'system'
            }
        )
        return root_group

    @classmethod
    def get_unassigned_group(cls, model):
        """获取或创建【空闲池】分组"""
        root_group = cls.get_root_group(model)
        unassigned_group, created = cls.objects.get_or_create(
            model=model,
            parent=root_group,
            label='空闲池',
            defaults={
                'built_in': True,
                'level': 2,
                'path': '所有/空闲池',
                'order': 1,
                'create_user': 'system',
                'update_user': 'system'
            }
        )
        return unassigned_group

    @classmethod
    def clear_group_cache(cls, group):
        """清除指定分组和空闲池的缓存"""
        unassigned_group = cls.get_unassigned_group(group.model)
        logger.info(f'Clearing instance count cache for group: {group.id}, {unassigned_group.id}')
        cache.delete(f'group_count_{group.id}')
        cache.delete(f'group_count_{unassigned_group.id}')
        logger.info(f'Cache cleared successfully')

    @classmethod
    def clear_groups_cache(cls, groups):
        """批量清除多个分组的缓存"""
        groups_to_clear = set()

        # 收集所有需要清除的分组ID
        for group in groups:
            groups_to_clear.add(group.id)
            parent = group.parent
            while parent:
                groups_to_clear.add(parent.id)
                parent = parent.parent
        logger.info(f'Clearing instance count cache for groups: {groups_to_clear}')

        cache_keys = [f'group_count_{gid}' for gid in groups_to_clear]
        cache.delete_many(cache_keys)
        logger.info(f'Cache cleared successfully')


class ModelInstanceGroupRelation(models.Model):
    """实例与分组的关联关系"""
    class Meta:
        db_table = 'model_instance_group_relation'
        managed = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey('ModelInstance', on_delete=models.CASCADE, related_name='group_relations')
    group = models.ForeignKey('ModelInstanceGroup', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


@register_audit(
    snapshot_fields={'id', 'name', 'source_model', 'target_model', 'topology_type'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    m2m_fields={'source_model', 'target_model'},
    public_name='relation_definition',
    field_resolvers={
        'source_model': resolve_model,
        'target_model': resolve_model
    }
)
class RelationDefinition(models.Model):
    class Meta:
        db_table = 'relation_definition'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, db_index=True, unique=True, null=False, blank=False)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    topology_type = models.CharField(
        max_length=50,
        choices=[
            ('directed', '有向图'),
            ('undirected', '无向图'),
            ('daggered', '有向无环图'),
        ],
        default='daggered',
        null=False,
        blank=False
    )
    forward_verb = models.CharField(max_length=50, null=False, blank=False)
    reverse_verb = models.CharField(max_length=50, null=False, blank=False)
    source_model = models.ManyToManyField(
        'Models',
        blank=True,
        related_name='relation_allowed_source_models'
    )
    target_model = models.ManyToManyField(
        'Models',
        blank=True,
        related_name='relation_allowed_target_models'
    )
    attribute_schema = models.JSONField(default=dict, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


@register_audit(
    snapshot_fields={'id', 'source_instance', 'target_instance', 'relation'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='relation'
)
class Relations(models.Model):
    class Meta:
        db_table = 'relations'
        managed = True
        app_label = 'cmdb'
        unique_together = ('source_instance', 'target_instance', 'relation')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_instance = models.ForeignKey('ModelInstance', related_name='relation_as_source', on_delete=models.CASCADE)
    target_instance = models.ForeignKey('ModelInstance', related_name='relation_as_target', on_delete=models.CASCADE)
    relation = models.ForeignKey('RelationDefinition', on_delete=models.CASCADE)
    target_attributes = models.JSONField(default=dict, blank=True, null=True)
    source_attributes = models.JSONField(default=dict, blank=True, null=True)
    relation_attributes = models.JSONField(default=dict, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


class ZabbixProxy(models.Model):
    class Meta:
        db_table = 'zabbix_proxy'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    ip = models.CharField(max_length=50, null=False, blank=False)
    port = models.IntegerField(default=10051, null=False, blank=False)
    user = models.CharField(default='root', max_length=50, null=False, blank=False)
    password = models.CharField(max_length=50, null=False, blank=False)
    proxy_id = models.CharField(max_length=50, null=False, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ZabbixSyncHost(models.Model):
    class Meta:
        db_table = 'zabbix_sync_host'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.OneToOneField('ModelInstance', on_delete=models.CASCADE)
    host_id = models.IntegerField(null=False, blank=False)
    ip = models.CharField(max_length=50, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    agent_installed = models.BooleanField(default=False)
    installation_error = models.TextField(null=True, blank=True)
    interface_available = models.IntegerField(default=0)
    proxy = models.ForeignKey('ZabbixProxy', on_delete=models.CASCADE, null=True, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class ProxyAssignRule(models.Model):
    class Meta:
        db_table = 'proxy_assign_rule'
        managed = True
        app_label = 'cmdb'

    RULE_TYPES = (
        # 使用优先级从高到低
        ('ip_exclude', 'IP排除式'),
        ('ip_list', 'IP列表'),
        ('ip_cidr', 'IP子网划分式'),
        ('ip_range', 'IP范围'),
        ('ip_regex', 'IP正则式'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    proxy = models.ForeignKey('ZabbixProxy', on_delete=models.CASCADE, null=False, blank=False)
    type = models.CharField(max_length=50, choices=RULE_TYPES, null=False, blank=False)
    rule = models.TextField()
    active = models.BooleanField(default=True, null=False, blank=False)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
