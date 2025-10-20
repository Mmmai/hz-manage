import uuid
import logging
from functools import wraps
from .registry import registry
from .context import audit_context

logger = logging.getLogger(__name__)

def register_audit(**kwargs):
    """
    一个类装饰器，用于声明一个模型需要被审计。
    它会将模型和所有配置参数传递给审计注册中心。
    """
    def wrapper(model_class):
        registry.register(model_class, **kwargs)
        return model_class
    return wrapper
