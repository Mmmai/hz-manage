from functools import wraps
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from .models import AuditLog

def audit_log(action):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            if response.status_code in [200, 201, 204]:  # Successful responses
                instance_id = kwargs.get('pk') or request.data.get('id')
                AuditLog.objects.create(
                    action=action,
                    instance_id=instance_id,
                    user=request.user,
                    # Add additional fields as necessary
                )
            return response
        return wrapper
    return decorator

# Method decorator for class-based views
def audit_log_class(action):
    def decorator(cls):
        for method_name in ['create', 'update', 'destroy']:
            if hasattr(cls, method_name):
                original_method = getattr(cls, method_name)

                @wraps(original_method)
                def wrapped_method(self, request, *args, **kwargs):
                    response = original_method(request, *args, **kwargs)
                    if response.status_code in [200, 201, 204]:  # Successful responses
                        instance_id = kwargs.get('pk') or request.data.get('id')
                        AuditLog.objects.create(
                            action=action,
                            instance_id=instance_id,
                            user=request.user,
                            # Add additional fields as necessary
                        )
                    return response

                setattr(cls, method_name, wrapped_method)
        return cls
    return decorator