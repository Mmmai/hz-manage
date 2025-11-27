import logging
import inspect
from functools import wraps
from typing import List
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, ValidationError
from audit.context import audit_context

from mapi.models import UserInfo
from permissions.manager import PermissionManager
from permissions.tools import has_password_permission
from audit.snapshots import capture_audit_snapshots
from .constants import FieldType
from .models import *
from .converters import ConverterFactory

logger = logging.getLogger(__name__)


def require_valid_user(func):
    """装饰器：确保传入的 user 参数是有效的 UserInfo 实例。"""
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())
    try:
        user_param_index = param_names.index('user')
    except ValueError:
        raise ValueError(f'Function {func.__name__} must have a "user" parameter')

    param_user = sig.parameters['user']

    @wraps(func)
    def wrapper(*args, **kwargs):
        user = None
        # 获取用户参数

        if param_user.name in kwargs.keys():
            user = kwargs[param_user.name]
        elif user_param_index < len(args):
            user = args[user_param_index]
        # 执行校验
        if not isinstance(user, UserInfo) or not user.username:
            logger.warning(f"Invalid parameter for user validation: {user}")
            raise ValueError('Invalid user received in cmdb services')

        return func(*args, **kwargs)
    return wrapper


class ModelGroupsService:

    @staticmethod
    @require_valid_user
    def delete_model_group(model_group: ModelGroups, user: UserInfo):
        """
        删除模型组
        """
        username = user.username
        if model_group.built_in:
            logger.warning(f"Attempt to delete built-in model group denied: {model_group.name} by {username}")
            raise PermissionDenied({'detail': 'Built-in model group cannot be deleted'})
        if not model_group.editable:
            logger.warning(f"Attempt to delete non-editable model group denied: {model_group.name} by {username}")
            raise PermissionDenied({'detail': 'Non-editable model group cannot be deleted'})

        with transaction.atomic():
            default_group = ModelGroups.objects.get_default_model_group()
            Models.objects.filter(model_group=model_group).update(model_group=default_group)
            model_group.delete()
            logger.info(f"Model group deleted successfully: {model_group.name} by {username}")


class ModelsService:

    @staticmethod
    @require_valid_user
    def create_model(validated_data: dict, user: UserInfo) -> Models:
        """
        创建模型，并自动初始化关联的模型组、字段组、实例组
        """
        username = user.username
        try:
            with transaction.atomic():
                # 没有指定分组时分配到默认组内
                if not validated_data.get('model_group'):
                    validated_data['model_group'] = ModelGroups.objects.get_default_model_group()

                validated_data['create_user'] = username
                validated_data['update_user'] = username
                model = Models.objects.create(**validated_data)
                logger.info(f"Created model: {model.name} by user: {username}")

                # 创建默认字段分组 (basic)
                ModelFieldGroupsService.create_default_field_group(model, user)
                logger.info(f"Created default field group for model: {model.name}")

                # 创建默认实例分组 (root/unassigned)
                ModelInstanceGroupService.create_root_group(model, user)
                ModelInstanceGroupService.create_unassigned_group(model, user)
                logger.info(f"Created initial instance groups for model: {model.name}")

                return model
        except Exception as e:
            logger.error(f"Error creating model and initial groups: {str(e)}")
            raise ValidationError(f"Failed to create model: {str(e)}")

    @staticmethod
    @require_valid_user
    @transaction.atomic
    def delete_model(model: Models, user: UserInfo):
        """
        删除模型
        """
        username = user.username
        if model.built_in:
            logger.warning(f"Attempt to delete built-in model denied: {model.name} by {username}")
            raise PermissionDenied({'detail': 'Built-in model cannot be deleted'})

        # TODO: 校验模型实例
        model.delete()
        logger.info(f"Model deleted successfully: {model.name} by {username}")

    @staticmethod
    def get_model_details(model_data: dict, field_groups_data: list, fields_data: list) -> dict:
        """
        组装模型详情数据，将字段分组及字段配置注入到模型详情中
        """

        # 组装字段到分组
        grouped_fields = {}
        for field in fields_data:
            group_id = field.get('model_field_group')
            grouped_fields.setdefault(str(group_id), []).append(field)

        for group in field_groups_data:
            group['fields'] = grouped_fields.get(group['id'], [])

        return {
            'model': model_data,
            'field_groups': field_groups_data
        }

    @staticmethod
    def enrich_models_list(models_data: list, field_groups_data: list, fields_data: list, instances_qs) -> list:
        """
        为模型列表数据注入含字段配置信息的字段分组数据field_groups
        """
        # 计算实例数量
        counts = instances_qs.values('model').annotate(count=models.Count('id'))
        instance_counts = {str(item['model']): item['count'] for item in counts}

        # 构建映射关系: Group ID -> Fields List
        group_to_fields_map = {group['id']: [] for group in field_groups_data}
        for field in fields_data:
            group_id = str(field.get('model_field_group'))
            if group_id in group_to_fields_map:
                group_to_fields_map[group_id].append(field)

        # 将字段注入分组
        for group in field_groups_data:
            group['fields'] = group_to_fields_map.get(str(group['id']), [])

        # 构建映射关系: Model ID -> Groups List
        model_to_groups_map = {}
        for group in field_groups_data:
            model_id = str(group.get('model'))
            model_to_groups_map.setdefault(model_id, []).append(group)

        # 注入数据
        for model_item in models_data:
            model_id = str(model_item['id'])
            model_item['field_groups'] = model_to_groups_map.get(model_id, [])
            model_item['instance_count'] = instance_counts.get(model_id, 0)

        return models_data


class ModelFieldGroupsService:

    @staticmethod
    @require_valid_user
    def create_default_field_group(model: Models, user: UserInfo) -> ModelFieldGroups:
        """
        为指定模型创建默认字段组
        """
        username = user.username
        data = {
            'name': 'basic',
            'verbose_name': '基础配置',
            'model': model,
            'built_in': True,
            'editable': False,
            'description': '默认字段组',
            'create_user': username,
            'update_user': username
        }
        field_group = ModelFieldGroups.objects.create(**data)
        logger.info(f"Created default field group for model: {model.name} by user: {username}")
        return field_group

    @staticmethod
    @require_valid_user
    @transaction.atomic
    def delete_field_group(field_group: ModelFieldGroups, user: UserInfo):
        """
        删除字段组
        """
        username = user.username
        if field_group.built_in:
            logger.warning(f"Attempt to delete built-in field group denied: {field_group.name} by {username}")
            raise PermissionDenied({'detail': 'Built-in field group cannot be deleted'})
        if not field_group.editable:
            logger.warning(f"Attempt to delete non-editable field group denied: {field_group.name} by {username}")
            raise PermissionDenied({'detail': 'Non-editable field group cannot be deleted'})

        default_group = ModelFieldGroups.objects.get_default_field_group(field_group.model)
        ModelFields.objects.filter(model_field_group=field_group).update(
            model_field_group=default_group,
            update_user=username
        )
        field_group.delete()
        logger.info(f"Field group deleted successfully: {field_group.name} by {username}")


class ModelFieldsService:

    @classmethod
    @require_valid_user
    def delete_field(cls, instance: ModelFields, user: UserInfo):
        """
        删除字段
        """
        username = user.username
        if instance.built_in:
            logger.warning(f"Attempt to delete built-in field denied: {instance.name} by {username}")
            raise PermissionDenied({'detail': 'Built-in field cannot be deleted'})
        if not instance.editable:
            logger.warning(f"Attempt to delete non-editable field denied: {instance.name} by {username}")
            raise PermissionDenied({'detail': 'Non-editable field cannot be deleted'})

        with transaction.atomic():
            # 同步唯一约束配置
            cls._sync_unique_constraints_on_field_deletion(instance, username)

            # 同步字段偏好设置
            cls._sync_field_preferences_on_deletion(instance, username)

            instance.delete()
            logger.info(f"Field deleted successfully: {instance.name} by {username}")

    @staticmethod
    def _sync_unique_constraints_on_field_deletion(instance: ModelFields, username: str):
        """
        在删除字段时，同步更新唯一约束配置
        """
        model = instance.model
        field_id_str = str(instance.id)
        constraints = UniqueConstraint.objects.filter(
            model=model,
            fields__contains=field_id_str
        )

        updated_count = 0
        for constraint in constraints:
            if field_id_str in constraint.fields:
                constraint.fields.remove(instance.id)
                constraint.save()
                updated_count += 1
        if updated_count > 0:
            logger.info(f"Updated {updated_count} unique constraints by removing field {instance.name} by {username}")

    @staticmethod
    def _sync_field_preferences_on_deletion(instance: ModelFields, username: str):
        """
        在删除字段时，移除字段偏好设置中的相关配置
        """
        model = instance.model
        field_id_str = str(instance.id)
        preferences = ModelFieldPreference.objects.filter(
            model=model,
            fields_preferred__contains=field_id_str
        )

        updated_count = 0
        for preference in preferences:
            if field_id_str in preference.fields_preferred:
                preference.fields_preferred.remove(instance.id)
                preference.save()
                updated_count += 1
        if updated_count > 0:
            logger.info(f"Updated {updated_count} field preferences by removing field {instance.name} by {username}")


class UniqueConstraintService:

    @staticmethod
    @require_valid_user
    @transaction.atomic
    def sync_from_instance_name_template(model: Models, instance_name_template: List[str], user: UserInfo, audit_ctx):
        """
        根据模型的实例名称模板同步唯一约束配置
        """
        username = user.username

        unique_constraint = UniqueConstraint.objects.get_sync_constraint_for_model(model)

        with audit_context(**audit_ctx):
            if not instance_name_template:
                # 删除已存在的唯一约束
                if unique_constraint:
                    unique_constraint.delete()
                    logger.info(f"Deleted unique constraint for model: {model.name} as no template is defined")
                return

            if not unique_constraint:
                # 创建唯一约束
                UniqueConstraint.objects.create(
                    model=model,
                    fields=instance_name_template,
                    built_in=True,
                    description='自动生成的实例名称唯一性约束',
                    create_user=username,
                    update_user=username
                )
                logger.info(f"Created unique constraint for model: {model.name} with fields: {instance_name_template}")
            else:
                # 更新唯一约束字段
                unique_constraint.fields = instance_name_template
                unique_constraint.update_user = username
                unique_constraint.save()
                logger.info(f"Updated unique constraint for model: {model.name} with fields: {instance_name_template}")


class ModelFieldPreferenceService:

    @staticmethod
    @require_valid_user
    def create_default_user_preference(model: Models, user: UserInfo):
        """
        在模型变更时，同步更新字段偏好设置，移除已不存在的字段
        """
        username = user.username
        pm = PermissionManager(user)
        current_field_ids = list(
            pm.get_queryset(ModelFields)
            .filter(model=model)
            .order_by('model_field_group__create_time', 'order')
            .values_list('id', flat=True)[:8]
        )

        current_field_str_ids = [str(fid) for fid in current_field_ids]

        data = {
            'model': model,
            'create_user': username,
            'update_user': username,
            'fields_preferred': current_field_str_ids
        }

        preference = ModelFieldPreference.objects.create(**data)
        return preference

    @staticmethod
    @require_valid_user
    def clear_invalidate_fields(preference: ModelFieldPreference, user: UserInfo):
        """
        更新字段偏好设置
        """
        username = user.username
        pm = PermissionManager(user)
        valid_field_ids = set(
            pm.get_queryset(ModelFields)
            .filter(model=preference.model)
            .values_list('id', flat=True)
        )
        valid_field_str_ids = {str(fid) for fid in valid_field_ids}
        current_field_str_ids = set(preference.fields_preferred)
        invalid_field_str_ids = current_field_str_ids - valid_field_str_ids

        if invalid_field_str_ids:
            updated_fields = [fid for fid in preference.fields_preferred if fid not in invalid_field_str_ids]
            preference.fields_preferred = updated_fields
            preference.update_user = username
            preference.save()
            logger.info(
                f"Cleared invalid fields from preference for user {preference.create_user} on model: {preference.model.name}")

    @staticmethod
    def delete_user_preference(preference: ModelFieldPreference):
        """
        删除字段偏好设置
        """
        preference.delete()
        logger.info(
            f"Field preference for user {preference.create_user} deleted successfully for model: {preference.model.name}")


class ModelInstanceService:

    @staticmethod
    def get_write_context(model: Models, fields_data: dict, user: UserInfo) -> dict:
        """
        为写入操作（创建/更新）准备序列化器上下文。
        此方法根据传入的原始字段数据构建必要的上下文，如 ref_instances。
        """
        pm = PermissionManager(user)
        context = {}

        ref_field_defs = pm.get_queryset(ModelFields).filter(
            model=model,
            type=FieldType.MODEL_REF,
            name__in=fields_data.keys()
        )

        ref_instance_ids = []
        for field_def in ref_field_defs:
            value = fields_data.get(field_def.name)
            if value:
                ref_instance_ids.append(value)

        ref_instances_map = {}
        if ref_instance_ids:
            ref_instances_map = ModelInstance.objects.get_instance_names_by_instance_ids(
                [str(rid) for rid in ref_instance_ids])
        context['ref_instances'] = ref_instances_map

        logger.debug(f"Prepared write context for ModelInstance: {context}")
        return context

    @staticmethod
    @require_valid_user
    def get_read_context(instances, user: UserInfo) -> dict:
        """
        准备序列化上下文
        """
        pm = PermissionManager(user)
        if not instances:
            return {}

        if isinstance(instances, (list, QuerySet, set, tuple)):
            instance_ids = [inst.id for inst in instances]
        elif isinstance(instances, ModelInstance):
            instance_ids = [instances.id]
        else:
            raise ValueError(f"Invalid type for instances parameter {type(instances)}")

        context = {}

        # 获取字段值
        field_meta_map = {}
        meta_qs = pm.get_queryset(ModelFieldMeta).filter(
            model_instance_id__in=instance_ids
        ).select_related('model_fields', 'model_fields__validation_rule')

        for meta in meta_qs:
            field_meta_map.setdefault(str(meta.model_instance_id), []).append(meta)
        context['field_meta'] = field_meta_map

        # 获取实例分组
        instance_group_map = {}
        group_relations = pm.get_queryset(ModelInstanceGroupRelation).filter(
            instance_id__in=instance_ids
        ).select_related('group').values('instance_id', 'group_id', 'group__path')

        for rel in group_relations:
            instance_group_map.setdefault(str(rel['instance_id']), []).append({
                'group_id': str(rel['group_id']),
                'group_path': rel['group__path']
            })
        context['instance_group'] = instance_group_map

        # 获取引用实例的名称
        ref_model_ids = set()
        # enum_rule_ids = set()
        for meta in meta_qs:
            if meta.model_fields.type == FieldType.MODEL_REF and meta.data:
                ref_model_ids.add(meta.data)
            # elif meta.model_fields.type == FieldType.ENUM and meta.data:
            #     enum_rule_ids.add(meta.model_fields.validation_rule.id)

        ref_instances_map = {}
        if ref_model_ids:
            ref_model_str_ids = [str(mid) for mid in ref_model_ids]
            ref_instances_map = ModelInstance.objects.get_instance_names_by_instance_ids(ref_model_str_ids)
        context['ref_instances'] = ref_instances_map

        logger.debug(f'''Prepared read context for ModelInstance: {context}''')
        return context

    @classmethod
    @require_valid_user
    @transaction.atomic
    def create_instance(cls, validated_data: dict, user: UserInfo, instance_group_ids: list = None) -> ModelInstance:
        """
        创建模型实例及其关联的字段元数据和分组关系
        """
        username = user.username
        fields_data = validated_data.pop('fields', {})

        # 创建实例
        validated_data['create_user'] = username
        validated_data['update_user'] = username

        instance_name = cls.prepare_instance_name(
            validated_data['model'],
            validated_data,
            is_create=True
        )
        if instance_name:
            validated_data['instance_name'] = instance_name

        instance = ModelInstance.objects.create(**validated_data)

        # 处理字段值
        cls._save_field_values(instance, fields_data, username)

        # 处理分组关联，如果未指定分组，加入默认空闲池
        if not instance_group_ids:
            unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(str(instance.model_id))
            if unassigned_group:
                instance_group_ids = [unassigned_group.id]

        if instance_group_ids:
            relations = [
                ModelInstanceGroupRelation(
                    instance=instance,
                    group_id=gid,
                    create_user=username,
                    update_user=username
                ) for gid in instance_group_ids
            ]
            ModelInstanceGroupRelation.objects.bulk_create(relations)

        logger.info(f"Model instance created: {instance.instance_name} ({instance.id}) by {username}")
        return instance

    @classmethod
    @require_valid_user
    @transaction.atomic
    def update_instance(cls, instance: ModelInstance, validated_data: dict, user: UserInfo) -> ModelInstance:
        """
        更新模型实例及其关联的字段元数据
        """
        username = user.username
        fields_data = validated_data.pop('fields', None)

        # 更新实例
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update_user = username
        instance_name = cls.prepare_instance_name(
            instance.model,
            validated_data,
            is_create=False
        )
        if instance_name:
            instance.instance_name = instance_name
        instance.save()

        # 更新字段值
        if fields_data is not None:
            cls._save_field_values(instance, fields_data, username)

        logger.info(f"Model instance updated: {instance.instance_name} ({instance.id}) by {username}")
        return instance

    @staticmethod
    def _save_field_values(instance: ModelInstance, fields_data: dict, username: str, from_excel: bool = False):
        """
        保存或更新实例的字段值
        :param from_excel: 是否来自 Excel 导入，默认Excel导入的密码字段为明文，需要双重加密
        """
        if not fields_data:
            return

        pm = PermissionManager(username)

        model = instance.model
        model_fields_map = {
            f.name: f for f in pm.get_queryset(ModelFields).filter(model=model)
        }

        extra_vars = {
            'plain': from_excel
        }

        for field_name, value in fields_data.items():
            field_def = model_fields_map.get(field_name)
            if not field_def:
                # 忽略未知字段/用户不具备权限的字段
                continue
            if from_excel:
                extra_vars['from_excel'] = True
                extra_vars['plain'] = True
            if field_def.type == FieldType.ENUM and field_def.validation_rule:
                enum_dict = ValidationRules.get_enum_dict(field_def.validation_rule.id)
                extra_vars['enum_dict'] = enum_dict
            elif field_def.type == FieldType.MODEL_REF:
                extra_vars['instance_map'] = ModelInstance.objects.get_instance_names_by_models(
                    [str(field_def.ref_model.id)])

            converter = ConverterFactory.get_converter(field_def.type)
            storage_value = converter.to_internal(value, **extra_vars)

            ModelFieldMeta.objects.update_or_create(
                model_instance=instance,
                model_fields=field_def,
                defaults={
                    'model': model,
                    'data': storage_value,
                    'update_user': username,
                    'create_user': username  # 如果是 create
                }
            )

    @classmethod
    @require_valid_user
    def bulk_update_instances(cls, instances_qs: QuerySet, validated_fields: dict, user: UserInfo, using_template: bool = False) -> int:
        """
        批量更新实例
        """
        if not instances_qs.exists():
            return 0

        model = instances_qs.first().model
        username = user.username

        updated_count = 0

        with transaction.atomic():
            instances = list(instances_qs.select_for_update())

            # 记录审计快照
            with capture_audit_snapshots(instances):
                for instance in instances:
                    cls._save_field_values(instance, validated_fields, username)

                    instance.update_user = username
                    if using_template is not None:
                        instance.using_template = using_template

                    should_regenerate_name = using_template if using_template is not None else instance.using_template

                    if should_regenerate_name and instance.model.instance_name_template:
                        new_name = instance.generate_name()
                        if new_name:
                            instance.instance_name = new_name

                    instance.save()
                    updated_count += 1

        logger.info(f"Bulk updated {updated_count} instances for model {model.name} by {username}")
        return updated_count

    @staticmethod
    def _convert_value_for_constraint(field_config, value, from_excel=False, ref_instances=None):
        if value is None:
            return None
        extra_vars = {}
        if from_excel:
            extra_vars['from_excel'] = True
            extra_vars['plain'] = True
        if field_config.type == FieldType.ENUM and field_config.validation_rule:
            enum_dict = ValidationRules.get_enum_dict(field_config.validation_rule.id)
            extra_vars['enum_dict'] = enum_dict
        elif field_config.type == FieldType.MODEL_REF and ref_instances is not None:
            extra_vars['instance_map'] = ref_instances
        logger.debug(
            f"Converting value for constraint: field={field_config.name}, type={field_config.type} value={value}, extra_vars={extra_vars}")
        logger.debug(f'Extra vars: {extra_vars}')
        converter = ConverterFactory.get_converter(field_config.type)
        return converter.to_internal(value, **extra_vars)

    @classmethod
    def validate_unique_constraints(cls, model: Models, fields_data: dict, instance: ModelInstance,
                                    ref_instances: dict = None, from_excel: bool = False):
        constraints = UniqueConstraint.objects.get_constraints_for_model(model)
        if not constraints.exists():
            return

        all_field_ids = set()
        for constraint in constraints:
            all_field_ids.update(constraint.fields or [])

        field_map = ModelFields.objects.get_fields_map(str(model.id), all_field_ids)
        instance_values = {}
        if instance:
            instance_values = ModelFieldMeta.objects.get_instance_field_values(str(instance.id), all_field_ids)

        for constraint in constraints:
            constraint_fields = constraint.fields or []
            normalized_values = {}
            has_null = False

            for field_id in constraint_fields:
                field_config = field_map.get(str(field_id))
                if not field_config:
                    continue

                field_name = field_config.name
                raw_value = fields_data.get(field_name)
                value_from_instance = False

                if raw_value is None and instance_values:
                    raw_value = instance_values.get(str(field_id))
                    value_from_instance = raw_value is not None

                if value_from_instance:
                    storage_value = raw_value
                else:
                    storage_value = cls._convert_value_for_constraint(
                        field_config,
                        raw_value,
                        from_excel=from_excel,
                        ref_instances=ref_instances
                    )

                normalized_values[field_name] = storage_value
                if storage_value in (None, ''):
                    has_null = True

            if not normalized_values:
                continue

            if has_null and not constraint.validate_null:
                logger.debug(
                    "Skipping constraint %s due to null values and validate_null=False",
                    constraint.id
                )
                continue

            duplicate_ids = ModelInstance.objects.check_uniqueness(
                model,
                normalized_values,
                instance_to_exclude=instance
            )

            if duplicate_ids:
                field_values_str = ", ".join(f"{k}={v}" for k, v in normalized_values.items())
                raise ValidationError({
                    'unique_constraint': f'Unique constraint violation: {field_values_str}'
                })

        logger.debug("All unique constraints validated for model %s", model.name)

    @staticmethod
    def prepare_instance_name(model: Models, fields_data: dict, instance: ModelInstance = None, is_create: bool = False) -> str:
        """
        准备实例名称。如果提供了名称则校验唯一性，否则尝试生成并校验。
        :param model: 模型对象
        :param fields_data: 待更新或创建的字段数据
        :param instance: 待更新的实例对象 (更新时提供)
        :param is_create: 是否为创建操作
        :return: 验证通过的实例名称，或在无需变更时返回 None
        """
        instance_name = fields_data.get('instance_name')
        using_template = fields_data.get('using_template', instance.using_template if instance else True)

        # 如果不使用模板且未提供名称，则在创建时报错
        if not using_template and not instance_name and is_create:
            raise ValidationError({"instance_name": "Instance name is required when not using a template."})

        # 如果使用模板，尝试生成名称
        if using_template and model.instance_name_template:
            # 准备用于生成名称的所有字段值
            all_field_values = {}
            if instance and not is_create:
                # 更新时，获取数据库中已有的值
                db_values = ModelFieldMeta.objects.filter(
                    model_instance=instance
                ).select_related('model_fields').values('model_fields__name', 'data')
                all_field_values = {item['model_fields__name']: item['data'] for item in db_values}

            # 使用传入的新值覆盖旧值
            all_field_values.update(fields_data.get('fields', {}))

            # 调用管理器方法生成名称
            generated_name = ModelInstance.objects.generate_instance_name(model, all_field_values)

            if generated_name:
                instance_name = generated_name
            elif is_create:
                # 仅在创建且无法生成名称时报错
                fields_str = ', '.join(f.name for f in ModelFields.objects.filter(id__in=model.instance_name_template))
                if not fields_str:
                    raise ValidationError({
                        "instance_name": f"Cannot generate instance name: all template fields [{fields_str}] are empty."
                    })

        # 如果最终有实例名称，则校验唯一性
        if instance_name:
            name_exists_query = ModelInstance.objects.filter(model=model, instance_name=instance_name)
            if instance and not is_create:
                name_exists_query = name_exists_query.exclude(id=instance.id)

            if name_exists_query.exists():
                raise ValidationError({
                    "instance_name": f"Instance name '{instance_name}' already exists in model '{model.name}'."
                })
            return instance_name

        return None


class ModelInstanceGroupService:

    @staticmethod
    @require_valid_user
    def create_root_group(model: Models, user: UserInfo) -> ModelInstanceGroup:
        """
        为指定模型创建根分组
        """
        username = user.username
        root_group = ModelInstanceGroup.objects.get_root_group(str(model.id))
        if not root_group:
            data = {
                'label': '所有',
                'built_in': True,
                'level': 1,
                'path': '所有',
                'order': 1,
                'create_user': username,
                'update_user': username
            }
            root_group = ModelInstanceGroup.objects.create(model=model, parent=None, **data)
            logger.info(f"Created root instance group for model: {model.name} by user: {username}")
        return root_group

    @staticmethod
    @require_valid_user
    def create_unassigned_group(model: Models, user: UserInfo) -> ModelInstanceGroup:
        """
        为指定模型创建空闲池分组
        """
        username = user.username
        unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(str(model.id))
        if not unassigned_group:
            root_group = cls.create_root_group(model, user)
            data = {
                'label': '空闲池',
                'built_in': True,
                'level': 2,
                'path': '所有/空闲池',
                'order': 1,
                'create_user': username,
                'update_user': username
            }
            unassigned_group = ModelInstanceGroup.objects.create(model=model, parent=root_group, **data)
            logger.info(f"Created unassigned instance group for model: {model.name} by user: {username}")
        return unassigned_group

    @staticmethod
    @require_valid_user
    @transaction.atomic
    def delete_group(group, user: UserInfo) -> dict:
        """
        删除一个分组及其所有子分组，并将无其他分组关联的实例迁移到空闲池。
        """
        username = user.username
        if group.built_in:
            raise PermissionDenied(f'Can not delete built-in group "{group.label}"')

        unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(str(group.model.id))

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
                    create_user=username,
                    update_user=username
                ) for instance_id in instances_to_move_ids
            ]
            ModelInstanceGroupRelation.objects.bulk_create(relations_to_create)
            logger.debug(f"Created {len(relations_to_create)} new relations in unassigned pool.")

        # 删除所有分组对象
        deleted_groups_count, _ = ModelInstanceGroup.objects.filter(id__in=all_group_ids_to_delete).delete()
        logger.debug(f"Successfully deleted {deleted_groups_count} groups from database.")

        # ModelInstanceGroup.clear_groups_cache(all_groups_to_delete)

        return {
            'deleted_groups_count': deleted_groups_count,
            'moved_instances_count': len(instances_to_move_ids)
        }

    @classmethod
    @require_valid_user
    def build_model_groups_tree(cls, user: UserInfo) -> list:
        """
        构建跨模型的分组树结构（用于左侧导航栏等）。
        """
        username = user.username
        pm = PermissionManager(user)

        # 获取用户可见的模型和分组
        visible_model_groups = pm.get_queryset(ModelGroups).prefetch_related('models').order_by('create_time')
        visible_models_qs = pm.get_queryset(Models)
        visible_models_ids = set(visible_models_qs.values_list('id', flat=True))

        # 获取所有可见的分组节点
        all_visible_instance_groups = pm.get_queryset(ModelInstanceGroup).select_related('model', 'parent')

        # 获取所有可见的实例
        visible_instances_qs = pm.get_queryset(ModelInstance)

        # 构建上下文
        context = cls._prepare_group_tree_context(all_visible_instance_groups, visible_instances_qs)

        # 组装树结构
        tree_structure = []
        for model_group in visible_model_groups:
            models_in_group_data = []
            models_in_group = [m for m in model_group.models.all() if m.id in visible_models_ids]

            if not models_in_group:
                continue

            for model in models_in_group:
                root_instance_groups = context['children_map'].get(None, [])
                model_root_instance_groups = [g for g in root_instance_groups if g.model_id == model.id]

                if model_root_instance_groups:
                    models_in_group_data.append({
                        'model': model,
                        'groups': model_root_instance_groups
                    })

            if models_in_group_data:
                tree_structure.append({
                    'model_group': model_group,
                    'models': models_in_group_data
                })

        return tree_structure, context

    @classmethod
    @require_valid_user
    def get_single_model_group_tree(cls, model_id: str, user: UserInfo):
        """
        获取单个模型的分组树（用于管理页面，包含计数）。
        """
        username = user.username
        pm = PermissionManager(user)

        # 获取骨架树节点
        visible_groups_qs = pm.get_queryset(ModelInstanceGroup).filter(model_id=model_id)
        skeleton_nodes = cls._get_skeleton_tree_nodes(visible_groups_qs, model_id)

        if not skeleton_nodes:
            return None, {}

        visible_instances_qs = pm.get_queryset(ModelInstance).filter(model_id=model_id)

        context = cls._prepare_group_tree_context(skeleton_nodes, visible_instances_qs)

        absolute_root_node = next((n for n in skeleton_nodes if n.parent_id is None), None)
        if not absolute_root_node:
            absolute_root_node = ModelInstanceGroup.objects.get_root_group(model_id)

        return absolute_root_node, context

    @staticmethod
    def _build_children_map(nodes) -> dict:
        """
        构建父子节点映射关系
        :param nodes: 节点列表或QuerySet
        """
        children_map = {}
        for node in nodes:
            parent_id = str(node.parent_id) if node.parent_id else None
            children_map.setdefault(parent_id, []).append(node)
        return children_map

    @classmethod
    def _calculate_instance_counts(cls, nodes, visible_instances_qs: QuerySet) -> dict:
        """
        计算每个分组（包含子分组）下的实例数量
        :param nodes: 涉及的分组节点列表
        :param visible_instances_qs: 经过权限过滤的实例 QuerySet
        """
        all_group_ids = {group.id for group in nodes}
        descendant_map = {}

        # 构建后代映射
        for group in nodes:
            descendants = cls._get_all_descendants(group, nodes)
            descendant_ids = {g.id for g in descendants}
            descendant_map[group.id] = descendant_ids | {group.id}
            all_group_ids.update(descendant_ids)

        # 批量查询关联关系
        relations = ModelInstanceGroupRelation.objects.filter(
            group_id__in=all_group_ids,
            instance__in=visible_instances_qs
        ).values('group_id', 'instance_id').distinct()

        # 内存聚合计算
        instance_counts = {}
        for group in nodes:
            group_and_descendant_ids = descendant_map[group.id]
            unique_instances = {
                r['instance_id'] for r in relations if r['group_id'] in group_and_descendant_ids
            }
            instance_counts[group.id] = len(unique_instances)

        return instance_counts

    @classmethod
    def _prepare_group_tree_context(cls, nodes, visible_instances_qs: QuerySet) -> dict:
        """
        准备管理树所需的上下文，聚合 children_map 和 instance_counts。
        """
        return {
            'children_map': cls._build_children_map(nodes),
            'instance_counts': cls._calculate_instance_counts(nodes, visible_instances_qs)
        }

    @classmethod
    def _get_all_descendants(cls, group, all_groups):
        """递归获取后代"""
        descendants = []
        children = [g for g in all_groups if g.parent_id == group.id]
        for child in children:
            descendants.append(child)
            descendants.extend(cls._get_all_descendants(child, all_groups))
        return descendants

    @staticmethod
    def _get_all_ancestors(groups_qs):
        """获取所有祖先节点"""
        ancestors = set()
        groups_with_parents = groups_qs.select_related('parent')
        queue = list(groups_with_parents)
        processed_ids = {g.id for g in queue}

        while queue:
            group = queue.pop(0)
            parent = group.parent
            if parent and parent.id not in processed_ids:
                ancestors.add(parent)
                processed_ids.add(parent.id)
                try:
                    full_parent = ModelInstanceGroup.objects.select_related('parent').get(id=parent.id)
                    queue.append(full_parent)
                except ModelInstanceGroup.DoesNotExist:
                    continue
        return list(ancestors)

    @staticmethod
    @require_valid_user
    @transaction.atomic
    def update_group_position(group: ModelInstanceGroup, target_id: str, position: str, user: UserInfo):
        """
        更新分组位置（排序/移动）。
        """
        username = user.username
        pm = PermissionManager(user)

        # 检查是否修改根节点
        if group.label == '所有' and group.built_in:
            raise PermissionDenied({'detail': 'Cannot modify root group "所有"'})

        # 检查对父节点的权限（如果涉及移动）
        if group.parent:
            has_parent_perm = pm.get_queryset(ModelInstanceGroup).filter(id=group.parent.id).exists()
            if not has_parent_perm:
                raise PermissionDenied({'detail': 'No permission to modify position under the current parent group'})

        # TODO: 处理排序和移动逻辑

    @classmethod
    def _get_skeleton_tree_nodes(cls, visible_groups_qs, model_id: str):
        """
        通用逻辑：构建骨架树节点集合。
        输入用户可见的节点 QuerySet，返回包含祖先路径的完整节点列表。
        """
        if not visible_groups_qs.exists():
            # 如果无权，尝试返回根节点作为空容器
            try:
                root = ModelInstanceGroup.objects.get_root_group(model_id)
                return [root]
            except ModelInstanceGroup.DoesNotExist:
                return []

        # 获取可见节点 + 祖先节点
        visible_ids = set(visible_groups_qs.values_list('id', flat=True))
        ancestors = cls._get_all_ancestors(visible_groups_qs)
        ancestor_ids = {g.id for g in ancestors}

        total_ids = visible_ids | ancestor_ids
        return list(ModelInstanceGroup.objects.filter(id__in=total_ids).order_by('level', 'order'))

    @classmethod
    @require_valid_user
    def get_tree(cls, model: Models, user: UserInfo):
        """
        获取指定模型的实例分组树结构（用于拓扑图或选择器，包含具体实例信息）。
        """
        username = user.username
        pm = PermissionManager(user)

        # 获取骨架树节点
        visible_groups_qs = pm.get_queryset(ModelInstanceGroup).filter(model=model)
        all_nodes = cls._get_skeleton_tree_nodes(visible_groups_qs, str(model.id))

        if not all_nodes:
            return []

        # 准备详细上下文
        visible_instances_qs = pm.get_queryset(ModelInstance).filter(model=model)
        context = cls._build_tree_context(all_nodes, visible_instances_qs)

        # 提取根节点
        roots = [n for n in all_nodes if n.parent_id is None]

        # 序列化数据
        return roots, context

    @classmethod
    def _build_tree_context(cls, nodes, visible_instances_qs: QuerySet) -> dict:
        """
        构建详细树所需的上下文
        """
        context = {}

        context['children_map'] = cls._build_children_map(nodes)

        visible_instance_ids = set(visible_instances_qs.values_list('id', flat=True))
        node_ids = {node.id for node in nodes}

        relations = ModelInstanceGroupRelation.objects.filter(
            group_id__in=node_ids,
            instance_id__in=visible_instance_ids
        ).values('group_id', 'instance_id')

        relation_map = {}
        relevant_instance_ids = set()
        for r in relations:
            gid = str(r['group_id'])
            iid = str(r['instance_id'])
            relation_map.setdefault(gid, []).append(iid)
            relevant_instance_ids.add(iid)
        context['relation_map'] = relation_map

        instance_map = {}
        if relevant_instance_ids:
            insts = ModelInstance.objects.filter(id__in=relevant_instance_ids).values('id', 'instance_name')
            instance_map = {str(i['id']): i['instance_name'] for i in insts}
        context['instance_map'] = instance_map

        return context
