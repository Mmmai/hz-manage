import uuid
from . import context


class AuditContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = getattr(request, "request_id", None) or str(uuid.uuid4())
        context.set_ctx(
            operator_id=getattr(getattr(request, "user", None), "id", None),
            operator_name=getattr(getattr(request, "user", None), "username", None),
            channel="api",
            request_id=rid,
            correlation_id=rid,
            source_ip=self._client_ip(request),
        )
        try:
            return self.get_response(request)
        finally:
            context.clear()

    def _client_ip(self, request):
        return request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
