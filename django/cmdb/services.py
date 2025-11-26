import logging
from typing import List
from django.db import transaction
from django.db.models import QuerySet
from rest_framework.exceptions import PermissionDenied, ValidationError
from audit.context import audit_context

from mapi.models import UserInfo
from .models import *
from .serializers import *

logger = logging.getLogger(__name__)


class CommonUserValidationService:
    @staticmethod
    def validate_user_permission(user: UserInfo):
        """
        校验用户参数
        """
        if not isinstance(user, UserInfo) or not user.username:
            logger.warning(f"Invalid parameter for user validation: {user}")
            raise ValueError('Invalid user received in cmdb services')
        return user.username


class ModelGroupsService:

    @staticmethod
    def delete_model_group(model_group: ModelGroups, user: UserInfo):
        """
        删除模型组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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
    def create_model(validated_data: dict, user: UserInfo) -> Models:
        """
        创建模型，并自动初始化关联的模型组、字段组、实例组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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
    @transaction.atomic
    def delete_model(model: Models, user: UserInfo):
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
        组装模型详情数据，将字段分组及字段配置注入到模型详情中
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
        为模型列表数据注入含字段配置信息的字段分组数据field_groups
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


class ModelFieldGroupsService:

    @classmethod
    def create_default_field_group(cls, model: Models, user: UserInfo) -> ModelFieldGroups:
        """
        为指定模型创建默认字段组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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

    @classmethod
    @transaction.atomic
    def delete_field_group(cls, field_group: ModelFieldGroups, user: UserInfo):
        """
        删除字段组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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
    pass


class UniqueConstraintService:

    @classmethod
    @transaction.atomic
    def sync_from_instance_name_template(cls, model: Models, instance_name_template: List[str], user: UserInfo, audit_ctx):
        """
        根据模型的实例名称模板同步唯一约束配置
        """
        username = CommonUserValidationService.validate_user_permission(user)

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


class ModelInstanceGroupService:

    @classmethod
    def create_root_group(cls, model: Models, user: UserInfo) -> ModelInstanceGroup:
        """
        为指定模型创建根分组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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
    def create_unassigned_group(cls, model: Models, user: UserInfo) -> ModelInstanceGroup:
        """
        为指定模型创建空闲池分组
        """
        username = CommonUserValidationService.validate_user_permission(user)
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

    @classmethod
    @transaction.atomic
    def delete_group(cls, group, user: UserInfo) -> dict:
        """
        删除一个分组及其所有子分组，并将无其他分组关联的实例迁移到空闲池。
        """
        username = CommonUserValidationService.validate_user_permission(user)
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

    @staticmethod
    def build_model_groups_tree(user: UserInfo) -> list:
        """
        构建跨模型的分组树结构（用于左侧导航栏等）。
        """
        username = CommonUserValidationService.validate_user_permission(user)
        result = []
        pm = PermissionManager(user)

        # 获取用户可见的模型和分组
        visible_model_groups = pm.get_queryset(ModelGroups).prefetch_related('models').order_by('create_time')
        visible_models_qs = pm.get_queryset(Models)
        visible_models_ids = set(visible_models_qs.values_list('id', flat=True))

        # 准备上下文
        all_visible_instance_groups = pm.get_queryset(ModelInstanceGroup).select_related('model', 'parent')
        context = ModelInstanceGroupService._prepare_group_tree_context(all_visible_instance_groups, user)

        # 组装树结构
        for model_group in visible_model_groups:
            models_in_group_data = []
            models_in_group = [m for m in model_group.models.all() if m.id in visible_models_ids]

            if not models_in_group:
                continue

            for model in models_in_group:
                root_instance_groups = context['children_map'].get(None, [])
                model_root_instance_groups = [g for g in root_instance_groups if g.model_id == model.id]

                if model_root_instance_groups:
                    groups_data = ModelInstanceGroupSerializer(
                        model_root_instance_groups,
                        many=True,
                        context=context
                    ).data

                    models_in_group_data.append({
                        'model_id': str(model.id),
                        'model_name': model.name,
                        'model_verbose_name': model.verbose_name,
                        'groups': groups_data
                    })

            if models_in_group_data:
                result.append({
                    'model_group_id': str(model_group.id),
                    'model_group_name': model_group.name,
                    'model_group_verbose_name': model_group.verbose_name,
                    'models': models_in_group_data
                })

        return result

    @staticmethod
    def get_single_model_group_tree(model_id: str, user: UserInfo):
        """
        获取单个模型的分组树（用于管理页面，包含计数）。
        """
        username = CommonUserValidationService.validate_user_permission(user)
        pm = PermissionManager(user)

        # 获取骨架树节点
        visible_groups_qs = pm.get_queryset(ModelInstanceGroup).filter(model_id=model_id)
        skeleton_nodes = ModelInstanceGroupService._get_skeleton_tree_nodes(visible_groups_qs, model_id)

        if not skeleton_nodes:
            return None, {}

        # 准备上下文 (包含计数)
        context = ModelInstanceGroupService._prepare_group_tree_context(skeleton_nodes, user)

        # 获取绝对根节点
        # 优化：直接从 skeleton_nodes 中查找根节点，避免再次查询 DB
        # 根节点是 parent 为 None 的节点
        absolute_root_node = next((n for n in skeleton_nodes if n.parent_id is None), None)

        if not absolute_root_node:
            absolute_root_node = ModelInstanceGroup.objects.get_root_group(model_id)

        return absolute_root_node, context

    @staticmethod
    def _prepare_group_tree_context(groups_queryset: QuerySet, user: UserInfo) -> dict:
        """
        准备树结构序列化所需的上下文（子节点映射、实例计数等）。
        """
        username = CommonUserValidationService.validate_user_permission(user)
        context = {}
        pm = PermissionManager(user)

        # 构建 children_map
        children_map = {}
        for group in groups_queryset:
            parent_id = str(group.parent_id) if group.parent_id else None
            children_map.setdefault(parent_id, []).append(group)
        context['children_map'] = children_map

        # 计算实例数量
        all_group_ids = {group.id for group in groups_queryset}

        descendant_map = {}
        for group in groups_queryset:
            descendants = ModelInstanceGroupService._get_all_descendants(group, groups_queryset)
            descendant_ids = {g.id for g in descendants}
            descendant_map[group.id] = descendant_ids | {group.id}
            all_group_ids.update(descendant_ids)

        visible_instances_qs = pm.get_queryset(ModelInstance)

        relations = ModelInstanceGroupRelation.objects.filter(
            group_id__in=all_group_ids,
            instance__in=visible_instances_qs
        ).values('group_id', 'instance_id').distinct()

        instance_counts = {}
        for group in groups_queryset:
            group_and_descendant_ids = descendant_map[group.id]
            unique_instances = {
                r['instance_id'] for r in relations if r['group_id'] in group_and_descendant_ids
            }
            instance_counts[group.id] = len(unique_instances)

        context['instance_counts'] = instance_counts
        return context

    @staticmethod
    def _get_all_descendants(group, all_groups):
        """递归获取后代"""
        descendants = []
        children = [g for g in all_groups if g.parent_id == group.id]
        for child in children:
            descendants.append(child)
            descendants.extend(ModelInstanceGroupService._get_all_descendants(child, all_groups))
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
    @transaction.atomic
    def update_group_position(group: ModelInstanceGroup, target_id: str, position: str, user: UserInfo):
        """
        更新分组位置（排序/移动）。
        """
        username = CommonUserValidationService.validate_user_permission(user)
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

    @staticmethod
    def _get_skeleton_tree_nodes(visible_groups_qs, model_id: str):
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
        ancestors = ModelInstanceGroupService._get_all_ancestors(visible_groups_qs)
        ancestor_ids = {g.id for g in ancestors}

        total_ids = visible_ids | ancestor_ids
        return list(ModelInstanceGroup.objects.filter(id__in=total_ids).order_by('level', 'order'))

    @staticmethod
    def get_tree(model: Models, user: UserInfo):
        """
        获取指定模型的实例分组树结构（用于拓扑图或选择器，包含具体实例信息）。
        """
        username = CommonUserValidationService.validate_user_permission(user)
        pm = PermissionManager(user)

        # 获取骨架树节点
        visible_groups_qs = pm.get_queryset(ModelInstanceGroup).filter(model=model)
        all_nodes = ModelInstanceGroupService._get_skeleton_tree_nodes(visible_groups_qs, str(model.id))

        if not all_nodes:
            return []

        # 准备详细上下文
        context = ModelInstanceGroupService._build_tree_context(all_nodes, model, user)

        # 提取根节点
        roots = [n for n in all_nodes if n.parent_id is None]

        # 序列化数据
        # TODO: 转移逻辑
        serializer = ModelInstanceGroupTreeSerializer(roots, many=True, context=context)
        return serializer.data

    @staticmethod
    def _build_tree_context(all_nodes, model: Models, user: UserInfo) -> dict:
        """
        通用逻辑：构建树所需的详细上下文（包含 children_map, relation_map, instance_map）。
        适用于需要展示具体实例的场景 (如 get_tree)。
        """
        username = CommonUserValidationService.validate_user_permission(user)
        context = {}
        pm = PermissionManager(user)

        # 1. 构建 children_map
        children_map = {}
        node_ids = set()
        for node in all_nodes:
            node_ids.add(node.id)
            if node.parent_id:
                children_map.setdefault(str(node.parent_id), []).append(node)
        context['children_map'] = children_map

        # 2. 获取用户可见的实例
        visible_instances_qs = pm.get_queryset(ModelInstance).filter(model=model)
        visible_instance_ids = set(visible_instances_qs.values_list('id', flat=True))

        # 3. 构建 relation_map (Group -> Visible Instances)
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

        # 4. 构建 instance_map
        instance_map = {}
        if relevant_instance_ids:
            insts = ModelInstance.objects.filter(id__in=relevant_instance_ids).values('id', 'instance_name')
            instance_map = {str(i['id']): i['instance_name'] for i in insts}
        context['instance_map'] = instance_map

        return context
