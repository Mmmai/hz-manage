import logging
from django.db import transaction
from django.contrib.auth.models import AbstractBaseUser
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)


class CommonUserValidationService:
    @staticmethod
    def validate_user_permission(user: AbstractBaseUser):
        """
        校验用户参数
        """
        if not isinstance(user, AbstractBaseUser) or not user.username:
            logger.warning(f"Invalid parameter for user validation: {user}")
            raise ValueError('Invalid user received in cmdb services')
        return user.username


class ModelsService:

    @staticmethod
    def create_model(validated_data: dict, user: AbstractBaseUser) -> Models:
        """
        创建模型，并自动初始化关联的默认分组
        """
        username = CommonUserValidationService.validate_user_permission(user)
        try:
            with transaction.atomic():
                # 没有指定分组时分配到默认组内
                if not validated_data.get('model_group'):
                    validated_data['model_group'] = ModelGroups.get_default_model_group()

                validated_data['create_user'] = username
                validated_data['update_user'] = username
                model = Models.objects.create(**validated_data)
                logger.info(f"Created model: {model.name} by user: {username}")

                # 创建默认字段分组 (basic)
                ModelFieldGroups.get_default_field_group(model)
                logger.info(f"Created default field group for model: {model.name}")

                # 创建默认实例分组 (root/unassigned)
                ModelInstanceGroup.get_root_group(model)
                ModelInstanceGroup.get_unassigned_group(model)
                logger.info(f"Created initial instance groups for model: {model.name}")

                return model
        except Exception as e:
            logger.error(f"Error creating model and initial groups: {str(e)}")
            raise ValidationError(f"Failed to create model: {str(e)}")

    @staticmethod
    @transaction.atomic
    def delete_model(model: Models, user: AbstractBaseUser):
        """
        删除模型
        """
        username = CommonUserValidationService.validate_user_permission(user)
        if model.built_in:
            logger.warning(f"Attempt to delete built-in model denied: {model.name} by {username}")
            raise PermissionDenied({'detail': 'Built-in model cannot be deleted'})

        # TODO: 校验模型实例
        model.delete()
        logger.info(f"Model deleted successfully: {model.name} by {username}")

    @staticmethod
    def get_model_details(model: Models, field_groups_qs, fields_qs) -> dict:
        """
        组装模型详情数据（包含字段分组和字段）
        """
        # 序列化基础数据
        model_data = ModelsSerializer(model).data
        field_groups_data = ModelFieldGroupsSerializer(field_groups_qs, many=True).data
        fields_data = ModelFieldsSerializer(fields_qs, many=True).data

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
    def enrich_models_list(models_data: list, field_groups_qs, fields_qs, instances_qs) -> list:
        """
        为模型列表数据填充字段分组和字段信息
        """
        # 计算实例数量
        counts = instances_qs.values('model').annotate(count=models.Count('id'))
        instance_counts = {str(item['model']): item['count'] for item in counts}

        # 序列化数据
        models_data = ModelsSerializer(
            models_data,
            many=True,
            context={'instance_counts_map': instance_counts}
        ).data
        field_groups_data = ModelFieldGroupsSerializer(field_groups_qs, many=True).data
        fields_data = ModelFieldsSerializer(fields_qs, many=True).data

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


class ModelFieldsService:
    pass
