import threading
import uuid
from django.utils.deprecation import MiddlewareMixin

# 线程本地存储
_thread_local = threading.local()


def get_current_user():
    """获取当前请求的用户"""
    if hasattr(_thread_local, 'user'):
        return _thread_local.user
    return None


def get_current_ip():
    """获取当前请求的IP地址"""
    if hasattr(_thread_local, 'ip'):
        return _thread_local.ip
    return None


def get_current_request_id():
    """获取当前请求ID，如果不存在则创建"""
    if not hasattr(_thread_local, 'request_id'):
        _thread_local.request_id = str(uuid.uuid4())
    return _thread_local.request_id


def get_audit_context():
    """获取完整的审计上下文"""
    return {
        'user': get_current_user(),
        'ip': get_current_ip(),
        'request_id': get_current_request_id(),
        # 可以扩展更多上下文信息
    }


class AuditContextMiddleware(MiddlewareMixin):
    """审计上下文中间件"""

    def process_request(self, request):
        """处理请求，保存审计上下文"""
        # 保存用户信息
        if hasattr(request, 'user'):
            _thread_local.user = request.user

        # 保存IP地址
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            _thread_local.ip = x_forwarded_for.split(',')[0]
        else:
            _thread_local.ip = request.META.get('REMOTE_ADDR')

        # 生成请求ID - 每个HTTP请求一个唯一ID
        _thread_local.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        """清理线程本地变量"""
        if hasattr(_thread_local, 'user'):
            delattr(_thread_local, 'user')
        if hasattr(_thread_local, 'ip'):
            delattr(_thread_local, 'ip')
        if hasattr(_thread_local, 'request_id'):
            delattr(_thread_local, 'request_id')

        return response
