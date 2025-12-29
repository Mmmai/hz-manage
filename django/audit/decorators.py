"""
审计装饰器模块
提供用于声明模型审计需求的类装饰器。
"""
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

    可接收的参数
    通用参数：
    - ignore_fields: List[str] - 指定不需要审计的字段列表
    - public_name: str - 用于api提交及查询指定对应模型的名称
    - snapshot_fields: List[str] - 当前模型作为外键字段被审计快照保存时指定需要保存的字段列表

    特殊参数：
    - field_resolvers: Dict[str, Callable] - 字段解析器映射，用于动态解析某些字段的值
    - m2m_fields: List[str] - 指定需要审计的ManyToMany字段列表
    - is_field_aware: bool - 指示模型是否为动态字段感知模型（仅用于CMDB实例）
    - restorer: Callable - 自定义的回退函数
    - locker: Callable - 自定义的数据库加锁函数
    """
    def wrapper(model_class):
        registry.register(model_class, **kwargs)
        return model_class
    return wrapper
