import time
import sys
import traceback
import logging
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, post_migrate
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.core.cache import cache
from cacheops import invalidate_model
from django.db import transaction
from django.db.utils import OperationalError
from .config import BUILT_IN_MODELS, BUILT_IN_RELATION_DEFINITION, BUILT_IN_VALIDATION_RULES
from node_mg.utils import sys_config
from .utils.zabbix import ZabbixAPI
from .constants import ValidationType
from .message import instance_group_relation_updated
from .models import *
from audit.context import audit_context
logger = logging.getLogger(__name__)


@receiver(post_save, sender=ModelFields)
def create_field_meta_for_instances(sender, instance, created, **kwargs):
    if created:
        # 获取所有关联的 ModelInstance 实例
        instances = ModelInstance.objects.filter(model=instance.model)

        for model_instance in instances:
            # 检查是否已经存在对应的 ModelFieldMeta 记录
            if not ModelFieldMeta.objects.filter(
                model_instance=model_instance,
                model_fields=instance
            ).exists():
                field_value = instance.default if instance.default is not None else None

                if instance.required and field_value is None:
                    raise ValidationError(f'Required field {instance.name} is missing default value')

                ModelFieldMeta.objects.create(
                    model=instance.model,
                    model_instance=model_instance,
                    model_fields=instance,
                    data=field_value,
                    create_user='system',
                    update_user='system'
                )


def get_model_group(name, model, verbose_name=None, description=None):
    group, created = ModelFieldGroups.objects.get_or_create(
        name=name,
        model=model,
        defaults={
            'verbose_name': verbose_name,
            'built_in': True,
            'editable': False,
            'description': description,
            'create_user': 'system',
            'update_user': 'system'
        }
    )
    return group


def _create_model_and_fields(model_name, model_config, model_group=None):
    """创建内置模型和相关字段"""
    from .models import (
        Models,
        ModelFields,
        ValidationRules,
        ModelFieldPreference,
        UniqueConstraint,
    )
    from .serializers import (
        ModelsSerializer,
        ModelFieldsSerializer,
        ModelFieldPreferenceSerializer,
        UniqueConstraintSerializer,
    )
    try:
        model_data = {
            'name': model_name,
            'verbose_name': model_config.get('verbose_name', ''),
            'model_group': model_group.id if model_group else None,
            'icon': model_config.get('icon', ''),
            'description': model_config.get('description', ''),
            'built_in': True,
            'create_user': 'system',
            'update_user': 'system'
        }
        with transaction.atomic():
            # 检查模型是否存在
            model = Models.objects.filter(name=model_name).first()
            if not model:
                model_serializer = ModelsSerializer(data=model_data)
                if model_serializer.is_valid():
                    model = model_serializer.save()
                    logger.info(f"Created new model: {model_name}")
                else:
                    logger.error(f"Model validation failed: {model_serializer.errors}")
                    raise ValueError(f"Invalid model data for {model_name}")

            group = None
            if model_name == 'hosts':
                group = get_model_group('auto_discover', model, '自动发现', '自动发现的配置信息')

            group_order = {}
            for index, field_config in enumerate(model_config.get('fields', [])):
                field_name = field_config['name']
                field = ModelFields.objects.filter(
                    model=model,
                    name=field_name
                ).first()

                if not field:
                    validation_rule = ValidationRules.objects.filter(name=field_config.get('validation_rule')).first()
                    ref_model = None
                    if field_config['type'] == 'model_ref':
                        ref_model = Models.objects.filter(name=field_config['ref_model']).first()
                        if not ref_model:
                            logger.error(f"Model reference {field_config['ref_model']} not found")
                            raise ValueError(f"Model reference {field_config['ref_model']} not found")
                    logger.debug(f'{type(validation_rule)}, validation_rule: {validation_rule}')

                    group_name = field_config.get('group', 'default')
                    group_order[group_name] = group_order.get(group_name, 0) + 1

                    field_data = {
                        'model': model.id,
                        'name': field_name,
                        'verbose_name': field_config.get('verbose_name', ''),
                        'type': field_config['type'],
                        'required': field_config.get('required', False),
                        'editable': field_config.get('editable', True),
                        'description': field_config.get('description', ''),
                        'order': group_order[group_name],
                        'validation_rule': validation_rule.id if validation_rule else None,
                        'default': field_config.get('default', None),
                        'built_in': True,
                        'ref_model': ref_model.id if ref_model else None,
                        'model_field_group': group.id if group and field_config.get('group') else None,
                        'create_user': 'system',
                        'update_user': 'system'
                    }

                    field_serializer = ModelFieldsSerializer(data=field_data)
                    if field_serializer.is_valid(raise_exception=True):
                        field_serializer.save()
                        logger.info(f"Created new field {field_name} for model {model_name}")
                    else:
                        logger.error(f"Field validation failed: {field_serializer.errors}")
                        raise ValueError(f"Invalid field data for {field_name}")

            # 创建字段偏好设置
            if not ModelFieldPreference.objects.filter(model=model).exists():
                preferred_fields = list(
                    ModelFields.objects.filter(
                        model=model
                    ).order_by('order').values_list('id', flat=True)[:8]
                )

                preference_data = {
                    'model': model.id,
                    'fields_preferred': [str(f) for f in preferred_fields],
                    'create_user': 'system',
                    'update_user': 'system'
                }

                preference_serializer = ModelFieldPreferenceSerializer(data=preference_data)
                if preference_serializer.is_valid(raise_exception=True):
                    preference_serializer.save()
                    logger.info(f"Created field preference for model {model_name}")
                else:
                    logger.error(f"Preference validation failed: {preference_serializer.errors}")

            # 为每个内置模型添加一个默认的唯一性校验规则：使用ip字段校验
            # 只给hosts 和 network设备添加
            # if model_name in ['hosts', 'switches', 'firewalls', 'dwdm', 'virtual_machines']:
            #     field_ip = ModelFields.objects.filter(
            #         model=model,
            #         name='ip'
            #     ).first()
            #     if not UniqueConstraint.objects.filter(
            #         model=model,
            #         fields=[str(field_ip.id)]
            #     ).exists() and field_ip:
            #         # 创建唯一性约束
            #         unique_constraint_data = {
            #             'model': model.id,
            #             'fields': [str(field_ip.id)],
            #             'built_in': True,
            #             'create_user': 'system',
            #             'update_user': 'system'
            #         }
            #         unique_constraint_serializer = UniqueConstraintSerializer(data=unique_constraint_data)
            #         if unique_constraint_serializer.is_valid(raise_exception=True):
            #             unique_constraint_serializer.save()
            #             logger.info(f"Created unique constraint for model {model_name}")
            #         else:
            #             logger.error(f"Unique constraint validation failed: {unique_constraint_serializer.errors}")

    except Exception as e:
        logger.error(f"Error creating model and fields for {model_name}: {str(e)}")
        raise


def _initialize_validation_rules():
    """初始化验证规则"""
    from .models import ValidationRules
    from .serializers import ValidationRulesSerializer

    invalidate_model(ValidationRules)
    for name, rule_config in BUILT_IN_VALIDATION_RULES.items():
        try:
            with transaction.atomic():
                rule_data = {
                    'name': name,
                    'verbose_name': rule_config['verbose_name'],
                    'field_type': rule_config['field_type'],
                    'type': rule_config['type'],
                    'rule': rule_config['rule'],
                    'built_in': True,
                    'editable': rule_config.get('editable', True),
                    'description': rule_config['description'],
                    'create_user': 'system',
                    'update_user': 'system'
                }
                if ValidationRules.objects.filter(name=name).exists():
                    # logger.info(f"Validation rule {name} already exists, skipping")
                    continue
                rule_serializer = ValidationRulesSerializer(data=rule_data)
                if rule_serializer.is_valid(raise_exception=True):
                    rule_serializer.save()
                    logger.info(f"Created validation rule: {name}")
                else:
                    logger.error(f"Validation rule validation failed: {rule_serializer.errors}")

        except Exception as e:
            logger.error(f"Error creating validation rule {name}: {str(e)}")
            raise


def _initialize_model_groups():
    """初始化模型分组"""
    from .models import ModelGroups
    from .serializers import ModelGroupsSerializer
    
    invalidate_model(ModelGroups)
    
    with transaction.atomic():
        # 创建初始模型组
        group_configs = [
            {'name': 'host', 'verbose_name': '主机'},
            {'name': 'network', 'verbose_name': '网络设备'},
            {'name': 'security', 'verbose_name': '安全设备'},
            {'name': 'resource', 'verbose_name': '资源组'},
            {'name': 'application', 'verbose_name': '应用服务'},
            {'name': 'others', 'verbose_name': '其他'}
        ]
        model_groups = {}
        for group_config in group_configs:
            group = ModelGroups.objects.filter(name=group_config['name']).first()
            if not group:
                group_data = {
                    **group_config,
                    'built_in': True,
                    'editable': False,
                    'description': f"{group_config['verbose_name']}模型组",
                    'create_user': 'system',
                    'update_user': 'system'
                }

                group_serializer = ModelGroupsSerializer(data=group_data)
                if group_serializer.is_valid():
                    group = group_serializer.save()
                    logger.info(f"Created new model group: {group_config['name']}")
                else:
                    logger.error(f"Model group validation failed: {group_serializer.errors}")
                    raise ValueError(f"Invalid model group data for {group_config['name']}")

            model_groups[group_config['name']] = group


def _initialize_relation_definition():
    """初始化关系定义"""
    from .models import RelationDefinition, Models, ValidationRules
    from .serializers import RelationDefinitionSerializer
    models_dict = {model.name: str(model.id) for model in Models.objects.all()}

    invalidate_model(RelationDefinition)
    for relation_config in BUILT_IN_RELATION_DEFINITION:
        try:
            with transaction.atomic():
                s_m = [models_dict.get(name) for name in relation_config['source_model']]
                t_m = [models_dict.get(name) for name in relation_config['target_model']]
                a_s = relation_config['attribute_schema']
                for t, a in a_s.items():
                    for attr_name, attr_config in a.items():
                        if attr_config['type'] == 'enum' and 'validation_rule' in attr_config:
                            vr = ValidationRules.objects.filter(name=attr_config['validation_rule']).first()
                            if vr:
                                attr_config['validation_rule'] = str(vr.id)
                            else:
                                logger.error(f"Validation rule {attr_config['validation_rule']} not found for relation attribute")
                                raise ValueError(f"Validation rule {attr_config['validation_rule']} not found")
                relation_data = {
                    'name': relation_config['name'],
                    'built_in': True,
                    'topology_type': relation_config['topology_type'],
                    'forward_verb': relation_config['forward_verb'],
                    'reverse_verb': relation_config['reverse_verb'],
                    'source_model': s_m,
                    'target_model': t_m,
                    'description': relation_config['description'],
                    'attribute_schema': a_s,
                    'built_in': True,
                    'create_user': 'system',
                    'update_user': 'system'
                }
                if RelationDefinition.objects.filter(name=relation_config['name']).exists():
                    # logger.info(f"Relation definition {relation_config['name']} already exists, skipping")
                    continue
                relation_serializer = RelationDefinitionSerializer(data=relation_data)
                if relation_serializer.is_valid(raise_exception=True):
                    relation_serializer.save()
                    logger.info(f"Created relation definition: {relation_config['name']}")
                else:
                    logger.error(f"Relation definition validation failed: {relation_serializer.errors}")
        except Exception as e:
            logger.error(f"Error creating relation definition {relation_config['name']}: {str(e)}")
            raise
    
@receiver(post_migrate)
def initialize_cmdb(sender, **kwargs):
    """初始化 CMDB 应用"""
    # 仅允许通过 migrate cmdb 命令触发初始化
    if sender.name != 'cmdb':
        return
    logger.info(f'Initializing CMDB application')
    with audit_context(
        request_id='migrate_cmdb_init',
        correlation_id='migrate_cmdb_init',
        operator='system',
        operator_ip='127.0.0.1',
        comment='初始化 CMDB 应用'
    ):
        try:
            # 创建模型分组
            _initialize_model_groups()

            # 创建验证规则
            _initialize_validation_rules()

            # 创建内置模型及其字段配置
            model_groups = {group.name: group for group in ModelGroups.objects.all()}
            for model_name, model_config in BUILT_IN_MODELS.items():
                group_name = model_config.get('model_group')
                model_group = model_groups.get(group_name, model_groups['others'])
                _create_model_and_fields(model_name, model_config, model_group)

            _initialize_relation_definition()
            
            logger.info(f'CMDB application initialized successfully')
        except OperationalError:
            logger.warning("Database not ready, skipping initialization")
        except Exception as e:
            logger.error(f"Error during CMDB initialization: {traceback.format_exc()}")


@receiver(post_save, sender=ModelFieldMeta)
def update_instance_name_on_field_change(sender, instance, created, **kwargs):
    """当字段值更新时，自动更新实例名称"""
    model_instance = instance.model_instance
    model = model_instance.model

    if not model.instance_name_template:
        return

    # 如果修改的字段不在模板中，无需更新名称
    if instance.model_fields.name not in model.instance_name_template:
        return

    try:
        # 生成新名称
        new_name = model_instance.generate_name()

        # 如果无法生成有效名称或名称未变，则不更新
        if not new_name or new_name == model_instance.instance_name:
            return

        # 检查名称唯一性
        if ModelInstance.objects.filter(
            model=model,
            instance_name=new_name
        ).exclude(id=model_instance.id).exists():
            logger.warning(
                f"Duplicate instance name detected: {new_name} for model {model.name}"
            )
            return

        # 更新名称
        model_instance.instance_name = new_name
        #model_instance.save(update_fields=['instance_name', 'update_time'])
        #logger.info(f"Updated instance name to {new_name} for instance {model_instance.id}")
    except Exception as e:
        logger.error(f"Error generating instance name: {str(e)}")


# @receiver(post_save, sender=ModelInstance)
# def sync_zabbix_host(sender, instance, created, **kwargs):
#     print(4444)
#     """同步Zabbix主机"""
#     if not sys_config.is_zabbix_sync_enabled():
#         return

#     def delayed_process():
#         try:
#             model = Models.objects.get(id=instance.model_id)
#             if model.name != 'hosts':
#                 return

#             # 获取主机信息
#             host_info = {}
#             field_values = ModelFieldMeta.objects.filter(
#                 model_instance=instance
#             ).select_related('model_fields')

#             for field in field_values:
#                 logger.debug(f"Field: {field.model_fields.name}, Value: {field.data}")
#                 if field.model_fields.name == 'ip':
#                     host_info[field.model_fields.name] = field.data
#                 elif field.model_fields.name == 'system_password':
#                     host_info[field.model_fields.name] = password_handler.decrypt_to_plain(field.data)

#             groups = []
#             instance_group_relations = ModelInstanceGroupRelation.objects.filter(
#                 instance=instance
#             ).select_related('group')
#             for relation in instance_group_relations:
#                 if relation.group.path not in ['所有', '所有/空闲池']:
#                     groups.append(relation.group.path.replace('所有/', ''))

#             if not host_info.get('ip'):
#                 logger.warning(f"Missing required host information for instance {instance.id}")
#                 return

#             logger.info(f"Syncing Zabbix host for IP: {host_info.get('ip')} instance: {instance.id}")

#             # 异步创建Zabbix主机
#             setup_host_monitoring.delay(
#                 instance_id=str(instance.id),
#                 instance_name=instance.instance_name,
#                 ip=host_info['ip'],
#                 password=host_info['system_password'],
#                 groups=groups
#             )

#         except Exception as e:
#             logger.error(f"Failed to sync Zabbix host: {str(e)}")

#     transaction.on_commit(delayed_process)
#     logger.info(f'Syncing Zabbix host for instance {instance.id} completed')


@receiver(pre_delete, sender=ModelInstance)
def prepare_delete_zabbix_host(sender, instance, **kwargs):
    """准备删除Zabbix主机"""
    if not sys_config.is_zabbix_sync_enabled():
        return
    logger.info(f"Preparing to delete Zabbix host for instance {instance.id}")
    try:
        a = time.perf_counter()
        model = Models.objects.get(id=instance.model_id)
        if model.name != 'hosts':
            return

        # 获取主机信息
        cache_key = f'delete_zabbix_host_{instance.id}'
        host_info = {}
        field_values = ModelFieldMeta.objects.filter(
            model_instance=instance
        ).select_related('model_fields')

        for field in field_values:
            logger.debug(f"Field: {field.model_fields.name}, Value: {field.data}")
            if field.model_fields.name == 'ip':
                host_info[field.model_fields.name] = field.data
        host_info.update({
            'instance_id': instance.id,
            'instance_name': instance.instance_name,
        })
        cache.set(cache_key, host_info, timeout=60)
        b = time.perf_counter()
        logger.debug(f'Cached host information for instance {instance.id}: {host_info} in {b - a}s')
    except Exception as e:
        logger.error(f"Failed to prepare delete Zabbix host: {str(e)}")


# @receiver(post_delete, sender=ModelInstance)
# def delete_zabbix_host(sender, instance, **kwargs):
#     """删除Zabbix主机"""
#     if not sys_config.is_zabbix_sync_enabled():
#         return
#     a = time.perf_counter()

#     def delayed_process():
#         logger.debug(f'Delayed process started for instance {instance.id}')
#         try:
#             model = Models.objects.get(id=instance.model_id)
#             if model.name != 'hosts':
#                 return

#             # 获取主机信息
#             cache_key = f'delete_zabbix_host_{instance.id}'
#             cache_data = cache.get(cache_key)
#             if not cache_data:
#                 logger.warning(f"Missing required host information for instance {instance.id}")
#                 return

#             logger.info(f"Deleting Zabbix host for IP: {cache_data.get('ip')} instance: {instance.id}")
#             # 异步删除Zabbix主机
#             setup_host_monitoring.delay(
#                 instance_id=str(instance.id),
#                 instance_name=instance.instance_name,
#                 ip=cache_data.get('ip'),
#                 password=None,
#                 delete=True
#             )

#         except Exception as e:
#             logger.error(f"Failed to delete Zabbix host: {str(e)}")

#     logger.debug(f'Scheduling delayed process for instance {instance.id}')
#     transaction.on_commit(delayed_process)
#     b = time.perf_counter()
#     logger.info(f'Deleting Zabbix host for instance {instance.id} completed in {b - a}s')

# 此信号弃用，实例自身path由模型方法主动计算，子节点path更新由update_descendant_paths处理
# @receiver(post_save, sender=ModelInstanceGroup)
def handle_group_path(sender, instance, created, **kwargs):
    """
    处理实例分组path更新和Zabbix主机组同步
    使用递归方式处理所有子节点
    """
    if not sys_config.is_zabbix_sync_enabled():
        return
    # 检查是否需要跳过信号处理
    if getattr(instance, '_skip_signal', False):
        return

    try:
        zapi = ZabbixAPI()
        new_path = instance.get_path()

        # 如果路径发生变化，更新当前节点
        if instance.path != new_path:
            old_path = instance.path
            instance.path = new_path
            # 使用skip_signal避免无限递归
            instance._skip_signal = True
            instance.save()
            # 同步Zabbix主机组
            if new_path != '所有' and instance.model.name == 'hosts':
                if not old_path:
                    # 新建主机组
                    children_count = ModelInstanceGroup.objects.filter(parent=instance.parent).count()
                    logger.info(f'Creating hostgroup: {new_path.replace("所有/", "")}')
                    if instance.parent and children_count == 1:
                        logger.info(f'Delete parent hostgroup '
                                    f'{instance.parent.path.replace("所有/", "")} since it has got children')
                        zapi.delete_hostgroup(instance.parent.path.replace('所有/', ''))
                    zapi.get_or_create_hostgroup(new_path.replace('所有/', ''))
                else:
                    # 重命名主机组
                    logger.info(f'Renaming hostgroup: {old_path.replace("所有/", "")} -> {new_path.replace("所有/", "")}')
                    zapi.rename_hostgroup(
                        old_path.replace('所有/', ''),
                        new_path.replace('所有/', '')
                    )

            # 在路径变化时递归处理所有子节点
            children = ModelInstanceGroup.objects.filter(parent=instance)
            for child in children:
                # 子节点的更新会触发各自的post_save信号
                child._skip_signal = False
                child.save()

    except Exception as e:
        logger.error(f"Update group path error: {str(e)}")

@receiver(pre_save, sender=ModelInstanceGroup)
def cache_old_path(sender, instance, **kwargs):
    """在保存前缓存旧的path值"""
    if not instance.pk or getattr(instance, '_skip_signal', False):
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        instance._old_path = old_instance.path
    except sender.DoesNotExist:
        instance._old_path = None
            
@receiver(post_save, sender=ModelInstanceGroup)
def update_descendant_paths(sender, instance, created, **kwargs):
    """
    当一个 ModelInstanceGroup 的 path 发生变化时，
    异步或在独立事务中递归更新其所有后代分组的 path。
    """
    if created:
        return
    if getattr(instance, '_skip_signal', False) or kwargs.get('_skip_path_update', False):
        return

    old_path = getattr(instance, '_old_path', None)
    new_path = instance.path

    # 只有在 path 确实发生变化时才执行更新
    if old_path != new_path:
        # logger.debug(f"Path for group '{instance.label}' changed from '{old_path}' to '{new_path}'. Triggering descendant path update.")

        def do_update():
            instance.update_child_path()

        transaction.on_commit(do_update)

@receiver(pre_delete, sender=ModelInstanceGroup)
def prepare_delete_instance_group(sender, instance, **kwargs):
    """准备删除实例分组"""
    if not sys_config.is_zabbix_sync_enabled():
        return
    try:
        if instance.model.name != 'hosts':
            return

        # 缓存删除信息，用于post_delete处理
        cache_key = f'delete_instance_group_{instance.id}'
        delete_info = {
            'parent_id': str(instance.parent.id) if instance.parent else None,
            'path': instance.path,
            'parent_path': instance.parent.path if instance.parent else None
        }
        cache.set(cache_key, delete_info, timeout=60)
        logger.debug(f'Cached group deletion info: {delete_info}')

    except Exception as e:
        logger.error(f"Failed to prepare delete instance group: {str(e)}")


@receiver(post_delete, sender=ModelInstanceGroup)
def handle_group_deletion(sender, instance, **kwargs):
    """处理实例分组删除后的操作"""
    if not sys_config.is_zabbix_sync_enabled():
        return
    try:

        if instance.model.name != 'hosts':
            return

        cache_key = f'delete_instance_group_{instance.id}'
        delete_info = cache.get(cache_key)
        if not delete_info:
            logger.warning(f"Missing deletion info for group {instance.id}")
            return

        zapi = ZabbixAPI()

        # 删除Zabbix中对应的主机组
        if instance.path != '所有':
            group_name = instance.path.replace('所有/', '')
            try:
                zapi.delete_hostgroup(group_name)
                logger.info(f'Deleted Zabbix hostgroup: {group_name}')
            except Exception as e:
                logger.error(f"Failed to delete Zabbix hostgroup: {str(e)}")

        # 如果父节点存在且没有其他子节点，则创建父节点的主机组
        if delete_info['parent_id']:
            remaining_children = ModelInstanceGroup.objects.filter(
                parent_id=delete_info['parent_id']
            ).count()

            if remaining_children == 0 and delete_info['parent_path'] != '所有':
                parent_group_name = delete_info['parent_path'].replace('所有/', '')
                try:
                    zapi.get_or_create_hostgroup(parent_group_name)
                    logger.info(f'Recreated parent Zabbix hostgroup: {parent_group_name}')
                except Exception as e:
                    logger.error(f"Failed to recreate parent Zabbix hostgroup: {str(e)}")

        # 清理缓存
        cache.delete(cache_key)

    except Exception as e:
        logger.error(f"Error handling group deletion: {str(e)}")


@receiver(instance_group_relation_updated)
def sync_zabbix_hostgroup_relation(sender, hosts, groups, **kwargs):
    """同步实例分组关联到Zabbix"""
    if not sys_config.is_zabbix_sync_enabled():
        return
    try:
        # 同步主机组关联
        zapi = ZabbixAPI()
        result = zapi.replace_host_hostgroup(hosts, [g.replace('所有/', '') for g in groups])
        logger.info(f'Successfully synced instance group relation to Zabbix: {result}')
    except Exception as e:
        logger.error(f"Error syncing instance groups to Zabbix: {str(e)}")


@receiver(pre_delete, sender=ModelFields)
def check_field_dependencies(sender, instance, **kwargs):
    """删除字段前检查其依赖关系"""
    try:
        model = instance.model
        field_id_str = str(instance.id)

        # 检查字段是否在instance_name_template中使用
        if model.instance_name_template and field_id_str in model.instance_name_template:
            logger.warning(f"Attempt to delete field {instance.name} that is used in instance_name_template")
            raise PermissionDenied({
                'detail': f'Field {instance.name} is used in instance name template and cannot be deleted'
            })

        # 检查字段是否在unique_constraints中使用
        constraints = UniqueConstraint.objects.filter(model=model)

        for constraint in constraints:
            if field_id_str in constraint.fields:
                logger.warning(
                    f"Attempt to delete field {instance.name} that is used in unique constraint")
                raise PermissionDenied({
                    'detail': f'Field {instance.name} is used in unique constraint and cannot be deleted'
                })

        logger.info(f"Field {instance.name} dependency check passed, proceeding with deletion")

    except PermissionDenied:
        raise
    except Exception as e:
        logger.error(f"Error checking field dependencies before delete: {str(e)}")
        raise PermissionDenied({
            'detail': f'Error checking field dependencies: {str(e)}'
        })


@receiver(post_save, sender=ValidationRules)
def on_validation_rule_save(sender, instance, **kwargs):
    if instance.type == ValidationType.ENUM:
        ValidationRules.clear_specific_enum_cache(instance.id)


@receiver(post_delete, sender=ValidationRules)
def on_validation_rule_delete(sender, instance, **kwargs):
    if instance.type == ValidationType.ENUM:
        ValidationRules.clear_specific_enum_cache(instance.id)



# 信跨应用传递信号
# 模型
model_signal = Signal(providing_args=["instance","action"])
@receiver(post_save,sender=Models)
def send_model_created_signal(sender, instance, created, **kwargs):
    """
    模型创建或更新时触发同步
    """
    if created:
        model_signal.send(sender=sender,instance=instance,action='create')
# 实例分组

# 模型实例
model_instance_signal = Signal(providing_args=["instance","action"])
# 创建或更新时，信号同步给node
@receiver(post_save, sender=ModelInstance,dispatch_uid="sync_to_nodes")
def send_model_instance_signal(sender, instance, created, **kwargs):
    model_instance_signal.send(sender=sender, instance=instance,action=created)
#删除时，信号同步给node
@receiver(pre_delete, sender=ModelInstance,dispatch_uid="delete_to_nodes")
def send_model_instance_delete_signal(sender, instance, **kwargs):
    model_instance_signal.send(sender=sender, instance=instance,action='delete')
# @receiver(post_save, sender=ModelInstance,dispatch_uid="111")
# def send_model_instance_signal(sender, instance, created, **kwargs):
#     print(123)
#     if instance.model.name not in model_sync_list:
#         print("模型不在同步列表中，跳过节点同步")
#         return 

