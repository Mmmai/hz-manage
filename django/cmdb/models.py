import json
import uuid
import logging
import functools

from django.db import models
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models import OuterRef, Exists

from .managers import *
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

    objects: ModelGroupsManager = ModelGroupsManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.built_in:
            raise PermissionDenied('Cannot delete a built-in model group.')
        if not self.editable:
            raise PermissionDenied('Cannot delete a non-editable model group.')
        super().delete(*args, **kwargs)


@register_audit(
    # 外键返回的具体字段
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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.built_in:
            raise PermissionDenied('Cannot delete a built-in model.')
        super().delete(*args, **kwargs)


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_field_group'
)
class ModelFieldGroups(models.Model):
    objects = ModelFieldGroupsManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.built_in:
            raise PermissionDenied('Cannot delete a built-in model field group.')
        if not self.editable:
            raise PermissionDenied('Cannot delete a non-editable model field group.')
        super().delete(*args, **kwargs)


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

    @staticmethod
    @functools.lru_cache(maxsize=128)  # maxsize 可根据枚举规则的数量调整
    def get_enum_dict(rule_id):
        # logger.debug(
        #     f"LRU Cache MISS for get_enum_dict(rule_id={rule_id})."
        #     f"Executing function body. Cache info: {ValidationRules.get_enum_dict.cache_info()}")
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


@register_audit(
    snapshot_fields={'id', 'name', 'verbose_name', 'type', 'unit', 'ref_model'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_field'
)
class ModelFields(models.Model):
    objects: ModelFieldsManager = ModelFieldsManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


@register_audit(
    snapshot_fields={'id', 'model', 'fields', 'validate_null'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='unique_constraint',
    field_resolvers={
        'fields': resolve_model_field_id_list
    }
)
class UniqueConstraint(models.Model):
    objects: UniqueConstraintManager = UniqueConstraintManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)

    def delete(self, *args, **kwargs):
        # 防止越过视图层调用意外删除
        if self.built_in:
            raise PermissionDenied('Cannot delete a built-in unique constraint.')
        super().delete(*args, **kwargs)


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

    objects: ModelInstanceManager = ModelInstanceManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
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


class ModelFieldMeta(models.Model):

    objects: ModelFieldMetaManager = ModelFieldMetaManager()

    class Meta:
        db_table = 'model_field_meta'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE)
    model_instance = models.ForeignKey('ModelInstance', on_delete=models.CASCADE, related_name='field_values')
    model_fields = models.ForeignKey('ModelFields', on_delete=models.CASCADE)
    data = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=True, blank=True)
    update_user = models.CharField(max_length=20, null=True, blank=True)


@register_audit(
    snapshot_fields={'id', 'label', 'path'},
    ignore_fields={'update_time', 'create_time', 'create_user', 'update_user'},
    public_name='model_instance_group'
)
class ModelInstanceGroup(models.Model):

    objects: ModelInstanceGroupManager = ModelInstanceGroupManager()

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
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
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

    # @classmethod
    # def clear_group_cache(cls, group):
    #     """清除指定分组和空闲池的缓存"""
    #     unassigned_group = cls.objects.get_unassigned_group(str(group.model.id))
    #     logger.info(f'Clearing instance count cache for group: {group.id}, {unassigned_group.id}')
    #     cache.delete(f'group_count_{group.id}')
    #     cache.delete(f'group_count_{unassigned_group.id}')
    #     logger.info(f'Cache cleared successfully')

    # @classmethod
    # def clear_groups_cache(cls, groups):
    #     """批量清除多个分组的缓存"""
    #     groups_to_clear = set()

    #     # 收集所有需要清除的分组ID
    #     for group in groups:
    #         groups_to_clear.add(group.id)
    #         parent = group.parent
    #         while parent:
    #             groups_to_clear.add(parent.id)
    #             parent = parent.parent
    #     logger.info(f'Clearing instance count cache for groups: {groups_to_clear}')

    #     cache_keys = [f'group_count_{gid}' for gid in groups_to_clear]
    #     cache.delete_many(cache_keys)
    #     logger.info(f'Cache cleared successfully')


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
