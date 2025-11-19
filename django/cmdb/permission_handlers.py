from django.db.models import Q
from permissions.registry import register_indirect_permission_handler

from .models import *


def get_cmdb_indirect_query(scope, model, username):
    """
    CMDB 应用的间接权限处理器。
    """
    model_name = model._meta.model_name

    query = Q()

    if model_name == 'models':
        model_group_ids = scope['targets'].get('cmdb.modelgroups')
        if model_group_ids:
            query |= Q(model_group_id__in=model_group_ids)

        # 如果分配了实例组权限，动态推导出相关模型权限
        instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
        if instance_group_ids:
            related_model_ids = ModelInstanceGroup.objects.filter(
                id__in=instance_group_ids
            ).values_list('model_id', flat=True)
            if related_model_ids:
                query |= Q(id__in=related_model_ids)

    if model_name == 'modelinstance':

        # 模型
        model_ids = scope['targets'].get('cmdb.models')
        if model_ids:
            query |= Q(model_id__in=model_ids)

        # 模型组
        model_group_ids = scope['targets'].get('cmdb.modelgroups')
        if model_group_ids:
            models_in_groups = model.__class__.objects.filter(
                model_group_id__in=model_group_ids
            ).values_list('id', flat=True)
            query |= Q(model_id__in=models_in_groups)

        # 实例组
        from .models import ModelInstanceGroupRelation
        instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
        if instance_group_ids:
            instance_ids = ModelInstanceGroupRelation.objects.filter(
                group_id__in=instance_group_ids
            ).values_list('instance_id', flat=True)
            query |= Q(id__in=instance_ids)

    if model_name == 'modelfields':
        model_field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
        if model_field_group_ids:
            query |= Q(model_field_group_id__in=model_field_group_ids)

        field_ids = scope['targets'].get('cmdb.modelfields')
        if field_ids:
            query |= Q(id__in=field_ids)

    return query


register_indirect_permission_handler('cmdb', get_cmdb_indirect_query)
