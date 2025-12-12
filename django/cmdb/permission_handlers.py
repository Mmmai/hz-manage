from abc import ABC, abstractmethod
from django.db.models import Q
from access.registry import register_indirect_permission_handler

from .models import *

# 注册过滤处理器
class BaseQueryHandler(ABC):

    @abstractmethod
    def get_query(self, scope, model, username):
        pass


class ModelsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'models':

            # 处理模型相关的权限查询逻辑
            # 不再允许授权模型组权限，忽略该授权
            # model_group_ids = scope['targets'].get('cmdb.modelgroups')
            # if model_group_ids:
            #     query |= Q(model_group_id__in=model_group_ids)

            # 如果分配了实例组权限，动态推导出相关模型权限
            instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            if instance_group_ids:
                related_model_ids = ModelInstanceGroup.objects.filter(
                    id__in=instance_group_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)
            logger.debug(f'CMDB indirect query for models: {query}')

            # 如果分配了模型字段权限，动态推导出相关模型权限
            model_field_ids = scope['targets'].get('cmdb.modelfields')
            if model_field_ids:
                related_model_ids = ModelFields.objects.filter(
                    id__in=model_field_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)

            # 如果分配了模型字段组权限，动态推导出相关模型权限
            model_field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
            if model_field_group_ids:
                related_model_ids = ModelFields.objects.filter(
                    model_field_group_id__in=model_field_group_ids
                ).values_list('model_id', flat=True)
                if related_model_ids:
                    query |= Q(id__in=related_model_ids)

            return query


class ModelGroupsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelgroups':
            # 处理模型组相关的权限查询逻辑
            # 不再允许进行模型级别的授权，忽略该授权
            # model_ids = scope['targets'].get('cmdb.models')
            # # 如果分配了模型权限，动态推导出相关模型组权限
            # if model_ids:
            #     model_group_ids = model.__class__.objects.filter(
            #         id__in=model_ids
            #     ).values_list('model_group_id', flat=True)
            #     if model_group_ids:
            #         query |= Q(id__in=model_group_ids)

            # 如果分配了实例组权限，动态推导出相关模型组权限
            if model_name == 'modelgroups':
                instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
                if instance_group_ids:
                    related_model_group_ids = ModelInstanceGroup.objects.filter(
                        id__in=instance_group_ids
                    ).values_list('model__model_group_id', flat=True)
                    if related_model_group_ids:
                        query |= Q(id__in=related_model_group_ids)

        return query


class ModelInstanceQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelinstance':

            # 模型
            # model_ids = scope['targets'].get('cmdb.models')
            # if model_ids:
            #     query |= Q(model_id__in=model_ids)

            # 模型组
            # model_group_ids = scope['targets'].get('cmdb.modelgroups')
            # if model_group_ids:
            #     models_in_groups = model.__class__.objects.filter(
            #         model_group_id__in=model_group_ids
            #     ).values_list('id', flat=True)
            #     query |= Q(model_id__in=models_in_groups)

            # 实例
            instance_ids = scope['targets'].get('cmdb.modelinstance')
            if instance_ids:
                query |= Q(id__in=instance_ids)

            # 实例组
            instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            children_ids = ModelInstanceGroup.objects.get_all_children_ids(instance_group_ids)
            if instance_group_ids:
                instance_ids = ModelInstanceGroupRelation.objects.filter(
                    group_id__in=set(instance_group_ids) | children_ids
                ).values_list('instance_id', flat=True)
                query |= Q(id__in=instance_ids)
        return query


class ModelFieldsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelfields':
            model_field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
            if model_field_group_ids:
                query |= Q(model_field_group_id__in=model_field_group_ids)

            field_ids = scope['targets'].get('cmdb.modelfields')
            if field_ids:
                query |= Q(id__in=field_ids)

        return query


class ModelFieldGroupsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelfieldgroups':
            model_field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
            if model_field_group_ids:
                query |= Q(id__in=model_field_group_ids)

            # 如果分配了字段权限，从字段推导字段组权限
            field_ids = scope['targets'].get('cmdb.modelfields')
            if field_ids:
                fields_in_groups = ModelFields.objects.filter(
                    id__in=field_ids
                ).values_list('model_field_group_id', flat=True)
                query |= Q(id__in=fields_in_groups)
            return query


class ModelFieldPreferenceQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelfieldpreference':
            # 处理字段偏好设置相关的权限查询逻辑
            query |= Q(create_user=username)  # 返回对应用户创建的偏好设置

        return query


class ModelFieldMetaQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelfieldmeta':
            instance_query = Q()
            field_ids = scope['targets'].get('cmdb.modelfields')
            if field_ids:
                query |= Q(model_fields_id__in=field_ids)

            field_group_ids = scope['targets'].get('cmdb.modelfieldgroups')
            if field_group_ids:
                fields_in_groups = ModelFields.objects.filter(
                    model_field_group_id__in=field_group_ids
                ).values_list('id', flat=True)
                query |= Q(model_fields_id__in=fields_in_groups)
                instance_ids = scope['targets'].get('cmdb.modelinstance')
            if instance_ids:
                instance_query |= Q(model_instance_id__in=instance_ids)

            instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            children_ids = ModelInstanceGroup.objects.get_all_children_ids(instance_group_ids)
            if instance_group_ids:
                related_instance_ids = ModelInstanceGroupRelation.objects.filter(
                    group_id__in=set(instance_group_ids) | children_ids
                ).values_list('instance_id', flat=True)
                instance_query |= Q(model_instance_id__in=related_instance_ids)

            if not query:
                # 没有字段过滤条件时直接设置为空
                query = Q(id__isnull=True)
            query &= instance_query

        return query


class ModelInstanceGroupQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelinstancegroup':
            group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            if group_ids:
                query |= Q(id__in=group_ids)

            children_ids = ModelInstanceGroup.objects.get_all_children_ids(group_ids)
            if children_ids:
                query |= Q(id__in=children_ids)

            # 如果分配了实例权限，从实例推导实例组权限
            instance_ids = scope['targets'].get('cmdb.modelinstance')
            if instance_ids:
                related_group_ids = ModelInstanceGroupRelation.objects.filter(
                    instance_id__in=instance_ids
                ).values_list('group_id', flat=True)
                if related_group_ids:
                    query |= Q(id__in=related_group_ids)

        return query


class ModelInstanceGroupRelationQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelinstancegrouprelation':
            instance_ids = scope['targets'].get('cmdb.modelinstance')
            if instance_ids:
                query |= Q(instance_id__in=instance_ids)

            group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            if group_ids:
                query |= Q(group_id__in=group_ids)
                children_ids = ModelInstanceGroup.objects.get_all_children_ids(group_ids)
                query |= Q(group_id__in=children_ids)

        return query


class ValidationRulesQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'validationrules':
            # 处理校验规则相关的权限查询逻辑
            query |= Q(id__isnull=False)  # 默认全放开

        return query


class ModelFieldPreferenceQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'modelfieldpreference':
            # 处理字段偏好设置相关的权限查询逻辑
            query |= Q(create_user=username)  # 返回对应用户创建的偏好设置

        return query


class UniqueConstraintQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'uniqueconstraint':
            # TODO: 获取具有权限的字段列表，返回对应的唯一约束
            query |= Q(id__isnull=False)  # 默认全放开

        return query


class RelationDefinitionQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'relationdefinition':
            # 默认全放开，允许查看所有关系定义
            # model_ids = scope['targets'].get('cmdb.models')
            # if model_ids:
            #     query |= Q(source_model__id__in=model_ids)
            #     query |= Q(target_model__id__in=model_ids)
            query = Q(id__isnull=False)

        return query


class RelationsQueryHandler(BaseQueryHandler):

    def get_query(self, scope, model, username):
        query = Q()
        model_name = model._meta.model_name

        if model_name == 'relations':
            # 获取用户有权限的实例ID列表
            instance_ids = scope['targets'].get('cmdb.modelinstance')

            # 获取用户有权限的实例组及其子组中的实例
            instance_group_ids = scope['targets'].get('cmdb.modelinstancegroup')
            group_instance_ids = set()

            if instance_group_ids:
                children_ids = ModelInstanceGroup.objects.get_all_children_ids(instance_group_ids)
                all_group_ids = set(instance_group_ids) | children_ids
                group_instance_ids = set(
                    ModelInstanceGroupRelation.objects.filter(
                        group_id__in=all_group_ids
                    ).values_list('instance_id', flat=True)
                )

            # 合并所有可见实例ID
            all_visible_instance_ids = set()
            if instance_ids:
                all_visible_instance_ids.update(instance_ids)
            all_visible_instance_ids.update(group_instance_ids)

            if all_visible_instance_ids:
                # 核心逻辑：源或目标任一可见，则关系可见
                query = Q(source_instance_id__in=all_visible_instance_ids) | \
                    Q(target_instance_id__in=all_visible_instance_ids)
            else:
                # 无任何实例权限时，检查是否有全局权限
                scope_type = scope.get('scope_type', 'none')
                if scope_type == 'all':
                    query = Q(id__isnull=False)
                elif scope_type == 'self':
                    # 自己创建的关系
                    query = Q(create_user=username)
                else:
                    # 无权限
                    query = Q(pk__in=[])

        return query


class CMDBIndirectQueryHandler:
    def __init__(self):
        self.handlers = {
            'models': ModelsQueryHandler(),
            'modelgroups': ModelGroupsQueryHandler(),
            'modelinstance': ModelInstanceQueryHandler(),
            'modelfields': ModelFieldsQueryHandler(),
            'modelfieldgroups': ModelFieldGroupsQueryHandler(),
            'modelfieldpreference': ModelFieldPreferenceQueryHandler(),
            'modelfieldmeta': ModelFieldMetaQueryHandler(),
            'modelinstancegroup': ModelInstanceGroupQueryHandler(),
            'validationrules': ValidationRulesQueryHandler(),
            'modelfieldpreference': ModelFieldPreferenceQueryHandler(),
            'uniqueconstraint': UniqueConstraintQueryHandler(),
            'relationdefinition': RelationDefinitionQueryHandler(),
            'relations': RelationsQueryHandler(),
        }

    def get_query(self, scope, model, username):
        model_name = model._meta.model_name
        handler = self.handlers.get(model_name)
        if handler:
            return handler.get_query(scope, model, username)
        return Q()


#注册到permissions模块
def get_cmdb_indirect_query(scope, model, username):
    """
    CMDB 应用的间接权限处理器。
    """
    cmdb_handler = CMDBIndirectQueryHandler()
    return cmdb_handler.get_query(scope, model, username)


register_indirect_permission_handler('cmdb', get_cmdb_indirect_query)
