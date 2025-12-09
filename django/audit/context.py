from contextvars import ContextVar, Token
from contextlib import contextmanager
from typing import Dict, Any


# 默认的上下文状态
DEFAULT_CONTEXT: Dict[str, Any] = {
    "channel": "api",
    "request_id": None,
    "correlation_id": None,
    "operator": "anonymous",
    "operator_ip": None,
    "is_rollback": False,
    "reverted_from": None,
    "comment": ""
}

audit_context_var: ContextVar[Dict[str, Any]] = ContextVar(
    "audit_context", default=DEFAULT_CONTEXT.copy()
)


@contextmanager
def audit_context(**kwargs):
    """
    一个健壮的上下文管理器，用于安全地设置和恢复审计上下文。
    这是修改上下文的唯一推荐方式。
    """
    # 获取当前上下文，并用传入的参数进行更新
    current_context = audit_context_var.get()
    new_context = {**current_context, **kwargs}
    
    # 设置新值并保存 token
    token: Token = audit_context_var.set(new_context)
    try:
        yield
    finally:
        # 无论如何，最终都会使用 token 恢复到之前的状态
        audit_context_var.reset(token)


def get_audit_context() -> Dict[str, Any]:
    """获取当前完整的审计上下文（只读）。"""
    return audit_context_var.get()


def get_context_value(key: str, default: Any = None) -> Any:
    """从上下文中获取单个值。"""
    return audit_context_var.get().get(key, default)

