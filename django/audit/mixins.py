import uuid
import logging
from .context import audit_context

logger = logging.getLogger(__name__)

class AuditContextMixin:
    """
    通过重写 initial 和 dispatch 方法，在DRF认证后设置审计上下文，并在请求结束时安全地清理。
    """
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        operator_name = "anonymous"

        if request.user:
            operator_name = request.user.username
        self.request.username = operator_name
        
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        source_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        request_id = str(uuid.uuid4())
        context_data = {
            "request_id": request_id,
            "correlation_id": request_id,
            "operator": operator_name,
            "operator_ip": source_ip,
        }
        # logger.debug(f"Context data prepared in initial(): {context_data}")
        self.audit_context = context_data
        self._audit_context_manager = audit_context(**context_data)
        self._audit_context_manager.__enter__()
        # logger.debug(f"--- Entering Audit Context via initial(): {context_data} ---")

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            if hasattr(self, '_audit_context_manager'):
                self._audit_context_manager.__exit__(None, None, None)
                # logger.debug("--- Exiting Audit Context ---")
                
    def get_audit_context(self):
        """获取当前请求的审计上下文。"""
        return getattr(self, 'audit_context', {})