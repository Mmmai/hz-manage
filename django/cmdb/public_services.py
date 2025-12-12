from .services import ModelInstanceService
from .serializers import ModelInstanceSerializer
from .models import ModelInstance, ModelInstanceGroup, ModelInstanceGroupRelation, ModelFieldMeta
from .constants import FieldType
from .utils import password_handler
from access.manager import PermissionManager


class PublicModelInstanceService:
    """对外的模型实例服务类"""

    @staticmethod
    def update_instance(instance, fields, user, **kwargs):
        """更新模型实例"""
        serializer = ModelInstanceSerializer(
            instance,
            data=fields,
            partial=True,
            context={'request_user': user}
        )
        serializer.is_valid(raise_exception=True)
        return ModelInstanceService.update_instance(
            instance,
            serializer.validated_data,
            user.username,
            **kwargs
        )

    @staticmethod
    def get_instance_field_value(obj, field_name):
        """获取节点关联的实例IP"""
        field_value = ModelFieldMeta.objects.filter(
            model_instance=obj,
            model_fields__name=field_name
        ).select_related('model_fields').first()
        if field_value:
            field = field_value
            if field.model_fields.type == FieldType.PASSWORD:
                return password_handler.decrypt_to_plain(field.data)
            else:
                return field.data
        return None

    @staticmethod
    def get_instance_fields(obj, field_name_list):
        """获取节点关联的实例字段值"""
        res = {}
        field_values = ModelFieldMeta.objects.filter(
            model_instance=obj,
            model_fields__name__in=field_name_list
        ).select_related('model_fields')

        for field in field_values:
            if field.model_fields.type == FieldType.PASSWORD:
                res[field.model_fields.name] = password_handler.decrypt_to_plain(field.data)
            else:
                res[field.model_fields.name] = field.data
        return res

    @staticmethod
    def get_instances_by_group_id(group_id, model_id, user) -> list:
        """通过分组ID获取模型实例列表"""
        children_ids = ModelInstanceGroup.objects.get_all_children_ids([group_id], model_id=model_id)
        children_ids.add(group_id)
        pm = PermissionManager(user)
        instances_qs = (
            pm.get_queryset(ModelInstanceGroupRelation)
            .filter(group_id__in=children_ids)
            .select_related('model_instance')
        )
        instances = list(set(rel.model_instance for rel in instances_qs if rel.model_instance))
        return instances
