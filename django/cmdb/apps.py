import os
import tempfile
from django.apps import AppConfig
from django.db import transaction
from django.db.utils import OperationalError
from cacheops import invalidate_all
import portalocker
from .config import BUILT_IN_MODELS, BUILT_IN_VALIDATION_RULES
from .utils import password_handler
import logging
import json

logger = logging.getLogger(__name__)

class CMDBConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cmdb'
    label = 'cmdb'
    
    def _create_model_and_fields(self, model_name, model_config, model_group=None):
        """创建内置模型和相关字段"""
        from .models import (
            Models, 
            ModelFields, 
            ModelFieldGroups, 
            ValidationRules, 
            ModelFieldPreference,
            ModelInstanceGroup,
            UniqueConstraint,
        )
        from .serializers import (
            ModelsSerializer, 
            ModelFieldsSerializer, 
            ModelFieldGroupsSerializer, 
            ValidationRulesSerializer, 
            ModelFieldPreferenceSerializer,
            ModelInstanceGroupSerializer,
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
            
            # 创建字段
            for field_config in model_config.get('fields', []):
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
                            continue
                        
                    field_data = {
                        'model': model.id,
                        'name': field_name,
                        'verbose_name': field_config.get('verbose_name', ''),
                        'type': field_config['type'],
                        'required': field_config.get('required', False),
                        'editable': field_config.get('editable', True),
                        'description': field_config.get('description', ''),
                        'order': field_config.get('order'),
                        'validation_rule': validation_rule.id if validation_rule else None,
                        'default': field_config.get('default', None),
                        'built_in': True,
                        'ref_model': ref_model.id if ref_model else None,
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
                    'fields_preferred': [ str(f) for f in preferred_fields ],
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
            if model_name in ['hosts', 'switches', 'firewalls', 'dwdm'] and \
                not UniqueConstraint.objects.filter(model=model, fields=['ip']).exists():
                unique_constraint_data = {
                    'model': model.id,
                    'fields': ['ip'],
                    'built_in': True,
                    'create_user': 'system',
                    'update_user': 'system'
                }
                
                unique_constraint_serializer = UniqueConstraintSerializer(data=unique_constraint_data)
                if unique_constraint_serializer.is_valid(raise_exception=True):
                    unique_constraint_serializer.save()
                    logger.info(f"Created unique constraint for model {model_name}")
                else:
                    logger.error(f"Unique constraint validation failed: {unique_constraint_serializer.errors}")

            
        except Exception as e:
            logger.error(f"Error creating model and fields for {model_name}: {str(e)}")
            raise

    def _initialize_validation_rules(self):
        """初始化验证规则"""
        from .models import ValidationRules
        from .serializers import ValidationRulesSerializer
        
        for name, rule_config in BUILT_IN_VALIDATION_RULES.items():
            try:
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

    def _initialize_lock(self):
        """获取文件锁"""
        lock_file = os.path.join(tempfile.gettempdir(), 'cmdb_init.lock')
        self._lock_fd = open(lock_file, 'w')
        try:
            portalocker.lock(self._lock_fd, portalocker.LOCK_EX | portalocker.LOCK_NB)
            logger.info("Acquired lock for CMDB initialization")
            return True
        except (IOError, BlockingIOError):
            return False
        
    def _release_lock(self):
        """释放文件锁"""
        if self._lock_fd:
            try:
                portalocker.unlock(self._lock_fd)
            finally:
                self._lock_fd.close()
                logger.info("Released lock for CMDB initialization")

    def ready(self):
        """应用启动时初始化内置模型和验证规则"""
        try:
            import sys
            if any(keyword in sys.argv for keyword in ['makemigrations', 'migrate', 'test', 'shell']):
                return
            elif 'runserver' in sys.argv:
                # 清除缓存
                invalidate_all()
            
            if not self._initialize_lock():
                logger.info("Another process is initializing, skipping")
                return
            
            password_handler.load_keys()
            with transaction.atomic():
                from .models import ModelGroups
                from .serializers import ModelGroupsSerializer
                
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
                    
                # 创建验证规则
                self._initialize_validation_rules()
                
                # 创建内置模型及其字段配置
                for model_name, model_config in BUILT_IN_MODELS.items():
                    group_name = model_config.get('model_group')
                    model_group = model_groups.get(group_name, model_groups['others'])
                    self._create_model_and_fields(model_name, model_config, model_group)
                    
        except OperationalError:
            logger.warning("Database not ready, skipping initialization")
        except Exception as e:
            logger.error(f"Error during initialization: {str(e)}")
        finally:
            self._release_lock()
        
        from .signals import create_field_meta_for_instances