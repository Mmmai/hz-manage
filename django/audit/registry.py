from typing import Dict, Type, Set
from django.db import models


class AuditRegistry:
    """
    注册模型及其审计策略
    """

    def __init__(self):
        self._schema_models = set()
        self._instance_models = set()
        self._field_aware_models: Set[Type[models.Model]] = set()
        self._config: Dict[Type[models.Model], dict] = {}

    def register_schema(self, model, *, ignore_fields=None, field_tracker=None):
        """注册模式变更审计"""
        self._schema_models.add(model)
        self._config[model] = {
            "ignore_fields": set(ignore_fields or []),
            "field_tracker": field_tracker
        }

    def register_instance(self, model, *, ignore_fields=None, field_tracker=None):
        """注册实例变更审计"""
        self._instance_models.add(model)
        self._config[model] = {
            "ignore_fields": set(ignore_fields or []),
            "field_tracker": field_tracker
        }

    def register_field_aware(self, model, *, field_definition_model, field_value_model,
                             instance_field_name='model_instance'):
        """
        注册字段感知模型（用于CMDB动态字段）
        这会同时将其注册为实例模型。
        """
        self.register_instance(model)
        self._field_aware_models.add(model)
        current_config = self._config.get(model, {})
        current_config.update({
            "field_definition_model": field_definition_model,
            "field_value_model": field_value_model,
            "instance_field_name": instance_field_name,
            "is_field_aware": True
        })
        self._config[model] = current_config

    def is_schema(self, model):
        return model in self._schema_models

    def is_instance(self, model):
        return model in self._instance_models

    def is_field_aware(self, model):
        """检查模型是否被注册为字段感知"""
        return model in self._field_aware_models

    def config(self, model):
        return self._config.get(model, {})


registry = AuditRegistry()
