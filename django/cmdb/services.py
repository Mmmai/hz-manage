"""
CMDB内部服务模块
抽象CMDB应用内部使用的服务类和函数，封装核心业务逻辑，供视图集和对外服务调用。
"""

import re
import logging
import inspect
import Levenshtein
import time
import networkx as nx

from dataclasses import dataclass
from functools import wraps
from typing import List
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.db import connection
from django.db.models import Exists, OuterRef

from audit.context import audit_context
from mapi.models import UserInfo
from mapi.system_user import SYSTEM_USER
from access.manager import PermissionManager
from access.tools import has_password_permission
from audit.snapshots import capture_audit_snapshots

from .validators import FieldValidator
from .constants import FieldType
from .utils import password_handler
from .utils.uuid_tools import UUIDFormatter
from .models import *
from .converters import ConverterFactory


logger = logging.getLogger(__name__)

# 模型通用的处理方法


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
        root_group = ModelInstanceGroup.objects.get_root_group(str(model.id))
        unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(str(model.id))
        unassigned_group.delete()
        root_group.delete()
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
    @transaction.atomic
    def create_field(cls, validated_data, user):
        """
        创建模型字段

        Args:
            validated_data: 已验证的数据
            user: 当前用户

        Returns:
            ModelFields: 创建的字段实例
        """
        model = validated_data.get('model')
        name = validated_data.get('name')
        field_type = validated_data.get('type')

        # 设置默认值
        if 'order' not in validated_data or validated_data['order'] is None:
            validated_data['order'] = cls._get_next_order(
                model.id,
                validated_data.get('model_field_group')
            )

        # 设置默认分组
        if not validated_data.get('model_field_group'):
            default_group = ModelFieldGroups.objects.get_default_field_group(str(model.id))
            if default_group:
                validated_data['model_field_group'] = default_group

        # 创建字段
        username = user.username
        field = ModelFields.objects.create(
            **validated_data,
            create_user=username,
            update_user=username
        )

        logger.info(f"Field '{field.name}' created for model '{model.name}' by {username}")
        return field

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

    @classmethod
    def _get_next_order(cls, model_id, group_id=None):
        """获取下一个顺序值"""
        return ModelFields.objects.get_max_order(model_id, group_id) + 1


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
        context['field_configs'] = ModelFields.objects.get_all_fields_for_model(str(model.id))

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

        model_id = None
        if isinstance(instances, (list, QuerySet, set, tuple)):
            instance_ids = [inst.id for inst in instances]
            model_id = str(instances[0].model_id) if instances else None
        elif isinstance(instances, ModelInstance):
            instance_ids = [instances.id]
            model_id = str(instances.model_id)
        else:
            raise ValueError(f"Invalid type for instances parameter {type(instances)}")

        context = {}

        if model_id is None:
            return context

        # 预加载字段配置
        fields_qs = pm.get_queryset(ModelFields).filter(model_id=model_id).select_related('validation_rule')
        fields_by_id = {str(f.id): f for f in fields_qs}

        # 获取字段元数据
        meta_raw = list(pm.get_queryset(ModelFieldMeta).filter(
            model_instance_id__in=instance_ids
        ).values(
            'id',
            'model_instance_id',
            'model_fields_id',
            'data'
        ))

        # 结构: {instance_id: [{'id': ..., 'field': ModelFields, 'data': ...}, ...]}
        field_meta_map = {}
        ref_model_ids = set()

        for row in meta_raw:
            inst_id = str(row['model_instance_id'])
            field_id = str(row['model_fields_id'])
            data = row['data']

            field_obj = fields_by_id.get(field_id)
            if not field_obj:
                continue

            # 构建轻量级数据结构
            meta_info = {
                'id': row['id'],
                'field': field_obj,  # 直接引用预加载的字段对象
                'data': data
            }
            field_meta_map.setdefault(inst_id, []).append(meta_info)

            # 收集引用实例 ID
            if field_obj.type == FieldType.MODEL_REF and data:
                ref_model_ids.add(data)

        context['field_meta'] = field_meta_map
        context['fields_by_id'] = fields_by_id

        # 获取实例分组
        instance_group_map = {}
        group_relations = pm.get_queryset(ModelInstanceGroupRelation).filter(
            instance_id__in=instance_ids
        ).select_related('group').distinct().values('instance_id', 'group_id', 'group__path')

        for rel in group_relations:
            instance_group_map.setdefault(str(rel['instance_id']), []).append({
                'group_id': str(rel['group_id']),
                'group_path': rel['group__path']
            })
        context['instance_group'] = instance_group_map

        # 获取引用实例名称
        ref_instances_map = {}
        if ref_model_ids:
            ref_model_str_ids = [str(mid) for mid in ref_model_ids]
            ref_instances_map = ModelInstance.objects.get_instance_names_by_instance_ids(ref_model_str_ids)
        context['ref_instances'] = ref_instances_map

        # 构建枚举缓存
        enum_cache = {}
        for field in fields_by_id.values():
            if field.type == FieldType.ENUM and field.validation_rule_id:
                enum_cache[str(field.id)] = ValidationRules.get_enum_dict(
                    field.validation_rule_id
                )
        context['enum_cache'] = enum_cache

        # 确认查看密码权限
        if has_password_permission(user):
            context['has_password_permission'] = True

        # logger.debug(f'''Prepared read context for ModelInstance: {context}''')
        return context

    @staticmethod
    def build_import_context(model: Models, all_instances_data: list):
        """
        构建批量导入的上下文信息。
        使用 Manager 中的特权方法获取数据，避免权限过滤。
        """
        context = {
            'from_excel': True,
            'field_configs': {},
            'required_fields': [],
            'enum_maps': {},
            'ref_instances_by_name': {},
            'existing_instances': {},
            'unassigned_group': None
        }

        context['field_configs'] = ModelFields.objects.get_all_fields_for_model(str(model.id))
        context['required_fields'] = ModelFields.objects.get_required_field_names(str(model.id))

        for field_name, field_config in context['field_configs'].items():
            if field_config.type == FieldType.ENUM and field_config.validation_rule:
                enum_dict = ValidationRules.get_enum_dict(field_config.validation_rule.id)
                # 构建双向映射
                context['enum_maps'][field_name] = {
                    'key_to_label': enum_dict,
                    'label_to_key': {v: k for k, v in enum_dict.items()}
                }

        ref_field_names = [
            name for name, cfg in context['field_configs'].items()
            if cfg.type == FieldType.MODEL_REF
        ]
        all_ref_values = set()
        for instance_data in all_instances_data:
            fields = instance_data.get('fields', {})
            for field_name in ref_field_names:
                value = fields.get(field_name)
                if value:
                    all_ref_values.add(value)

        if all_ref_values:
            context['ref_instances_by_name'] = ModelInstance.objects.get_ref_instances_by_names(list(all_ref_values))

        existing_names = [d.get('instance_name') for d in all_instances_data if d.get('instance_name')]
        logger.debug(f'Existing names to check for import: {existing_names}')
        if existing_names:
            context['existing_instances'] = ModelInstance.objects.get_existing_instances_by_names(
                str(model.id), existing_names
            )
            logger.debug(f'Existing instances found for import: {list(context["existing_instances"].keys())}')

        context['unassigned_group'] = ModelInstanceGroup.objects.get_unassigned_group(str(model.id))

        logger.info(
            f"Built import context for model {model.name}: "
            f"fields={len(context['field_configs'])}, "
            f"refs={len(context['ref_instances_by_name'])}, "
            f"existing={len(context['existing_instances'])}"
        )

        return context

    @staticmethod
    def validate_fields(model: Models, fields_data: dict, field_configs: dict):
        for field, value in fields_data.items():
            field_config = field_configs.get(field)
            logger.debug(f'Validating {field} {value} with {field_config}')
            if field_config:
                FieldValidator.validate(value, field_config)

    @staticmethod
    @require_valid_user
    def validate_import_fields(model: Models, fields_data: dict, user: UserInfo):
        _missed_value = object()
        pm = PermissionManager(user)
        all_fields = ModelFields.objects.get_all_fields_for_model(str(model.id))
        allowed_fields = set(
            pm.get_queryset(ModelFields)
            .filter(model=model)
            .values_list('name', flat=True)
        )

        for field in all_fields:
            data = fields_data.get(field.name, _missed_value)

            # 提供了未授权的字段
            if data is not _missed_value and field.name not in allowed_fields:
                logger.warning(f"User {user.username} attempted to import unauthorized field: {field.name}")
                # 设置为空，后续使用默认逻辑
                data = _missed_value

            # 字段取值，传入值 > default > None
            if data is _missed_value:
                value = field.default if field.default else None
            else:
                value = data

            if field.required and (value is None or value == ""):
                raise ValidationError(f'Received empty value for required field: {field.name}')

    @staticmethod
    def validate_fields_for_import_update(model: Models, input_fields: dict, user: UserInfo, import_context: dict):
        input_fields = input_fields or {}
        field_configs = import_context.get('field_configs', {}) or {}

        pm = PermissionManager(user)
        allowed = set(
            pm.get_queryset(ModelFields)
            .filter(model=model)
            .values_list('name', flat=True)
        )

        # 校验用户是否试图导入无权限字段
        perm_errors = {}
        for name in input_fields.keys():
            if name not in field_configs:
                perm_errors[name] = 'Unknown field'
            elif name not in allowed:
                perm_errors[name] = 'No permission to set this field'
        if perm_errors:
            raise ValidationError({'fields': perm_errors})

    @staticmethod
    def prepare_fields_for_import_creation(model: Models, input_fields: dict, user: UserInfo, import_context: dict) -> dict:
        input_fields = input_fields or {}
        field_configs = import_context.get('field_configs', {}) or {}
        required_fields = import_context.get('required_fields', []) or []

        pm = PermissionManager(user)
        allowed = pm.get_queryset(ModelFields).filter(model=model).values_list('name', flat=True)

        # 校验用户是否试图导入无权限字段
        perm_errors = {}
        for name in input_fields.keys():
            if name not in field_configs:
                perm_errors[name] = 'Unknown field'
            elif name not in allowed:
                perm_errors[name] = 'No permission to set this field'
        if perm_errors:
            raise ValidationError({'fields': perm_errors})

        # 补全未给出字段的最终写入值（default/None）
        filled = {}
        for name, cfg in field_configs.items():
            if name in input_fields:
                filled[name] = input_fields.get(name)
                continue

            dv = getattr(cfg, 'default_value', None)
            if dv in (None, ''):
                filled[name] = None
            else:
                filled[name] = dv

        # 校验必填
        req_errors = {}
        for name in required_fields:
            val = filled.get(name, None)
            # 0 / False 视为有效；None/'' 视为缺失
            if val is None or val == '':
                if name not in allowed:
                    req_errors[name] = 'Required field missing and the current user has no permission and no default value'
                else:
                    req_errors[name] = 'Required field missing'
        if req_errors:
            raise ValidationError({'fields': req_errors})

        return filled

    @staticmethod
    def preprocess_import_fields(fields_data: dict, import_context: dict) -> dict:
        """
        预处理导入的字段数据：将 Excel 中的显示值转换为存储值。
        枚举的 label -> key，引用的 instance_name -> id
        """
        processed = {}
        fields_not_provided = []
        required_fields = import_context.get('required_fields', [])
        field_configs = import_context.get('field_configs', {})
        enum_maps = import_context.get('enum_maps', {})
        ref_by_name = import_context.get('ref_instances_by_name', {})

        for field_name, raw_value in fields_data.items():
            if raw_value in (None, ''):
                fields_not_provided.append(field_name)
                continue

            field_config = field_configs.get(field_name)
            if not field_config:
                fields_not_provided.append(field_name)
                continue

            processed_value = raw_value

            # 枚举：label -> key
            if field_config.type == FieldType.ENUM:
                enum_info = enum_maps.get(field_name, {})
                label_to_key = enum_info.get('label_to_key', {})
                if str(raw_value) in label_to_key:
                    processed_value = label_to_key[str(raw_value)]

            # 模型引用：instance_name -> id
            elif field_config.type == FieldType.MODEL_REF:
                ref_id = ref_by_name.get(str(raw_value))
                if ref_id:
                    processed_value = ref_id

            processed[field_name] = processed_value

        return processed

    @classmethod
    @require_valid_user
    @transaction.atomic
    def create_instance(cls, validated_data: dict, user: UserInfo, instance_group_ids: list = None, **kwargs) -> ModelInstance:
        """
        创建模型实例及其关联的字段元数据和分组关系
        """
        username = user.username

        from_excel = kwargs.get('from_excel', False)

        fields_data = validated_data.pop('fields', {})

        # 创建实例
        validated_data['create_user'] = username
        validated_data['update_user'] = username

        prepare_data = {**validated_data, 'fields': fields_data}
        instance_name = cls.prepare_instance_name(
            validated_data['model'],
            prepare_data,
            is_create=True
        )
        if instance_name:
            validated_data['instance_name'] = instance_name

        instance = ModelInstance.objects.create(**validated_data)
        model_id = str(instance.model_id)
        pm = PermissionManager(user)

        # 处理字段值
        if fields_data:
            cls._save_field_values(instance, fields_data, username, from_excel=from_excel)

        # 处理实例分组关系
        valid_instance_group_ids = ModelInstanceGroupService.validate_group_ids(model_id, instance_group_ids, user)

        if valid_instance_group_ids:
            relations = [
                ModelInstanceGroupRelation(
                    instance=instance,
                    group_id=gid,
                    create_user=username,
                    update_user=username
                ) for gid in valid_instance_group_ids
            ]
            ModelInstanceGroupRelation.objects.bulk_create(relations)

        logger.info(f"Model instance created: {instance.instance_name} ({instance.id}) by {username}")
        return instance

    @classmethod
    @require_valid_user
    @transaction.atomic
    def update_instance(cls, instance: ModelInstance, validated_data: dict, user: UserInfo, **kwargs) -> ModelInstance:
        """
        更新模型实例及其关联的字段元数据
        """
        username = user.username

        from_excel = kwargs.get('from_excel', False)
        fields_data = validated_data.pop('fields', {})

        # 更新实例
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update_user = username

        prepare_data = {**validated_data, 'fields': fields_data}
        instance_name = cls.prepare_instance_name(
            instance.model,
            prepare_data,
            instance=instance,
            is_create=False
        )
        if instance_name:
            instance.instance_name = instance_name
        instance.save()

        # 更新字段值
        if fields_data:
            cls._save_field_values(instance, fields_data, username, from_excel=from_excel)

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

            # logger.debug(f'Converting value for field {field_name} with value {value} type {type(value)}')
            # logger.debug(f'Extra vars for conversion: {extra_vars}')
            converter = ConverterFactory.get_converter(field_def.type)
            storage_value = converter.to_internal(value, **extra_vars)

            ModelFieldMeta.objects.update_or_create(
                model_instance=instance,
                model_fields=field_def,
                defaults={
                    'model': model,
                    'data': storage_value,
                    'update_user': username,
                    'create_user': username  # 默认更新时重置创建用户，meta的用户信息不重要
                }
            )

    @staticmethod
    def backfill_field_values(instance: ModelInstance, fields_data: dict, from_excel: bool = False):
        """
        导入并【创建】实例时以系统用户补全未提供字段，调用前必须完成校验
        """
        if not fields_data:
            return

        model = instance.model
        # 不经权限过滤，直接取字段定义
        model_fields_map = {
            f.name: f for f in ModelFields.objects.filter(model=model, name__in=list(fields_data.keys()))
        }

        extra_vars = {'plain': from_excel}

        for field_name, value in fields_data.items():
            field_def = model_fields_map.get(field_name)
            if not field_def:
                continue

            if from_excel:
                extra_vars['from_excel'] = True
                extra_vars['plain'] = True

            if field_def.type == FieldType.ENUM and field_def.validation_rule:
                extra_vars['enum_dict'] = ValidationRules.get_enum_dict(field_def.validation_rule.id)
            elif field_def.type == FieldType.MODEL_REF and field_def.ref_model_id:
                extra_vars['instance_map'] = ModelInstance.objects.get_instance_names_by_models(
                    [str(field_def.ref_model.id)]
                )

            converter = ConverterFactory.get_converter(field_def.type)
            storage_value = converter.to_internal(value, **extra_vars)

            ModelFieldMeta.objects.update_or_create(
                model_instance=instance,
                model_fields=field_def,
                defaults={
                    'model': model,
                    'data': storage_value,
                    'update_user': SYSTEM_USER.username,
                    'create_user': SYSTEM_USER.username
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
            for instance in instances:
                with capture_audit_snapshots(instance):
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
            logger.debug(f"Validating instance name uniqueness: {instance_name} for model {model.name}")
            name_exists_query = ModelInstance.objects.filter(model=model, instance_name=instance_name)
            if instance and not is_create:
                name_exists_query = name_exists_query.exclude(id=str(instance.id))

            if name_exists_query.exists():
                raise ValidationError({
                    "instance_name": f"Instance name '{instance_name}' already exists in model '{model.name}'."
                })
            return instance_name

        return None

    @classmethod
    def export_instances_data(cls, model: Models, instances_qs, fields_qs, user: UserInfo, restricted_field_names: list) -> dict:
        """
        导出实例数据，返回格式与导入模板一致。

        :param model: 模型对象
        :param instances_qs: 实例查询集
        :param fields_qs: 字段查询集
        :param user: 用户对象
        :param restricted_field_names: 限制导出的字段名列表
        :return: {'fields': [...], 'instances_data': [...], 'enum_data': {...}, 'ref_data': {...}}
        """

        pm = PermissionManager(user)

        if restricted_field_names:
            fields_qs = fields_qs.filter(name__in=restricted_field_names)

        fields = list(
            fields_qs.select_related(
                'validation_rule', 'model_field_group', 'ref_model'
            ).order_by('model_field_group__create_time', 'order')
        )

        if not fields:
            return {'fields': [], 'instances_data': [], 'enum_data': {}, 'ref_data': {}}

        instance_ids = list(instances_qs.values_list('id', flat=True))
        field_meta_map = {}
        meta_qs = pm.get_queryset(ModelFieldMeta).filter(
            model_instance_id__in=instance_ids
        ).select_related('model_fields', 'model_fields__validation_rule')

        for meta in meta_qs:
            field_meta_map.setdefault(str(meta.model_instance_id), {})[meta.model_fields.name] = meta.data

        enum_data = {}  # {field_name: {key: label}}
        ref_data = {}   # {field_name: {instance_id: instance_name}}
        ref_model_ids = set()

        for field in fields:
            if field.type == FieldType.ENUM and field.validation_rule:
                enum_dict = ValidationRules.get_enum_dict(field.validation_rule.id)
                enum_data[field.name] = enum_dict
            elif field.type == FieldType.MODEL_REF and field.ref_model:
                ref_model_ids.add(str(field.ref_model.id))

        if ref_model_ids:
            ref_instances = ModelInstance.objects.filter(
                model_id__in=ref_model_ids
            ).values('id', 'instance_name', 'model_id')

            # 按字段组织引用数据
            ref_by_model = {}
            for inst in ref_instances:
                model_id = str(inst['model_id'])
                ref_by_model.setdefault(model_id, {})[str(inst['id'])] = inst['instance_name']

            for field in fields:
                if field.type == FieldType.MODEL_REF and field.ref_model:
                    ref_data[field.name] = ref_by_model.get(str(field.ref_model.id), {})

        instances_data = []
        for instance in instances_qs:
            instance_id = str(instance.id)
            field_values = field_meta_map.get(instance_id, {})

            # 转换字段值为显示格式
            converted_fields = {}
            for field in fields:
                raw_value = field_values.get(field.name)

                if raw_value is None:
                    converted_fields[field.name] = None
                    continue

                if field.type == FieldType.ENUM:
                    # 枚举：key -> label
                    enum_dict = enum_data.get(field.name, {})
                    converted_fields[field.name] = enum_dict.get(str(raw_value), raw_value)
                elif field.type == FieldType.MODEL_REF:
                    # 引用：id -> instance_name
                    ref_dict = ref_data.get(field.name, {})
                    converted_fields[field.name] = ref_dict.get(str(raw_value), raw_value)
                elif field.type == FieldType.PASSWORD:
                    # 密码：解密
                    try:
                        logger.debug(f"Decrypting password field {field.name} for instance {instance.instance_name}")
                        logger.debug(f"Raw encrypted value: {raw_value}")
                        converted_fields[field.name] = password_handler.decrypt_to_plain(raw_value)
                        logger.debug(f"Decrypted password value: {converted_fields[field.name]}")
                    except Exception:
                        converted_fields[field.name] = ''
                elif field.type == FieldType.BOOLEAN:
                    # 布尔：转换为 TRUE/FALSE
                    converted_fields[field.name] = 'TRUE' if raw_value in (True, 'true', 'True', '1', 1) else 'FALSE'
                else:
                    converted_fields[field.name] = raw_value

            instances_data.append({
                'instance_name': instance.instance_name,
                'fields': converted_fields
            })

        logger.info(f"Exported {len(instances_data)} instances for model {model.name}")

        return {
            'fields': fields,
            'instances_data': instances_data,
            'enum_data': enum_data,
            'ref_data': ref_data
        }


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

    @classmethod
    @require_valid_user
    def create_unassigned_group(cls, model: Models, user: UserInfo) -> ModelInstanceGroup:
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
    def delete_group(group: ModelInstanceGroup, user: UserInfo) -> dict:
        """
        删除一个分组及其所有子分组，并将无其他分组关联的实例迁移到空闲池。
        """
        username = user.username
        model_id = str(group.model.id)
        if group.built_in:
            raise PermissionDenied(f'Can not delete built-in group "{group.label}"')

        unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(model_id)

        # 递归获取所有待删除的子分组
        children_ids = ModelInstanceGroup.objects.get_all_children_ids(group.id, model_id)
        children_ids.add(str(group.id))
        logger.debug(f"Preparing to delete {len(children_ids)} groups, including '{group.label}'.")

        instances_in_deleted_groups = ModelInstance.objects.filter(
            group_relations__group_id__in=children_ids
        ).distinct()

        # 检查实例是否存在其他关联分组
        other_groups_subquery = ModelInstanceGroupRelation.objects.filter(
            instance_id=OuterRef('pk'),
        ).exclude(
            group_id__in=children_ids
        )

        instances_to_move_qs = instances_in_deleted_groups.annotate(
            in_other_groups=Exists(other_groups_subquery)
        ).filter(in_other_groups=False)

        instances_to_move_ids = list(instances_to_move_qs.values_list('id', flat=True))
        logger.debug(f"Found {len(instances_to_move_ids)} instances to move to unassigned pool.")

        deleted_relations_count, _ = ModelInstanceGroupRelation.objects.filter(
            group_id__in=children_ids
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
        deleted_groups_count, _ = ModelInstanceGroup.objects.filter(id__in=children_ids).delete()
        logger.debug(f"Successfully deleted {deleted_groups_count} groups from database.")

        # ModelInstanceGroup.clear_groups_cache(all_groups_to_delete)

        return {
            'deleted_groups_count': deleted_groups_count,
            'moved_instances_count': len(instances_to_move_ids)
        }

    @classmethod
    @require_valid_user
    def validate_group_ids(cls, model_id: str, group_ids: list, user: UserInfo) -> tuple:
        """
        校验并规范化实例分组 ID 列表

        规则:
        1. 未提交分组 -> 分配到空闲池
        2. 仅提交根分组 -> 转换为空闲池
        3. 提交多个分组时移除根分组和空闲池（除非仅剩空闲池）
        4. 过滤无权限和不属于当前模型的分组
        5. 过滤后无有效分组 -> 分配到空闲池

        Args:
            model_id: 模型 ID
            group_ids: 原始分组 ID 列表
            user: 用户信息

        Returns:
            tuple: (valid_group_ids: list, validation_info: dict)
                - valid_group_ids: 校验后的有效分组 ID 列表
        """
        pm = PermissionManager(user)

        # 获取特殊分组
        root_group = ModelInstanceGroup.objects.get_root_group(model_id)
        unassigned_group = ModelInstanceGroup.objects.get_unassigned_group(model_id)

        if not root_group or not unassigned_group:
            raise ValidationError({'groups': f'Model {model_id} is missing required root or unassigned group'})

        root_group_id = str(root_group.id)
        unassigned_group_id = str(unassigned_group.id)

        # 未提交分组 -> 空闲池
        if not group_ids:
            return [unassigned_group_id]

        # 转换为字符串集合
        original_group_ids = set(str(gid) for gid in group_ids)
        working_group_ids = original_group_ids.copy()

        # 移除根分组
        if root_group_id in working_group_ids:
            working_group_ids.discard(root_group_id)

        # 如果有多个分组，移除空闲池
        if len(working_group_ids) > 1 and unassigned_group_id in working_group_ids:
            working_group_ids.discard(unassigned_group_id)

        # 过滤无效分组（不属于当前模型或用户无权限）
        if working_group_ids:
            # 获取属于当前模型的分组
            valid_model_groups = set(
                str(gid) for gid in ModelInstanceGroup.objects.filter_groups_by_model(
                    model_id, list(working_group_ids)
                ).values_list('id', flat=True)
            )

            # 获取用户有权限的分组
            visible_groups = set(
                str(gid) for gid in pm.get_queryset(ModelInstanceGroup).filter(
                    model_id=model_id,
                    id__in=working_group_ids
                ).values_list('id', flat=True)
            )

            # 找出无效的分组
            # invalid_model_groups = working_group_ids - valid_model_groups
            # invalid_permission_groups = (working_group_ids & valid_model_groups) - visible_groups

            # 保留有效分组
            working_group_ids = working_group_ids & valid_model_groups & visible_groups

        # 无有效分组 -> 空闲池
        if not working_group_ids:
            return [unassigned_group_id]

        return list(working_group_ids)

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


class ModelFieldMetaSearchService:
    """
    ModelFieldMeta 全文检索服务
    使用 django-mysql 的 Match 函数实现 MySQL FULLTEXT 搜索
    """

    # MySQL ngram 解析器默认 token 大小
    NGRAM_TOKEN_SIZE = 2
    # 默认最大返回结果数
    MAX_RESULTS = 5000
    RE_CASE_SENSITIVE = 'c'
    RE_CASE_INSENSITIVE = 'i'
    COLLATE_CASE_SENSITIVE = 'utf8mb4_bin'
    COLLATE_CASE_INSENSITIVE = 'utf8mb4_general_ci'

    @classmethod
    def _get_regexp_flag(cls, case_sensitive: bool) -> str:
        """
        获取正则表达式标志
        """
        return cls.RE_CASE_SENSITIVE if case_sensitive else cls.RE_CASE_INSENSITIVE

    @classmethod
    def _get_collation(cls, case_sensitive: bool) -> str:
        """
        获取字符集排序规则
        """
        return cls.COLLATE_CASE_SENSITIVE if case_sensitive else cls.COLLATE_CASE_INSENSITIVE

    @classmethod
    @require_valid_user
    def search(cls, query: str, user: UserInfo, model_ids: list = None, limit: int = 100, threshold: float = 0.0, regexp: bool = False, case_sensitive: bool = False, search_mode: str = 'boolean', quick: bool = False) -> dict:
        """
        全文检索 ModelFieldMeta

        Args:
            query: 搜索关键词
            user: 用户信息
            model_ids: 限定搜索的模型ID列表
            limit: 返回结果数量限制
            threshold: 相似度阈值（FULLTEXT relevance score）
            regexp: 是否启用正则表达式搜索
            case_sensitive: 是否区分大小写
            search_mode: 搜索模式
                - 'natural': 自然语言模式
                - 'boolean': 布尔模式（支持 +, -, *, "" 等操作符）
                - 'expansion': 查询扩展模式

        Returns:
            搜索结果字典
        """
        if not query or not query.strip():
            return {'results': [], 'total': 0, 'query': query}

        if len(query.strip()) < cls.NGRAM_TOKEN_SIZE:
            logger.warning(f'Query "{query}" is shorter than ngram token size {cls.NGRAM_TOKEN_SIZE}. Skipping search.')
            # return {'results': [], 'total': 0, 'query': query}

        query = query.strip()
        pm = PermissionManager(user)

        if regexp:
            try:
                re.compile(query)
            except re.error as e:
                logger.warning(f'Invalid regular expression "{query}": {e}. Skipping search.')
                return {'results': [], 'total': 0, 'query': query, 'error': f'Invalid regular expression: {str(e)}'}

        # 加载模型列表
        models_qs = pm.get_queryset(Models)
        if model_ids:
            models_qs = models_qs.filter(id__in=model_ids)
        models_map = {str(m.id): m for m in models_qs}

        logger.debug(f'Searching ModelFieldMeta for query="{query}" in models: {list(models_map.keys())}')
        if not models_map:
            logger.debug('No models found for the given model IDs or user permissions.')
            return {'results': [], 'total': 0, 'query': query}

        # 获取字段配置（排除密码字段）
        fields_qs = pm.get_queryset(ModelFields).filter(
            model_id__in=models_map.keys()
        ).exclude(
            type=FieldType.PASSWORD
        ).select_related('validation_rule')

        fields_by_id = {str(f.id): f for f in fields_qs}

        if not fields_by_id and not quick:
            return {'results': [], 'total': 0, 'query': query}

        # 加载枚举和引用映射
        enum_cache, ref_instance_cache = cls._build_conversion_cache(fields_qs)

        if regexp:
            search_variants = {query}
        else:
            # 构建搜索变体
            search_variants = cls._build_search_variants(
                query,
                enum_cache,
                ref_instance_cache,
                case_sensitive=case_sensitive
            )
        logger.debug(f'Search variants generated: {list(search_variants)[:10]}')

        # 获取候选实例列表
        instance_ids = list(pm.get_queryset(ModelInstance).filter(
            model_id__in=models_map.keys()
        ).values_list('id', flat=True))

        if not instance_ids:
            return {'results': [], 'total': 0, 'query': query}

        # 搜索实例唯一标识
        instance_matches = cls._search_instance_names(
            query=query,
            search_variants=search_variants,
            instance_ids=instance_ids,
            models_map=models_map,
            regexp=regexp,
            case_sensitive=case_sensitive
        )

        # 搜索字段值，快速搜索时不匹配字段值
        if fields_by_id and not quick:
            if regexp:
                meta_results = cls._execute_field_regexp_search(
                    pattern=query,
                    case_sensitive=case_sensitive,
                    instance_ids=instance_ids,
                    field_ids=list(fields_by_id.keys())
                )
            else:
                meta_results = cls._execute_field_fulltext_search(
                    query=query,
                    search_variants=search_variants,
                    instance_ids=instance_ids,
                    field_ids=list(fields_by_id.keys())
                )

            # 合并字段匹配结果
            cls._merge_field_matches(
                instance_matches=instance_matches,
                meta_results=meta_results,
                fields_by_id=fields_by_id,
                enum_cache=enum_cache,
                ref_instance_cache=ref_instance_cache,
                search_variants=search_variants,
                threshold=threshold,
                regexp=regexp
            )
            logger.debug(f'Found {len(meta_results)} matching ModelFieldMeta entries.')

        # 构建最终结果
        results = cls._build_results(
            instance_matches=instance_matches,
            models_map=models_map
        )

        total = len(results)
        results = results[:limit]
        logger.debug(f'Returning {len(results)} results out of {total} total.')
        return {
            'results': results,
            'total': total,
            'query': query,
            'search_mode': search_mode,
            'variants_used': list(search_variants)[:10]  # 返回部分变体用于调试
        }

    @classmethod
    def _search_instance_names(cls, query: str, search_variants: set, instance_ids: list, models_map: dict, regexp: bool = False, case_sensitive: bool = False) -> dict:
        """
        搜索 ModelInstance.instance_name
        返回初始的 instance_matches 字典
        """
        instance_matches = {}

        if not instance_ids:
            return instance_matches

        instance_id_strs = [UUIDFormatter.normalize(uid) for uid in instance_ids]
        instance_placeholders = ','.join(['%s'] * len(instance_id_strs))

        if regexp:
            match_type = cls._get_regexp_flag(case_sensitive)
            sql = f"""
                SELECT 
                    id,
                    instance_name,
                    model_id,
                    CASE
                        WHEN REGEXP_LIKE(instance_name, %s, %s) THEN 80.0
                        ELSE 0.0
                    END AS relevance
                FROM model_instance
                WHERE id IN ({instance_placeholders})
                    AND REGEXP_LIKE(instance_name, %s, %s)
                ORDER BY relevance DESC, LENGTH(instance_name) ASC
                LIMIT {cls.MAX_RESULTS}
            """

            params = [
                query, match_type,  # CASE 语句
            ] + instance_id_strs + [
                query, match_type   # WHERE 条件
            ]
        else:
            collation = cls._get_collation(case_sensitive)
            # 转义 LIKE 特殊字符

            def escape_like(s):
                return s.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

            exact_query = escape_like(query)

            # 构建变体的 LIKE 条件
            like_conditions = []
            like_params = []
            for variant in search_variants:
                escaped = escape_like(variant)
                like_conditions.append(f"instance_name COLLATE {collation} LIKE %s")
                like_params.append(f'%{escaped}%')

            like_clause = ' OR '.join(like_conditions) if like_conditions else '1=0'

            sql = f"""
                SELECT 
                    id,
                    instance_name,
                    model_id,
                    CASE
                        WHEN instance_name = %s THEN 100.0
                        WHEN instance_name COLLATE {collation} LIKE %s THEN 80.0
                        WHEN instance_name COLLATE {collation} LIKE %s THEN 80.0
                        WHEN instance_name COLLATE {collation} LIKE %s THEN 70.0
                        ELSE 30.0
                    END AS relevance
                FROM model_instance
                WHERE id IN ({instance_placeholders})
                    AND ({like_clause})
                ORDER BY 
                    CASE WHEN instance_name = %s THEN 0 ELSE 1 END,
                    relevance DESC,
                    LENGTH(instance_name) ASC
                LIMIT {cls.MAX_RESULTS}
            """

            params = [
                query,                  # 精确匹配
                f'{exact_query}%',      # 前缀匹配
                f'%{exact_query}',      # 后缀匹配
                f'%{exact_query}%',     # 包含匹配
            ] + instance_id_strs + like_params + [
                query  # ORDER BY
            ]

            from django.db.models import Q
            qs = ModelInstance.objects.filter(id__in=instance_ids).filter(
                Q(instance_name__exact=query) |
                Q(instance_name__contains=query)
            )
            logger.debug(f'{qs.count()} instances match the instance_name criteria before SQL execution.')

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                logger.debug(f'Executed instance_name search SQL: {connection.queries[-1]["sql"]}')
                columns = [col[0] for col in cursor.description]
                raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            results = UUIDFormatter.convert_rows(
                raw_results,
                uuid_fields=['id', 'model_id']
            )

            for row in results:
                inst_id = row['id']
                relevance = float(row.get('relevance', 0))

                # 计算分数
                if regexp:
                    score = Levenshtein.ratio(query, row['instance_name'])
                else:
                    if relevance >= 100:
                        score = 1.0
                    elif relevance >= 80:
                        score = 0.95
                    elif relevance >= 60:
                        score = 0.85
                    else:
                        score = 0.7

                instance_matches[inst_id] = {
                    'instance_name': row['instance_name'],
                    'model_id': row['model_id'],
                    'matches': [{
                        'field_name': 'instance_name',
                        'field_verbose_name': '实例名称',
                        'field_id': None,
                        'field_type': 'instance_name',
                        'value': row['instance_name'],
                        'display_value': row['instance_name'],
                        'score': round(score, 3),
                        'relevance': round(relevance, 3),
                        'is_exact': relevance >= 100
                    }],
                    'max_score': score
                }

            logger.debug(f'Instance name search returned {len(results)} results')
        except Exception as e:
            logger.warning(f'Instance name search failed: {e}')
            raise Exception(f'Instance name search failed: {str(e)}')

        return instance_matches

    @classmethod
    def _execute_field_regexp_search(cls, pattern: str, instance_ids: list, field_ids: list, case_sensitive: bool = False) -> list:
        """
        使用 MySQL REGEXP_LIKE 执行正则表达式搜索

        Args:
            pattern: 正则表达式模式
            instance_ids: 实例 ID 列表
            field_ids: 字段 ID 列表
            case_sensitive: 是否区分大小写

        Returns:
            匹配结果列表
        """
        if not instance_ids or not field_ids:
            return []

        instance_id_strs = [UUIDFormatter.normalize(uid) for uid in instance_ids]
        field_id_strs = [UUIDFormatter.normalize(uid) for uid in field_ids]

        instance_placeholders = ','.join(['%s'] * len(instance_id_strs))
        field_placeholders = ','.join(['%s'] * len(field_id_strs))

        match_type = cls._get_regexp_flag(case_sensitive)

        sql = f"""
            SELECT 
                id,
                model_instance_id,
                model_fields_id,
                `data`,
                80.0 AS relevance,
                0 AS is_exact_match
            FROM model_field_meta
            WHERE model_instance_id IN ({instance_placeholders})
                AND model_fields_id IN ({field_placeholders})
                AND `data` IS NOT NULL
                AND `data` <> ''
                AND REGEXP_LIKE(`data`, %s, %s)
            ORDER BY LENGTH(`data`) ASC
            LIMIT {cls.MAX_RESULTS}
        """

        params = instance_id_strs + field_id_strs + [pattern, match_type]

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                logger.debug(f'Executed REGEXP_LIKE search SQL: {connection.queries[-1]["sql"]}')
                columns = [col[0] for col in cursor.description]
                raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            results = UUIDFormatter.convert_rows(
                raw_results,
                uuid_fields=['id', 'model_instance_id', 'model_fields_id']
            )
            logger.debug(f'REGEXP_LIKE search returned {len(results)} results (case_sensitive={case_sensitive})')
            return results
        except Exception as e:
            logger.warning(f'Error occurred during REGEXP_LIKE search: {e}')
            raise Exception(f'REGEXP_LIKE search failed: {str(e)}')

    @classmethod
    def _execute_field_fulltext_search(cls, query: str, search_variants: set, instance_ids: list, field_ids: list, search_mode: str = 'boolean', threshold: float = 0.0) -> list:
        """
        使用原生 SQL 执行 MySQL FULLTEXT 搜索
        结合精确匹配提升相关性
        """
        if not instance_ids or not field_ids:
            return []

        collation = cls._get_collation(case_sensitive=False)

        # 构建布尔模式查询字符串
        if search_mode == 'boolean':
            boolean_terms = []
            for variant in search_variants:
                safe_variant = (
                    variant
                    .replace('\\', '')  # 移除已有的转义
                    .replace('+', '')
                    .replace('-', '')
                    .replace('*', '')
                    .replace('(', '')
                    .replace(')', '')
                    .replace('"', '')
                    .replace('@', '')
                    .replace('<', '')
                    .replace('>', '')
                    .replace('~', '')
                ).strip()
                if safe_variant:
                    # 不使用 * 后缀，避免过度匹配
                    boolean_terms.append(f'"{safe_variant}"')  # 使用短语匹配
            search_query = ' '.join(boolean_terms)
            match_mode = 'IN BOOLEAN MODE'
        elif search_mode == 'expansion':
            search_query = query
            match_mode = 'WITH QUERY EXPANSION'
        else:  # natural
            search_query = query
            match_mode = 'IN NATURAL LANGUAGE MODE'

        if not search_query.strip():
            return []

        instance_id_strs = [UUIDFormatter.normalize(uid) for uid in instance_ids]
        field_id_strs = [UUIDFormatter.normalize(uid) for uid in field_ids]

        instance_placeholders = ','.join(['%s'] * len(instance_id_strs))
        field_placeholders = ','.join(['%s'] * len(field_id_strs))

        # 转义原始查询用于 LIKE 精确匹配
        exact_query = query.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

        # 构建变体的 LIKE 条件用于模糊匹配
        like_conditions = []
        like_params = []
        for variant in search_variants:
            like_conditions.append(f"`data` COLLATE {collation} LIKE %s")
            like_params.append(f'%{variant}%')

        like_clause = ' OR '.join(like_conditions) if like_conditions else '1=0'

        sql = f"""
            SELECT 
                id,
                model_instance_id,
                model_fields_id,
                `data`,
                CASE
                    WHEN `data` = %s THEN 100.0
                    WHEN `data` COLLATE {collation} LIKE %s THEN 80.0
                    WHEN `data` COLLATE {collation} LIKE %s THEN 80.0
                    WHEN ({like_clause}) THEN 70.0
                    ELSE MATCH(`data`) AGAINST(%s {match_mode})
                END AS relevance,
                CASE WHEN `data` = %s THEN 1 ELSE 0 END AS is_exact_match
            FROM model_field_meta
            WHERE model_instance_id IN ({instance_placeholders})
                AND model_fields_id IN ({field_placeholders})
                AND `data` IS NOT NULL
                AND `data` <> ''
                AND (
                    `data` = %s
                    OR `data` COLLATE {collation} LIKE %s
                    OR `data` COLLATE {collation} LIKE %s
                    OR ({like_clause})
                    OR MATCH(`data`) AGAINST(%s {match_mode}) > 0.7
                )
            ORDER BY is_exact_match DESC, relevance DESC
            LIMIT {cls.MAX_RESULTS}
        """

        # 构建参数列表
        params = [
            # CASE 语句参数
            query,              # 精确匹配
            f'{exact_query}%',  # 前缀匹配
            f'%{exact_query}',  # 后缀匹配
        ] + like_params + [     # LIKE 变体匹配
            search_query,       # FULLTEXT
            query,              # is_exact_match
        ] + instance_id_strs + field_id_strs + [
            # WHERE 条件参数
            query,              # 精确匹配
            f'{exact_query}%',  # 前缀匹配
            f'%{exact_query}',  # 后缀匹配
        ] + like_params + [     # LIKE 变体匹配
            search_query,       # FULLTEXT
            threshold
        ]

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                raw_results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            results = UUIDFormatter.convert_rows(
                raw_results,
                uuid_fields=['id', 'model_instance_id', 'model_fields_id']
            )
            logger.debug(f'Hybrid search returned {len(results)} results')
            return results
        except Exception as e:
            logger.warning(f'Hybrid search failed: {e}, falling back to LIKE search')
            return cls._fallback_like_search(
                search_variants, instance_id_strs, field_id_strs
            )

    @staticmethod
    def _fallback_like_search(search_variants: set, instance_ids: list, field_ids: list) -> list:
        """
        FULLTEXT 失败时的 LIKE 回退搜索
        """
        from django.db.models import Q

        if not instance_ids or not field_ids:
            return []

        q_filter = Q()
        for variant in search_variants:
            if variant and variant.strip():
                q_filter |= Q(data__contains=variant)

        if not q_filter:
            return []

        results = ModelFieldMeta.objects.filter(
            model_instance_id__in=instance_ids,
            model_fields_id__in=field_ids,
            data__isnull=False
        ).exclude(
            data__exact=''
        ).filter(
            q_filter
        ).values(
            'id', 'model_instance_id', 'model_fields_id', 'data'
        )[:5000]

        # 添加默认的 relevance 字段
        return [
            {**item, 'relevance': 0.5}
            for item in results
        ]

    @classmethod
    def _merge_field_matches(cls, instance_matches: dict, meta_results: list, fields_by_id: dict, enum_cache: dict, ref_instance_cache: dict, search_variants: set, threshold: float, regexp: bool = False):
        """
        将字段匹配结果合并到 instance_matches 中
        """
        for meta in meta_results:
            inst_id = str(meta['model_instance_id'])
            field_id = str(meta['model_fields_id'])
            raw_data = meta['data']
            relevance = float(meta.get('relevance', 0))

            # 查找字段配置
            field = fields_by_id.get(field_id)
            if not field:
                logger.debug(f'Field ID {field_id} not found during merge, skipping.')
                continue

            # 获取显示值
            display_value = cls._get_display_value(
                raw_data, field, enum_cache, ref_instance_cache
            )

            if regexp:
                score = Levenshtein.ratio(next(iter(search_variants)), raw_data)
            else:
                # 计算分数
                if relevance >= 100:
                    score = 1.0
                elif relevance >= 80:
                    score = 0.95
                elif relevance >= 70:
                    score = 0.85
                elif relevance > 0:
                    score = cls._calculate_similarity(search_variants, raw_data, display_value)

            if score < threshold:
                continue

            match_item = {
                'field_name': field.name,
                'field_verbose_name': field.verbose_name,
                'field_id': field_id,
                'field_type': field.type,
                'value': raw_data,
                'display_value': display_value,
                'score': round(score, 3),
                'relevance': round(relevance, 3),
                'is_exact': relevance >= 100
            }

            if inst_id in instance_matches:
                instance_matches[inst_id]['matches'].append(match_item)
                if score > instance_matches[inst_id]['max_score']:
                    instance_matches[inst_id]['max_score'] = score
            else:
                instance_matches[inst_id] = {
                    'matches': [match_item],
                    'max_score': score
                }

    @staticmethod
    def _build_conversion_cache(fields_qs) -> tuple:
        """构建枚举和引用的双向映射缓存"""
        enum_cache = {}
        ref_instance_cache = {}
        ref_model_ids = set()

        for field in fields_qs:
            field_id = str(field.id)

            if field.type == FieldType.ENUM and field.validation_rule_id:
                enum_dict = ValidationRules.get_enum_dict(field.validation_rule_id)
                enum_cache[field_id] = {
                    'key_to_label': enum_dict,
                    'label_to_key': {v: k for k, v in enum_dict.items()}
                }
            elif field.type == FieldType.MODEL_REF and field.ref_model_id:
                ref_model_ids.add(field.ref_model_id)

        # 批量获取所有引用模型的实例
        if ref_model_ids:
            ref_instances = ModelInstance.objects.filter(
                model_id__in=ref_model_ids
            ).values('id', 'instance_name')

            for inst in ref_instances:
                inst_id = str(inst['id'])
                inst_name = inst['instance_name']
                ref_instance_cache[inst_id] = inst_name
                # 反向映射：名称 -> ID
                # if inst_name not in ref_instance_cache:
                #     ref_instance_cache[inst_name] = inst_id

        return enum_cache, ref_instance_cache

    @staticmethod
    def _build_search_variants(query: str, enum_cache: dict, ref_instance_cache: dict, case_sensitive: bool = False) -> set:
        """
        构建搜索变体集合
        包含原始查询、枚举转换、实例名称/ID转换
        """
        variants = {query}

        if not case_sensitive:
            variants.add(query.lower())
            variants.add(query.upper())
        else:
            variants.add(query)

        search_key = query if case_sensitive else query.lower()

        # 枚举 key/value 互转
        for field_id, cache in enum_cache.items():
            for key, label in cache['key_to_label'].items():
                if search_key == (key if case_sensitive else key.lower()):
                    variants.add(label)
                if search_key == (label if case_sensitive else label.lower()):
                    variants.add(key)

        # 搜索实例
        for key, value in ref_instance_cache.items():
            if search_key in (value if case_sensitive else value.lower()):
                variants.add(value)
                variants.add(key)

        return variants

    @staticmethod
    def _get_display_value(raw_data, field, enum_cache, ref_instance_cache) -> str:
        """获取字段的显示值"""
        if not raw_data:
            return ''

        field_id = str(field.id).replace('-', '')

        if field.type == FieldType.ENUM:
            cache = enum_cache.get(field_id, {})
            return cache.get('key_to_label', {}).get(raw_data, raw_data)

        elif field.type == FieldType.MODEL_REF:
            return ref_instance_cache.get(raw_data, raw_data)

        elif field.type == FieldType.BOOLEAN:
            if isinstance(raw_data, bool):
                return '是' if raw_data else '否'
            if isinstance(raw_data, str):
                return '是' if raw_data.lower() in ('true', '1', 'yes') else '否'
            return str(raw_data)

        return str(raw_data)

    @staticmethod
    def _calculate_similarity(search_variants: set, raw_data: str, display_value: str) -> float:
        """计算字符串相似度"""
        if not raw_data and not display_value:
            return 0.0

        max_score = 0.0
        targets = [raw_data, display_value]

        for variant in search_variants:

            for target in targets:
                if not target:
                    continue

                score = Levenshtein.ratio(variant, target)
                max_score = max(max_score, score)

        return max_score

    @staticmethod
    def _build_results(instance_matches: dict, models_map: dict) -> list:
        """构建最终结果列表"""
        if not instance_matches:
            return []

        matched_instance_ids = list(instance_matches.keys())
        instances = ModelInstance.objects.filter(
            id__in=matched_instance_ids
        ).values('id', 'instance_name', 'model_id')

        instance_info = {str(inst['id']): inst for inst in instances}

        results = []
        for inst_id, match_data in instance_matches.items():
            inst = instance_info.get(inst_id)
            if not inst:
                continue

            model_id = str(inst['model_id'])
            model = models_map.get(model_id)

            results.append({
                'instance_id': inst_id,
                'instance_name': inst['instance_name'],
                'model_id': model_id,
                'model_name': model.name if model else None,
                'model_verbose_name': model.verbose_name if model else None,
                'matches': sorted(match_data['matches'], key=lambda x: -x['score']),
                'max_score': round(match_data['max_score'], 3)
            })

        # 按最高相似度排序
        results.sort(key=lambda x: -x['max_score'])
        return results

    @staticmethod
    @require_valid_user
    def search_instances_by_name(query: str, user: UserInfo, model_ids: list = None, limit: int = 50) -> list:
        """
        按实例名称搜索
        """
        from django_mysql.models.functions import Match

        pm = PermissionManager(user)

        queryset = pm.get_queryset(ModelInstance)

        if model_ids:
            queryset = queryset.filter(model_id__in=model_ids)

        # 构建布尔搜索查询
        safe_query = query.replace('+', '\\+').replace('-', '\\-')
        search_query = f'{safe_query}*'

        results = queryset.annotate(
            relevance=Match('instance_name', search_query, mode=Match.BOOLEAN)
        ).filter(
            relevance__gt=0
        ).order_by('-relevance').values(
            'id', 'instance_name', 'model_id'
        )[:limit]

        return list(results)


class RelationDefinitionService:

    @staticmethod
    @require_valid_user
    def create_relation_definition(validated_data: dict, user: UserInfo) -> 'RelationDefinition':
        """创建关系定义"""

        username = user.username
        source_models = validated_data.pop('source_model', [])
        target_models = validated_data.pop('target_model', [])

        relation_def = RelationDefinition.objects.create(
            **validated_data,
            create_user=username,
            update_user=username
        )

        if source_models:
            relation_def.source_model.set(source_models)
        if target_models:
            relation_def.target_model.set(target_models)

        logger.info(f"User {username} created relation definition: {relation_def.name}")
        return relation_def

    @staticmethod
    @require_valid_user
    def update_relation_definition(instance: 'RelationDefinition', validated_data: dict, user: UserInfo) -> 'RelationDefinition':
        """更新关系定义"""
        username = user.username
        source_models = validated_data.pop('source_model', None)
        target_models = validated_data.pop('target_model', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.update_user = username
        instance.save()

        if source_models is not None:
            instance.source_model.set(source_models)
        if target_models is not None:
            instance.target_model.set(target_models)

        logger.info(f"User {username} updated relation definition: {instance.name}")
        return instance

    @staticmethod
    @require_valid_user
    def delete_relation_definition(instance: 'RelationDefinition', user: UserInfo):
        """删除关系定义"""
        from .models import Relations

        if instance.built_in:
            raise PermissionDenied("Cannot delete built-in relation definition.")

        # 检查是否有关系实例使用此定义
        if Relations.objects.filter(relation=instance).exists():
            raise ValidationError(
                "This relation definition is in use and cannot be deleted. "
                "Please remove all relation instances first."
            )

        name = instance.name
        instance.delete()
        logger.info(f"User {user.username} deleted relation definition: {name}")


@dataclass
class TopologyNode:
    """拓扑节点数据结构"""
    id: str
    instance: 'ModelInstance'
    is_visible: bool
    model_id: str = None
    instance_name: str = None


@dataclass
class TopologyEdge:
    """拓扑边数据结构"""
    relation: 'Relations'
    source_visible: bool
    target_visible: bool


@dataclass
class TopologyResult:
    """拓扑查询结果"""
    nodes: List[TopologyNode]
    edges: List[TopologyEdge]
    visible_node_count: int
    restricted_node_count: int


class RelationsService:
    """关系实例服务层"""

    @classmethod
    @require_valid_user
    def create_relation(cls, validated_data: dict, user: UserInfo) -> 'Relations':
        """创建关系"""

        # TODO: 校验逻辑转移到调用方处理

        username = user.username
        pm = PermissionManager(user)

        source_instance_id = validated_data.get('source_instance')
        target_instance_id = validated_data.get('target_instance')
        relation_id = validated_data.get('relation')

        # 验证关系实例是否存在
        if Relations.objects.check_relation_exists(
            source_instance_id,
            target_instance_id,
            relation_id
        ):
            raise ValidationError("This relation already exists for the given source, target, and relation type.")

        # 验证用户对源和目标实例的权限
        source_instance = pm.get_queryset(ModelInstance).filter(id=source_instance_id)
        target_instance = pm.get_queryset(ModelInstance).filter(id=target_instance_id)
        if not (source_instance.exists() or target_instance.exists()):
            source_exists = ModelInstance.objects.check_instance_id_exists(source_instance_id)
            target_exists = ModelInstance.objects.check_instance_id_exists(target_instance_id)
            if not source_exists:
                raise ValidationError(f"Source instance {source_instance_id} does not exist.")
            if not target_exists:
                raise ValidationError(f"Target instance {target_instance_id} does not exist.")
            raise PermissionDenied("No permission to create this relation.")

        # 验证关系定义约束
        relation_def = RelationDefinition.objects.get(id=relation_id)

        # 检查模型约束
        if relation_def.source_model.exists():
            if not relation_def.source_model.filter(id=source_instance.first().model_id).exists():
                raise ValidationError(f"Source instance model is not allowed for this relation type.")

        if relation_def.target_model.exists():
            if not relation_def.target_model.filter(id=target_instance.first().model_id).exists():
                raise ValidationError(f"Target instance model is not allowed for this relation type.")

        # 检查DAG约束（有向无环图）
        if relation_def.topology_type == 'daggered':
            if cls._would_create_cycle(source_instance_id, target_instance_id, relation_id):
                raise ValidationError("This relation would create a cycle, which is not allowed for DAG topology.")

        relation = Relations.objects.create(
            source_instance=source_instance.first(),
            target_instance=target_instance.first(),
            relation=relation_def,
            source_attributes=validated_data.get('source_attributes', {}),
            target_attributes=validated_data.get('target_attributes', {}),
            relation_attributes=validated_data.get('relation_attributes', {}),
            create_user=username,
            update_user=username
        )

        logger.info(f"User {username} created relation: {source_instance} -> {target_instance}")
        return relation

    @staticmethod
    def _would_create_cycle(source_id: str, target_id: str, relation_id: str) -> bool:
        """检查添加关系是否会创建环"""
        from .models import Relations

        # 使用BFS检查从target到source是否存在路径
        visited = set()
        queue = [str(target_id)]

        while queue:
            current = queue.pop(0)
            if current == str(source_id):
                return True

            if current in visited:
                continue
            visited.add(current)

            # 获取当前节点的所有出边目标
            next_nodes = Relations.objects.get_connected_instances(
                current,
                direction='forward'
            )

            queue.extend(str(n) for n in next_nodes if str(n) not in visited)

        return False

    @classmethod
    @require_valid_user
    def bulk_create_relations(cls, relations_data: list, user: UserInfo) -> list:
        """批量创建关系"""

        username = user.username
        created_relations = []

        for data in relations_data:
            try:
                relation = cls.create_relation(data, user)
                created_relations.append(relation)
            except (ValidationError, PermissionDenied) as e:
                logger.warning(f"Failed to create relation: {e}")
                continue

        logger.info(f"User {username} bulk created {len(created_relations)} relations")
        return created_relations

    @staticmethod
    @require_valid_user
    def delete_relation(instance: 'Relations', user: UserInfo):
        """删除关系"""
        pm = PermissionManager(user)

        # 检查用户是否有权限删除（对源或目标有权限）
        source_visible = pm.get_queryset(ModelInstance).filter(id=instance.source_instance_id).exists()
        target_visible = pm.get_queryset(ModelInstance).filter(id=instance.target_instance_id).exists()

        if not (source_visible or target_visible):
            raise PermissionDenied("You don't have permission to delete this relation.")

        instance.delete()
        logger.info(f"User {user.username} deleted relation: {instance}")

    @classmethod
    @require_valid_user
    def bulk_delete_relations(cls, relations: List['Relations'], user: UserInfo) -> dict:
        """批量删除关系"""
        from .models import Relations

        pm = PermissionManager(user)
        results = {'deleted': 0, 'failed': 0, 'errors': []}

        for relation in relations:
            try:
                cls.delete_relation(relation, user)
                results['deleted'] += 1
            except Relations.DoesNotExist:
                results['failed'] += 1
                results['errors'].append(f"Relation {relation.id} not found")
            except PermissionDenied as e:
                results['failed'] += 1
                results['errors'].append(f"Relation {relation.id}: {str(e)}")

        return results

    @classmethod
    @require_valid_user
    def get_topology(
        cls,
        user: UserInfo,
        start_node_ids: List[str],
        end_node_ids: List[str] = None,
        depth: int = 3,
        direction: str = 'both',
        mode: str = 'blast'
    ) -> TopologyResult:
        """
        权限处理策略：
        1. 使用特权方法获取完整拓扑结构（边）
        2. 使用权限管理器过滤可见节点
        3. 不可见节点标记为"受限"，保留连通性
        """
        from .models import Relations, ModelInstance

        pm = PermissionManager(user)

        G = nx.DiGraph()

        if mode == 'path':
            all_relations, all_node_ids = cls._build_path_graph(
                start_node_ids, end_node_ids, depth
            )
        elif mode == 'blast':
            all_relations, all_node_ids = Relations.objects.get_topology_edges(
                start_node_ids, depth, direction
            )
        elif mode == 'neighbor':
            all_relations, all_node_ids = cls._build_neighbor_graph(
                start_node_ids, direction
            )
        else:
            all_relations, all_node_ids = [], set()

        visible_instances = pm.get_queryset(ModelInstance).filter(
            id__in=all_node_ids
        ).in_bulk()
        visible_instance_ids = set(str(id) for id in visible_instances.keys())

        nodes = []
        node_map = {}

        for node_id in all_node_ids:
            node_id_str = str(node_id)
            instance = visible_instances.get(node_id) if node_id in visible_instances else None

            if instance:
                node = TopologyNode(
                    id=node_id_str,
                    instance=instance,
                    is_visible=True,
                    model_id=str(instance.model_id),
                    instance_name=instance.instance_name
                )
            else:
                # 受限节点：保留ID但不暴露详情
                node = TopologyNode(
                    id=node_id_str,
                    instance=None,
                    is_visible=False,
                    model_id=None,
                    instance_name="[无权限]"
                )

            nodes.append(node)
            node_map[node_id_str] = node

        # 构建边信息
        edges = []
        for rel in all_relations:
            source_id = str(rel.source_instance_id)
            target_id = str(rel.target_instance_id)

            edge = TopologyEdge(
                relation=rel,
                source_visible=source_id in visible_instance_ids,
                target_visible=target_id in visible_instance_ids
            )
            edges.append(edge)

            # 添加到图中用于路径分析
            G.add_edge(source_id, target_id, relation=rel)

        visible_count = sum(1 for n in nodes if n.is_visible)
        restricted_count = len(nodes) - visible_count

        return TopologyResult(
            nodes=nodes,
            edges=edges,
            visible_node_count=visible_count,
            restricted_node_count=restricted_count
        )

    @staticmethod
    def _build_path_graph(start_node_ids: List[str], end_node_ids: List[str], depth: int):
        """构建路径查询图"""
        from .models import Relations

        all_relations = []
        all_node_ids = set(start_node_ids + end_node_ids)
        visited = set()
        queue = set(start_node_ids + end_node_ids)

        for _ in range(depth + 1):
            if not queue:
                break

            current_nodes = list(queue)
            visited.update(current_nodes)
            queue.clear()

            relations = Relations.objects.filter(
                Q(source_instance_id__in=current_nodes) |
                Q(target_instance_id__in=current_nodes)
            ).select_related('source_instance', 'target_instance', 'relation')

            for rel in relations:
                all_relations.append(rel)
                source_id = str(rel.source_instance_id)
                target_id = str(rel.target_instance_id)

                all_node_ids.add(source_id)
                all_node_ids.add(target_id)

                if source_id not in visited:
                    queue.add(source_id)
                if target_id not in visited:
                    queue.add(target_id)

        return all_relations, all_node_ids

    @staticmethod
    def _build_neighbor_graph(start_node_ids: List[str], direction: str):
        """构建邻居查询图"""
        from .models import Relations

        all_relations = []
        all_node_ids = set(start_node_ids)

        for start_node in start_node_ids:
            q_filter = Q()
            if direction in ('forward', 'both'):
                q_filter |= Q(source_instance_id=start_node)
            if direction in ('reverse', 'both'):
                q_filter |= Q(target_instance_id=start_node)

            relations = Relations.objects.filter(q_filter).select_related(
                'source_instance', 'target_instance', 'relation'
            )

            for rel in relations:
                all_relations.append(rel)
                all_node_ids.add(str(rel.source_instance_id))
                all_node_ids.add(str(rel.target_instance_id))

        return all_relations, all_node_ids

    @staticmethod
    def serialize_topology_result(result: TopologyResult) -> dict:
        """序列化拓扑结果"""
        from .serializers import ModelInstanceBasicViewSerializer, RelationsSerializer

        # 序列化可见节点
        visible_instances = [n.instance for n in result.nodes if n.is_visible and n.instance]
        node_data = ModelInstanceBasicViewSerializer(visible_instances, many=True).data

        # 添加受限节点信息
        for node in result.nodes:
            if not node.is_visible:
                node_data.append({
                    'id': node.id,
                    'instance_name': node.instance_name,
                    'is_restricted': True
                })

        # 序列化边
        edge_data = RelationsSerializer([e.relation for e in result.edges], many=True).data

        return {
            'nodes': node_data,
            'edges': edge_data,
            'statistics': {
                'total_nodes': len(result.nodes),
                'visible_nodes': result.visible_node_count,
                'restricted_nodes': result.restricted_node_count,
                'total_edges': len(result.edges)
            }
        }
