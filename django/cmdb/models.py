from django.db import models
from django.db.models import JSONField
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
from cacheops import cached_as
import json
import uuid
import logging
from .constants import ValidationType

logger = logging.getLogger(__name__)


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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

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
            default_group = self.__class__.get_default_group()
            Models.objects.filter(model_group=self).update(model_group=default_group)
            super().delete(*args, **kwargs)


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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

    def save(self, *args, **kwargs):
        # 保存模型
        super().save(*args, **kwargs)

        if self.instance_name_template:
            self.sync_unique_constraint()

    def sync_unique_constraint(self):
        constraint = UniqueConstraint.objects.filter(
            model=self,
            built_in=True,
            description='自动生成的实例名称唯一性约束'
        ).first()

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


class ModelFieldGroups(models.Model):
    class Meta:
        db_table = 'model_field_groups'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, db_index=True, null=False, blank=False)
    verbose_name = models.CharField(max_length=50, null=False, blank=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
    built_in = models.BooleanField(default=False, null=False, blank=False)
    editable = models.BooleanField(default=True, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

    @classmethod
    def get_enum_dict(cls, rule_id):

        @cached_as(ValidationRules, timeout=60 * 60)
        def _get_enum_dict(rule_id):
            """获取枚举规则字典"""
            try:
                rule = cls.objects.get(id=rule_id)
                if rule.type == ValidationType.ENUM:
                    return json.loads(rule.rule)
            except (cls.DoesNotExist, json.JSONDecodeError):
                pass
            return {}

        return _get_enum_dict(rule_id)


class ModelFields(models.Model):
    class Meta:
        db_table = 'model_fields'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


class ModelFieldOrder(models.Model):
    class Meta:
        db_table = 'model_field_order'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey('Models', on_delete=models.CASCADE, db_index=True)
    field_order = models.JSONField(default=list, blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


class ModelInstance(models.Model):
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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


class ModelInstanceGroup(models.Model):
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
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)

    def save(self, *args, **kwargs):
        self._skip_signal = kwargs.pop('skip_signal', getattr(self, '_skip_signal', False))
        super().save(*args, **kwargs)

    def get_path(self):
        if self.parent:
            return f'{self.parent.path}/{self.label}'
        return self.label

    # 弃用该函数，统一由post_save信号触发更新
    def update_child_path(self):
        """更新子分组的path"""
        children = self.__class__.objects.filter(parent=self)
        for child in children:
            child.path = child.get_path()
            child.save()
            child.update_child_path()

    @classmethod
    def get_root_group(cls, model):
        """获取或创建根分组【所有】"""
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
    instance = models.ForeignKey('ModelInstance', on_delete=models.CASCADE)
    group = models.ForeignKey('ModelInstanceGroup', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


class RelationDefinition(models.Model):
    class Meta:
        db_table = 'relation_definition'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, db_index=True, null=False, blank=False)
    type = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')


class Relations(models.Model):
    class Meta:
        db_table = 'relations'
        managed = True
        app_label = 'cmdb'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_instance = models.ForeignKey('ModelInstance', related_name='source_instance', on_delete=models.CASCADE)
    target_instance = models.ForeignKey('ModelInstance', related_name='target_instance', on_delete=models.CASCADE)
    relation = models.ForeignKey('RelationDefinition', on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    create_user = models.CharField(max_length=20, null=False, blank=False)
    update_user = models.CharField(max_length=20, null=False, blank=False)


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
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
