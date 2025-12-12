import logging

logger = logging.getLogger(__name__)

# 全局注册表，用于存储 app_label -> handler_function 的映射
INDIRECT_PERMISSION_HANDLERS = {}


def register_indirect_permission_handler(app_label, handler_func):
    """
    注册一个用于处理特定 app 间接权限的函数。
    """
    if app_label in INDIRECT_PERMISSION_HANDLERS:
        logger.warning(f"Handler for app '{app_label}' is being overridden.")

    logger.info(f"Registering indirect permission handler for app: '{app_label}'")
    INDIRECT_PERMISSION_HANDLERS[app_label] = handler_func


def get_handler(app_label):
    """
    获取注册的间接权限处理器函数。
    """
    return INDIRECT_PERMISSION_HANDLERS.get(app_label)
