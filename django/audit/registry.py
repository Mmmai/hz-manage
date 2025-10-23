import logging
from typing import Dict, Type
from django.db import models

logger = logging.getLogger(__name__)

class AuditRegistry:
    """
    统一的模型审计注册中心。
    使用单一的 register 方法，通过配置参数驱动行为。
    """

    def __init__(self):
        self._config: Dict[Type[models.Model], dict] = {}
        self._public_name_map: Dict[str, Type[models.Model]] = {}
        self._model_map: Dict[str, Type[models.Model]] = {}

    def register(self, model: Type[models.Model], **kwargs):
        """统一的注册方法。"""
        kwargs['ignore_fields'] = set(kwargs.get('ignore_fields', []))
        self._config[model] = kwargs
        
        public_name = kwargs.get('public_name')
        if public_name:
            if public_name in self._public_name_map:
                raise ValueError(f"Public name '{public_name}' 已被注册给模型 {self._public_name_map[public_name].__name__}。")
            self._public_name_map[public_name] = model
            self._model_map[model] = public_name
            logger.debug(f"Registered model {model} with public name '{public_name}' in AuditRegistry.")

    def is_registered(self, model: Type[models.Model]) -> bool:
        """检查一个模型是否已被注册"""
        return model in self._config

    def config(self, model: Type[models.Model]) -> dict:
        """获取一个已注册模型的配置"""
        return self._config.get(model, {})

    def is_field_aware(self, model: Type[models.Model]) -> bool:
        """检查一个模型是否被配置为“字段感知”"""
        return self.config(model).get('is_field_aware', False)
    
    def get_model_by_public_name(self, public_name: str) -> Type[models.Model]:
        """通过公开名称获取模型类"""
        return self._public_name_map.get(public_name)
    
    def get_public_name_by_model(self, model: Type[models.Model]) -> str:
        """通过模型类获取公开名称"""
        return self._model_map.get(model)
    
    def get_snapshot_fields(self, model: Type[models.Model]) -> set:
        """获取模型的快照字段配置"""
        return set(self.config(model).get('snapshot_fields', {'id'}))

    def get_field_resolver(self, model: Type[models.Model], field_name: str) -> callable:
        """获取模型的字段解析器配置"""
        return self.config(model).get('field_resolvers', {}).get(field_name)

    def get_dynamic_value_resolver(self, model: Type[models.Model]) -> callable:
        """获取模型的动态值解析器配置"""
        return self.config(model).get('dynamic_value_resolver')

registry = AuditRegistry()