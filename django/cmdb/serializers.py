import json
import re
import traceback
from datetime import date, datetime
from uuid import UUID
from ast import literal_eval
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import operator
from functools import reduce
from django.db.models import Max, F, Q, Count
from django.core.cache import cache
from types import SimpleNamespace
from cacheops import invalidate_model, invalidate_obj
from .utils import password_handler
from .validators import FieldValidator
from .constants import FieldMapping, ValidationType, FieldType, limit_field_names
from .models import (
    ModelGroups,
    Models,
    ModelFieldGroups,
    ValidationRules,
    ModelFields,
    ModelFieldOrder,
    ModelFieldPreference,
    UniqueConstraint,
    ModelInstance,
    ModelInstanceGroup,
    ModelInstanceGroupRelation,
    ModelFieldMeta,
    RelationDefinition,
    Relations,
)
import logging
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 20)
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ModelGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelGroups
        fields = '__all__'

    def validate_name(self, value):
        """Validate model group name"""
        if not value:
            raise serializers.ValidationError({'name': 'Model group name cannot be empty'})

        exists = ModelGroups.objects.filter(name__iexact=value)
        if self.instance:  # 更新时排除自身
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError({'name': f'Model group name {value} already exists'})
        # 如果是更新操作且模型组为内置或不可编辑，不允许修改名称
        if self.instance and (self.instance.built_in or not self.instance.editable):
            if self.instance.name != value:
                raise PermissionDenied({
                    'detail': 'Built-in or non-editable model group name cannot be modified'
                })
        return value


class ModelsSerializer(serializers.ModelSerializer):
    instance_count = serializers.SerializerMethodField()

    class Meta:
        model = Models
        fields = '__all__'

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.Meta.fields = list(self.Meta.fields) + ['instance_count']

    def get_instance_count(self, obj):
        """获取模型关联的实例总数"""
        try:
            return ModelInstance.objects.filter(model=obj).count()
        except Exception as e:
            logger.error(f"Error counting instances for model {obj.id}: {str(e)}")
            return 0

    def validate_name(self, value):
        # 检查更新时是否是内置模型
        if self.instance and self.instance.built_in and self.instance.name != value:
            raise PermissionDenied({
                'detail': 'Built-in model name cannot be modified'
            })

        # 检查名称唯一性
        if Models.objects.filter(name=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError({
                'name': f'Model with name {value} already exists'
            })
        return value

    def create(self, validated_data):
        try:
            with transaction.atomic():
                if not validated_data.get('model_group'):
                    validated_data['model_group'] = ModelGroups.get_default_model_group()

                model = super().create(validated_data)
                logger.info(f"Created model: {model.name}")

                model_field_group = ModelFieldGroups.get_default_field_group(model)
                logger.info(f"Created default field group for model: {model.name}")

                root_group = ModelInstanceGroup.get_root_group(model)
                logger.info(f"Created root group for model: {model.name}")

                unassigned_group = ModelInstanceGroup.get_unassigned_group(model)
                logger.info(f"Created unassigned pool group for model: {model.name}")

                return model

        except Exception as e:
            logger.error(f"Error creating model and initial groups: {str(e)}")
            raise serializers.ValidationError(f"Failed to create model and initial groups: {str(e)}")

    def update(self, instance, validated_data):
        if not validated_data.get('model_group') or not ModelGroups.objects.filter(id=validated_data['model_group'].id).exists():
            validated_data['model_group'] = ModelGroups.get_default_model_group()
        return super().update(instance, validated_data)


class ModelFieldGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelFieldGroups
        fields = '__all__'

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError({'name': 'Model field group name cannot be empty'})
        exists = ModelFieldGroups.objects.filter(name__iexact=value)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError({'name': f'Model field group name {value} already exists'})
        if self.instance and (self.instance.built_in or not self.instance.editable):
            if self.instance.name != value:
                raise PermissionDenied({
                    'detail': 'Built-in or non-editable model field group name cannot be modified'
                })
        return value


class ValidationRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRules
        fields = '__all__'

    def validate(self, data):
        instance = self.instance
        is_update = instance is not None

        # 更新校验
        if is_update:
            # 内置且不可编辑规则不允许任何修改
            if not instance.editable:
                raise serializers.ValidationError(
                    "Cannot modify non-editable validation rules"
                )
            # 内置可编辑规则只允许修改 enum 类型的规则内容
            if instance.built_in and instance.editable:
                if instance.type != ValidationType.ENUM:
                    raise serializers.ValidationError(
                        "Can only modify rule content for editable enum type built_in rules"
                    )
                # 检查所有字段变更
                allowed_fields = {'rule', 'description', 'verbose_name', 'update_user'}
                for field, new_value in data.items():
                    old_value = getattr(instance, field)
                    if new_value != old_value and field not in allowed_fields:
                        raise serializers.ValidationError(f"Cannot modify {field} for built-in enum rules")

        # 基础字段验证
        field_type = data.get('field_type')
        validation_type = data.get('type')
        if not field_type and self.instance:
            field_type = self.instance.field_type
        if not validation_type and self.instance:
            validation_type = self.instance.type

        if not validation_type:
            raise serializers.ValidationError(
                f"Validation type is required for field type '{field_type}'"
            )
        if validation_type not in ValidationType.__members__.values():
            raise serializers.ValidationError(
                f"Validation type '{validation_type}' is not valid for field type '{field_type}'"
            )

        # 规则内容验证
        if data.get('rule') == '':
            data['rule'] = None

        if validation_type == ValidationType.ENUM:
            rule_data = data.get('rule')
            try:
                enum_data = json.loads(rule_data) if isinstance(rule_data, str) else rule_data
                if isinstance(enum_data, str):
                    enum_data = json.loads(enum_data)
                if not isinstance(enum_data, dict):
                    raise serializers.ValidationError("Enum rule must be a dict")
                if len(enum_data) != len(set(enum_data.values())):
                    raise serializers.ValidationError("Enum labels must be unique")
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for enum rule")
            except Exception as e:
                raise serializers.ValidationError(f"Invalid enum rule: {str(e)}")

        return data


class ModelFieldsSerializer(serializers.ModelSerializer):
    default = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ModelFields
        fields = '__all__'

    def get_enum_display(self, obj):
        if not obj.model_fields.enum_options or not obj.data:
            return None

        try:
            enum_options = obj.model_fields.enum_options
            for option in enum_options:
                if option['value'] == obj.data:
                    return option['label']
        except (AttributeError, KeyError):
            return None

    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError({'name': 'Model field name cannot be empty'})
        exists = ModelFields.objects.filter(name__iexact=value, model=self.initial_data.get('model'))
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError({'name': f'Model field name {value} already exists'})
        return value

    def to_internal_value(self, data):
        """在验证之前预处理数据"""
        data_copy = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'type' in data_copy and data_copy['type'] in (FieldType.PASSWORD, FieldType.MODEL_REF):
            data_copy['default'] = None
        if 'default' in data_copy and data_copy['default'] is not None:
            # 如果是布尔值，预先转换为字符串
            if isinstance(data_copy['default'], bool):
                data_copy['default'] = str(data_copy['default']).lower()
            # 确保其他类型也转换为字符串
            elif data_copy['default'] is not None:
                data_copy['default'] = str(data_copy['default'])

        return super().to_internal_value(data_copy)

    def _convert_to_storage_value(self, value, field_type):
        """转换值为存储格式"""
        if value is None:
            return None

        if field_type == FieldType.BOOLEAN:
            return str(value).lower()
        elif self.instance and self.instance.validation_rule and self.instance.validation_rule.type == ValidationType.ENUM:
            # 枚举值只存储key
            try:
                enum_data = json.loads(self.instance.validation_rule.rule)
                if value in enum_data:
                    return value
                raise ValueError(f"Invalid enum key: {value}")
            except json.JSONDecodeError:
                raise ValueError("Invalid enum configuration")
        elif not self.instance:
            pass

        return value

    def _convert_from_storage_value(self, value, field_type):
        """从存储格式转换回实际类型"""
        if value is None:
            return None

        if field_type == FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return value.lower() in ('true', '1', 't', 'y', 'yes')
            else:
                raise ValueError(f"Invalid boolean value: {value}")
        elif field_type == FieldType.INTEGER:
            return int(value) if value is not None else None

        elif field_type == FieldType.FLOAT:
            return float(value) if value is not None else None

        return value

    def validate(self, data):
        if data.get('name') in limit_field_names:
            raise serializers.ValidationError({
                'name': f"Field name '{data.get('name')}' is conflict with system reserved field names"
            })
        if self.instance:
            if not self.instance.editable:
                restricted_fields = ['name', 'model', 'verbose_name', 'type', 'validation', 'validation_rule']
                for field in restricted_fields:
                    if field in data and data[field] != getattr(self.instance, field):
                        raise PermissionDenied({
                            'detail': f'Non-editable field cannot modify {field}',
                            'field': field
                        })
            if self.instance.built_in:
                restricted_fields = ['name', 'model', 'type']
                for field in restricted_fields:
                    if field in data and data[field] != getattr(self.instance, field):
                        raise PermissionDenied({
                            'detail': f'Built-in field cannot modify {field}'
                        })
            return data
        else:
            if data.get('type') not in FieldType.__members__.values():
                raise serializers.ValidationError({
                    'type': f"Invalid field type: {data.get('type')}"
                })

            if data.get('type') == FieldType.MODEL_REF:
                data['default'] = None
                if not data.get('ref_model'):
                    raise serializers.ValidationError({
                        'ref_model': 'Reference model is required for model_ref type field'
                    })
                # 验证引用模型是否存在
                try:
                    ref_model = Models.objects.get(id=data['ref_model'].id)
                except Models.DoesNotExist:
                    raise serializers.ValidationError({
                        'ref_model': f"Referenced model {data['ref_model']} does not exist"
                    })

            if data['default'] == '':
                data['default'] = None

            temp_obj = SimpleNamespace()
            # 标记为创建字段，避免被要求required验证
            setattr(temp_obj, 'create_field_flag', True)
            # 将字典数据转换为对象以适配ModelFieldMeta采用的验证器代码
            for key, value in data.items():
                setattr(temp_obj, key, value)
            if not hasattr(temp_obj, 'default'):
                setattr(temp_obj, 'default', None)
            validation_rule_exists = hasattr(temp_obj, 'validation_rule')
            if not validation_rule_exists:
                setattr(temp_obj, 'validation_rule', None)
                temp_obj.validation_rule = SimpleNamespace()
                setattr(temp_obj.validation_rule, 'type', None)
                temp_obj.validation_rule.type = temp_obj.type
            try:
                default = temp_obj.default
                if temp_obj.type == FieldType.BOOLEAN:
                    if isinstance(temp_obj.default, bool):
                        default = str(temp_obj.default).lower()
                validated_default = FieldValidator.validate(default, temp_obj)
                if validated_default is not None:
                    temp_obj.default = self._convert_to_storage_value(
                        validated_default,
                        temp_obj
                    )
            except ValueError as e:
                raise serializers.ValidationError({
                    'detail': str(e),
                    'field': temp_obj.name
                })
            if not validation_rule_exists:
                delattr(temp_obj, 'validation_rule')
            delattr(temp_obj, 'create_field_flag')
            # 将对象转换回字典
            data_new = {}
            for key, value in temp_obj.__dict__.items():
                data_new[key] = value
            return data_new

    def validate_order(self, value):
        # 如果没有提供order值,自动计算下一个序号
        if not value:
            model = self.initial_data.get('model')
            if model:
                max_order = ModelFields.objects.filter(model=model).aggregate(
                    Max('order'))['order__max']
                return 1 if not max_order else int(max_order) + 1
        return value

    def create(self, validated_data):
        if not validated_data.get('model_field_group') or not ModelFieldGroups.objects.filter(id=validated_data['model_field_group'].id).exists():
            validated_data['model_field_group'] = ModelFieldGroups.get_default_field_group(validated_data['model'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if 'type' in validated_data and validated_data['type'] != instance.type:
            raise PermissionDenied({
                'detail': 'Field type cannot be modified'
            })
        if request and request.method == 'PUT':
            if 'model_field_group' not in validated_data:
                validated_data['model_field_group'] = ModelFieldGroups.get_default_field_group(
                    instance.model
                )
        else:
            if 'model_field_group' not in validated_data:
                validated_data['model_field_group'] = instance.model_field_group

        if not validated_data['model_field_group'] or not ModelFieldGroups.objects.filter(
            id=validated_data['model_field_group'].id
        ).exists():
            validated_data['model_field_group'] = ModelFieldGroups.get_default_field_group(
                instance.model
            )

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 返回时转换回实际类型
        if 'default' in data:
            data['default'] = self._convert_from_storage_value(data['default'], instance.type)
        return data


class ModelFieldOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelFieldOrder
        fields = '__all__'


class ModelFieldPreferenceSerializer(serializers.ModelSerializer):
    fields_preferred = serializers.ListField()

    class Meta:
        model = ModelFieldPreference
        fields = '__all__'

    def to_representation(self, instance):
        # 将 UUID 转换为字符串列表
        data = super().to_representation(instance)
        data['fields_preferred'] = [str(field_id) for field_id in instance.fields_preferred]
        return data

    def to_internal_value(self, data):
        if 'fields_preferred' in data:
            try:
                data['fields_preferred'] = [str(field_id) for field_id in data['fields_preferred']]
            except (ValueError, AttributeError, TypeError):
                raise serializers.ValidationError({
                    'fields_preferred': 'Invalid UUID format in fields_preferred'
                })
        return super().to_internal_value(data)


class UniqueConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueConstraint
        fields = '__all__'

    def validate(self, data):
        """自定义验证方法"""
        model = data.get('model')
        fields = data.get('fields', [])

        existing = UniqueConstraint.objects.filter(model=model)

        if self.instance:
            existing = existing.exclude(id=self.instance.id)

        if self.instance and self.instance.built_in:
            raise PermissionDenied({
                'detail': 'Built-in unique constraint cannot be modified'
            })

        for field in fields:
            if field not in ModelFields.objects.filter(model=model).values_list('name', flat=True):
                raise serializers.ValidationError({
                    'fields': f'Field {field} does not exist in model {model.name}'
                })

        # 在应用层检查数组长度和内容
        for constraint in existing:
            if (len(constraint.fields) == len(fields) and
                    set(constraint.fields) == set(fields)):
                raise serializers.ValidationError({
                    'fields': f'模型 {model.name} 已存在字段组合 {", ".join(fields)} 的唯一性校验规则'
                })

        return data

    def to_representation(self, instance):
        """返回数据时，确保 fields 是列表"""
        data = super().to_representation(instance)
        if isinstance(data['fields'], str):
            try:
                data['fields'] = literal_eval(data['fields'])
            except (ValueError, SyntaxError):
                # 降级处理
                cleaned_str = data['fields'].strip('[]').replace("'", "").replace('"', "")
                data['fields'] = [field.strip() for field in cleaned_str.split(',') if field.strip()]

        return data


class ModelFieldMetaSerializer(serializers.ModelSerializer):
    data = serializers.CharField(required=False, allow_null=True)
    field_name = serializers.CharField(source='model_fields.name', read_only=True)
    field_verbose_name = serializers.CharField(source='model_fields.verbose_name', read_only=True)

    class Meta:
        model = ModelFieldMeta
        fields = ['id', 'model_fields', 'field_name', 'field_verbose_name', 'data']

    def _convert_to_storage_value(self, value, field_config):
        """转换值为存储格式"""
        if value is None:
            return None
        logger.info(f'Converting value {value} to storage format for field {field_config.name}')
        if field_config.type == FieldType.BOOLEAN:
            logger.info(f'Converting boolean value {value} to storage format')
            # 改进布尔值的转换逻辑
            if isinstance(value, bool):
                return str(value).lower()
            if isinstance(value, str):
                return str(value.lower() in ('true', '1', 't', 'y', 'yes')).lower()
            return str(bool(value)).lower()
        elif field_config.validation_rule and field_config.validation_rule.type == ValidationType.ENUM:
            # 枚举值只存储key
            try:
                enum_data = json.loads(field_config.validation_rule.rule)
                if value in enum_data:
                    return value
                raise ValueError(f"Invalid enum key: {value}")
            except json.JSONDecodeError:
                raise ValueError("Invalid enum configuration")
        elif field_config.type in (FieldType.INTEGER, FieldType.FLOAT):
            return str(value) if value is not None else None
        elif field_config.type in (FieldType.STRING, FieldType.TEXT):
            return str(value) if value is not None else None
        # elif field_config.type in (FieldType.DATE, FieldType.DATETIME):
        #     return value.isoformat() if isinstance(value, (datetime, date)) else str(value) if value is not None else None
        elif field_config.type == FieldType.JSON:
            try:
                if isinstance(value, str):
                    return value
                return json.dumps(value, ensure_ascii=False)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
        elif field_config.type == FieldType.PASSWORD:
            return password_handler.encrypt(value)
        elif field_config.type == FieldType.MODEL_REF:
            instance = ModelInstance.objects.filter(id=value).first()
        return str(value) if value is not None else None

    def _convert_from_storage_value(self, value, field_config):
        """从存储格式转换回实际类型"""
        if value is None:
            return None

        if field_config is None:
            raise ValueError("Field configuration is required")
        if field_config.type == FieldType.BOOLEAN:
            # 改进布尔值的转换逻辑
            if isinstance(value, bool):
                return value
            return str(value).lower() in ('true', '1', 't', 'y', 'yes')
        elif field_config.type == FieldType.INTEGER:
            return int(value)
        elif field_config.type == FieldType.FLOAT:
            return float(value)
        elif field_config.type == FieldType.STRING:
            return str(value)
        elif field_config.type == FieldType.TEXT:
            return str(value)
        # elif field_config.type == FieldType.DATE:
        #     if isinstance(value, str):
        #         date_obj = datetime.fromisoformat(value).date()
        #         return date_obj.strftime('%Y-%m-%d')
        #     return value
        # elif field_config.type == FieldType.DATETIME:
        #     if isinstance(value, str):
        #         dt_obj = datetime.fromisoformat(value)
        #         return dt_obj.strftime('%Y-%m-%d %H:%M:%S')
        #     return value
        elif field_config.type == FieldType.JSON:
            return value

        return value

    def validate(self, data):
        field_config = data.get('model_fields')
        value = data.get('data')
        logger.info(f'Validating field {field_config.name} with value {value} type {type(value)}')
        if value is None:
            if field_config.default is not None:
                data['data'] = self._convert_to_storage_value(field_config.default, field_config)
                value = data.get('data')
            else:
                return data
        try:
            # 在验证之前预处理布尔值
            if field_config.type == FieldType.BOOLEAN:
                if isinstance(value, bool):
                    value = str(value).lower()
                    logger.info(f'Converted boolean value to string: {value}')
            validated_value = FieldValidator.validate(value, field_config)
            logger.info(f'Validated value: {validated_value}')
            if validated_value is not None:
                data['data'] = self._convert_to_storage_value(
                    validated_value,
                    field_config
                )
            logger.info(f'Field {field_config.name} converted value: {data["data"]}, type: {type(data["data"])}')
        except ValueError as e:
            raise serializers.ValidationError({
                'detail': str(e),
                'field': field_config.name
            })

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 返回时转换回实际类型
        if 'data' in data and instance.model_fields:
            data['data'] = self._convert_from_storage_value(
                data['data'],
                instance.model_fields
            )
        return data


class ModelFieldMetaNestedSerializer(ModelFieldMetaSerializer):
    class Meta:
        model = ModelFieldMeta
        exclude = ('model', 'model_instance', 'create_user', 'update_user')

    def to_internal_value(self, data):
        """在验证之前预处理数据"""
        if 'data' in data:
            # 将空字符串转换为 None
            if data['data'] == '':
                data['data'] = None
            # 如果是布尔值，预先转换为字符串
            elif isinstance(data['data'], bool):
                data['data'] = str(data['data']).lower()
            # 确保其他非None值转换为字符串
            elif data['data'] is not None:
                data['data'] = str(data['data'])

        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.model_fields.type == FieldType.MODEL_REF and data.get('data'):
            try:
                ref_instance = ModelInstance.objects.get(id=data['data'])
                # 转换为嵌套字典
                data['data'] = {
                    'id': str(ref_instance.id),
                    'instance_name': ref_instance.instance_name
                }
            except ModelInstance.DoesNotExist:
                data['data'] = {
                    'id': data['data'],
                    'instance_name': None
                }
        elif instance.model_fields.type == FieldType.ENUM:
            if instance.model_fields.validation_rule \
                    and instance.model_fields.validation_rule.type == ValidationType.ENUM:
                # 从缓存获取枚举字典
                rule_id = instance.model_fields.validation_rule.id
                enum_dict = ValidationRules.get_enum_dict(rule_id)

                value = data['data']
                data['data'] = {
                    'value': value,
                    'label': enum_dict.get(value, '')
                }
            else:
                data['data'] = {
                    'value': data['data'],
                    'label': None
                }
        elif instance.model_fields.type == FieldType.PASSWORD:
            try:
                data['data'] = password_handler.decrypt(data['data'])
            except:
                data['data'] = None
        return data


class ModelInstanceSerializer(serializers.ModelSerializer):
    fields = serializers.DictField(write_only=True, required=True)
    field_values = serializers.SerializerMethodField()
    instance_group = serializers.SerializerMethodField()

    class Meta:
        model = ModelInstance
        fields = ['id', 'model', 'instance_name',  'create_time', 'update_time',
                  'create_user', 'update_user', 'fields', 'field_values', 'instance_group']
        extra_kwargs = {
            'model': {'required': False},
            'instance_name': {'required': False},
            'create_user': {'required': False},
            'update_user': {'required': False}
        }

    def get_instance_group(self, obj):
        """获取实例关联的分组列表"""
        group_ids = ModelInstanceGroupRelation.objects.filter(
            instance=obj
        ).values_list('group_id', flat=True)
        if group_ids:
            return [str(group_id) for group_id in group_ids]
        return None

    def get_field_values(self, obj):
        """获取实例的字段值"""
        queryset = ModelFieldMeta.objects.filter(
            model_instance=obj
        ).select_related('model_fields')
        return ModelFieldMetaNestedSerializer(
            queryset,
            many=True,
            context=self.context
        ).data

    def validate_fields(self, fields_data):
        """验证字段值"""
        request = self.context.get('request', None)
        from_excel = self.context.get('from_excel', False)
        if from_excel:
            return fields_data
        if request and request.method in ['PUT', 'POST']:
            model = self.initial_data.get('model')
            if not model:
                raise serializers.ValidationError("Model is required")
            if not self.instance:
                # 获取模型的所有必填字段
                required_fields = ModelFields.objects.filter(
                    model=model,
                    required=True
                ).values_list('name', flat=True)

                # 检查必填字段是否都提供了
                missing_fields = [
                    field for field in required_fields
                    if field not in fields_data or fields_data[field] is None
                ]

                if missing_fields:
                    raise serializers.ValidationError({
                        'fields': f'Required fields are missing: {", ".join(missing_fields)}'
                    })
        elif request and request.method == 'PATCH':
            # 检查是否有提供字段
            if not fields_data:
                logger.info(f'Fields data not provided: {fields_data}')
                return fields_data
                # raise serializers.ValidationError("Fields data is required")

            if self.context.get('bulk_update'):
                instances = self.context.get('instances', [])
                if not instances:
                    raise serializers.ValidationError("No instances provided for bulk update")
                models = set(instance.model_id for instance in instances)
                if len(models) > 1:
                    raise serializers.ValidationError(
                        "All instances must belong to the same model"
                    )
                model = instances[0].model
            else:
                model = self.instance.model
            # 检查是否有未知字段
            valid_fields = ModelFields.objects.filter(model=model).values_list('name', flat=True)
            unknown_fields = [field for field in fields_data if field not in valid_fields]
            if unknown_fields:
                raise serializers.ValidationError({
                    'fields': f'Unknown fields: {", ".join(unknown_fields)}'
                })
        return fields_data

    def _process_field_value_from_excel(self, field, value):
        """
        Excel 数据导入特殊处理
        - 密码字段: 明文 -> SM4
        - 枚举字段: value -> key
        - 引用字段: name -> id
        """
        if value is None or value == '':
            return None
        value = str(value)
        try:
            # 密码字段处理
            if field.type == FieldType.PASSWORD:
                sm4_encrypted = password_handler.encrypt_to_sm4(value)
                return sm4_encrypted
            # 枚举字段处理
            elif field.validation_rule and field.validation_rule.type == ValidationType.ENUM:
                enum_dict = ValidationRules.get_enum_dict(field.validation_rule.id)
                reverse_dict = {v: k for k, v in enum_dict.items()}
                if value in reverse_dict:
                    return reverse_dict[value]
                raise ValidationError(f"Invalid enum value: {value}")
            # 引用字段处理
            elif field.type == FieldType.MODEL_REF:
                target_model = field.ref_model
                instance = ModelInstance.objects.filter(
                    model=target_model,
                    instance_name=value
                ).first()
                if instance:
                    return str(instance.id)
                raise ValidationError(f"Invalid model instance name: {value}")

            return value

        except Exception as e:
            raise ValidationError(f"Error processing field {field.name}: {str(e)}")

    def create(self, validated_data):
        fields_data = validated_data.pop('fields')
        instance_group_ids = self.context['request'].data.get('instance_group', [])
        if instance_group_ids and isinstance(instance_group_ids, str):
            instance_group_ids = [instance_group_ids]
        logger.info(f'Processing fields data: {fields_data}')

        try:
            with transaction.atomic():
                model_fields = ModelFields.objects.filter(
                    model=validated_data['model']
                ).select_related('validation_rule')

                field_serializers = []
                for field in model_fields:
                    value = fields_data.get(field.name)
                    if self.context.get('from_excel', False):
                        value = self._process_field_value_from_excel(field, value)
                    logger.info(f'Processed field {field.name} with value {value}')

                    field_meta_data = {
                        'model_fields': field.id,
                        'data': value
                    }
                    serializer = ModelFieldMetaNestedSerializer(data=field_meta_data)
                    serializer.is_valid(raise_exception=True)
                    field_serializers.append(serializer)
                    logger.info(f'Field {field.name} validated successfully')

                logger.info(f'Trying to create model instance: {validated_data}')
                instance = super().create(validated_data)
                for serializer in field_serializers:
                    serializer.save(
                        model=instance.model,
                        model_instance=instance,
                        create_user=validated_data['create_user'],
                        update_user=validated_data['update_user']
                    )
                    logger.info(f'Field meta data created: {serializer.data}')
                logger.info(f'Model instance created: {instance}')

                target_group = None
                logger.info(f'Instance group ids: {instance_group_ids}')
                unassigned_group = ModelInstanceGroup.objects.get(
                    model=instance.model,
                    label='空闲池',
                    built_in=True
                )
                valid_flag = False
                group_cache_to_clear = []
                if unassigned_group.id in instance_group_ids and len(instance_group_ids) > 1:
                    instance_group_ids.remove(unassigned_group.id)
                if instance_group_ids:
                    for instance_group_id in instance_group_ids:
                        target_group = ModelInstanceGroup.objects.filter(
                            model=instance.model,
                            id=instance_group_id
                        ).first()
                        logger.info(f'Target group: {target_group}')
                        if not target_group:
                            logger.error(f'Group {instance_group_id} not found')
                            continue
                        if ModelInstanceGroup.objects.filter(parent=target_group, model=instance.model).exists():
                            logger.error(f'Cannot assign instance to non-leaf group {target_group.label}')
                            continue
                        else:
                            valid_flag = True
                            ModelInstanceGroupRelation.objects.create(
                                instance=instance,
                                group=target_group,
                                create_user=validated_data.get('create_user', 'system'),
                                update_user=validated_data.get('update_user', 'system')
                            )
                            logger.info(f"Added instance {instance.id} to {target_group.label}")
                            group_cache_to_clear.append(target_group)
                if not valid_flag or not instance_group_ids:
                    ModelInstanceGroupRelation.objects.create(
                        instance=instance,
                        group=unassigned_group,
                        create_user=validated_data.get('create_user', 'system'),
                        update_user=validated_data.get('update_user', 'system')
                    )
                    logger.info(f"Added instance {instance.id} to {unassigned_group.label}")
                    group_cache_to_clear.append(unassigned_group)
                ModelInstanceGroup.clear_groups_cache(group_cache_to_clear)

                return instance

        except Exception as e:
            logger.error(f"Error creating model instance: {str(e)}")
            raise serializers.ValidationError(str(e))

    def _format_name_with_validation(self, template, fields_data):
        """格式化并验证名称模板"""
        # 检查必填字段
        if template:
            required_fields = [
                field.strip('{}')
                for field in re.findall(r'\{([^}]+)\}', template)
            ]
        else:
            raise serializers.ValidationError("Instance name template is required")

        empty_fields = [
            field for field in required_fields
            if field not in fields_data or
            fields_data[field] is None or
            fields_data[field] == '' or
            fields_data[field] == []
        ]

        if empty_fields:
            raise serializers.ValidationError(
                f"Required fields are missing: {', '.join(empty_fields)}"
            )

        return template.format(**fields_data)

    def validate_instance_name(self, value):
        """验证实例名称"""
        request = self.context.get('request')
        from_excel = self.context.get('from_excel', False)
        if not request:
            return value

        if not from_excel:
            is_create = request.method == 'POST'
            if 'model' in request.data:
                model = Models.objects.filter(id=request.data['model']).first()
            else:
                model = self.instance.model if self.instance else None
            fields_data = request.data.get('fields', {})
            logger.info(f'Fields data: {fields_data}')

            # 创建时如果未提供name则生成
            if not value and is_create:
                if not model or not model.instance_name_template:
                    raise serializers.ValidationError("Neither instance_name nor instance_name_template provided")

                try:
                    value = self._format_name_with_validation(
                        model.instance_name_template,
                        fields_data
                    )
                except KeyError as e:
                    raise serializers.ValidationError(f"Key not found in fields data: {str(e)}")
                except Exception as e:
                    raise serializers.ValidationError(f"Error generating instance_name: {str(e)}")

            if not value and not is_create and ('instance_name' not in request.data or not request.data['instance_name']):
                try:
                    db_fields = ModelFieldMeta.objects.filter(
                        model_instance=self.instance
                    ).select_related('model_fields').values(
                        'model_fields__name', 'data'
                    )
                    db_fields = {
                        item['model_fields__name']: item['data']
                        for item in db_fields
                    }
                    merged_fields = db_fields.copy()
                    merged_fields.update(fields_data)
                    logger.info(f'Merged fields: {merged_fields}')
                    value = self._format_name_with_validation(
                        self.instance.model.instance_name_template,
                        merged_fields
                    )
                except KeyError as e:
                    raise serializers.ValidationError(f"Key not found in fields data: {str(e)}")
                except Exception as e:
                    raise serializers.ValidationError(f"Error generating instance_name: {str(e)}")

            # 验证唯一性
            if value:
                name_exists_query = ModelInstance.objects.filter(
                    model=model,
                    instance_name=value
                )
                if not is_create:
                    name_exists_query = name_exists_query.exclude(id=self.instance.id)

                if name_exists_query.exists():
                    raise serializers.ValidationError(f"Instance_name {value} already exists in model {model.name}")

            return value
        else:
            return value

    def _validate_field_value(self, field, value):
        """验证单个字段值"""
        field_meta_data = {
            'model_fields': field.id,
            'data': value
        }
        if self.context.get('from_excel', False):
            field_meta_data['data'] = self._process_field_value_from_excel(field, value)
        serializer = ModelFieldMetaNestedSerializer(data=field_meta_data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def bulk_update_fields(self, instances, fields_data, user):
        """批量更新实例字段值"""
        try:
            with transaction.atomic():
                model = instances[0].model

                # 获取字段配置
                fields_config = {
                    field.name: field
                    for field in ModelFields.objects.filter(
                        model=model,
                        name__in=fields_data.keys()
                    ).select_related('validation_rule')
                }

                # 验证字段值（仅验证一次）
                validated_values = {}
                for field_name, value in fields_data.items():
                    field = fields_config.get(field_name)
                    if not field:
                        continue
                    validated_values[field_name] = self._validate_field_value(field, value)

                # 批量更新
                field_metas = []
                for instance in instances:
                    for field_name, validated_data in validated_values.items():
                        field = fields_config[field_name]

                        # 删除可能存在的重复记录
                        ModelFieldMeta.objects.filter(
                            model_instance=instance,
                            model_fields=field
                        ).delete()

                        # 创建新记录
                        meta = ModelFieldMeta.objects.create(
                            model_instance=instance,
                            model_fields=field,
                            data=validated_data['data'],
                            model=instance.model,
                            update_user=user
                        )
                        field_metas.append(meta)
                return field_metas
        except Exception as e:
            logger.error(f"Error in bulk update: {str(e)}")
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        validated_data.pop('field_values', None)
        instances = self.context.get('instances', [instance])
        fields_data = validated_data.pop('fields', {})
        user = validated_data.pop('update_user', 'unknown')

        if fields_data:
            # 执行批量更新
            self.bulk_update_fields(instances, fields_data, user)
        return super().update(instance, validated_data)

    def _convert_to_storage_value(self, value, field_config):
        """转换值为存储格式"""
        if value is None:
            return None
        logger.info(f'Converting value {value} to storage format for field {field_config.name}')
        if field_config.type == FieldType.BOOLEAN:
            logger.info(f'Converting boolean value {value} to storage format')
            # 改进布尔值的转换逻辑
            if isinstance(value, bool):
                return str(value).lower()
            if isinstance(value, str):
                return str(value.lower() in ('true', '1', 't', 'y', 'yes')).lower()
            return str(bool(value)).lower()
        elif field_config.validation_rule and field_config.validation_rule.type == ValidationType.ENUM:
            # 枚举值只存储key
            try:
                enum_data = json.loads(field_config.validation_rule.rule)
                if value in enum_data:
                    return enum_data.get(value)
                raise ValueError(f"Invalid enum key: {value}")
            except json.JSONDecodeError:
                raise ValueError("Invalid enum configuration")
        elif field_config.type in (FieldType.INTEGER, FieldType.FLOAT):
            return str(value) if value is not None else None
        elif field_config.type in (FieldType.STRING, FieldType.TEXT):
            return str(value) if value is not None else None
        elif field_config.type == FieldType.JSON:
            try:
                if isinstance(value, str):
                    return value
                return json.dumps(value, ensure_ascii=False)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
        return str(value) if value is not None else None

    def check_duplicate_fields(self, field_values, model, instance=None):
        matching_instances = set()
        first = True

        for field_name, value in field_values.items():
            # 查找匹配当前字段值的实例
            instances = ModelFieldMeta.objects.filter(
                model_fields__name=field_name,
                model=model,
                data=str(value)
            ).values_list('model_instance', flat=True)

            # 取交集
            if first:
                matching_instances = set(instances)
                first = False
            else:
                matching_instances &= set(instances)

        # 排除当前实例
        if instance:
            matching_instances.discard(instance.id)

        return list(matching_instances)

    def _validate_unique_constraints(self, instance, model, fields_data, is_bulk=False):
        """验证复合字段唯一性约束"""
        constraints = UniqueConstraint.objects.filter(model=model)
        logger.info(f'Found {constraints.count()} unique constraints for model {model.name}')

        for constraint in constraints:
            constraint_fields = constraint.fields
            logger.info(f'Validating unique constraint for fields {", ".join(constraint_fields)}')
            field_values = {}
            has_null = False
            # 收集所有约束字段的值
            for field_name in constraint_fields:
                field_config = ModelFields.objects.filter(name=field_name, model=model).first()
                if field_name in fields_data:
                    # 使用提交的新值
                    field_values[field_name] = fields_data[field_name]
                elif instance:
                    # 获取现有实例的字段值
                    existing_value = ModelFieldMeta.objects.filter(
                        model_instance=instance,
                        model_fields__name=field_name,
                        model=model
                    ).values_list('data', flat=True).first()
                    field_values[field_name] = existing_value
                else:
                    field_values[field_name] = None
                converted_value = self._convert_to_storage_value(
                    field_values[field_name],
                    field_config
                )
                field_values[field_name] = converted_value
                if converted_value is None or converted_value == '':
                    has_null = True

            logger.info(f'Field values: {field_values}')

            # 没有空值或唯一性约束要求验证空值
            if not has_null or constraint.validate_null:
                logger.info(f'Beginning unique constraint validation')
                duplicate_ids = self.check_duplicate_fields(field_values, model, instance)
                if duplicate_ids:
                    field_names = ", ".join(field_values.keys())
                    field_values_str = ", ".join(f"{k}={v}" for k, v in field_values.items())
                    raise ValidationError({
                        'unique_constraint': f'Unique constraint violation: {field_names} with values {field_values_str} already exists'
                    })
                logger.info(f'Unique constraint for fields {", ".join(constraint_fields)} validated successfully')
            else:
                logger.info(f'Unique constraint for fields {", ".join(constraint_fields)} skipped due to null values or constraint settings')
        logger.info(f'All unique constraints validated successfully')

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = self.instance
        model = attrs.get('model')
        if not model:
            model = instance.model
        group = attrs.get('group')
        fields_data = attrs.get('fields', {})

        if group and ModelInstanceGroup.objects.filter(parent=group).exists():
            raise ValidationError({
                'group': 'Cannot assign instance to a non-leaf group'
            })

        is_bulk = self.context.get('bulk_update', False)

        self._validate_unique_constraints(instance, model, fields_data, is_bulk)
        return attrs

    def to_representation(self, instance):
        self.fields['field_values'].context.update(self.context)
        representation = super().to_representation(instance)
        field_values = representation.pop('field_values')
        representation.setdefault('fields', {})
        for field_info in field_values:
            representation['fields'][field_info['field_name']] = field_info['data']
        return representation


class ModelInstanceGroupSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = ModelInstanceGroup
        fields = ['id', 'label', 'children', 'count', 'built_in', 'level', 'model', 'parent']

    def get_children(self, obj):
        children = ModelInstanceGroup.objects.filter(parent=obj)
        return ModelInstanceGroupSerializer(children, many=True).data

    def get_count(self, obj):
        """带缓存的计数方法"""
        cache_key = f'group_count_{obj.id}'
        count = cache.get(cache_key)

        if count is None:
            group_ids = self.get_all_child_groups(obj)
            relations = ModelInstanceGroupRelation.objects.filter(
                group_id__in=group_ids
            )
            unique_instances = set(
                relations.values_list('instance', flat=True)
            )
            count = len(unique_instances)
            cache.set(cache_key, count, timeout=300)

        return count

    def to_representation(self, instance):
        return {
            'id': str(instance.id),
            'label': instance.label,
            'instance_count': self.get_count(instance),
            'built_in': instance.built_in,
            'level': instance.level,
            'children': self.get_children(instance),
        }

    def _get_max_child_depth(self, group):
        """递归获取最大子分组深度"""
        children = ModelInstanceGroup.objects.filter(parent=group)
        if not children:
            return 0
        return 1 + max(self._get_max_child_depth(child) for child in children)

    def _validate_parent_change(self, instance, new_parent):
        """验证父分组变更的合法性"""
        if new_parent:
            new_level = new_parent.level + 1

            max_child_depth = self._get_max_child_depth(instance)

            max_future_level = new_level + max_child_depth

            if max_future_level > 5:
                raise serializers.ValidationError({
                    'parent': f'Moving this group would exceed maximum level (5) for some child groups. '
                    f'Maximum resulting level would be {max_future_level}'
                })

            # 检查是否会导致循环引用
            parent = new_parent
            while parent:
                if parent == instance:
                    raise serializers.ValidationError({
                        'parent': 'Cannot set a group as parent that would create a circular reference'
                    })
                parent = parent.parent

            return new_level
        return 1

    def _get_all_descendants(self, group_id):
        all_descendants = set()
        to_process = {group_id}

        while to_process:
            current_id = to_process.pop()
            children = set(ModelInstanceGroup.objects.filter(
                parent_id=current_id
            ).values_list('id', flat=True))

            new_descendants = children - all_descendants
            to_process.update(new_descendants)
            all_descendants.update(children)

        return all_descendants - {group_id}

    def _update_descendants_level(self, group_id, level_diff):
        """更新所有后代分组的层级"""
        try:
            # 获取所有后代分组ID
            descendant_ids = self._get_all_descendants(group_id)

            # 逐个更新每个后代分组
            for descendant_id in descendant_ids:
                descendant = ModelInstanceGroup.objects.get(id=descendant_id)
                descendant.level += level_diff
                descendant.save(update_fields=['level'])

            if descendant_ids:
                logger.info(
                    f"Updated levels for {len(descendant_ids)} descendants "
                    f"of group {group_id} by {level_diff}"
                )

        except Exception as e:
            logger.error(f"Error updating descendant levels: {str(e)}")
            raise

    def validate(self, attrs):
        """验证分组操作"""
        try:
            instance = self.instance
            model = attrs.get('model')
            parent = attrs.get('parent')
            label = attrs.get('label')
            group = attrs.get('group')

            if instance and instance.built_in:
                requested_changes = set(self.initial_data.keys())
                allowed_changes = {'update_time', 'update_user'}
                restricted_changes = requested_changes - allowed_changes

                if restricted_changes:
                    logger.warning(f"Attempt to modify built-in group {instance.label}")
                    raise PermissionDenied({
                        'detail': f'Cannot modify built-in group "{instance.label}"'
                    })

            if self.instance:
                if 'model' in self.initial_data and str(self.instance.model.id) != self.initial_data['model']:
                    raise serializers.ValidationError({
                        'model': 'Model cannot be modified for ModelInstanceGroup'
                    })
                exists = ModelInstanceGroup.objects.filter(
                    model=model or self.instance.model,
                    parent=parent or self.instance.parent,
                    label=label or self.instance.label
                ).exclude(id=self.instance.id).exists()
            else:
                exists = ModelInstanceGroup.objects.filter(
                    model=model,
                    parent=parent,
                    label=label
                ).exists()

            if exists:
                raise ValidationError({
                    'label': f'Group with label "{label}" already exists for this model'
                })

            if 'parent' in attrs.keys():
                if parent:
                    if model and parent.model != model:
                        raise ValidationError({
                            'model': 'Child group must have the same model as its parent'
                        })

                    expected_level = parent.level + 1
                    if expected_level > 5:
                        raise ValidationError({
                            'level': 'Maximum nesting level (5) exceeded'
                        })

                    if 'level' in attrs and attrs['level'] != expected_level:
                        logger.warning(
                            f"Correcting level from {attrs['level']} to {expected_level} "
                            f"for group {label}"
                        )
                    attrs['level'] = expected_level
                else:
                    attrs['level'] = 1

            return attrs
        except Exception as e:
            logger.error(f"Error validating group: {str(e)}")
            raise serializers.ValidationError(str(e))

    def get_all_child_groups(self, group):
        """递归获取所有子分组ID"""
        group_ids = [group.id]
        children = ModelInstanceGroup.objects.filter(parent=group)
        for child in children:
            group_ids.extend(self.get_all_child_groups(child))
        return group_ids

    def get_instances(self, obj, is_leaf=False):
        """获取分组及其所有子分组下的实例"""
        request = self.context.get('request')
        if not request or not is_leaf:
            return None

        # 检查是否请求了实例列表
        load_instances = request.query_params.get('load_instances')
        if not load_instances or load_instances.lower() != 'true':
            return None

        # 获取所有子分组ID
        group_ids = self.get_all_child_groups(obj)

        # 获取分页参数
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        # 获取所有实例
        instance_ids = ModelInstanceGroupRelation.objects.filter(
            group__in=group_ids
        ).values_list('instance_id', flat=True)
        instances = ModelInstance.objects.filter(
            id__in=instance_ids
        ).order_by('id')  # 添加排序以确保分页一致性

        # 分页
        paginator = StandardResultsSetPagination()
        paginated_instances = paginator.paginate_queryset(instances, request)
        if paginated_instances is not None:
            serializer = ModelInstanceSerializer(paginated_instances, many=True)
            return {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'results': serializer.data
            }

        return None

    def create(self, validated_data):
        """创建分组时设置正确的层级"""
        parent = validated_data.get('parent')
        if parent:
            validated_data['level'] = parent.level + 1
            if parent.built_in and parent.label == '空闲池':
                # complete error information
                raise ValidationError({
                    'Instance group': 'Cannot create group under idle pool'
                })
        else:
            validated_data['level'] = 1
        with transaction.atomic():
            instance = super().create(validated_data)
            if parent and ModelInstanceGroupRelation.objects.filter(group=parent).exists():
                ModelInstanceGroupRelation.objects.filter(group=parent).update(
                    group=instance
                )
                logger.info(f'Moved instances from group {parent.label} to {instance.label}')
                ModelInstanceGroup.clear_group_cache(parent)
        return instance

    def update(self, instance, validated_data):
        """更新分组"""
        try:
            with transaction.atomic():
                groups_to_update = [instance]
                # 如果更改了父分组
                if 'parent' in validated_data and validated_data['parent'] != instance.parent:
                    groups_to_update.append(validated_data['parent'])
                    groups_to_update.append(instance.parent)
                    old_level = instance.level
                    new_level = self._validate_parent_change(instance, validated_data['parent'])
                    level_diff = new_level - old_level

                    instance = super().update(instance, validated_data)

                    # 更新所有子分组的层级
                    if level_diff != 0:
                        self._update_descendants_level(instance.id, level_diff)

                    ModelInstanceGroup.clear_groups_cache(groups_to_update)

                    return instance

                # 如果没有更改父分组，正常更新
                return super().update(instance, validated_data)

        except Exception as e:
            logger.error(f"Error updating group: {str(e)}")
            raise


class ModelInstanceBasicViewSerializer(ModelInstanceSerializer):
    class Meta:
        model = ModelInstance
        fields = ['id', 'model', 'instance_name', 'create_time', 'update_time', 'create_user', 'update_user']

    def to_representation(self, instance):
        return super(ModelInstanceSerializer, self).to_representation(instance)


class ModelInstanceGroupRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelInstanceGroupRelation
        fields = '__all__'

    def _validate_groups_combination(self, instance, new_groups):
        """验证分组的合法性"""
        # 获取新分组中的空闲池数量
        free_pool_groups = [g for g in new_groups if g.label == '空闲池']

        # 如果新分组中同时包含空闲池和其他分组，抛出异常
        if free_pool_groups and len(new_groups) > len(free_pool_groups):
            raise serializers.ValidationError(
                'Cannot assign instance to both idle pool and other groups'
            )

    def _validate_leaf_groups(self, groups):
        """验证是否都是底层分组"""
        non_leaf_groups = [
            g.label for g in groups
            if ModelInstanceGroup.objects.filter(parent=g).exists()
        ]
        if non_leaf_groups:
            raise serializers.ValidationError(
                f"以下分组不是底层分组: {', '.join(non_leaf_groups)}"
            )

    def _handle_group_relations(self, instance, new_groups):
        """处理实例与分组的关联关系"""
        with transaction.atomic():
            # 获取实例当前的所有关联
            current_relations = ModelInstanceGroupRelation.objects.filter(
                instance=instance
            )

            # 如果没有提供新分组，默认使用空闲池
            if not new_groups:
                free_pool = ModelInstanceGroup.objects.get(
                    model=instance.model,
                    label='空闲池'
                )
                current_relations.delete()
                ModelInstanceGroupRelation.objects.create(
                    instance=instance,
                    group=free_pool
                )
                return

            # 如果新分组包含空闲池，删除所有现有关联
            if any(group.label == '空闲池' for group in new_groups):
                current_relations.delete()
            else:
                # 否则只删除空闲池关联
                current_relations.filter(group__label='空闲池').delete()

            # 创建新的关联
            for group in new_groups:
                if not ModelInstanceGroupRelation.objects.filter(
                    instance=instance,
                    group=group
                ).exists():
                    ModelInstanceGroupRelation.objects.create(
                        instance=instance,
                        group=group
                    )

    def create(self, validated_data):
        instance = validated_data['instance']
        group = validated_data['group']

        # 验证是否是底层分组
        self._validate_leaf_groups([group])

        # 验证分组组合
        self._validate_groups_combination(instance, [group])

        # 处理关联关系
        self._handle_group_relations(instance, [group])

        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_instance = validated_data['instance']
        new_group = validated_data['group']

        # 验证是否是底层分组
        self._validate_leaf_groups([new_group])

        # 验证分组组合
        self._validate_groups_combination(new_instance, [new_group])

        # 处理关联关系
        self._handle_group_relations(new_instance, [new_group])

        return super().update(instance, validated_data)


class BulkInstanceGroupRelationSerializer(serializers.Serializer):
    instances = serializers.ListField(child=serializers.UUIDField())
    groups = serializers.ListField(child=serializers.UUIDField())

    class Meta:
        model = ModelInstanceGroupRelation
        fields = '__all__'

    def validate(self, data):
        """验证分组数据"""
        groups = ModelInstanceGroup.objects.filter(id__in=data['groups'])

        # 验证是否为底层分组
        non_leaf_groups = [
            g for g in groups
            if ModelInstanceGroup.objects.filter(parent=g).exists()
        ]
        logger.info(f'Non-leaf groups: {non_leaf_groups}')
        if non_leaf_groups:
            raise serializers.ValidationError(
                f"Non-leaf group exists: {', '.join(g.label for g in non_leaf_groups)}"
            )

        # 验证是否同时包含空闲池和其他分组
        has_unassigned_pool = groups.filter(label='空闲池').exists()
        has_other = groups.exclude(label='空闲池').exists()
        logger.info(f'Has free pool: {has_unassigned_pool}, has other: {has_other}')
        if has_unassigned_pool and has_other:
            raise serializers.ValidationError('Cannot assign instance to both idle pool and other groups')

        return {
            'instances': data['instances'],
            'groups': list(groups),
            'has_unassigned_pool': has_unassigned_pool
        }

    def create(self, validated_data):
        instances = validated_data['instances']
        groups = validated_data['groups']
        has_unassigned_pool = validated_data['has_unassigned_pool']
        created_relations = []
        groups_to_clear = set()
        logger.info(f'Creating group relations for instances {instances} and groups {groups}')

        try:
            with transaction.atomic():
                for instance_id in instances:
                    logger.info(f'Processing instance {instance_id}')
                    instance = ModelInstance.objects.get(id=instance_id)
                    existing_query = ModelInstanceGroupRelation.objects.filter(
                        instance=instance
                    ).select_related('group')
                    groups_to_clear.update(relation.group for relation in existing_query)

                    existing_query.delete()

                    # 创建新的关联关系
                    logger.info(f'Creating new relations for instance {instance_id}')
                    for group in groups:
                        logger.info(f'Creating relation for group {group.label}')
                        relation = ModelInstanceGroupRelation.objects.create(
                            instance=instance,
                            group=group,
                            create_user='system',
                            update_user='system'
                        )
                        created_relations.append(relation)
                    invalidate_obj(instance)

                logger.info(f'Saved {len(created_relations)} relations')
                groups_to_clear.update(
                    relation.group for relation in created_relations
                )
                ModelInstanceGroup.clear_groups_cache(groups_to_clear)
                return created_relations
        except Exception as e:
            logger.error(f'Error creating group relations: {traceback.format_exc()}')
            raise serializers.ValidationError(str(e))


class RelationDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelationDefinition
        fields = '__all__'


class RelationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relations
        fields = '__all__'
